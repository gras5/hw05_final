from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostsUrlTests(TestCase):
    @ classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = User.objects.create_user(username="TestUsername")
        cls.another_user = User.objects.create_user(username="TestUsername_2")
        cls.group = Group.objects.create(
            title='Тестовая группа 1',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Этот текст для проверки тестового поста 1',
            group=cls.group
        )

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_posts_reversed_names_equal_urls(self):
        """
        Проверка соответствия url и пространства имен posts
        """

        reversed_names_with_urls = [
            (reverse('posts:index'), '/'),

            (reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ), f'/group/{self.group.slug}/'),

            (reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ), f'/profile/{self.user.username}/'),

            (reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            ), f'/posts/{self.post.pk}/'),

            (reverse('posts:post_create'), '/create/'),

            (reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            ), f'/posts/{self.post.pk}/edit/'),

            (reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.pk}
            ), f'/posts/{self.post.pk}/comment/'),

            (reverse('posts:follow_index'), '/follow/'),

            (reverse(
                'posts:profile_follow',
                kwargs={'username': self.user.username}
            ), f'/profile/{self.user.username}/follow/'),

            (reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.user.username}
            ), f'/profile/{self.user.username}/unfollow/')
        ]

        for reversed_name, expected_url in reversed_names_with_urls:
            with self.subTest(reversed_name=reversed_name):
                self.assertEqual(reversed_name, expected_url)

    def test_posts_urls_exists_at_desired_locations(self):
        """Проверка ссылок приложения Posts"""
        urls_with_status_codes = [
            (reverse('posts:index'), HTTPStatus.OK, False),

            (reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ), HTTPStatus.OK, False),

            (reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ), HTTPStatus.OK, False),

            (reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            ), HTTPStatus.OK, False),

            ('/unexisting_page/', HTTPStatus.NOT_FOUND, False),

            (reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            ), HTTPStatus.OK, True),

            (reverse('posts:post_create'), HTTPStatus.OK, True),

            (reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.pk}
            ), HTTPStatus.OK, True),

            (reverse('posts:follow_index'), HTTPStatus.OK, True),

            (reverse(
                'posts:profile_follow',
                kwargs={'username': self.user.username}
            ), HTTPStatus.OK, True),

            (reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.user.username}
            ), HTTPStatus.OK, True),
        ]

        for url, expected_status_code, need_auth in urls_with_status_codes:
            with self.subTest(url=url):
                response = (
                    self.authorized_client.get(url, follow=True) if need_auth
                    else self.guest_client.get(url, follow=True)
                )
                self.assertEqual(response.status_code, expected_status_code)

    def test_posts_redirects_for_anonymous_users(self):
        """Проверка перенаправлений для неавторизованных пользователей"""
        urls_with_redirects = [
            (reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
             '/auth/login/?next='),

            (reverse('posts:post_create'), '/auth/login/?next='),

            (reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.pk}
            ), '/auth/login/?next='),

            (reverse('posts:follow_index'), '/auth/login/?next='),

            (reverse(
                'posts:profile_follow',
                kwargs={'username': self.user.username}
            ), '/auth/login/?next='),

            (reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.user.username}
            ), '/auth/login/?next=')
        ]

        for url, expected_redirect in urls_with_redirects:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, expected_redirect + url)

    def test_post_edit_url_redirect_another_authorized_user(self):
        """
        Проверка перенаправления при попытке редактировать чужой пост.
        """
        self.authorized_client.force_login(self.another_user)

        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            follow=True
        )

        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            )
        )

    def test_posts_urls_uses_correct_template(self):
        """URL-адрес (posts) использует соответствующий шаблон."""

        templates_url_names = [
            (reverse('posts:index'), 'posts/index.html'),

            (reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ), 'posts/group_list.html'),

            (reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            ), 'posts/post_detail.html'),

            (reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ), 'posts/profile.html'),

            (reverse('posts:post_create'), 'posts/create_post.html'),

            (reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            ), 'posts/create_post.html'),

            (reverse('posts:follow_index'), 'posts/follow.html')
        ]

        for address, template in templates_url_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_404_error_page_uses_correct_template(self):
        """При выводе ошибки 404 используется корректный шаблон."""

        address = '/nonexist-page/'
        template = 'core/404.html'

        response = self.authorized_client.get(address)
        self.assertTemplateUsed(response, template)
