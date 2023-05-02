from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from http import HTTPStatus

from ..models import Follow, Post

User = get_user_model()


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_biba = User.objects.create_user(username='biba')
        cls.user_boba = User.objects.create_user(username='boba')
        cls.post = Post.objects.create(
            text='Следуй за мной!',
            author=cls.user_boba
        )

    def setUp(self):
        self.user_biba = FollowTest.user_biba
        self.user_boba = FollowTest.user_boba
        self.authorized_client1 = Client()
        self.authorized_client1.force_login(self.user_biba)

    def test_follow(self):
        """Подписываесмся и отписываемся от автора."""
        response = self.authorized_client1.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user_boba.username},
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertFalse(self.user_biba.following.filter(
            author=self.user_boba).exists())
        response = self.authorized_client1.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.user_boba.username},
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertFalse(self.user_biba.following.filter(
            author=self.user_boba).exists())

    def test_new_author_post_on_follow_index_page(self):
        """Автор написал новый пост который виден только преследователям.""" 
        subscription = Follow.objects.create(
            user=self.user_biba, author=self.user_boba)
        response = self.authorized_client1.get(reverse('posts:follow_index'))
        new_post_author = response.context.get(
            'page_obj').object_list[0].author
        self.assertEqual(new_post_author, self.user_boba)
        subscription.delete()
        response = self.authorized_client1.get(reverse('posts:follow_index'))
        post_list = response.context.get('page_obj').object_list
        self.assertEqual(len(post_list), 0)
