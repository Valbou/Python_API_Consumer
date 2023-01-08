import asyncio
from functools import partial
from typing import Union

import requests

from .exceptions import ApiConsumerException


class Api:
    """
    Base class to consume Django REST Framework APIs

    url: Endpoint URL
    output: expected output format
    prev: URL to previous page
    next: URL to next page
    headers: headers for requests calls
    """

    _url: str = ""
    _output: str = "json"
    _prev: str = ""
    _next: str = ""
    _headers: dict = {
        "user-agent": "Vb API Consumer",
        "content-type": "application/json; charset=utf8",
    }

    def config(
        self,
        url: str,
        output: str = "json",
        verbose=False,
    ) -> None:
        """Permit to change config on the fly if needed"""
        self._url = url
        self._output = output
        self.verbose = verbose

    async def async_req(self, funct, **kargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, partial(funct, **kargs))

    def get_list(self, item: str, options: list = None, page=None) -> list:
        """To collect a list of items"""
        options = options or []

        # DRF pagination management
        if page == "next" and self._next:
            url = self._next
        elif page == "prev" and self._prev:
            url = self._prev
        elif page is None:
            self._prev = ""
            self._next = ""
            url = self._gen_url(item, options=options)
        else:
            return []

        r = asyncio.run(
            self.async_req(funct=requests.get, url=url, headers=self._headers)
        )

        if r.status_code != 200:
            self.debug(item, r)
        else:
            datas = r.json()
            self._prev = datas["previous"]
            self._next = datas["next"]
            return datas["results"]

    def get_instance(self, item: str, id_instance: Union[str, int], options=[]) -> dict:
        """To collect an unique item"""
        r = asyncio.run(
            self.async_req(
                funct=requests.get,
                url=self._gen_url(item, id_instance=id_instance, options=options),
                headers=self._headers,
            )
        )
        if r.status_code == 200:
            return r.json()
        else:
            self.debug(item, r)

    def post_instance(self, item, payload={}, options=[]):
        """To save a new item"""
        r = asyncio.run(
            self.async_req(
                funct=requests.post,
                url=self._gen_url(item, options=options),
                headers=self._headers,
                json=payload,
            )
        )
        if r.status_code != 201:
            self.debug(item, r)
        return r.json()

    def put_instance(self, item, payload={}, options=[]):
        """To update a complete item"""
        id_instance = payload.get("id", None)
        if id_instance:
            r = asyncio.run(
                self.async_req(
                    funct=requests.put,
                    url=self._gen_url(item, id_instance, options),
                    headers=self._headers,
                    json=payload,
                )
            )
            if r.status_code != 200:
                self.debug(item, r)
            return r.json()
        return False

    def patch_instance(self, item, payload={}, options=[]):
        """To update partially an item"""
        id_instance = payload.get("id", None)
        if id_instance:
            r = asyncio.run(
                self.async_req(
                    funct=requests.patch,
                    url=self._gen_url(item, id_instance, options),
                    headers=self._headers,
                    json=payload,
                )
            )
            if r.status_code != 200:
                self.debug(item, r)
            return r.json()
        return False

    def delete_instance(self, item, payload={}, options=[]):
        """To delete an item"""
        id_instance = payload.get("id", None)
        r = asyncio.run(
            self.async_req(
                funct=requests.delete,
                url=self._gen_url(item, id_instance, options),
                headers=self._headers,
                data=payload,
            )
        )
        if r.status_code != 204:
            self.debug(item, r)
            return False
        return True

    def debug(self, item, r):
        """Helper for debug purposes"""
        complement = ""
        if self.verbose:
            complement = "\nErr {} {}\n{}\n##########\n{}\n##########".format(
                r.request.method, r.status_code, r.url, r.content
            )
        else:
            complement = f" - Err {r.request.method} {r.status_code}"
        err = f"API error ({item}){complement}"
        raise ApiConsumerException(err)

    def __str__(self):
        return f"{self._url}"

    def _gen_url(self, item, id_instance="", options=[]):
        """To construct URL"""
        # TODO: permit to add an URL formatter object to get more flexibility
        return "{}/{}/{}?format={}{}".format(
            self._url,
            item,
            id_instance,
            self._output,
            self._options(options),
        )

    def _options(self, options):
        """Permit to add options on call"""
        return ("&" + "&".join(options)) if len(options) else ""
