from unittest import TestCase

from api_consumer.model import Model


class User(Model):
    pass


class TestModel(TestCase):
    def test_model_creation(self):
        user = User("http://test.com/api/user")
        self.assertEqual(user.item, "user")
        self.assertEqual(user._url, "http://test.com/api/user")


# TODO:
# - Mock API methods
# - Test model methods
