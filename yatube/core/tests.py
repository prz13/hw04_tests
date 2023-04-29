from http import HTTPStatus

from django.test import Client, TestCase


class ViewTestClass(TestCase):
    def setUp(self):
        self.client = Client()


def test_for_error_404_page(self):
    """Запрос к несуществующей странице вернет 404
    будет использован кастомный шаблон."""
    response = self.client.get('/badpage-test', follow=True)
    self.assertEqual(response.status_code,HTTPStatus.NOT_FOUND,
                            'Стрнаица с адресом: url не существует!')
    self.assertTemplateUsed(response, 'core/404.html')
