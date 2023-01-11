from unittest import TestCase
from unittest.mock import patch

from requests import Response

from api_consumer.model import Model


class User(Model):
    """For testing only"""

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
        # Please avoid use of property decorator on Model inheritance classes
        # Else we may attempt to set a value to a property getter or send it in payload
        self.assertDictEqual(
            result,
            {"get_private": "private", "id": 0, "public": "public"},
        )

    def test_get_url(self):
        user = User("http://test.com")
        self.assertEqual(user.get_url(), "http://test.com")

    def test_save(self):
        user = User("http://test.com")
        user.id = 0
        user.public = "not public"
        self.assertEqual(user.public, "not public")

        # Without id it's a creation
        with patch("requests.post") as mock:
            r = Response()
            r.status_code = 201
            r.json = lambda: {"id": 123, "public": "public"}
            mock.return_value = r

            user_copy = user.save()
            self.assertDictEqual(user_copy, {"id": 123, "public": "public"})
            self.assertEqual(user.public, "public")
            self.assertEqual(user.id, 123)

        # With id it's an update
        with patch("requests.patch") as mock:
            r = Response()
            r.status_code = 200
            r.json = lambda: {"id": 123, "public": "public patched"}
            mock.return_value = r

            user_copy = user.save()
            self.assertDictEqual(user_copy, {"id": 123, "public": "public patched"})
            self.assertEqual(user.public, "public patched")
            self.assertEqual(user.id, 123)

    def test_from_db_with_id_in_args(self):
        user = User("http://test.com")

        with patch("requests.get") as mock:
            r = Response()
            r.status_code = 200
            r.json = lambda: {
                "id": 321, "public": "public test"
            }
            mock.return_value = r

            user.from_db(321)
            self.assertEqual(user.id, 321)
            self.assertEqual(user.public, "public test")

    def test_from_db_with_id_in_model(self):
        user = User("http://test.com")
        user.id = 321

        with patch("requests.get") as mock:
            r = Response()
            r.status_code = 200
            r.json = lambda: {
                "id": 321, "public": "public test 2"
            }
            mock.return_value = r

            user.from_db()
            self.assertEqual(user.id, 321)
            self.assertEqual(user.public, "public test 2")
