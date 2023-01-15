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


class Group(Model):
    """For testing only"""

    _item = "grouped"


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

    def test_save_post(self):
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

    def test_save_patch(self):
        user = User("http://test.com")
        user.id = 123
        user.public = "not public"
        self.assertEqual(user.public, "not public")

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
            r.json = lambda: {"id": 321, "public": "public test"}
            mock.return_value = r

            result = user.from_db(321)
            self.assertTrue(result)
            self.assertEqual(user.id, 321)
            self.assertEqual(user.public, "public test")

    def test_from_db_with_id_in_model(self):
        user = User("http://test.com")
        user.id = 321

        with patch("requests.get") as mock:
            r = Response()
            r.status_code = 200
            r.json = lambda: {"id": 321, "public": "public test 2"}
            mock.return_value = r

            result = user.from_db()
            self.assertTrue(result)
            self.assertEqual(user.id, 321)
            self.assertEqual(user.public, "public test 2")

    def test_limitless_not_paginated_results(self):
        user = User("http://test.com")

        with patch("requests.get") as mock:
            r = Response()
            r.status_code = 200
            r.json = lambda: [
                {"id": 123, "public": "public test 1"},
                {"id": 321, "public": "public test 2"},
            ]
            mock.return_value = r

            results = user._paginated_results("user", 0, [])
            mock.assert_called()
            self.assertEqual(
                results,
                [
                    {"id": 123, "public": "public test 1"},
                    {"id": 321, "public": "public test 2"},
                ],
            )

    def test_limited_to_one_paginated_results(self):
        user = User("http://test.com")

        with patch("requests.get") as mock:
            r = Response()
            r.status_code = 200
            r.json = lambda: [
                {"id": 123, "public": "public test 1"},
                {"id": 321, "public": "public test 2"},
                {"id": 147, "public": "public test 3"},
                {"id": 369, "public": "public test 4"},
            ]
            mock.return_value = r

            results = user._paginated_results("user", 2, [])
            mock.assert_called()
            self.assertEqual(
                results,
                [
                    {"id": 123, "public": "public test 1"},
                    {"id": 321, "public": "public test 2"},
                ],
            )

    def test_limited_to_many_paginated_results(self):
        user = User("http://test.com")

        with patch("requests.get") as mock:
            r = Response()
            r.status_code = 200
            r.json = lambda: {
                "previous": "page0",
                "next": "page2",
                "results": [
                    {"id": 123, "public": "public test 1"},
                    {"id": 321, "public": "public test 2"},
                ],
            }
            mock.return_value = r

            results = user._paginated_results("user", 3, [])
            mock.assert_called()
            self.assertEqual(mock.call_count, 2)
            self.assertEqual(
                results,
                [
                    {"id": 123, "public": "public test 1"},
                    {"id": 321, "public": "public test 2"},
                    {"id": 123, "public": "public test 1"},
                ],
            )

    def test_define_item(self):
        user = User("http://test.com")
        result = user._define_item(User)
        self.assertEqual(result, User._item)
        self.assertEqual(result, "user")

    def test_define_item_without_class(self):
        user = User("http://test.com")
        result = user._define_item()
        self.assertEqual(result, User._item)
        self.assertEqual(result, "user")

    def test_define_item_with_another_class(self):
        user = User("http://test.com")
        self.assertEqual(Group._item, "grouped")
        result = user._define_item(Group)
        self.assertEqual(result, Group._item)
        self.assertEqual(result, "grouped")

    def test_define_item_without_item_and_with_another_class(self):
        user = User("http://test.com")
        Group._item = ""
        self.assertEqual(user._item, "user")
        self.assertEqual(Group._item, "")
        result = user._define_item(Group)
        self.assertEqual(result, "group")
        Group._item = "group"

    def test_from_query(self):
        user = User("http://test.com")

        with patch("requests.get") as mock:
            r = Response()
            r.status_code = 200
            r.json = lambda: [
                {"id": 123, "public": "public test 1"},
                {"id": 321, "public": "public test 2"},
            ]
            mock.return_value = r

            results = user.from_query(model_class=User)
            self.assertIsInstance(results, list)
            for i, result in enumerate(results):
                with self.subTest(i):
                    self.assertIsInstance(result, User)

    def test_from_query_fetch_one_instance(self):
        user = User("http://test.com")

        with patch("requests.get") as mock:
            r = Response()
            r.status_code = 200
            r.json = lambda: [
                {"id": 123, "public": "public test 1"},
                {"id": 321, "public": "public test 2"},
            ]
            mock.return_value = r

            results = user.from_query(limit=1, model_class=User)
            self.assertIsInstance(results, User)

    def test_from_json(self):
        user = User("http://test.com")
        datas = {"id": 123, "public": "public from json"}
        result = user.from_json(datas)
        self.assertTrue(result)
        self.assertEqual(user.id, 123)
        self.assertEqual(user.public, "public from json")

    def test_auto_typing_int(self):
        user = User("http://test.com")
        result = user._auto_typing("id", "123")
        self.assertIsInstance(result, int)
        self.assertEqual(result, 123)

    def test_auto_typing_str(self):
        user = User("http://test.com")
        result = user._auto_typing("public", 123)
        self.assertIsInstance(result, str)
        self.assertEqual(result, "123")

    def test_auto_typing_not_modified(self):
        user = User("http://test.com")
        result = user._auto_typing("id", "test")
        self.assertEqual(result, "test")

    def test_check_model_class(self):
        user = User("http://test.com")
        result = user._check_model_class(User)
        self.assertEqual(result, User)

    def test_factory_without_model_class(self):
        user = User("http://test.com")
        data = {"id": 123, "public": "public from factory"}
        new_user = user.factory(data)
        self.assertIsInstance(new_user, User)
        self.assertEqual(new_user.id, 123)
        self.assertEqual(new_user.public, "public from factory")

    def test_factory_with_model_class(self):
        user = User("http://test.com")
        data = {"id": 123, "public": "public from factory"}
        new_group = user.factory(data, Group)
        self.assertIsInstance(new_group, Group)
        self.assertEqual(new_group.id, 123)
        self.assertEqual(new_group.public, "public from factory")

    def test_factory_list(self):
        user = User("http://test.com")
        data_list = [
            {"id": 1, "public": "public test 1"},
            {"id": 2, "public": "public test 2"},
            {"id": 3, "public": "public test 3"},
        ]
        results = user.factory_list(data_list)
        for i, r in enumerate(results):
            with self.subTest(i):
                self.assertIsInstance(r, User)
                self.assertEqual(r.id, i + 1)
                self.assertEqual(r.public, f"public test {i+1}")
