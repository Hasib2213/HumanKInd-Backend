from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from Authapp.models import User
from .models import Post

class CommunityTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='password123', first_name='Test', last_name='User')
        self.client.force_authenticate(user=self.user)

    def test_create_post(self):
        url = reverse('post-list-create')
        data = {
            'content': 'This is a test post',
            'is_anonymous': False
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(response.data['user']['email'], 'test@example.com')

    def test_create_anonymous_post(self):
        url = reverse('post-list-create')
        data = {
            'content': 'This is an anonymous test post',
            'is_anonymous': True
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data['user'])

    def test_like_post(self):
        post = Post.objects.create(user=self.user, content='Like me')
        url = reverse('like-toggle', kwargs={'post_id': post.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['is_liked'])
        
        # Test unlike
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_liked'])

    def test_report_post(self):
        post = Post.objects.create(user=self.user, content='Report me')
        url = reverse('report-create')
        data = {
            'post': post.id,
            'title': 'Inappropriate content',
            'description': 'This post violates community guidelines.'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
