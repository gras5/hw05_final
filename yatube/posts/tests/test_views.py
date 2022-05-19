import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Comment, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
TEST_IMAGE = SimpleUploadedFile(
    name='small.gif',
    content=(
        b'\x47\x49\x46\x38\x39\x61\x02\x00'
        b'\x01\x00\x80\x00\x00\x00\x00\x00'
        b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
        b'\x00\x00\x00\x2C\x00\x00\x00\x00'
        b'\x02\x00\x01\x00\x00\x02\x02\x0C'
        b'\x0A\x00\x3B'
    ),
    content_type='image/gif'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUsername')
        cls.POSTS_COUNT = 1

        cls.group = Group.objects.create(
            title='Тестовая группа 1',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Этот текст для проверки тестового поста 1',
            group=cls.group,
            image=TEST_IMAGE
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тест комментариев'
        )
        cls.another_group = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug_2',
            description='Тестовое описание 2',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        cache.clear()

    def test_post_create_edit_page_show_correct_context(self):
        """
        Шаблон для posts:post_create post_edit сформирован
         с правильным контекстом
        """

        reversed_names = [
            reverse('posts:post_create'),
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            )
        ]

        for reversed_name in reversed_names:
            with self.subTest(reversed_name=reversed_name):
                response = self.authorized_client.get(reversed_name)

                post_form = response.context.get('form')

                if(response.context.get('edited_post_id')):
                    post_from_form = post_form.instance
                    self.assertEqual(post_from_form, self.post)

                self.assertIsInstance(post_form, PostForm)

    def test_posts_pages_show_correct_context(self):
        """
        Шаблоны group_list, profile и post_detail
         сформированы с правильным контекстом.
        """

        urls_with_context = [
            (
                'group',
                self.group,
                reverse('posts:group_list', kwargs={'slug': self.group.slug})
            ),

            (
                'author',
                self.user,
                reverse(
                    'posts:profile',
                    kwargs={'username': self.user.username}
                )
            ),

            (
                'posts_number',
                self.POSTS_COUNT,
                reverse(
                    'posts:profile',
                    kwargs={'username': self.user.username}
                )
            ),

            (
                'post',
                self.post,
                reverse(
                    'posts:post_detail',
                    kwargs={'post_id': self.post.pk}
                )
            ),

            (
                'author_posts_number',
                self.POSTS_COUNT,
                reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
            ),
        ]

        for context_var, exp_value, reversed_name in urls_with_context:
            with self.subTest(reversed_name=reversed_name):
                response = self.authorized_client.get(reversed_name)
                context_var_value = response.context.get(context_var)

                self.assertEqual(context_var_value, exp_value)

    def test_posts_pages_show_correct_post_on_page(self):
        """
        Шаблоны posts:index, group_list, profile и post_detail с
         контекстами отображают корректные посты.
        """

        expected_post_on_pages = [
            (
                self.post,
                reverse('posts:index')
            ),

            (
                self.post,
                reverse('posts:group_list', kwargs={'slug': self.group.slug})
            ),

            (
                self.post,
                reverse(
                    'posts:profile',
                    kwargs={'username': self.user.username}
                )
            ),

        ]

        for expected_post, url in expected_post_on_pages:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                posts_on_page = response.context.get('page_obj').object_list

                self.assertIn(expected_post, posts_on_page)

    def test_posts_post_detail_show_correct_context(self):
        """
        На странице поста отображается корректный пост
        """
        url = reverse('posts:post_detail', kwargs={'post_id': self.post.pk})

        response = self.authorized_client.get(url)
        post_on_page = response.context.get('post')

        self.assertEqual(post_on_page, self.post)

    def test_posts_post_not_viewed_in_other_group(self):
        """
        Пост не отображается в группе к которой он не относится
        """
        url = reverse(
            'posts:group_list',
            kwargs={'slug': self.another_group.slug}
        )

        response = self.authorized_client.get(url)
        posts_group_list = response.context.get('page_obj').object_list

        self.assertNotIn(self.post, posts_group_list)

    def test_post_detail_page_show_post_comments(self):
        """
        Страница post:detail отображает комментарии под постом
        """
        url = reverse('posts:post_detail', kwargs={'post_id': self.post.pk})

        response = self.authorized_client.get(url)
        post = response.context.get('post')
        comments_on_page = post.comments.all()

        self.assertIn(self.comment, comments_on_page)

    def test_index_page_cache(self):
        """
        Проверка кеширования главной страницы
        """
        url = reverse('posts:index')

        another_post = Post.objects.create(
            text='Пост для проверки кэширования',
            author=self.user
        )

        response_1 = self.authorized_client.get(url)
        another_post.delete()
        response_2 = self.authorized_client.get(url)

        self.assertEqual(
            response_1.content,
            response_2.content
        )

        cache.clear()
        response_3 = self.authorized_client.get(url)

        self.assertNotEqual(
            response_1.content,
            response_3.content
        )
