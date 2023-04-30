from django.test import Client, TestCase


class ViewTestClass(TestCase):
    def setUp(self):
        self.client = Client()


    def test_page_404(self):
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'core/404.html')

