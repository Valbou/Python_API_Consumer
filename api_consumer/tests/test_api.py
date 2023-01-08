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
