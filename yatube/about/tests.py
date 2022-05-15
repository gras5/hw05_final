from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class AboutUrlTests(TestCase):
    def setUp(self) -> None:
        self.guest_client = Client()

    def test_about_reversed_names_equal_urls(self):
        """Проверка соответствия url и пространства имен About"""

        reversed_names_with_urls = [
            (reverse('about:author'), '/about/author/'),
            (reverse('about:tech'), '/about/tech/'),
        ]

        for reversed_name, expected_url in reversed_names_with_urls:
            with self.subTest(reversed_name=reversed_name):
                self.assertEqual(reversed_name, expected_url)

    def test_about_public_urls_exists_at_desired_locations(self):
        """Проверка общедоступных ссылок About"""
        urls_with_status_codes = [
            (reverse('about:author'), HTTPStatus.OK),
            (reverse('about:tech'), HTTPStatus.OK),
        ]

        for url, expected_status_code in urls_with_status_codes:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, expected_status_code)

    def test_about_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_url_names = [
            (reverse('about:author'), 'about/author.html'),
            (reverse('about:tech'), 'about/tech.html'),
        ]
        for address, template in templates_url_names:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
