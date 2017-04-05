from django.test import TestCase
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
        self.assertEqual(r.json(), 'Malformed JSON input', "[API][Auth] Wrong error message.")

    def testMissingCredentials(self):
        r = self.client.post('/api/auth/new/', data=json.dumps({'creds': {
            'username': 'user1'
        }}), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 401, "[API][Auth] Wrong status code.")
        self.assertEqual(r.json(), 'Missing parameters for registration', "[API][Auth] Wrong error message.")

    def testExistingUsername(self):
        r = self.client.post('/api/auth/new/', data=json.dumps({'creds': {
            'username': 'user1',
            'password': 'newpass',
            'email': 'mycoolemail@hey.me'
        }}), content_type=JSON_CONTENT_TYPE)
        self.assertEqual(r.status_code, 401, "[API][Auth] Wrong status code.")
        self.assertEqual(r.json(), "Nom d'utilisateur déjà utilisé.", "[API][Auth] Wrong error message.")

    def testCorrectRegistration(self):
        pass


class UpdatePositionTest(TestCase):
    pass


class SingleQuestionTest(TestCase):
    pass


class NeighbouringQuestionsTest(TestCase):
    pass


class PlayerInfoTest(TestCase):
    pass
