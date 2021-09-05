"""
This module contains the API service.

This file is part of the vaccination.py.

(c) 2021 Temuri Takalandze <me@abgeo.dev>

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.
"""

import json
from datetime import date
from string import Template
from typing import Dict, Union, List

import requests
from requests.models import Response

ResponseData = Union[str, List, Dict]


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


class APIService:
    """
    Service for working with the API.
    """

    url_template = "https://booking.moh.gov.ge/$app/API/api/$path"
    security_numbers = []

    def __get_security_number(self) -> str:
        if not self.security_numbers:
            self.security_numbers = requests.get(
                "https://vaccination.abgeo.dev/api/numbers?count=10"
            ).json()

        return self.security_numbers.pop(0)

    def __compose_url(self, app: str, path: str) -> str:
        return Template(self.url_template).substitute(app=app, path=path)

    @retry_request(times=20)
    def __make_request(
        self,
        method: str,
        app: str,
        path: str,
        params: Dict[str, any] = None,
        data: Dict[str, any] = None,
    ) -> Response:
        kwargs = {
            "headers": {
                "SecurityNumber": self.__get_security_number(),
            },
        }

        if params:
            kwargs["params"] = params

        if data:
            kwargs["json"] = data

        return requests.request(method, self.__compose_url(app, path), **kwargs)

    def __get(self, app: str, path: str, params: Dict[str, any] = None) -> ResponseData:
        return self.__make_request("get", app, path, params=params).json()

    def __post(self, app: str, path: str, data: Dict[str, any] = None) -> ResponseData:
        return self.__make_request("post", app, path, data=data).json()

    def get_available_quantities(self, app: str = "def") -> Dict[str, int]:
        """
        Make GET request to the "/Public/GetAvailableQuantities" endpoint.

        :param app: Application.
        :return: Endpoint response.
        """

        _quantities = self.__get(app, "/Public/GetAvailableQuantities")
        _quantities = json.loads(_quantities)
        quantities = {}
        for service, quantity in _quantities.items():
            quantities[service.lower()] = quantity

        return quantities

    def get_service_types(self, app: str = "def") -> List[Dict[str, str]]:
        """
        Make GET request to the "/CommonData/GetServicesTypes" endpoint.

        :param app: Application.
        :return: Endpoint response.
        """

        return self.__get(app, "/CommonData/GetServicesTypes")

    def get_regions(
        self, service: str, only_free: bool = True, app: str = "def"
    ) -> List[Dict[str, str]]:
        """
        Make GET request to the "/CommonData/GetRegions" endpoint.

        :param str service: Service ID.
        :param bool only_free: Get only free.
        :param app: Application.
        :return: Endpoint response.
        """

        return self.__get(
            app, "/CommonData/GetRegions", {"serviceId": service, "onlyFree": only_free}
        )

    def get_municipalities(
        self, region: str, service: str, only_free: bool = True, app: str = "def"
    ) -> List[Dict[str, str]]:
        """
        Make GET request to the "/CommonData/GetMunicipalities/{region}" endpoint.

        :param str region: Region ID.
        :param str service: Service ID.
        :param bool only_free: Get only free.
        :param app: Application.
        :return: Endpoint response.
        """

        return self.__get(
            app,
            f"/CommonData/GetMunicipalities/{region}",
            {"serviceId": service, "onlyFree": only_free},
        )

    def get_municipality_branches(
        self, service: str, municipality: str, only_free: bool = True, app: str = "def"
    ) -> List[Dict[str, str]]:
        """
        Make GET request to the
        "/CommonData/GetMunicipalityBranches/{service}/{municipality}" endpoint.

        :param str service: Service ID.
        :param str municipality: Municipality ID.
        :param bool only_free: Get only free.
        :param str app: Application.
        :return: Endpoint response.
        """

        return self.__get(
            app,
            f"/CommonData/GetMunicipalityBranches/{service}/{municipality}",
            {"onlyFree": only_free},
        )

    def get_slots(
        self,
        branch: str,
        region: str,
        service: str,
        start_date: date,
        end_date: date,
        app: str = "def",
    ) -> List[Dict[str, Union[str, List]]]:
        """
        Make POST request to the "/PublicBooking/GetSlots" endpoint.

        :param str branch: Branch ID.=
        :param str region: Region ID.
        :param str service: Service ID.
        :param date start_date: Start date.
        :param date end_date: End date.
        :param str app: Application.
        :return: Endpoint response.
        """

        return self.__post(
            app,
            "/PublicBooking/GetSlots",
            {
                "branchID": branch,
                "startDate": start_date.strftime("%Y-%m-%d"),
                "endDate": end_date.strftime("%Y-%m-%d"),
                "regionID": region,
                "serviceID": service,
            },
        )
