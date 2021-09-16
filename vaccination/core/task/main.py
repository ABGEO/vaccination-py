"""
This file is part of the vaccination.py.

(c) 2021 Temuri Takalandze <me@abgeo.dev>

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.
"""

from typing import Dict

from PyInquirer import prompt

from vaccination.core.task.base import BaseTask
from vaccination.core.task.lotto import LottoTask
from vaccination.core.task.vaccination import VaccinationTask


class MainTask(BaseTask):
    """
    Main CLI Task.
    """

    def __init__(self):
        self.steps = [
            [self._select_task, {}],
            [self._run_task, {}],
        ]

    def _select_task(self) -> Dict[str, callable]:
        tasks = {
            "ვაქცინაცია": VaccinationTask,
            "ლოტო": LottoTask,
        }
        answers = prompt(
            {
                "type": "list",
                "name": "task",
                "message": "აირჩიეთ სერვისი",
                "choices": self._dict_to_choices(tasks, False),
            },
            style=self.style,
        )

        task = answers.get("task")
        if not task:
            raise InterruptedError

        return {"task": tasks[task]}

    @staticmethod
    def _run_task(task: callable) -> Dict[str, str]:
        return task().run()
