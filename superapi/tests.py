from django.test import TestCase
from django.utils.translation import ugettext_lazy as _
from django.core.validators import EmailValidator
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from api.models import *
from tokenapi.tokens import token_generator
import json, math

JSON_CONTENT_TYPE = 'application/json'
# Create your tests here.

class AuthTest(TestCase):

    def setUp(self):
        self.test_admin1 = User.objects.create_user(username='admin1', email='admin1@myemail.com', password='ada1pass', is_staff=True)
        self.assertNotEqual(self.test_admin1, None, "[API][Auth] Could not create test user.")

    def testEmptyInput(self):
        r = self.client.post('/superapi/auth/', data={}, content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 403, "[API][Auth] Wrong status code.")
        self.assertEqual(r.json(), "Must include 'username' and 'password' as parameters.",
                         "[API][Auth] Wrong error message.")

    def testBadPassword(self):
        r = self.client.post('/superapi/auth/', data=json.dumps({
            'username': 'admin1',
            'password': 'verywrongpass'
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 403, "[API][Auth] Wrong status code.")
        self.assertEqual(r.json(), "Unable to log you in, please try again.", "[API][Auth] Wrong error message.")

    def testGoodPassword(self):
        r = self.client.post('/superapi/auth/', data=json.dumps({
            'username': 'admin1',
            'password': 'ada1pass'
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 200, "[API][Auth] Wrong status code.")
        data = r.json()
        self.assertEqual(token_generator.make_token(self.test_admin1), data['token'], "[API][Auth] Wrong token.")
        self.assertEqual(self.test_admin1.pk, data['user_id'], "[API][Auth] Wrong user_id")


class SpotTest(TestCase):

    def setUp(self):
        self.test_admin = User.objects.create_user(username='admin1', email='admin1@myemail.com', password='ada1pass', is_staff=True)
        self.test_question = Question(
            questionText='Would a woodchuck ... ?',
            answer1='Yes',
            answer2='No',
            answer3='I said Yes',
            answer4="YOU'RE WRONG",
            difficulty=100,
            score=100,
            topic='Memetics',
            rightAnswer=1
        )
        self.test_question.save()
        self.test_spot = Spot(
            centrex=-2.569111,
            centrey=1.256950,
            centrez=0,
            currentQuestion=self.test_question,
            delay=0,
            rayon=5,
            questionList='1',
        )
        self.test_spot.save()
        self.token = token_generator.make_token(self.test_admin)
        self.info = {
            "centrex": self.test_spot.centrex,
            "centrey": self.test_spot.centrey,
            "centrez": self.test_spot.centrez,
            "rayon": self.test_spot.rayon,
            "startTime": self.test_spot.startTime,
            "delay": self.test_spot.delay,
            "currentQuestion": {
                'id': self.test_question.id,
                'question': self.test_question.questionText,
                'answer1': self.test_question.answer1,
                'answer2': self.test_question.answer2,
                'answer3': self.test_question.answer3,
                'answer4': self.test_question.answer4,
                'score': self.test_question.score,
                'difficulty': self.test_question.difficulty,
                'topic': self.test_question.topic
            },
            "questions": [{
                'id': self.test_question.id,
                'question': self.test_question.questionText,
                'answer1': self.test_question.answer1,
                'answer2': self.test_question.answer2,
                'answer3': self.test_question.answer3,
                'answer4': self.test_question.answer4,
                'score': self.test_question.score,
                'difficulty': self.test_question.difficulty,
                'topic': self.test_question.topic
            }]
        }
        self.maxDiff = None

    def testSpotView(self):
        r = self.client.get('/superapi/spots/', data={
            'user_id': self.test_admin.pk,
            'token': self.token,
        }, content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 200, "[SUPERAPI][SpotTest] Wrong status code")
        self.assertEqual(r.json(), {"spots": [self.info]}, "[SUPERAPI][SpotTest] Wrong information")

    def testOneSpotView(self):
        r = self.client.get('/superapi/spots/1/', data={
            'user_id': self.test_admin.pk,
            'token': self.token,
        }, content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 200, "[SUPERAPI][SpotTest] Wrong status code")
        self.assertEqual(r.json(), self.info, "[SUPERAPI][SpotTest] Wrong information")

    def testInexistentSpotView(self):
        r = self.client.get('/superapi/spots/15/', data={
            'user_id': self.test_admin.pk,
            'token': self.token,
        }, content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 404, "[SUPERAPI][SpotTest] Wrong status code")


class SpotAddTest(TestCase):
    #ToDo Add a spot with a list of questions (more than 1)
    def setUp(self):
        self.test_admin = User.objects.create_user(username='admin1', email='admin1@myemail.com', password='ada1pass', is_staff=True)
        self.test_question = Question(
            questionText='Would a woodchuck ... ?',
            answer1='Yes',
            answer2='No',
            answer3='I said Yes',
            answer4="YOU'RE WRONG",
            difficulty=100,
            score=100,
            topic='Memetics',
            rightAnswer=1
        )
        self.test_question.save()
        self.test_spot = {
            "centrex": -2.569111,
            "centrey": 1.256950,
            "centrez": 0,
            "currentQuestion": 1,
            "delay": 0,
            "rayon": 5,
            "questionList": [1],
            "startTime": getTime()
        }
        self.token = token_generator.make_token(self.test_admin)

    def testAddSpot(self):
        r = self.client.post('/superapi/spots/', data=json.dumps({
            'user_id': self.test_admin.pk,
            'token': self.token,
            'spot': self.test_spot
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 200, "[SUPERAPI][SpotAddTest] Wrong status code")

    def testAddEmptySpot(self):
        r = self.client.post('/superapi/spots/', data=json.dumps({
            'user_id': self.test_admin.pk,
            'token': self.token,
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 401, "[SUPERAPI][SpotAddTest] Wrong status code")

    def testAddWrongSpot(self):
        self.test_spot['centrex'] = 92.0
        r = self.client.post('/superapi/spots/', data=json.dumps({
            'user_id': self.test_admin.pk,
            'token': self.token,
            'spot': self.test_spot
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 401, "[SUPERAPI][SpotAddTest] Wrong status code")
        self.assertEqual(r.json(), 'Latitude and Longitude are out of range.', "[SUPERAPI][SpotAddTest] Wrong reason")

        self.test_spot['centrex'] = math.inf
        r = self.client.post('/superapi/spots/', data=json.dumps({
            'user_id': self.test_admin.pk,
            'token': self.token,
            'spot': self.test_spot
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 401, "[SUPERAPI][SpotAddTest] Wrong status code")
        self.assertEqual(r.json(), 'Spot coordinates can\'t be infinity or NaN.', "[SUPERAPI][SpotAddTest] Wrong reason")

        self.test_spot.pop('centrex')
        r = self.client.post('/superapi/spots/', data=json.dumps({
            'user_id': self.test_admin.pk,
            'token': self.token,
            'spot': self.test_spot
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 401, "[SUPERAPI][SpotAddTest] Wrong status code")
        self.assertEqual(r.json(), 'Malformed JSON input.', "[SUPERAPI][SpotAddTest] Wrong reason")

        self.test_spot['centrex'] = 'x'
        r = self.client.post('/superapi/spots/', data=json.dumps({
            'user_id': self.test_admin.pk,
            'token': self.token,
            'spot': self.test_spot
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 401, "[SUPERAPI][SpotAddTest] Wrong status code")
        self.assertEqual(r.json(), 'Unable to parse correct numeric literals.', "[SUPERAPI][SpotAddTest] Wrong reason")

        r = self.client.post('/superapi/spots/', data=json.dumps({
            'user_id': self.test_admin.pk,
            'token': self.token,
            'spot': [self.test_spot]
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 401, "[SUPERAPI][SpotAddTest] Wrong status code")
        self.assertEqual(r.json(), 'Malformed JSON input.', "[SUPERAPI][SpotAddTest] Wrong reason")

        self.test_spot['centrex'] = -2.569111
        self.test_spot['questionList'] = '7'
        r = self.client.post('/superapi/spots/', data=json.dumps({
            'user_id': self.test_admin.pk,
            'token': self.token,
            'spot': self.test_spot
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 401, "[SUPERAPI][SpotAddTest] Wrong status code")
        self.assertEqual(r.json(), 'Unable to parse correct question list.', "[SUPERAPI][SpotAddTest] Wrong reason")

        self.test_spot['questionList'] = []
        r = self.client.post('/superapi/spots/', data=json.dumps({
            'user_id': self.test_admin.pk,
            'token': self.token,
            'spot': self.test_spot
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 401, "[SUPERAPI][SpotAddTest] Wrong status code")
        self.assertEqual(r.json(), 'A spot needs at least one question.', "[SUPERAPI][SpotAddTest] Wrong reason")

        self.test_spot['questionList'] = [2]
        r = self.client.post('/superapi/spots/', data=json.dumps({
            'user_id': self.test_admin.pk,
            'token': self.token,
            'spot': self.test_spot
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 401, "[SUPERAPI][SpotAddTest] Wrong status code")
        self.assertEqual(r.json(), 'Incorrect question IDs in questionList.', "[SUPERAPI][SpotAddTest] Wrong reason")

        self.test_spot['questionList'] = [1]
        self.test_spot['currentQuestion'] = 2
        r = self.client.post('/superapi/spots/', data=json.dumps({
            'user_id': self.test_admin.pk,
            'token': self.token,
            'spot': self.test_spot
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 401, "[SUPERAPI][SpotAddTest] Wrong status code")
        self.assertEqual(r.json(), 'Unable find chosen currentQuestion with provided ID.', "[SUPERAPI][SpotAddTest] Wrong reason")


class SpotDeleteTest(TestCase):

    def setUp(self):
        self.test_admin = User.objects.create_user(username='admin1', email='admin1@myemail.com', password='ada1pass', is_staff=True)
        self.test_question = Question(
            questionText='Would a woodchuck ... ?',
            answer1='Yes',
            answer2='No',
            answer3='I said Yes',
            answer4="YOU'RE WRONG",
            difficulty=100,
            score=100,
            topic='Memetics',
            rightAnswer=1
        )
        self.test_question.save()
        self.test_spot = Spot(
            centrex=-2.569111,
            centrey=1.256950,
            centrez=0,
            currentQuestion=self.test_question,
            delay=0,
            rayon=5,
            questionList='1',
        )
        self.test_spot.save()
        self.token = token_generator.make_token(self.test_admin)

    def testDeleteSpot(self):
        r = self.client.delete('/superapi/spots/1/', data=json.dumps({
            'user_id': self.test_admin.pk,
            'token': self.token
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 200, "[SUPERAPI][DeleteSpotTest] Wrong status code")
        self.assertEqual(r.json(), 'Spot successfully deleted.', "[SUPERAPI][DeleteSpotTest] Wrong reason")


class QuestionViewTest(TestCase):

    def setUp(self):
        self.test_admin = User.objects.create_user(username='admin1', email='admin1@myemail.com', password='ada1pass', is_staff=True)
        self.test_question = Question(
            questionText='Would a woodchuck ... ?',
            answer1='Yes',
            answer2='No',
            answer3='I said Yes',
            answer4="YOU'RE WRONG",
            difficulty=100,
            score=100,
            topic='Memetics',
            rightAnswer=1
        )
        self.test_question.save()
        self.questionInfo = {
                'id': self.test_question.id,
                'question': self.test_question.questionText,
                'answer1': self.test_question.answer1,
                'answer2': self.test_question.answer2,
                'answer3': self.test_question.answer3,
                'answer4': self.test_question.answer4,
                'score': self.test_question.score,
                'difficulty': self.test_question.difficulty,
                'topic': self.test_question.topic
            }
        self.token = token_generator.make_token(self.test_admin)

    def testAllQuestion(self):
        r = self.client.get('/superapi/questions/', data={
            'user_id': self.test_admin.pk,
            'token': self.token
        }, content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 200, "[SUPERAPI][QuestionViewTest] Wrong status code")
        self.assertEqual(r.json()['questions'], [self.questionInfo], "[SUPERAPI][QuestionViewTest] Wrong information")

    def testOneQuestion(self):
        r = self.client.get('/superapi/questions/1/', data={
            'user_id': self.test_admin.pk,
            'token': self.token
        }, content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 200, "[SUPERAPI][QuestionViewTest] Wrong status code")
        self.assertEqual(r.json(), self.questionInfo, "[SUPERAPI][QuestionViewTest] Wrong information")

    def testInexistentQuestion(self):
        r = self.client.get('/superapi/questions/5/', data={
            'user_id': self.test_admin.pk,
            'token': self.token
        }, content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 404, "[SUPERAPI][QuestionViewTest] Wrong status code")
        self.assertEqual(r.json(), 'Question not Found', "[SUPERAPI][QuestionViewTest] Wrong reason")


class QuestionAddTest(TestCase):

    def setUp(self):
        self.test_admin = User.objects.create_user(username='admin1', email='admin1@myemail.com', password='ada1pass', is_staff=True)
        self.test_question = {
            "questionText": 'Would a woodchuck ... ?',
            "answer1": 'Yes',
            "answer2": 'No',
            "answer3": 'I said Yes',
            "answer4": "YOU'RE WRONG",
            "difficulty": 100,
            "score": 100,
            "topic": 'Memetics',
            "rightAnswer": 1
        }
        self.token = token_generator.make_token(self.test_admin)

    def testAddQuestion(self):
        r = self.client.post('/superapi/questions/', data=json.dumps({
            'user_id': self.test_admin.pk,
            'token': self.token,
            'question': self.test_question
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 200, "[SUPERAPI][SpotAddTest] Wrong status code")