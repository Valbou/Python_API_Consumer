import asyncio
import logging
from functools import partial
from typing import Optional, Union

import requests

from .exceptions import ApiConsumerException

logger = logging.getLogger(__name__)


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
        self._verbose = verbose
        # reset prev/next URL
        self._prev = ""
        self._next = ""

    # TODO: change to permit to add more requests to executor
    # with a pending status of queries flushed on demand
    async def async_req(self, funct, **kargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, partial(funct, **kargs))

    def get_list(
        self, item: str, options: Optional[list] = None, page: Optional[str] = None
    ) -> list:
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
            self._debug(item, r)
        else:
            datas = r.json()
            if isinstance(datas, dict):
                # TODO: permit to overload names
                self._prev = datas.get("previous", "")
                self._next = datas.get("next", "")
                return datas.get("results", [])
            else:
                return datas

    def get_instance(
        self, item: str, id_instance: Union[str, int], options: Optional[list] = None
    ) -> dict:
        """To collect an unique item"""
        options = options or []

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
            self._debug(item, r)

    def post_instance(
        self, item: str, payload: Optional[dict] = None, options: Optional[list] = None
    ) -> dict:
        """To save a new item"""
        options = options or []

        r = asyncio.run(
            self.async_req(
                funct=requests.post,
                url=self._gen_url(item, options=options),
                headers=self._headers,
                json=payload,
            )
        )
        if r.status_code != 201:
            self._debug(item, r)
        return r.json()

    def put_instance(
        self, item: str, payload: Optional[dict] = None, options: Optional[list] = None
    ) -> Optional[dict]:
        """To update a complete item"""
        options = options or []
        payload = payload or dict()
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
                self._debug(item, r)
            return r.json()
        return None

    def patch_instance(
        self, item: str, payload: Optional[dict] = None, options: Optional[list] = None
    ) -> Optional[dict]:
        """To update partially an item"""
        options = options or []
        payload = payload or dict()
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
                self._debug(item, r)
            return r.json()
        return None

    def delete_instance(
        self, item: str, payload: Optional[dict] = None, options: Optional[list] = None
    ) -> bool:
        """To delete an item"""
        options = options or []
        payload = payload or dict()
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
            self._debug(item, r)
        return True

    def _debug(self, item: str, r: requests.Response):
        """Helper for debug purposes"""
        complement = ""
        if self._verbose:
            complement = (
                f"\nErr {r.request.method} {r.status_code}\n"
                f"{r.url}\n##########\n{r.content}\n##########"
            )
        else:
            complement = f" - Err {r.request.method} {r.status_code}"
        err = f"API error ({item}){complement}"
        logger.error(err)
        raise ApiConsumerException(err)

    def __str__(self) -> str:
        return f"API base endpoint: {self._url}"

    def _gen_url(
        self, item: str, id_instance: str = "", options: Optional[list] = None
    ) -> str:
        """To construct URL"""
        options = options or []

        # TODO: permit to add an URL formatter object to get more flexibility
        return f"{self._url}/{item}/{id_instance}?format={self._output}{self._options(options)}"

    def _options(self, options: list) -> str:
        """Permit to add options on call"""
        return ("&" + "&".join(options)) if len(options) else ""
