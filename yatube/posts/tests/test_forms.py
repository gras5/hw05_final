import shutil

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post

from .test_views import TEMP_MEDIA_ROOT, TEST_IMAGE

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username='TestUsername')
        cls.group = Group.objects.create(
            title='Тестовая группа 1',
            slug='test_slug',
            description='Тестовое описание',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_posts_form_create_post(self):
        """
        Проверка создания поста через форму на странице post_create
        """

        posts_count = Post.objects.count()

        form_data = {
            'text': 'Текст для тестового поста 1',
            'image': TEST_IMAGE,
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            )
        )
        self.assertTrue(Post.objects.count() > posts_count)
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text=form_data['text'],
                image=f'posts/{form_data["image"]}'
            ).exists()
        )

    def test_posts_form_edit_post(self):
        """
        Проверка редактирования поста через форму на странице post_edit
        """

        post = Post.objects.create(
            text='Текст для тестового поста 1',
            author=self.user,
            group=self.group
        )

        posts_count = Post.objects.count()

        form_data = {
            'text': 'Измененный текст для тестового поста 1',
        }

        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.pk}),
            data=form_data,
            follow=True
        )

        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={
                'post_id': post.pk
            }))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                pk=post.pk,
                author=self.user,
                text=form_data['text']
            ).exists()
        )

    def test_comment_create_form(self):
        """
        Проверка создания комментария через форму под постом
        """
        post = Post.objects.create(
            text='Пост для комментариев',
            author=self.user,
            group=self.group
        )

        comments_count = post.comments.count()

        form_data = {
            'text': 'Тест комментариев'
        }

        url = reverse('posts:add_comment', kwargs={'post_id': post.pk})

        response = self.authorized_client.post(
            url,
            data=form_data,
            follow=True
        )

        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={
                'post_id': post.pk
            }))

        self.assertTrue(comments_count < post.comments.count())

        self.assertTrue(
            post.comments.filter(
                text=form_data['text']
            ).exists()
        )
