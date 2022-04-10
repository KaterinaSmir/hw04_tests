from django.test import TestCase
from http import HTTPStatus


class ViewTestClass(TestCase):
    def setUp(self):
        self.response_404 = HTTPStatus.NOT_FOUND
        self.response_200 = HTTPStatus.OK

    def test_error_page(self):
        response = self.client.get('/this_page_does_not_exist/')
        self.assertEqual(response.status_code, self.response_404)
        self.assertTemplateUsed(response, 'core/404.html')
