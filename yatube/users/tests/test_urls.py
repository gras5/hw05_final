from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UsersUrlTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = User.objects.create_user(username="TestUsername")

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_users_reversed_names_equal_urls(self):
        """
        Проверка соответствия url и пространства имен users
        """

        reversed_names_with_urls = [
            (reverse('users:signup'), '/auth/signup/'),

            (reverse('users:logout'), '/auth/logout/'),

            (reverse('users:login'), '/auth/login/'),

            (reverse('users:password_change_form'),
             '/auth/password_change/'),

            (reverse('users:password_change_done'),
             '/auth/password_change/done/'),

            (reverse('users:password_reset_form'), '/auth/password_reset/'),

            (reverse('users:password_reset_done'),
             '/auth/password_reset/done/'),

            (reverse(
                'users:password_reset_confirm',
                kwargs={'uidb64': 'Aa', 'token': 12345}
            ), '/auth/reset/Aa/12345/'),

            (reverse('users:password_reset_complete'), '/auth/reset/done/')
        ]

        for reversed_name, expected_url in reversed_names_with_urls:
            with self.subTest(reversed_name=reversed_name):
                self.assertEqual(reversed_name, expected_url)

    def test_users_public_urls_exists_at_desired_locations(self):
        """Проверка общедоступных ссылок приложения Users"""
        urls_with_status_codes = [
            (reverse('users:signup'), HTTPStatus.OK, False),
            (reverse('users:login'), HTTPStatus.OK, False),
            (reverse('users:logout'), HTTPStatus.OK, False),
            (reverse('users:password_reset_form'), HTTPStatus.OK, False),
            (reverse('users:password_reset_complete'), HTTPStatus.OK, False),
            (reverse('users:password_change_form'), HTTPStatus.OK, True),
            (reverse('users:password_change_done'), HTTPStatus.OK, True),
            (reverse(
                'users:password_reset_confirm',
                kwargs={'uidb64': 'Aa', 'token': 12345}
            ), HTTPStatus.OK, True),
        ]

        for url, expected_status, need_auth in urls_with_status_codes:
            with self.subTest(url=url):
                response = (self.authorized_client.get(url)
                            if need_auth else self.guest_client.get(url))

                self.assertEqual(response.status_code, expected_status)

    def test_users_public_urls_uses_correct_template(self):
        """URL-адрес (users) использует соответствующий шаблон."""

        templates_url_names = [
            (reverse('users:signup'), 'users/signup.html'),

            (reverse('users:login'), 'users/login.html'),

            (reverse('users:logout'), 'users/logged_out.html'),

            (reverse('users:password_reset_form'),
             'users/password_change.html'),

            (reverse('users:password_reset_complete'),
             'users/password_change.html'),

            (reverse(
                'users:password_reset_confirm',
                kwargs={'uidb64': 'Aa', 'token': 12345}),
             'users/password_change.html'),
        ]

        for url, template in templates_url_names:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
