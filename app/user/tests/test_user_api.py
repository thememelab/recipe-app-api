""" test for the user Api"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    """ Create and return a new user """
    return get_user_model().objects.create_user(**params)

class PublicUsertests(TestCase):
    """" test the public feature of the user API."""
    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """ test creating a user is success"""
        payload = {
            'email':'test@exmaple.com',
            'password':'testpass123',
            'name':'Test Name',
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password',res.data)

    def test_user_with_exits_error(self):
        """ Test error returned if user with email exist. """
        payload = {
            'email':'test@exmaple.com',
            'password':'testpass123',
            'name':'Test Name',
        }

        create_user(**payload)
        res = self.client.post(CREATE_USER_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """ Test an error is returned of password less than 5 chars. """
        payload = {
            'email':'test@exmaple.com',
            'password':'pw',
            'name':'Test Name',
        }

        res = self.client.post(CREATE_USER_URL,payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """ Test genrate tokne for valid credentials"""
        user_details = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': 'test-user-password123',
        }
        create_user(**user_details)

        payload = {
            'email':user_details['email'],
            'password': user_details['password'],
        }

        res = self.client.post(TOKEN_URL,payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """ Test returnd error if crdential arre invalid """
        create_user(email='test@exmaple.com',password='goodpass')
        payload = {'email':'test@exmaple.com', 'password':'badpass'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """ test posting a blank password return an error. """
        payload = { 'email':'test@exmaple.com','password':'' }
        res = self.client.post(TOKEN_URL,payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauhtorized(self):
        """ test authentication is required for user. """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateUserApiTest(TestCase):
    """ test Api request that requires authentication"""

    def setUp(self):
        self.user = create_user(
            email='test@exmaple.com',
            password='testpass123',
            name='Test Name'
            )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retriever_profile_success(self):
        """ test retrieve the profile of the Authenticated user """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email':self.user.email,
        })

    def test_post_noyt_allowed(self):
        """ test POST is not allowed for the me ednpoint."""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """ test uopdating the user profile for the authenticated user"""
        payload = {
            'name':'updated name',
            'password':'newpassword123',
            }
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)