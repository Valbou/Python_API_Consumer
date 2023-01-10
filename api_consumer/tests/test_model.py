from unittest import TestCase

from api_consumer.model import Model


class User(Model):
    public = "public"
    _protected = "protected"
    __private = "private"

    def set_protected(self, value: str) -> str:
        self._protected = value
        return self._protected

    def get_protected(self) -> str:
        return self._protected

    @property
    def get_private(self) -> str:
        return self.__private


class TestModel(TestCase):
    def test_model_creation(self):
        user = User("http://test.com/api")
        self.assertEqual(user._item, "user")
        self.assertEqual(user._url, "http://test.com/api")

    def test_model_creation_with_given_item(self):
        user = User("http://test.com/api", "account")
        self.assertEqual(user._item, "account")
        self.assertEqual(user._url, "http://test.com/api")

    def test_is_public_attribute(self):
        user = User("http://test.com")
        self.assertTrue(user._is_public_attribute(("public", "public")))
        self.assertFalse(user._is_public_attribute(("_protected", "protected")))
        self.assertFalse(user._is_public_attribute(("__private", "private")))
        self.assertFalse(
            user._is_public_attribute(
                ("_is_public_attribute", user._is_public_attribute)
            )
        )
        self.assertFalse(user._is_public_attribute(("save", user.save)))

    def test_is_object_model(self):
        user = User("http://test.com")
        self.assertTrue(user._is_object(("user", user)))
        self.assertFalse(user._is_object(("public", "public")))
        self.assertFalse(user._is_object(("__private", 12)))

    def test_build_dictionary(self):
        user = User("http://test.com")
        result = user._build_dictionary()
        self.assertEqual(
            set(result.keys()), 
            {"get_private", "id", "verbose", "public"}
        )
