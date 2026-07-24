import json
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from rest_framework import status

User = get_user_model()

class UserManagementTests(TestCase):

    def setUp(self):
        self.client = Client()
        
        # Create an administrator user
        self.admin_user = User.objects.create_user(
            username='admin_test',
            password='password123',
            email='admin@lms.com',
            role=User.ROLE_ADMINISTRATOR,
            is_staff=True
        )
        
        # Create a regular receptionist user
        self.receptionist_user = User.objects.create_user(
            username='reception_test',
            password='password123',
            email='reception@lms.com',
            role=User.ROLE_RECEPTIONIST,
            is_staff=False
        )
        
        self.users_url = '/api/users/'
        self.me_url = '/api/users/me/'

    def test_admin_can_list_users(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('results', data)
        self.assertTrue(len(data['results']) >= 2)

    def test_receptionist_cannot_list_users(self):
        self.client.force_login(self.receptionist_user)
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_user(self):
        self.client.force_login(self.admin_user)
        data = {
            'username': 'new_scientist',
            'password': 'secPass123!',
            'email': 'scientist@lms.com',
            'role': User.ROLE_LAB_SCIENTIST,
            'first_name': 'Isaac',
            'last_name': 'Newton',
            'is_staff': False
        }
        response = self.client.post(self.users_url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        res_data = response.json()
        self.assertEqual(res_data['username'], 'new_scientist')
        
        # Verify password is set & hashed correctly
        new_user = User.objects.get(username='new_scientist')
        self.assertTrue(new_user.check_password('secPass123!'))

    def test_receptionist_cannot_create_user(self):
        self.client.force_login(self.receptionist_user)
        data = {
            'username': 'new_scientist',
            'password': 'secPass123!',
            'email': 'scientist@lms.com',
            'role': User.ROLE_LAB_SCIENTIST,
        }
        response = self.client.post(self.users_url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_any_user_can_access_me_profile(self):
        self.client.force_login(self.receptionist_user)
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['username'], 'reception_test')

    def test_user_can_update_own_profile(self):
        self.client.force_login(self.receptionist_user)
        data = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'password': 'newpassword789'
        }
        response = self.client.patch(self.me_url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['first_name'], 'Jane')
        
        # Verify receptionist password was updated correctly
        self.receptionist_user.refresh_from_db()
        self.assertTrue(self.receptionist_user.check_password('newpassword789'))
        self.assertFalse(self.receptionist_user.check_password('password123'))
