from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Post

User = get_user_model()


class SubscriptionsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_1 = User.objects.create(username='test_user_1')
        cls.user_2 = User.objects.create(username='test_user_2')
        cls.user_3 = User.objects.create(username='test_user_3')

        Follow.objects.create(
            user=cls.user_1,
            author=cls.user_3
        )

    def setUp(self) -> None:
        self.authorized_client_1 = Client()
        self.authorized_client_1.force_login(self.user_1)

        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)

        self.authorized_client_3 = Client()
        self.authorized_client_3.force_login(self.user_3)

    def test_user_1_subscribe_to_another_user(self):
        """
        Проверка подписки пользователя на автора
        """
        url = reverse(
            'posts:profile_follow',
            kwargs={'username': self.user_2.username}
        )
        expected_redirect = reverse(
            'posts:profile',
            kwargs={'username': self.user_2.username}
        )

        following_count = self.user_1.follower.count()

        response = self.authorized_client_1.get(
            url,
            follow=True
        )

        self.assertRedirects(response, expected_redirect)
        self.assertTrue(following_count < self.user_1.follower.count())
        self.assertTrue(
            Follow.objects.filter(
                user=self.user_1,
                author=self.user_2,
            ).exists()
        )

    def test_user_1_unsubscribe_from_another_user(self):
        """
        Проверка отписки пользователя от автора
        """
        url = reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.user_3.username}
        )
        expected_redirect = reverse(
            'posts:profile',
            kwargs={'username': self.user_3.username}
        )

        following_count = self.user_1.follower.count()

        response = self.authorized_client_1.get(
            url,
            follow=True
        )

        self.assertRedirects(response, expected_redirect)
        self.assertTrue(following_count > self.user_1.follower.count())
        self.assertFalse(
            Follow.objects.filter(
                user=self.user_1,
                author=self.user_3,
            ).exists()
        )

    def test_user_3_post_visible_to_followers(self):
        """
        Проверка видимости постов для подписанного
         и неподписанного пользователя
        """
        post = Post.objects.create(
            text='Тестовый пост для подписчиков',
            author=self.user_3
        )

        client_url_result = (
            (self.authorized_client_1, reverse('posts:follow_index'), True),
            (self.authorized_client_2, reverse('posts:follow_index'), False),
        )

        for client, url, expected_result in client_url_result:
            with self.subTest(client=client):
                response = client.get(url)
                following_posts = response.context.get('page_obj').object_list

                self.assertEqual(post in following_posts, expected_result)
