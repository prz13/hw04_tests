from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


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
            )
        }

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def posts_check_all_fields(self, post):
        """Метод, проверяющий поля поста."""
        with self.subTest(post=post):
            self.assertEqual(post.text, self.post.text)
            self.assertEqual(post.author, self.post.author)
            self.assertEqual(post.group.id, self.post.group.id)

        # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/create_post.html': reverse('posts:create'),
            'posts/group_list.html': reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug'},
            )
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.posts_check_all_fields(response.context['page_obj'][0])
        last_post = response.context['page_obj'][0]
        self.assertEqual(last_post, self.post)

        # в первом элементе списка posts/group_list содержит ожидаемые значения
    def test_group_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            )
        )
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        test_group = response.context['group']
        self.posts_check_all_fields(response.context['page_obj'][0])
        test_post = str(response.context['page_obj'][0])
        self.assertEqual(test_group, self.group)
        self.assertEqual(test_post, str(self.post))

    def test_posts_context_profile_context(self):
        """Проверка profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username},
            )
        )
        profile = {'user': self.post.author}

        for value, expected in profile.items():
            with self.subTest(value=value):
                context = response.context[value]
                self.assertEqual(context, expected)

        self.posts_check_all_fields(response.context['page_obj'][0])
        test_page = response.context['page_obj'][0]
        self.assertEqual(test_page, self.user.posts.all()[0])

    def test_posts_context_post_detail_context(self):
        """Проверка post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id},
            )
        )

        profile = {'post': self.post}

        for value, expected in profile.items():
            with self.subTest(value=value):
                context = response.context[value]
                self.assertEqual(context, expected)


class PostsPaginatorViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='admin1')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        for count in range(13):
            cls.post = Post.objects.create(
                text=f'Тестовый текст поста номер {count}',
                author=cls.user,
            )

    def test_posts_if_first_page_has_ten_records(self):
        """Проверка: первая страница 10 записей."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context.get('page_obj').object_list), 10)

    def test_posts_if_second_page_has_three_records(self):
        """Проверка: вторая страница 3 записи."""
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2'
        )
        self.assertEqual(len(response.context.get('page_obj').object_list), 3)
