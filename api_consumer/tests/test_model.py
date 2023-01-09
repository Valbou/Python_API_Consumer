from unittest import TestCase

from api_consumer.model import Model


class User(Model):
    pass


class TestModel(TestCase):
    def test_model_creation(self):
        user = User("http://test.com/api")
        self.assertEqual(user.item, "user")
        self.assertEqual(user._url, "http://test.com/api")

    def test_model_creation_with_given_item(self):
        user = User("http://test.com/api", "account")
        self.assertEqual(user.item, "account")
        self.assertEqual(user._url, "http://test.com/api")
