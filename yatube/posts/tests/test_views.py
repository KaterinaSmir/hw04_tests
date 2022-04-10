import time
from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Group, Post
from ..views import NUMBER_OF_ENTIES


User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test_description',
        )
        cls.another_group = Group.objects.create(
            title='another_test_group',
            slug='another_test_slug',
            description='another_test_description',
        )
        posts = []
        for num in range(12):
            posts.append(
                Post.objects.create(
                    author=cls.user,
                    text=f'test_text_{num}',
                    group=cls.group,
                )
            )
            time.sleep(0.01)
        cls.post = Post.objects.create(
            author=cls.user,
            text='test_text',
            group=cls.group,
        )
        cls.posts_num = Post.objects.count()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_url_names_use_correct_templates(self):
        templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse('posts:profile',
                kwargs={'username': self.user.username}
            ): 'posts/profile.html',
            reverse('posts:post_detail',
                kwargs={'post_id': self.post.pk}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                kwargs={'post_id': self.post.pk}
            ): 'posts/create_post.html',
        }
        for name, template in templates.items():
            with self.subTest(name=name):
                response = self.authorized_client.get(name)
                self.assertTemplateUsed(response, template)

    def test_index_page_get_correct_context(self):
        response = self.client.get(reverse('posts:index'))
        first_post = response.context['page_obj'][0]
        context_items = {
            first_post.author: self.user,
            first_post.text: self.post.text,
            first_post.group: self.post.group,
            first_post.id: self.post.pk,
            first_post.group.slug: self.post.group.slug,
            first_post.group.title: self.group.title
        }
        for context_data, test_data in context_items.items():
            with self.subTest(context_data=context_data):
                self.assertEqual(context_data, test_data)

    def test_group_list_page_get_correct_context(self):
        response = self.client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            )
        )
        first_post = response.context['page_obj'][0]
        context_items = {
            first_post.author: self.user,
            first_post.text: self.post.text,
            first_post.group: self.post.group,
            first_post.id: self.post.pk,
            first_post.group.slug: self.post.group.slug,
            first_post.group.title: self.group.title
        }
        for context_data, test_data in context_items.items():
            with self.subTest(context_data=context_data):
                self.assertEqual(context_data, test_data)

    def test_profile_page_get_correct_context(self):
        response = self.client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            )
        )
        first_post = response.context['page_obj'][0]
        context_items = {
            first_post.author: self.user,
            first_post.text: self.post.text,
            first_post.group: self.post.group,
            first_post.id: self.post.pk,
            first_post.group.slug: self.post.group.slug,
            first_post.group.title: self.group.title
        }
        for context_data, test_data in context_items.items():
            with self.subTest(context_data=context_data):
                self.assertEqual(context_data, test_data)
        self.assertEqual(response.context['author'], self.user)

    def test_post_detail_page_get_correct_context(self):
        response = self.client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            )
        )
        post = response.context['post']
        self.assertEqual(post.id, self.post.pk)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.post.author)

    def test_post_create_page_get_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_get_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            )
        )
        form = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
        self.assertTrue(response.context['is_edit'])

    def test_posts_number_on_first_page(self):
        pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username})
        ]
        for page in pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertEqual(
                    len(response.context['page_obj']), NUMBER_OF_ENTIES
                )

    def test_posts_number_on_last_page(self):
        last_page_num = self.posts_num // NUMBER_OF_ENTIES + 1
        pages = [
            reverse('posts:index') + f'?page={last_page_num}',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ) + f'?page={last_page_num}',
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ) + f'?page={last_page_num}'
        ]
        for page in pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertEqual(
                    len(response.context['page_obj']),
                    self.posts_num % NUMBER_OF_ENTIES
                )

    def test_posts_pages_with_new_group(self):
        last_page_num = self.posts_num // NUMBER_OF_ENTIES + 1
        pages = [
            reverse('posts:index') + f'?page={last_page_num}',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.another_group.slug}
            ) + f'?page={last_page_num}',
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ) + f'?page={last_page_num}'
        ]
        for page in pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                posts_on_page = response.context['page_obj']
                Post.objects.create(
                    author=self.user,
                    text=self.post.text,
                    group=self.another_group,
                )
                response = self.authorized_client.get(page)
                self.assertEqual(
                    len(response.context['page_obj']),
                    len(posts_on_page) + 1
                )
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ) + f'?page={last_page_num}'
        )
        posts_on_page = response.context['page_obj']
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ) + f'?page={last_page_num}'
        )
        self.assertEqual(
            len(response.context['page_obj']),
            len(posts_on_page)
        )
