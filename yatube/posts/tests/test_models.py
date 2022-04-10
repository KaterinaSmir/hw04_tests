from django.contrib.auth import get_user_model
from django.test import TestCase
from ..models import Group, Post


User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test_description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test_text',
            group=cls.group,
        )

    def test_model_have_correct_str_in_group(self):
        self.assertEqual(self.group.title, str(self.group))

    def test_model_have_correct_str_in_post(self):
        self.assertEqual(self.post.text[:15], str(self.post))
