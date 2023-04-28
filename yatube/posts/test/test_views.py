import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django import forms

from posts.models import Group, Post, User
from posts.forms import PostForm

User = get_user_model()

TEN_POSTS = 10
THREE_POSTS = 3

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
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
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.image_name = 'small.gif'
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.post = Post.objects.create(
            text='Тестовая запись для создания нового поста',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded,
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

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
        self.assertTrue(last_post, 'image/gif')

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
        self.posts_check_all_fields(test_post)
        self.assertEqual(test_group, self.group)
        self.assertEqual(test_post, self.post)
        self.assertTrue(test_post, 'image/gif')

    def test_posts_context_profile_context(self):
        """Проверка profile сформирован с правильным контекстом-5."""
        response = self.authorized_client_author.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username},
            )
        )
        self.assertEqual(response.context['author'], self.user)
        test_post = response.context['page_obj'][0]
        self.posts_check_all_fields(test_post)
        self.assertEqual(test_post, self.post)
        self.assertTrue(test_post, 'image/gif')

    def test_posts_context_post_detail_context(self):
        """Проверка post_detail сформирован с правильным контекстом-6."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id},
            )
        )
        self.assertEqual(response.context['post'], self.post)

    def test_posts_context_post_create_context(self):
        """Проверка post_create сформирован с правильным контекстом-7."""
        response = self.authorized_client.get(
            reverse('posts:create')
        )
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertFalse('is_edit' in response.context)
        self.assertTrue('posts:create', 'image/gif')

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
        self.assertTrue(response.context['is_edit'])

    def test_comment_post_authorized_user(self):
        """Комментировать пост может только авторизованный пользователь-9."""
        comment_count = Comment.objects.count()
        response = self.create_comment(self.user, 'комментарий', self.post)
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            args=(self.post.id,)
        ))
        self.assertTrue(
            Comment.objects.filter(
                text='комментарий'
            ).exists()
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        comment = Comment.objects.first()
        self.assertEqual(comment.text, 'комментарий')

    def test_comment_add_unauthorized_user(self):
        """Неавторизованный пользователь не может создавать комментарии-10."""
        comment_count = Comment.objects.count()
        response = self.client.post(
            reverse('posts:add_comment', args=(self.post.id,))
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response,
            reverse('login') + f'?next=/posts/{self.post.id}/comment/')
        self.assertEqual(Comment.objects.count(), comment_count)

    def test_cache_index(self):
        """Тестируем кеш index.html-11."""
        response_1 =reverse('posts:index')
        time.sleep(2)
        response_2 = reverse('posts:index')
        assert(response_1 == response_2)



class PostsPaginatorViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='admin1')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        post_list = [Post(
            text=f'Тестовый текст поста{count}',
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
        for url in self.urls_paginator:
            with self.subTest(msg='slug:test-slug', posts='group_list'):
                response = self.authorized_client.get(url)
                page_obj = response.context.get(url)
                if page_obj is not None:
                    self.assertEqual(len(
                        'page_obj'), TEN_POSTS)

    def test_posts_if_second_page_has_three_records(self):
        """Проверка: вторая страница 3 записи."""
        for url in self.urls_paginator:
            with self.subTest(msg='slug:test-slug', posts='group_list'):
                response = self.authorized_client.get(
                    (url) + '?page=2')
                page_obj = response.context.get(url)
                if page_obj is not None:
                    self.assertEqual(len(
                        'page_obj'), THREE_POSTS)
