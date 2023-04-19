from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая запись для создания нового поста'
        )

    def test_post_text(self):
        """Проверяем, что кореектно выводится первые 15
        символов поста метода __str__ Post."""
        self.assertEqual(
            self.post.__str__()[:15],
                self.post.text[:15]
        )

