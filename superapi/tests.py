from django.test import TestCase
from django.utils.translation import ugettext_lazy as _
from django.core.validators import EmailValidator
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from api.models import *
from tokenapi.tokens import token_generator
import json

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
            "questionList": '1',
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

    def testAddWrongSpot(self):
        r = self.client.post('/superapi/spots/', data=json.dumps({
            'user_id': self.test_admin.pk,
            'token': self.token,
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 401, "[SUPERAPI][SpotAddTest] Wrong status code")
