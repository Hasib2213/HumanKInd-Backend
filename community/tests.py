from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from Authapp.models import User
from .models import Post, Comment, Like

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

    def test_comments_include_replies_and_likers(self):
        post = Post.objects.create(user=self.user, content='Interactive post')
        second_user = User.objects.create_user(email='friend@example.com', password='password123', first_name='Friend', last_name='One')
        self.client.force_authenticate(user=second_user)

        like_url = reverse('like-toggle', kwargs={'post_id': post.id})
        self.client.post(like_url)

        comment_url = reverse('comment-list-create', kwargs={'post_id': post.id})
        comment_response = self.client.post(comment_url, {'content': 'Nice post!'}, format='json')
        self.assertEqual(comment_response.status_code, status.HTTP_201_CREATED)
        comment_id = comment_response.data['id']

        third_user = User.objects.create_user(email='reply@example.com', password='password123', first_name='Reply', last_name='User')
        self.client.force_authenticate(user=third_user)
        reply_response = self.client.post(comment_url, {'content': 'I agree', 'parent': comment_id}, format='json')
        self.assertEqual(reply_response.status_code, status.HTTP_201_CREATED)

        detail_url = reverse('post-detail', kwargs={'pk': post.id})
        detail_response = self.client.get(detail_url)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(detail_response.data['liked_by']), 1)
        self.assertEqual(detail_response.data['liked_by'][0]['email'], 'friend@example.com')
        self.assertEqual(len(detail_response.data['comments']), 1)
        self.assertEqual(detail_response.data['comments'][0]['content'], 'Nice post!')
        self.assertEqual(detail_response.data['comments'][0]['replies'][0]['content'], 'I agree')

    def test_reply_must_stay_on_same_post(self):
        first_post = Post.objects.create(user=self.user, content='First post')
        second_post = Post.objects.create(user=self.user, content='Second post')
        parent_comment = Comment.objects.create(post=first_post, user=self.user, content='Parent comment')

        url = reverse('comment-list-create', kwargs={'post_id': second_post.id})
        response = self.client.post(url, {'content': 'Bad reply', 'parent': parent_comment.id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
