import math

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.POSTS_COUNT = 13

        cls.user = User.objects.create_user(username='TestUsername')
        cls.group = Group.objects.create(
            title='Тестовая группа 1',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.posts = Post.objects.bulk_create([
            Post(
                text=f'Текст тестового поста #{post_number}',
                author=cls.user,
                group=cls.group,
            ) for post_number in range(cls.POSTS_COUNT)
        ])

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_posts_show_correct_posts_quantity_on_page(self):
        """
        Paginator Posts отображает корректное количество
         постов на каждой странице
        """

        reverse_name = [
            reverse('posts:index'),
            reverse('posts:profile', kwargs={
                    'username': self.user.username}),
            reverse('posts:group_list', kwargs={
                    'slug': self.group.slug})
        ]

        remaining_posts_page: int = (
            math.ceil(self.POSTS_COUNT / settings.POSTS_DISPLAYED)
        )
        remaining_posts_count: int = (
            self.POSTS_COUNT
            - (remaining_posts_page - 1)
            * settings.POSTS_DISPLAYED
        )

        first_page_posts_count = (
            settings.POSTS_DISPLAYED
            if self.POSTS_COUNT >= settings.POSTS_DISPLAYED
            else remaining_posts_count
        )

        for reversed_name in reverse_name:
            with self.subTest(reversed_name=reversed_name):
                response = self.authorized_client.get(reversed_name)
                posts_on_page = len(response.context['page_obj'])
                self.assertEqual(posts_on_page, first_page_posts_count)

                response = self.authorized_client.get(
                    f'{reversed_name}?page={remaining_posts_page}'
                )
                posts_on_page = len(response.context['page_obj'])
                self.assertEqual(posts_on_page, remaining_posts_count)
