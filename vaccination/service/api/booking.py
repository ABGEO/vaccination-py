"""
This module contains the API service for working with booking.moh.gov.ge's API.

This file is part of the vaccination.py.

(c) 2021 Temuri Takalandze <me@abgeo.dev>

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.
"""

import json
from datetime import date
from typing import Dict, Union, List

import requests
from requests.models import Response

from vaccination.service.api.base import BaseAPIService


class BookingAPIService(BaseAPIService):
    """
    Service for working with the booking.moh.gov.ge's API.
    """

    url_template = "https://booking.moh.gov.ge/$app/API/api/$path"
    security_numbers = []

    def _make_request(self, method: str, **kwargs) -> Response:
        kwargs["headers"] = {"SecurityNumber": self.__get_security_number()}
        return super()._make_request(method, **kwargs)

    def __get_security_number(self) -> str:
        if not self.security_numbers:
            self.security_numbers = requests.get(
                "https://vaccination.abgeo.dev/api/numbers?count=10"
            ).json()

        return self.security_numbers.pop(0)

    def get_available_quantities(self, app: str = "def") -> Dict[str, int]:
        """
        Make GET request to the "/Public/GetAvailableQuantities" endpoint.

        :param app: Application.
        :return: Endpoint response.
        """

        _quantities = self._get(
            url={"app": app, "path": "/Public/GetAvailableQuantities"}
        )
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

        return self._get(url={"app": app, "path": "/CommonData/GetServicesTypes"})

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

        return self._get(
            url={"app": app, "path": "/CommonData/GetRegions"},
            data={"serviceId": service, "onlyFree": only_free},
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

        return self._get(
            url={"app": app, "path": f"/CommonData/GetMunicipalities/{region}"},
            data={"serviceId": service, "onlyFree": only_free},
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

        return self._get(
            url={
                "app": app,
                "path": f"/CommonData/GetMunicipalityBranches/{service}/{municipality}",
            },
            data={"onlyFree": only_free},
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

        return self._post(
            url={"app": app, "path": "/PublicBooking/GetSlots"},
            json={
                "branchID": branch,
                "startDate": start_date.strftime("%Y-%m-%d"),
                "endDate": end_date.strftime("%Y-%m-%d"),
                "regionID": region,
                "serviceID": service,
            },
        )
