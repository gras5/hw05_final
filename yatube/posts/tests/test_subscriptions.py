from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Post

User = get_user_model()


class SubscriptionsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_user')
        cls.author = User.objects.create(username='test_author')

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_user_subscribe_to_author(self):
        """
        Проверка подписки пользователя на автора
        """
        url = reverse(
            'posts:profile_follow',
            kwargs={'username': self.author.username}
        )
        expected_redirect = reverse(
            'posts:profile',
            kwargs={'username': self.author.username}
        )

        following_count = self.user.follower.count()

        response = self.authorized_client.get(
            url,
            follow=True
        )

        self.assertRedirects(response, expected_redirect)
        self.assertTrue(following_count < self.user.follower.count())
        self.assertTrue(
            Follow.objects.filter(
                user=self.user,
                author=self.author,
            ).exists()
        )

    def test_user_unsubscribe_from_author(self):
        """
        Проверка отписки пользователя от автора
        """
        Follow.objects.create(
            user=self.user,
            author=self.author,
        )

        url = reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.author.username}
        )
        expected_redirect = reverse(
            'posts:profile',
            kwargs={'username': self.author.username}
        )

        following_count = self.user.follower.count()

        response = self.authorized_client.get(
            url,
            follow=True
        )

        self.assertRedirects(response, expected_redirect)
        self.assertTrue(following_count > self.user.follower.count())
        self.assertFalse(
            Follow.objects.filter(
                user=self.user,
                author=self.author,
            ).exists()
        )

    def test_author_post_visible_to_followers(self):
        """
        Проверка видимости постов для подписанного
         и неподписанного пользователя
        """
        post = Post.objects.create(
            text='Тестовый пост для подписчиков',
            author=self.author
        )

        url = reverse('posts:follow_index')

        response = self.authorized_client.get(url)
        following_posts = response.context.get('page_obj').object_list

        self.assertNotIn(post, following_posts)

        Follow.objects.create(
            user=self.user,
            author=self.author
        )

        response = self.authorized_client.get(url)
        following_posts = response.context.get('page_obj').object_list

        self.assertIn(post, following_posts)
