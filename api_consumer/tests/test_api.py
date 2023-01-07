from unittest import TestCase
from unittest.mock import patch

from requests import Response

from api_consumer.api import Api


class TestApi(TestCase):
    def test_default_values_api(self):
        api = Api()
        self.assertEqual(api.url, "")
        self.assertEqual(api.output, "json")
        self.assertEqual(api.prev, "")
        self.assertEqual(api.next, "")
        self.assertDictEqual(
            api.headers,
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
        self.assertEqual(api.url, "http://test.com")
        self.assertEqual(api.output, "json")
        self.assertEqual(api.prev, "")
        self.assertEqual(api.next, "")
        self.assertDictEqual(
            api.headers,
            {
                "user-agent": "Vb API Consumer",
                "content-type": "application/json; charset=utf8",
            },
        )

    def test_get_instance(self):
        api = Api()
        api.config("http://test.com", secure=False)
        with patch("requests.get") as mock:
            r = Response()
            r.status_code = 200
            r.json = lambda: {"test": "ok"}
            mock.return_value = r

            result = api.get_instance("item", 1)
            self.assertTrue(mock.called)
            self.assertDictEqual(result, {"test": "ok"})
