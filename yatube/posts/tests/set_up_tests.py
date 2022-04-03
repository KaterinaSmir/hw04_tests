import tempfile
import shutil

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from ..models import Post, Group, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


class UserLocators:
    USERNAME = 'auth'
    USERNAME2 = 'auth2'
    USERNAME3 = 'auth3'


class GroupLocators:
    TITLE = 'Тестовая группа'
    SLUG = 'new_test_group'
    DESCRIPTION = 'Тестовое описание'
    PK = 1


class PostLocators:
    TEXT = 'Тестовый пост'
    PK = '4242'
    TEXT_VERBOSE = 'Содержание поста'
    TEXT_HELP_TEXT = 'Введите текст поста'
    COMMENT_POST_TEXT = 'Комментарий для поста'
    COMMENT_POST_TEXT_FORM = 'Комментарий для формы'
    PUB_DATE_VERBOSE = 'Дата публикации поста'
    PUB_DATE_HELP_TEXT = 'Дата публикации поста (автоматически определяется)'
    AUTHOR_VERBOSE_AND_HELP = 'Автор поста'
    GROUP_VERBOSE = 'Название группы'
    GROUP_HELP_TEXT = 'Группа, к которой будет относиться пост'
    TEXT_FOR_FORM = 'Тестовый текст формы'
    EDIT_FORM_TEXT = 'Edit_new_text'
    GIF_FOR_TEST = (
        b'\x47\x49\x46\x38\x39\x61\x01\x00'
        b'\x01\x00\x00\x00\x00\x21\xf9\x04'
        b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
        b'\x00\x00\x01\x00\x01\x00\x00\x02'
        b'\x02\x4c\x01\x00\x3b'
    )
    GIF_FOR_TEST_NAME = 'gif_for_test.gif'
    GIF_FOR_TEST_NAME_VIEWS = 'gif_for_test2.gif'
    GIF_FOR_TEST_TYPE = 'image/gif'
    IMAGE_UPLOADED = SimpleUploadedFile(
        name=GIF_FOR_TEST_NAME,
        content=GIF_FOR_TEST,
        content_type=GIF_FOR_TEST_TYPE,
    )
    IMAGE_UPLOADED_VIEWS = SimpleUploadedFile(
        name=GIF_FOR_TEST_NAME_VIEWS,
        content=GIF_FOR_TEST,
        content_type=GIF_FOR_TEST_TYPE,
    )


class PostPagesLocators:
    GUEST_PAGES = (
        '/', '/group/new_test_group/', '/profile/auth/', '/posts/4242/',
    )
    PAGE_404 = '/test_404_page/'
    CREATE_EDIT_PAGES = ('/create/', '/posts/4242/edit/')
    POST_INDEX = reverse('posts:index')
    POST_CREATE = reverse('posts:post_create')
    POST_PROFILE = reverse('posts:profile', kwargs={'username': 'auth'})
    POST_EDIT = reverse('posts:post_edit', kwargs={'post_id': '4242'})
    POST_DETAIL = reverse('posts:post_detail', kwargs={'post_id': '4242'})
    ADD_COMMENT = reverse('posts:add_comment', kwargs={'post_id': '4242'})
    FOLLOW_USER_AUTHOR = reverse('posts:profile_follow',
                                 kwargs={'username': 'auth2'}
                                )
    UNFOLLOW_USER_AUTHOR = reverse('posts:profile_unfollow',
                                   kwargs={'username': 'auth2'}
                                  )
    FOLLOW_INDEX = reverse('posts:follow_index')
    templates_url_names = (
        ('posts/index.html', '/'),
        ('posts/group_list.html', '/group/new_test_group/'),
        ('posts/profile.html', '/profile/auth/'),
        ('posts/post_detail.html', '/posts/4242/'),
        ('posts/create_post.html', '/create/'),
        ('posts/create_post.html', '/posts/4242/edit/'),
    )
    templates = (
        ('posts/index.html', reverse('posts:index')),
        ('posts/group_list.html',
         reverse('posts:group_posts', kwargs={'slug': 'new_test_group'})),
        ('posts/profile.html',
         reverse('posts:profile', kwargs={'username': 'auth'})),
        ('posts/post_detail.html',
         reverse('posts:post_detail', kwargs={'post_id': '4242'})),
        ('posts/create_post.html', reverse('posts:post_create')),
        ('posts/create_post.html',
         reverse('posts:post_edit', kwargs={'post_id': '4242'})),
    )
    templates_1_post = (
        reverse('posts:index'),
        reverse('posts:group_posts', kwargs={'slug': 'new_test_group'}),
        reverse('posts:profile', kwargs={'username': 'auth'}),
    )
    templates_context = (
        reverse('posts:index'),
        reverse('posts:group_posts', kwargs={'slug': 'new_test_group'}),
        reverse('posts:post_detail', kwargs={'post_id': '4242'}),
        reverse('posts:profile', kwargs={'username': 'auth'}),
    )
    templates_paginator = (
        reverse('posts:index'),
        reverse('posts:group_posts', kwargs={'slug': 'new_test_group'}),
        reverse('posts:profile', kwargs={'username': 'auth'}),
    )


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostTestSetUpMixin(TestCase):
    @classmethod
    def setUpClass(cls):
        """Создаем тестового пользователя, группу и пост."""
        super().setUpClass()
        cls.user = User.objects.create_user(username=UserLocators.USERNAME)
        cls.group = Group.objects.create(
            title=GroupLocators.TITLE,
            slug=GroupLocators.SLUG,
            description=GroupLocators.DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=PostLocators.TEXT,
            pk=PostLocators.PK,
            group=cls.group,
            image=PostLocators.IMAGE_UPLOADED_VIEWS,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text=PostLocators.COMMENT_POST_TEXT,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def check_url_response(self, pages, redirect=False, authorized=False):
        for url in pages:
            with self.subTest(url=url):
                if redirect:
                    response = self.guest_client.get(url, follow=True)
                    self.assertRedirects(response, f'/auth/login/?next={url}')
                elif authorized:
                    response = self.authorized_client.get(url)
                    self.assertEqual(response.status_code, self.response_200, )
                else:
                    response = self.guest_client.get(url)
                    self.assertEqual(response.status_code, self.response_200,
                                     f'url - {url} код {response.status_code}',
                                     )

    def check_correct_meta(self, dict_name, verbose=False, help_text=False):
        for value, expected in dict_name.items():
            with self.subTest(value=value):
                if verbose:
                    self.assertEqual(
                        self.post._meta.get_field(value).verbose_name, expected
                    )
                elif help_text:
                    self.assertEqual(
                        self.post._meta.get_field(value).help_text, expected
                    )
                else:
                    raise Exception(
                        'Мета параметр не определен или определен неверно'
                    )
