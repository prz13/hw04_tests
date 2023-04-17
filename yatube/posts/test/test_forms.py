from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post


User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='NoName')
        cls.post = Post.objects.create(
            text='Тестовая запись для создания нового поста',
            author=cls.author,
        )
        cls.group = Group.objects.create(
            title='Тестовое название',
            description='Тестовое описание',
            slug='test-slug'
        )

    def setUp(self):
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

    def post_create_form(self):
        """Создали новый пост."""
        # Подсчитаем количество записей
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст для проверки',
            'group': self.group.slug
        }
        response = self.authorized_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        post_latest = Post.objects.latest('id')
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': self.post.author})
        )
        self.assertEqual(post_latest.text, form_data['text'])
        self.assertEqual(post_latest.group.id, form_data['group'])

    def post_edit_forms(self):
        """Отредактировали пост."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Измененный текст',
            'group': self.group.slug
        }
        response = self.authorized_author.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        edit_post_var = Post.objects.get(id=self.post.id)
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id})
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(edit_post_var.text, form_data['text'])
        self.assertEqual(edit_post_var.author, self.post.author)
