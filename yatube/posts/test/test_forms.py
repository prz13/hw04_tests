import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings

from posts.models import Group, Post


User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
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

    def setUp(self):
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)
        self.post = Post.objects.create(
            text='Тестовый пост',
            author=self.author,
            group=self.group,
            image=None
        )

    def post_create_form(self):
        """Создали новый пост."""
        # Подсчитаем количество записей
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст для проверки',
            'group': self.group.slug,
            'image': self.uploaded
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
        self.assertTrue(Post.objects.filter(
            group_id=form_data['group'],
            text=form_data['text'],
            image='posts/small.gif').exists(),
        )

    def post_edit_forms(self):
        """Отредактировали пост."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Измененный текст',
            'group': self.group.slug,
            'image':self.uploaded
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
        self.assertNotEqual(edit_post.image,
                            self.post.image
        )

