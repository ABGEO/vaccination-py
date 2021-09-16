"""
This module contains the API service for working with stopcov-api.lotto.ge's API.

This file is part of the vaccination.py.

(c) 2021 Temuri Takalandze <me@abgeo.dev>

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.
"""

from vaccination.service.api.base import BaseAPIService


class LottoAPIService(BaseAPIService):
    """
    Service for working with the stopcov-api.lotto.ge's API.
    """

    url_template = "https://stopcov-api.lotto.ge/$path"

    def check_winning(self, personal_number: str) -> bool:
        """
        Check Lotto results for given Personal ID.

        :param str personal_number: Personal ID to check results for.
        :return: Winning status.
        """

        return self._get(url={"path": f"Public/Winnings/{personal_number}"})
