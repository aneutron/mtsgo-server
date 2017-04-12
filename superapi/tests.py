# -*- coding: utf8 -*-
from django.test import TestCase
from api.models import *
from tokenapi.tokens import token_generator
from numpy import inf as np_inf
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
        r = self.client.get('/superapi/spots/'+str(self.test_spot.pk)+'/', data={
            'user_id': self.test_admin.pk,
            'token': self.token,
        }, content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 200, "[SUPERAPI][SpotTest] Wrong status code")
        self.assertEqual(r.json(), self.info, "[SUPERAPI][SpotTest] Wrong information")

    def testInexistentSpotView(self):
        r = self.client.get('/superapi/spots/15555/', data={
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
            "questionList": [self.test_question.pk],
            "startTime": get_time()
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

        self.test_spot['centrex'] = np_inf
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
            questionList=str(self.test_question.pk),
        )
        self.test_spot.save()
        self.token = token_generator.make_token(self.test_admin)

    def testDeleteSpot(self):
        r = self.client.delete('/superapi/spots/'+str(self.test_spot.pk)+'/', data=json.dumps({
            'user_id': self.test_admin.pk,
            'token': self.token
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 200, "[SUPERAPI][DeleteSpotTest] Wrong status code")
        self.assertEqual(r.json(), 'Spot successfully deleted.', "[SUPERAPI][DeleteSpotTest] Wrong reason")

        r = self.client.delete('/superapi/spots/156985/', data=json.dumps({
            'user_id': self.test_admin.pk,
            'token': self.token
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 404, "[SUPERAPI][DeleteSpotTest] Wrong status code")
        self.assertEqual(r.json(), 'Spot with ID=' + '156985' + ' not found.', "[SUPERAPI][DeleteSpotTest] Wrong reason")


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
        r = self.client.get('/superapi/questions/'+str(self.test_question.pk)+'/', data={
            'user_id': self.test_admin.pk,
            'token': self.token
        }, content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 200, "[SUPERAPI][QuestionViewTest] Wrong status code")
        self.assertEqual(r.json(), self.questionInfo, "[SUPERAPI][QuestionViewTest] Wrong information")

    def testInexistentQuestion(self):
        r = self.client.get('/superapi/questions/56985/', data={
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
        self.assertEqual(r.status_code, 200, "[SUPERAPI][QuestionAddTest] Wrong status code")

    def testAddEmptyQuestion(self):
        r = self.client.post('/superapi/questions/', data=json.dumps({
            'user_id': self.test_admin.pk,
            'token': self.token,
            'ques': self.test_question
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 401, "[SUPERAPI][QuestionAddTest] Wrong status code")
        self.assertEqual(r.json(), 'Invalid JSON input.', "[SUPERAPI][QuestionAddTest] Wrong reason")

    def testAddWrongEntryQuestion(self):
        self.test_question.pop('topic')
        r = self.client.post('/superapi/questions/', data=json.dumps({
            'user_id': self.test_admin.pk,
            'token': self.token,
            'question': self.test_question
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 401, "[SUPERAPI][QuestionAddTest] Wrong status code")
        self.assertEqual(r.json(), 'Invalid JSON input.', "[SUPERAPI][QuestionAddTest] Wrong reason")

    def testAddWrongQuestion(self):
        self.test_question['score'] = 'hundred'
        r = self.client.post('/superapi/questions/', data=json.dumps({
            'user_id': self.test_admin.pk,
            'token': self.token,
            'question': self.test_question
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 401, "[SUPERAPI][QuestionAddTest] Wrong status code")
        self.assertEqual(r.json(), 'Unable to parse correct numeric literals.', "[SUPERAPI][QuestionAddTest] Wrong reason")


class QuestionUpdateTest(TestCase):

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
        self.question = Question(
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
        self.question.save()
        self.token = token_generator.make_token(self.test_admin)

    def testUpdateQuestion(self):
        r = self.client.post('/superapi/questions/'+str(self.question.pk)+'/', data=json.dumps({
            'user_id': self.test_admin.pk,
            'token': self.token,
            'question': self.test_question
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 200, "[SUPERAPI][QuestionUpdateTest] Wrong status code")
        self.assertEqual(r.json(), 'Question updated successfully.', "[SUPERAPI][QuestionUpdateTest] Wrong reason")

    def testUpdateInexistentQuestion(self):
        r = self.client.post('/superapi/questions/987965/', data=json.dumps({
            'user_id': self.test_admin.pk,
            'token': self.token,
            'question': self.test_question
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 404, "[SUPERAPI][QuestionUpdateTest] Wrong status code")
        self.assertEqual(r.json(), 'Question with ID='+'987965'+' not found.', "[SUPERAPI][QuestionUpdateTest] Wrong reason")

    def testUpdateWrongQuestion(self):
        self.test_question['difficulty']='hard'
        r = self.client.post('/superapi/questions/'+str(self.question.pk)+'/', data=json.dumps({
            'user_id': self.test_admin.pk,
            'token': self.token,
            'question': self.test_question
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 401, "[SUPERAPI][QuestionUpdateTest] Wrong status code")
        self.assertEqual(r.json(), 'Unable to parse correct numeric literals.', "[SUPERAPI][QuestionUpdateTest] Wrong reason")

    def testUpdateWrongEntryQuestion(self):
        r = self.client.post('/superapi/questions/'+str(self.question.pk)+'/', data=json.dumps({
            'user_id': self.test_admin.pk,
            'token': self.token,
            'ques': self.test_question
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 401, "[SUPERAPI][QuestionUpdateTest] Wrong status code")
        self.assertEqual(r.json(), 'Invalid JSON input.', "[SUPERAPI][QuestionUpdateTest] Wrong reason")

    def testUpdateWrongKeysQuestion(self):
        self.test_question.pop('topic')
        r = self.client.post('/superapi/questions/'+str(self.question.pk)+'/', data=json.dumps({
            'user_id': self.test_admin.pk,
            'token': self.token,
            'question': self.test_question
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 401, "[SUPERAPI][QuestionUpdateTest] Wrong status code")
        self.assertEqual(r.json(), 'Invalid JSON input.', "[SUPERAPI][QuestionUpdateTest] Wrong reason")


class ServerStateViewTest(TestCase):

    def setUp(self):
        self.test_admin = User.objects.create_user(username='admin1', email='admin1@myemail.com', password='ada1pass', is_staff=True)
        self.token = token_generator.make_token(self.test_admin)

    def testGetServerState(self):
        r = self.client.get('/superapi/state/', data={
            'user_id': self.test_admin.pk,
            'token': self.token,
        }, content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 200, "[SUPERAPI][ServerStateViewTest] Wrong status code")


class PlayerPositionViewTest(TestCase):

    def setUp(self):
        self.test_user1 = User.objects.create_user(username='user1', email='user1@myemail.com', password='uza1pass')
        self.player = Player(account=self.test_user1)
        self.player.positionx = -2.569110
        self.player.positiony = 1.256957
        self.player.save()
        self.playerInfo1 = {'id': self.player.pk, 'x': -2.569110, 'y': 1.256957, 'z': 0.0}

        self.test_user2 = User.objects.create_user(username='user2', email='user2@myemail.com', password='uza2pass')
        self.player = Player(account=self.test_user2)
        self.player.positionx = -3.569110
        self.player.positiony = 2.256957
        self.player.save()
        self.playerInfo2 = {'id': self.player.pk, 'x': -3.569110, 'y': 2.256957, 'z': 0.0}

        self.test_admin = User.objects.create_user(username='admin1', email='admin1@myemail.com', password='ada1pass', is_staff=True)
        self.token = token_generator.make_token(self.test_admin)

    def testGetAllPosition(self):
        r = self.client.get('/superapi/position/', data={
            'user_id': self.test_admin.pk,
            'token': self.token,
        }, content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 200, "[SUPERAPI][PlayerPositionViewTest] Wrong status code")
        self.assertEqual(r.json().sort(key=lambda i: i['id']), [self.playerInfo1,self.playerInfo2].sort(key=lambda i: i['id']), "[SUPERAPI][PlayerPositionViewTest] Wrong information")

    def testGetOnePosition(self):
        r = self.client.get('/superapi/position/'+str(self.player.pk)+'/', data={
            'user_id': self.test_admin.pk,
            'token': self.token,
        }, content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 200, "[SUPERAPI][PlayerPositionViewTest] Wrong status code")
        self.assertEqual(r.json(), self.playerInfo1, "[SUPERAPI][PlayerPositionViewTest] Wrong information")

    def testGetInexistentPosition(self):
        r = self.client.get('/superapi/position/158959/', data={
            'user_id': self.test_admin.pk,
            'token': self.token,
        }, content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 404, "[SUPERAPI][PlayerPositionViewTest] Wrong status code")
        self.assertEqual(r.json(), 'Unable to find player with ID='+'158959'+'.', "[SUPERAPI][PlayerPositionViewTest] Wrong reason")


class StatsViewTest(TestCase):

    def setUp(self):
        self.test_user1 = User.objects.create_user(username='user1', email='user1@myemail.com', password='uza1pass')
        self.player = Player(account=self.test_user1)
        self.player.positionx = -2.569110
        self.player.positiony = 1.256957
        self.player.lastActivity = get_time() - 1000
        self.player.save()

        self.test_user2 = User.objects.create_user(username='user2', email='user2@myemail.com', password='uza2pass')
        self.player = Player(account=self.test_user2)
        self.player.positionx = -3.569110
        self.player.positiony = 2.256957
        self.player.save()

        self.question = Question(
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
        self.question.save()
        self.stats = {'nbrQ':1, 'nbrJ':2, 'nbrJConnected':1}
        self.test_admin = User.objects.create_user(username='admin1', email='admin1@myemail.com', password='ada1pass', is_staff=True)
        self.token = token_generator.make_token(self.test_admin)

    def testGetStats(self):
        r = self.client.get('/superapi/stats/', data={
            'user_id': self.test_admin.pk,
            'token': self.token,
        }, content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 200, "[SUPERAPI][PlayerPositionViewTest] Wrong status code")
        self.assertEqual(r.json(), self.stats, "[SUPERAPI][PlayerPositionViewTest] Wrong information")

