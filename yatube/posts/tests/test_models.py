from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа 1',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Этот текст для проверки тестового поста 1',
            group=cls.group
        )

    def test_models_have_correct_str_method(self):
        """Проверяем, что у моделей корректно работает __str__."""

        str_method_results = [
            (self.post.text[:settings.POST_SYMBOLS_DISPLAYED], str(self.post)),
            (self.group.title, str(self.group)),
        ]

        for expected_result, str_result in str_method_results:
            with self.subTest(expected_result=expected_result):
                self.assertEqual(
                    expected_result,
                    str_result,
                    'Функция __str__ в модели Post работает неверно'
                )

    def test_models_have_correct_verbose_names(self):
        """Проверяем, что у полей моделей Post и Group задан verbose_name"""

        models_with_verbose_names = [
            ('title', 'Название', self.group),
            ('slug', 'Ссылка', self.group),
            ('description', 'Описание', self.group),
            ('text', 'Текст поста', self.post),
            ('pub_date', 'Дата публикации', self.post),
            ('author', 'Автор', self.post),
            ('group', 'Группа', self.post)
        ]

        for field, expected_verbose_name, model in models_with_verbose_names:
            with self.subTest(field=field):
                self.assertEqual(
                    model._meta.get_field(field).verbose_name,
                    expected_verbose_name
                )

    def test_models_have_correct_help_texts(self):
        """Проверяем, что у полей моделей Post и Group задан help_text"""

        models_with_help_texts = [
            ('title', 'Укажите название группы', self.group),
            (
                'slug',
                'Укажите уникальную ссылку (на английском) для группы',
                self.group
            ),
            ('description', 'Укажите описание группы', self.group),
            ('text', 'Текст поста', self.post),
            ('author', 'Укажите автора поста', self.post),
            ('group', 'Группа, к которой будет относиться пост', self.post)
        ]

        for field, expected_help_text, model in models_with_help_texts:
            with self.subTest(field=field):
                self.assertEqual(
                    model._meta.get_field(field).help_text,
                    expected_help_text
                )
