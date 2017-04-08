from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _
from django.core.validators import EmailValidator
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from api.models import *
from tokenapi.tokens import token_generator
import json

JSON_CONTENT_TYPE = 'application/json'


class AuthTest(TestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(username='user1', email='user1@myemail.com', password='uza1pass')

    def testEmptyInput(self):
        r = self.client.post('/api/auth/', data={}, content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 403, "[API][Auth] Wrong status code.")
        self.assertEqual(r.json(), "Must include 'username' and 'password' as parameters.",
                         "[API][Auth] Wrong error message.")

    def testBadPassword(self):
        r = self.client.post('/api/auth/', data=json.dumps({
            'username': 'user1',
            'password': 'verywrongpass'
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 403, "[API][Auth] Wrong status code.")
        self.assertEqual(r.json(), "Unable to log you in, please try again.", "[API][Auth] Wrong error message.")

    def testGoodPassword(self):
        r = self.client.post('/api/auth/', data=json.dumps({
            'username': 'user1',
            'password': 'uza1pass'
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 200, "[API][Auth] Wrong status code.")
        data = r.json()
        self.assertEqual(token_generator.make_token(self.test_user), data['token'], "[API][Auth] Wrong token.")
        self.assertEqual(self.test_user.pk, data['user_id'], "[API][Auth] Wrong user_id")


class RegisterTest(TestCase):
    def setUp(self):
        self.test_user1 = User.objects.create_user(username='user1', email='user1@myemail.com', password='uza1pass')
        self.assertNotEqual(self.test_user1, None, "[API][Auth] Could not create test user.")
        self.test_user2 = {
            'username': 'user1',
            'email': 'user1@myemail.com',
            'password': 'uza1pass'
        }

    def testNoCreds(self):
        r = self.client.post('/api/auth/new/', data={}, content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 401, "[API][Auth] Wrong status code.")
        self.assertEqual(r.json(), _('Malformed JSON input'), "[API][Auth] Wrong error message.")

    def testMissingCredentials(self):
        r = self.client.post('/api/auth/new/', data=json.dumps({'creds': {
            'username': 'user1'
        }}), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 401, "[API][Auth] Wrong status code.")
        self.assertEqual(r.json(), _('Missing parameters for registration'), "[API][Auth] Wrong error message.")

    def testExistingUsername(self):
        r = self.client.post('/api/auth/new/', data=json.dumps({'creds': {
            'username': 'user1',
            'password': 'newpass',
            'email': 'mycoolemail@hey.me'
        }}), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 401, "[API][Auth] Wrong status code.")
        self.assertEqual(r.json(), _("Username already in use."), "[API][Auth] Wrong error message.")

    def testBadPassword(self):
        # Password validators are run with this, in the same order, so we should get this error
        # message. As one error will fail the whole block.
        error_msg = None
        try:
            validate_password('n')
        except ValidationError as e:
            error_msg = e.messages[0]
        # Now test the error_msg
        r = self.client.post('/api/auth/new/', data=json.dumps({'creds': {
            'username': 'user2ddkd',
            'password': 'n',
            'email': 'mycoolemail@heye.fr'
        }}), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 401, "[API][Auth] Wrong status code.")
        self.assertEqual(r.json(), error_msg, "[API][Auth] Wrong error message.")

    def testBadEmail(self):
        error_msg = str(EmailValidator.message)
        r = self.client.post('/api/auth/new/', data=json.dumps({'creds': {
            'username': 'user2ddkd',
            'password': 'dfkkdkdkdn',
            'email': 'mycoolemail@heyr'
        }}), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 401, "[API][Auth] Wrong status code.")
        self.assertEqual(r.json(), error_msg, "[API][Auth] Wrong error message.")

    def testCorrectRegistration(self):
        r = self.client.post('/api/auth/new/', data=json.dumps({'creds': {
            'username': 'user2ddkd',
            'password': 'nsshhhhh',
            'email': 'mycoolemail@heye.fr'
        }}), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 200, "[API][Auth] Wrong status code.")
        self.assertEqual(r.json(), _('Account creation successful.'), "[API][Auth] Wrong success message.")
        user = authenticate(username='user2ddkd', password='nsshhhhh')
        self.assertNotEqual(user, False, "[API][Auth] Account creation unsuccessful.")
        self.assertEqual(user.email, 'mycoolemail@heye.fr', "[API][Auth] Wrong e-mail upon registration.")


class UpdatePositionTest(TestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(username='user1', email='user1@myemail.com', password='uza1pass')
        self.player = Player(account=self.test_user)
        self.player.save()
        self.token = token_generator.make_token(self.test_user)

    def testMalformedInput(self):
        # Missing position field.
        r = self.client.post('/api/position/', data=json.dumps({
            'user_id': self.test_user.pk,
            'token': self.token
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 401, "[API][Position] Wrong status code.")
        self.assertEqual(r.json(), str(_('Malformed JSON Input')), "[API][Position] Wrong error message.")
        # Missing x,y or z fields
        r = self.client.post('/api/position/', data=json.dumps({
            'user_id': self.test_user.pk,
            'token': self.token,
            'position': {
                'x': 125,
            }
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 401, "[API][Position] Wrong status code.")
        self.assertEqual(r.json(), str(_('Malformed JSON Input')), "[API][Position] Wrong error message.")
        # Badly written coordinates.
        r = self.client.post('/api/position/', data=json.dumps({
            'user_id': self.test_user.pk,
            'token': self.token,
            'position': {
                'x': 'totoro',
                'y': '1.jo',
                'z': '',  # John Cena's Value
            }
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 401, "[API][Position] Wrong status code.")
        self.assertEqual(r.json(), str(_('Malformed coordinates. Unable to parse to float.')),
                         "[API][Position] Wrong error message.")
        # Infinite coordinates
        r = self.client.post('/api/position/', data=json.dumps({
            'user_id': self.test_user.pk,
            'token': self.token,
            'position': {
                'x': 'inf',
                'y': 12,
                'z': 5
            }
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 401, "[API][Position] Wrong status code.")
        self.assertEqual(r.json(), str(_('Your coordinates can\'t be infinity or NaN, idiot. TG.')),
                         "[API][Position] Wrong error message.")
        # Out of range

    def testBadValues(self):
        # Badly written coordinates.
        r = self.client.post('/api/position/', data=json.dumps({
            'user_id': self.test_user.pk,
            'token': self.token,
            'position': {
                'x': 'totoro',
                'y': '1.jo',
                'z': '',  # John Cena's Value
            }
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 401, "[API][Position] Wrong status code.")
        self.assertEqual(r.json(), str(_('Malformed coordinates. Unable to parse to float.')),
                         "[API][Position] Wrong error message.")
        # Infinite coordinates
        r = self.client.post('/api/position/', data=json.dumps({
            'user_id': self.test_user.pk,
            'token': self.token,
            'position': {
                'x': 'inf',
                'y': 12,
                'z': 5
            }
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 401, "[API][Position] Wrong status code.")
        self.assertEqual(r.json(), str(_('Your coordinates can\'t be infinity or NaN, idiot. TG.')),
                         "[API][Position] Wrong error message.")
        # Out of range
        r = self.client.post('/api/position/', data=json.dumps({
            'user_id': self.test_user.pk,
            'token': self.token,
            'position': {
                'x': 5689,
                'y': 12,
                'z': 5
            }
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 401, "[API][Position] Wrong status code.")
        self.assertEqual(r.json(), str(_('Coordinates out of range.')), "[API][Position] Wrong error message.")

    def testCorrectPosUpdate(self):
        # Out of range
        r = self.client.post('/api/position/', data=json.dumps({
            'user_id': self.test_user.pk,
            'token': self.token,
            'position': {
                'x': -2.3569,
                'y': 12.2365,
                'z': 0
            }
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 200, "[API][Position] Wrong status code.")
        self.assertEqual(r.json(), str(_('Position updated successfully.')), "[API][Position] Wrong success message.")
        del self.player
        player = Player.objects.get(account=self.test_user)
        self.assertEqual(player.getPosition(), (-2.3569, 12.2365, 0), "[API][Position] Position not updated.")


class SingleQuestionTest(TestCase):
    def setUp(self):
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
        self.test_user = User.objects.create_user(username='user1', email='user1@myemail.com', password='uza1pass')
        self.token = token_generator.make_token(self.test_user)

    def testCorrectRetrieve(self):
        r = self.client.get('/api/questions/' + str(self.test_question.pk) + "/", data={
            'user_id': self.test_user.pk,
            'token': self.token
        })
        # Flemmard
        packet_quest = None
        quest = self.test_question
        packed_quest = {
            'question': quest.questionText,
            'answer1': quest.answer1,
            'answer2': quest.answer2,
            'answer3': quest.answer3,
            'answer4': quest.answer4,
            'score': quest.score,
            'difficulty': quest.difficulty,
            'topic': quest.topic
        }
        self.assertEqual(r.status_code, 200, "[API][SingleQuestion] Wrong status code.")
        self.assertEqual(r.json(), packed_quest, "[API][SingleQuestion] Wrong question returned.")

    def testBadIdInput(self):
        # Not an int value.
        r = self.client.get('/api/questions/5sffg/', data={
            'user_id': self.test_user.pk,
            'token': self.token
        })
        self.assertEqual(r.status_code, 404, "[API][SingleQuestion] Wrong status code.")
        # Not an int value.
        r = self.client.get('/api/questions/58956/', data={
            'user_id': self.test_user.pk,
            'token': self.token
        })
        self.assertEqual(r.status_code, 404, "[API][SingleQuestion] Wrong status code.")
        self.assertEqual(r.json(), str(_('Question non trouvée.')), "[API][SingleQuestion] Wrong error message.")


# TODO: Test at different precision points. (https://en.wikipedia.org/wiki/Decimal_degrees#Precision)
# For now we'll be tasting human-precision decimal degrees.
class NeighbouringQuestionsTest(TestCase):
    def setUp(self):
        # TODO: Use mockup to properly test this.
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
        self.test_user = User.objects.create_user(username='user1', email='user1@myemail.com', password='uza1pass')
        self.player = Player(account=self.test_user)
        self.token = token_generator.make_token(self.test_user)

    def testCloseQuestions(self):
        self.player.positionx = -2.569110
        self.player.positiony = 1.256957
        self.player.save()
        r = self.client.get('/api/questions/', data={
            'user_id': self.test_user.pk,
            'token': self.token,
        })
        spot = self.test_spot
        packed_quests = {
            'questions': [{
                'id': spot.pk,
                'question': spot.currentQuestion.questionText,
                'resp1': spot.currentQuestion.answer1,
                'resp2': spot.currentQuestion.answer2,
                'resp3': spot.currentQuestion.answer3,
                'resp4': spot.currentQuestion.answer4,
                'score': spot.currentQuestion.score,
                'difficulty': spot.currentQuestion.difficulty,
                'position': [spot.centrex, spot.centrey, spot.centrez],
            }]
        }
        self.maxDiff = None
        self.assertEqual(r.status_code, 200, "[API][NeighbouringQuestions] Wrong status code.")
        self.assertEqual(r.json(), packed_quests, "[API][NeighbouringQuestions] Wrong packed questions.")

    def testFarQuestions(self):
        self.player.positionx = -20.569110
        self.player.positiony = 11.256957
        self.player.save()
        r = self.client.get('/api/questions/', data={
            'user_id': self.test_user.pk,
            'token': self.token,
        })
        spot = self.test_spot
        self.assertEqual(r.status_code, 200, "[API][NeighbouringQuestions] Wrong status code.")
        self.assertEqual(r.json(), {'questions': []}, "[API][NeighbouringQuestions] Wrong packed questions.")


# This bad boy over here ...
class AnswerQuestionTest(TestCase):
    def setUp(self):
        # TODO: Use mockup to properly test this.
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
            delay=500,
            rayon=5,
            questionList='1',
        )
        self.test_spot.save()
        self.test_zone = ExclusionZone(
            name='Test Zone',
            points=json.dumps([
                [48.2251, -3.8735, 0],
                [48.1961, -3.8371, 0],
                [48.2005, -3.9015, 0]
            ])
        )
        self.test_zone.save()
        self.test_user = User.objects.create_user(username='user1', email='user1@myemail.com', password='uza1pass')
        self.player = Player(account=self.test_user)
        self.token = token_generator.make_token(self.test_user)
        self.player.save()

    def testPositionVerification(self):
        # User is in an exclusion zone.
        self.player.positionx = 48.215
        self.player.positiony = -3.8742
        self.player.save()
        r = self.client.post('/api/questions/', data=json.dumps({
            'user_id': self.test_user.pk,
            'token': self.token,
            'answer': {
                'qid': self.test_question.pk,
                'answ_number': 1,
            }
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 401, "[API][AnswerQuestionTest] Wrong status code.")
        self.assertEqual(r.json(), _('Cannot play in an exclusion zone.'),
                         "[API][AnswerQuestionTest] Wrong error message.")
        # User far from spot.
        self.player.positionx = -20.569110
        self.player.positiony = 15.256957
        self.player.save()
        r = self.client.post('/api/questions/', data=json.dumps({
            'user_id': self.test_user.pk,
            'token': self.token,
            'answer': {
                'qid': self.test_question.pk,
                'answ_number': 1,
            }
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 401, "[API][AnswerQuestionTest] Wrong status code.")
        self.assertEqual(r.json(), _('Too far to answer this question.'),
                         "[API][AnswerQuestionTest] Wrong error message.")

    def testGoodAnswer(self):
        # Test if the answer is taken into account.
        self.player.positionx = -2.569114
        self.player.positiony = 1.256958
        self.player.save()
        before_score = self.player.score
        del self.player.score
        self.test_spot.startTime = int(time.time())
        p = self.client.post('/api/questions/', data=json.dumps({
            'user_id': self.test_user.pk,
            'token': self.token,
            'answer': {
                'qid': self.test_spot.pk,
                'answ_number': 1,
            }
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(p.status_code, 200, "[API][AnswerQuestionTest] Wrong status code.")
        self.assertEqual(p.json(), 'Successfully answered the question.',
                         "[API][AnswerQuestionTest] Wrong information.")
        # Test if user has the appropriate score afterwards.
        new_score = self.player.score
        self.assertEqual(new_score, before_score + self.test_question.score,
                         "[API][AnswerQuestionTest] Score not added to player.")
        # Test if the spot has effectively been delayed.
        del self.test_spot.startTime
        self.assertAlmostEqual(self.test_spot.startTime, int(time.time()) + self.test_spot.delay, delta=2)

    def testBadAnswer(self):
        self.test_spot.startTime = int(time.time())
        self.test_spot.save()
        self.player.positionx = -2.569114
        self.player.positiony = 1.256958
        self.player.save()
        p = self.client.post('/api/questions/', data=json.dumps({
            'user_id': self.test_user.pk,
            'token': self.token,
            'answer': {
                'qid': self.test_spot.pk,
                'answ_number': 4,
            }
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(p.status_code, 402, "[API][AnswerQuestionTest] Wrong status code.")
        self.assertEqual(p.json(), _('Sorry wrong answer.'),
                         "[API][AnswerQuestionTest] Wrong information.")

    def testBadInput(self):
        # Test missing "answer" field.
        p = self.client.post('/api/questions/', data=json.dumps({
            'user_id': self.test_user.pk,
            'token': self.token,
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(p.status_code, 401, "[API][AnswerQuestionTest] Wrong status code.")
        self.assertEqual(p.json(), _('Malformed JSON input.'),
                         "[API][AnswerQuestionTest] Wrong error message.")
        # Test missing 'qid" or 'answ_number' field.
        p = self.client.post('/api/questions/', data=json.dumps({
            'user_id': self.test_user.pk,
            'token': self.token,
            'answer': {
                'answ_number': 4,
            }
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(p.status_code, 401, "[API][AnswerQuestionTest] Wrong status code.")
        self.assertEqual(p.json(), _('Malformed JSON input.'),
                         "[API][AnswerQuestionTest] Wrong error message.")
        # Test unparsable numeric literal.
        p = self.client.post('/api/questions/', data=json.dumps({
            'user_id': self.test_user.pk,
            'token': self.token,
            'answer': {
                'qid': 'jfjfjfj',
                'answ_number': 4,
            }
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(p.status_code, 401, "[API][AnswerQuestionTest] Wrong status code.")
        self.assertEqual(p.json(), _('Unable to parse numeric literals from the request.'),
                         "[API][AnswerQuestionTest] Wrong information.")
        # Test bad spot id.
        p = self.client.post('/api/questions/', data=json.dumps({
            'user_id': self.test_user.pk,
            'token': self.token,
            'answer': {
                'qid': 3938,
                'answ_number': 4,
            }
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(p.status_code, 404, "[API][AnswerQuestionTest] Wrong status code.")
        self.assertEqual(p.json(), _('Spot not found.'),
                         "[API][AnswerQuestionTest] Wrong information.")
        # Test spot activation time
        self.test_spot.startTime = int(time.time()) + 1520
        self.test_spot.save()
        p = self.client.post('/api/questions/', data=json.dumps({
            'user_id': self.test_user.pk,
            'token': self.token,
            'answer': {
                'qid': 1,
                'answ_number': 4,
            }
        }), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(p.status_code, 404, "[API][AnswerQuestionTest] Wrong status code.")
        self.assertEqual(p.json(), _('Spot not found.'),
                         "[API][AnswerQuestionTest] Wrong information.")


class PlayerInfoTest(TestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(username='user1', email='user1@myemail.com', password='uza1pass')
        self.player = Player(account=self.test_user)
        self.player.save()
        self.token = token_generator.make_token(self.test_user)

    def testBeforeAnsweringQuestion(self):
        r = self.client.get('/api/player/', data={
            'user_id': self.test_user.pk,
            'token': self.token,
        })
        self.assertEqual(r.status_code, 200, "[API][PlayerInfoTest] Wrong status code.")
        self.assertEqual(r.json(), {'nickname': 'user1', 'score': 0}, "[API][PlayerInfoTest] Wrong information.")


class PlayerHistoryTest(TestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(username='user1', email='user1@myemail.com', password='uza1pass')
        self.player = Player(account=self.test_user, questionHistory='1')
        self.player.save()
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
        self.token = token_generator.make_token(self.test_user)

    def testCorrectHistory(self):
        data = {'history': [
            {
                'question': self.test_question.questionText,
                'score': self.test_question.score,
                'difficulty': self.test_question.difficulty,
                'topic': self.test_question.topic,
            }
        ]}
        r = self.client.get('/api/history/', data={
            'user_id': self.test_user.pk,
            'token': self.token,
        })
        self.assertEqual(r.status_code, 200, "[API][PlayerHistoryTest] Wrong status code.")
        self.assertEqual(r.json(), data, "[API][PlayerHistoryTest] Wrong data.")
