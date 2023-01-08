from unittest import TestCase
from unittest.mock import patch, MagicMock

from requests import Response

from api_consumer.api import Api
from api_consumer.exceptions import ApiConsumerException


class TestApi(TestCase):
    def test_default_values_api(self):
        api = Api()
        self.assertEqual(api._url, "")
        self.assertEqual(api._output, "json")
        self.assertEqual(api._prev, "")
        self.assertEqual(api._next, "")
        self.assertDictEqual(
            api._headers,
            {
                "user-agent": "Vb API Consumer",
                "content-type": "application/json; charset=utf8",
            },
        )

    def test_config(self):
        api = Api()
        api.config(
            url="http://test.com",
        )
        self.assertEqual(api._url, "http://test.com")
        self.assertEqual(api._output, "json")
        self.assertEqual(api._prev, "")
        self.assertEqual(api._next, "")
        self.assertDictEqual(
            api._headers,
            {
                "user-agent": "Vb API Consumer",
                "content-type": "application/json; charset=utf8",
            },
        )

    def test_get_instance(self):
        api = Api()
        api.config("http://test.com")

        with patch("requests.get") as mock:
            r = Response()
            r.status_code = 200
            r.json = lambda: {"test": "ok"}
            mock.return_value = r

            result = api.get_instance("item", 1)
            self.assertTrue(mock.called)
            self.assertDictEqual(result, {"test": "ok"})

    def test_error_get_instance(self):
        api = Api()
        api.config("http://test.com")

        with patch("requests.get") as mock:
            r = Response()
            r.status_code = 404
            r.request = MagicMock()
            r.request.method = "get"
            mock.return_value = r

            with self.assertRaises(ApiConsumerException):
                api.get_instance("item", 1)
            self.assertTrue(mock.called)

    def test_get_list(self):
        api = Api()
        api.config("http://test.com")

        with patch("requests.get") as mock:
            r = Response()
            r.status_code = 200
            r.json = lambda: {
                "previous": "page0",
                "next": "page2",
                "results": [{"test1": "ok"}, {"test2": "ok"}],
            }
            mock.return_value = r

            result = api.get_list("item")
            self.assertTrue(mock.called)
            self.assertEqual(result, [{"test1": "ok"}, {"test2": "ok"}])

    def test_error_get_list(self):
        api = Api()
        api.config("http://test.com")

        with patch("requests.get") as mock:
            r = Response()
            r.status_code = 404
            r.request = MagicMock()
            r.request.method = "get"
            mock.return_value = r

            with self.assertRaises(ApiConsumerException):
                api.get_list("item")
            self.assertTrue(mock.called)

    def test_post_instance(self):
        api = Api()
        api.config("http://test.com")

        with patch("requests.post") as mock:
            r = Response()
            r.status_code = 201
            r.json = lambda: {"test": "ok"}
            mock.return_value = r

            result = api.post_instance("item")
            self.assertTrue(mock.called)
            self.assertDictEqual(result, {"test": "ok"})

    def test_error_post_instance(self):
        api = Api()
        api.config("http://test.com")

        with patch("requests.post") as mock:
            r = Response()
            r.status_code = 500
            r.request = MagicMock()
            r.request.method = "post"
            mock.return_value = r

            with self.assertRaises(ApiConsumerException):
                api.post_instance("item")
            self.assertTrue(mock.called)

    def test_put_instance(self):
        api = Api()
        api.config("http://test.com")
        payload = {"id": "1"}

        with patch("requests.put") as mock:
            r = Response()
            r.status_code = 200
            r.json = lambda: {"id": "1", "test": "ok"}
            mock.return_value = r

            result = api.put_instance("item", payload)
            self.assertTrue(mock.called)
            self.assertDictEqual(result, {"id": "1", "test": "ok"})

    def test_patch_instance(self):
        api = Api()
        api.config("http://test.com")
        payload = {"id": "1"}

        with patch("requests.patch") as mock:
            r = Response()
            r.status_code = 200
            r.json = lambda: {"id": "1", "test": "ok"}
            mock.return_value = r

            result = api.patch_instance("item", payload)
            self.assertTrue(mock.called)
            self.assertDictEqual(result, {"id": "1", "test": "ok"})

    def test_delete_instance(self):
        api = Api()
        api.config("http://test.com")
        payload = {"id": "1"}

        with patch("requests.delete") as mock:
            r = Response()
            r.status_code = 204
            mock.return_value = r

            result = api.delete_instance("item", payload)
            self.assertTrue(mock.called)
            self.assertTrue(result)
