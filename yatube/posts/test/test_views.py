from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User
from posts.forms import PostForm

User = get_user_model()

TEN_POSTS = 10
THREE_POSTS = 3


class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='admin1')
        cls.group = Group.objects.create(
            title='Тестовое название',
            slug='test-slug',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            text='Привет!',
            author=cls.user,
            group=cls.group,
        )
        cls.templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/create_post.html': reverse('posts:create'),
            'posts/group_list.html': reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug'},
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': cls.user.username}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail',
                kwargs={'post_id': cls.post.id},
            ),
            'posts/post_create.html': reverse(
                'posts:edit',
                kwargs={'post_id': cls.post.id}
            ),
        }

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client.force_login(self.user)

    def posts_check_all_fields(self, post):
        """Метод, проверяющий поля поста-1."""
        with self.subTest(post=post):
            self.assertEqual(post.text, self.post.text)
            self.assertEqual(post.author, self.post.author)
            self.assertEqual(post.group.id, self.post.group.id)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон-2."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/create_post.html': reverse('posts:create'),
            'posts/group_list.html': reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug'},
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом-3."""
        response = self.authorized_client.get(reverse('posts:index'))
        last_post = response.context['page_obj'][0]
        self.assertEqual(last_post, self.post)

    def test_group_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом-4."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            )
        )
        test_group = response.context['group']
        test_post = response.context['page_obj'][0]
        self.posts_check_all_fields(response.context['page_obj'][0])
        self.assertEqual(test_group, self.group)
        self.assertEqual(test_post, self.post)

    def test_posts_context_profile_context(self):
        """Проверка profile сформирован с правильным контекстом-5."""
        response = self.authorized_client_author.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username},
            )
        )
        self.assertEqual(response.context['author'], self.user)

    def test_posts_context_post_detail_context(self):
        """Проверка post_detail сформирован с правильным контекстом-6."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id},
            )
        )
        self.assertEqual(response.context['post'].text, self.post.text)

    def test_posts_context_post_create_context(self):
        """Проверка post_create сформирован с правильным контекстом-7."""
        response = self.authorized_client.get(
            reverse('posts:create')
        )
        self.assertIsInstance(response.context['form'], PostForm)

    def test_posts_context_post_edit_context(self):
        """Проверка post_edit сформирован с правильным контекстом-8."""
        response = self.authorized_client.get(
            reverse(
                'posts:edit',
                kwargs={'post_id': self.post.id},
            )
        )
        self.assertEqual(
            response.context['form'].initial['text'],
            self.post.text
        )


class PostsPaginatorViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='admin1')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        post_list = [Post(text=f'Тестовый текст поста номер {count}',
                            author=cls.user)
                        for count in range(TEN_POSTS + THREE_POSTS)]
        Post.objects.bulk_create(post_list, batch_size=500)
        cls.urls_paginator = {
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug'},
            ),
            reverse(
                'posts:profile',
                kwargs={'username': cls.user.username}
            ),
        }

    def test_posts_if_first_page_has_ten_records(self):
        """Проверка: первая страница 10 записей."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context.get(
            'page_obj').object_list), TEN_POSTS)

    def test_posts_if_second_page_has_three_records(self):
        """Проверка: вторая страница 3 записи."""
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2'
        )
        self.assertEqual(len(response.context.get(
            'page_obj').object_list), THREE_POSTS)
