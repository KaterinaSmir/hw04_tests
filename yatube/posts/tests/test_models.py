from django.conf import settings
from .set_up_tests import PostLocators, PostTestSetUpMixin


class PostModelTest(PostTestSetUpMixin):
    def setUp(self):
        self.post = PostModelTest.post

    def test_post_models_have_correct_object_names(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        self.assertEqual(
            str(self.post), self.post.text[:settings.POST_SYMBOLS],
        )

    def test_post_models_have_correct_verbose_names(self):
        field_verbose = {
            'text': PostLocators.TEXT_VERBOSE,
            'pub_date': PostLocators.PUB_DATE_VERBOSE,
            'author': PostLocators.AUTHOR_VERBOSE_AND_HELP,
            'group': PostLocators.GROUP_VERBOSE,
        }
        self.check_correct_meta(field_verbose, verbose=True)

    def test_post_models_have_correct_help_text(self):
        field_help_text = {
            'text': PostLocators.TEXT_HELP_TEXT,
            'pub_date': PostLocators.PUB_DATE_HELP_TEXT,
            'author': PostLocators.AUTHOR_VERBOSE_AND_HELP,
            'group': PostLocators.GROUP_HELP_TEXT,
        }
        self.check_correct_meta(field_help_text, help_text=True)


class GroupModelTest(PostTestSetUpMixin):
    def test_group_models_have_correct_object_names(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        group = GroupModelTest.group
        self.assertEqual(str(group), group.title, )
