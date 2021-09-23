"""
This file is part of the vaccination.py.

(c) 2021 Temuri Takalandze <me@abgeo.dev>

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.
"""

from typing import Dict, Union

import regex
from PyInquirer import prompt
from prettytable import PrettyTable, NONE
from prompt_toolkit.validation import Validator, ValidationError

from vaccination.core.task.base import BaseTask
from vaccination.service.api.booking import BookingAPIService


class _NumberValidator(Validator):
    def __init__(self):
        self.pattern = r""
        self.message = ""

    def validate(self, document):
        if not regex.match(self.pattern, document.text):
            raise ValidationError(
                message=self.message, cursor_position=len(document.text)
            )


class _PersonalNumberValidator(_NumberValidator):
    def __init__(self):
        super().__init__()
        self.pattern = r"^\d{11}$"
        self.message = "პირადი ნომერი არასწორია"


class _BookingNumberValidator(_NumberValidator):
    def __init__(self):
        super().__init__()
        self.pattern = r"^\d{6}$"
        self.message = "ჯავშნის ნომერი არასწორია"


class VaccinationCheckTask(BaseTask):
    """
    Vaccination Check CLI Task.
    """

    def __init__(self):
        self.api_service = BookingAPIService()
        self.steps = [
            [self._ask_personal_number, {}],
            [self._ask_booking_number, {}],
            [self._print_result, {}],
        ]

    def _ask_number(self, message: str, validator) -> str:
        answers = prompt(
            {
                "type": "input",
                "name": "number",
                "message": message,
                "validate": validator,
            },
            style=self.style,
        )

        number = answers.get("number")
        if not number:
            raise InterruptedError

        return number

    def _ask_personal_number(self) -> Dict[str, str]:
        return {
            "personal_number": self._ask_number(
                "აკრიფეთ პირადი ნომერი", _PersonalNumberValidator
            )
        }

    def _ask_booking_number(self, personal_number: str) -> Dict[str, str]:
        return {
            "personal_number": personal_number,
            "booking_number": self._ask_number(
                "აკრიფეთ ჯავშნის ნომერი", _BookingNumberValidator
            ),
        }

    def _print_result(
        self, personal_number: str = None, booking_number: str = None
    ) -> Union[Dict, None]:
        result = self.api_service.search_booking(personal_number, booking_number)

        if "value" in result and result["value"]:
            result = result["value"]
            table = PrettyTable(
                ["", " "],
                header=False,
                hrules=NONE,
                vrules=NONE,
                align="l",
            )

            table.add_rows(
                [
                    ["პიროვნება", f'- \t {result["firstName"]} {result["lastName"]}'],
                    ["დაბადების წელი", f'- \t {result["birthYear"]}'],
                    ["პირადი ნომერი", f'- \t {result["personalID"]}'],
                    ["ტელეფონის ნომერი", f'- \t {result["phone"]}'],
                    ["", ""],
                    ["სერვისი", f'- \t {result["testName"]}'],
                    ["დაწესებულება", f'- \t {result["branchName"]}'],
                    ["ოთახი", f'- \t {result["roomNumber"]}'],
                    ["თარიღი/დრო", f'- \t {result["scheduleDateName"]}'],
                ]
            )

            print(f"\n{table}\n")
        else:
            print(f"\033[91m{result['message']}\033[0m")

        return {}
