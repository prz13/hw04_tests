# posts/tests/test_urls.py
from http import HTTPStatus


from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post


User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            author=User.objects.create_user(
                username='admin1',
                email='root@root.net',
                password='1234'
            ),
            text='Тестовая запись для создания нового поста',
        )

        cls.another_user = User.objects.create_user(
            username='any_user', password='password'
        )

        cls.group = Group.objects.create(
            title=('Заголовок для группы'),
            slug='test_slug'
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='NoNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_and_group(self):
        """страницы группы и главная доступны всем"""
        url_names = (
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.user.username}/',
            f'/posts/{self.post.pk}/',
        )
        for adress in url_names:
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_for_authorized(self):
        """Страница доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unauthorized_url(self):
        """Страница без авторизации недоступна"""
        post_id = 1
        url_names = {
            '/create/': '/auth/login/?next=/create/',
            '/admin/': '/admin/login/?next=/admin/',
            f'/posts/{post_id}/edit/':
                f'/auth/login/?next=/posts/{post_id}/edit/',
        }
        for url, redirect in url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
                self.assertIn('Location', response)
            self.assertRedirects(response, redirect)

    def test_url_uses_correct_template(self):
        """Проверка шаблона для адресов."""
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test_slug/',
            'posts/create_post.html': '/create/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_unauthorized_user_cannot_edit_post_of_another_user(self):
        self.authorized_client.force_login(self.another_user)
        response = self.authorized_client.get(
            f'/posts/{self.post.id}/edit/'
        )
        self.assertRedirects(
            response,
            f'/posts/{self.post.id}/'
        )
