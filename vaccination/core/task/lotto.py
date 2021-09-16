"""
This file is part of the vaccination.py.

(c) 2021 Temuri Takalandze <me@abgeo.dev>

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.
"""

from typing import Dict, Union

import regex
from PyInquirer import prompt
from prompt_toolkit.validation import Validator, ValidationError

from vaccination.core.task.base import BaseTask
from vaccination.service.api.lotto import LottoAPIService


class _PersonalNumberValidator(Validator):
    def validate(self, document):
        if not regex.match(r"^\d{11}$", document.text):
            raise ValidationError(
                message="პირადი ნომერი არასწორია", cursor_position=len(document.text)
            )


class LottoTask(BaseTask):
    """
    Lotto CLI Task.
    """

    def __init__(self):
        self.api_service = LottoAPIService()
        self.steps = [
            [self._ask_personal_number, {}],
            [self._print_result, {}],
        ]

    def _ask_personal_number(self) -> Dict[str, str]:
        answers = prompt(
            {
                "type": "input",
                "name": "personal_number",
                "message": "აკრიფეთ პირადი ნომერი",
                "validate": _PersonalNumberValidator,
            },
            style=self.style,
        )

        personal_number = answers.get("personal_number")
        if not personal_number:
            raise InterruptedError

        return {"personal_number": personal_number}

    def _print_result(self, personal_number) -> Union[Dict, None]:
        winning = self.api_service.check_winning(personal_number)

        if winning:
            print("\033[92mგილოცავთ, თქვენ გაიმარჯვეთ!\033[0m")
        else:
            print("\033[91mსამწუხაროდ, თქვენ ვერ გაიმარჯვეთ!\033[0m")

        return None if self._ask_to_retry("გსურთ სხვა მონაცემის შემოწმება?") else {}
