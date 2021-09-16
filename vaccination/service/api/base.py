"""
Abstract API service.

This file is part of the vaccination.py.

(c) 2021 Temuri Takalandze <me@abgeo.dev>

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.
"""


from string import Template

import requests
from requests.models import Response


def retry_request(times):
    """
    Request Retry Decorator.

    :param times: The number of times to repeat the wrapped function/method.
    :return:
    """

    def decorator(function):
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < times:
                response = function(*args, **kwargs)
                if response.status_code == 404:
                    attempt += 1
                    continue

                return response

            return function(*args, **kwargs)

        return wrapper

    return decorator


class BaseAPIService:
    """
    Base service for working with the APIs.
    """

    url_template = None

    @retry_request(times=20)
    def _make_request(self, method: str, **kwargs) -> Response:
        url = Template(self.url_template).substitute(**kwargs.get("url", {}))
        del kwargs["url"]
        return requests.request(method, url, **kwargs)

    def _get(self, **kwargs):
        return self._make_request("get", **kwargs).json()

    def _post(self, **kwargs):
        return self._make_request("post", **kwargs).json()
