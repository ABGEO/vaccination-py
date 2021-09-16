"""
This file is part of the vaccination.py.

(c) 2021 Temuri Takalandze <me@abgeo.dev>

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.
"""

from typing import List, Dict

from PyInquirer import style_from_dict, Token, Separator, prompt


class BaseTask:
    """
    Base CLI Task.
    """

    style = style_from_dict(
        {
            Token.Separator: "#6C6C6C",
            Token.QuestionMark: "#FF9D00 bold",
            Token.Selected: "#5F819D",
            Token.Pointer: "#FF9D00 bold",
            Token.Instruction: "",
            Token.Answer: "#5F819D bold",
            Token.Question: "",
        }
    )
    back_choice = "<< უკან დაბრუნება"
    steps = []

    def _dict_to_choices(
        self, raw: Dict[str, any], navigation: bool = True
    ) -> List[str]:
        choices = list(raw.keys())
        return (
            choices + [Separator("-" * 18), self.back_choice] if navigation else choices
        )

    def _ask_to_retry(self, message: str, default: bool = False) -> bool:
        answers = prompt(
            {
                "type": "confirm",
                "message": message,
                "name": "retry",
                "default": default,
            },
            style=self.style,
        )

        return answers.get("retry")

    def run(self) -> int:
        """
        Run task.

        :return: Exit code.
        """

        i = 0
        while i < len(self.steps):
            input_data = self.steps[i - 1][1] if i != 0 else {}

            try:
                output_data = self.steps[i][0](**input_data)
            except InterruptedError:
                return 0

            if output_data is None:
                i = i - 1
                continue

            self.steps[i][1] = output_data
            i = i + 1

        return 0
