from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Follow

User = get_user_model()


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(
            username='Biba')
        cls.follower = User.objects.create_user(
            username='Boba')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client.force_login(
            FollowTest.follower)

    def test_follow(self):
        self.assertEqual(Follow.objects.count(), 0)
        follow = Follow.objects.create(
            author=FollowTest.author,
            user=FollowTest.follower)
        self.assertEqual(Follow.objects.count(), 1)
        follows = Follow.objects.filter(
            author=FollowTest.author,
            user=FollowTest.follower)
        self.assertEqual(len(follows), 1)
        follow = follows.first()
        self.assertEqual(follow.author, FollowTest.author)
        self.assertEqual(follow.user, FollowTest.follower)


    def test_don_t_follow(self):
        self.assertEqual(Follow.objects.count(), 0)
        Follow.objects.create(
            author=FollowTest.author,
            user=FollowTest.follower)
        self.assertEqual(Follow.objects.count(), 1)
        client_follower = Client()
        client_follower.force_login(FollowTest.follower)
        client_follower.get(
            reverse(
                'posts:profile_unfollow',
                args=(FollowTest.author.username,)))
        self.assertEqual(Follow.objects.count(), 0)
        follows = Follow.objects.filter(
            author=FollowTest.author,
            user=FollowTest.follower)
        self.assertFalse(follows)
