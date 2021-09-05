"""
Main application module.

This file is part of the vaccination.py.

(c) 2021 Temuri Takalandze <me@abgeo.dev>

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.
"""

import copy
import datetime
import os
from datetime import date
from typing import List, Dict, Union

from PyInquirer import prompt, style_from_dict, Token, Separator
from prettytable import PrettyTable, ALL

from vaccination.service.api import APIService


class App:
    """
    Application class.
    """

    def __init__(self):
        self.style = style_from_dict(
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
        self.back_choice = "<< უკან დაბრუნება"
        self.api_service = APIService()
        self.steps = [
            [self._select_service, {}],
            [self._select_region, {}],
            [self._select_municipality, {}],
            [self._select_branch, {}],
            [self._select_room, {}],
            [self._print_result_and_ask_to_retry, {}],
        ]

    def _dict_to_choices(
        self, raw: Dict[str, any], navigation: bool = True
    ) -> List[str]:
        choices = list(raw.keys())
        return (
            choices + [Separator("-" * 18), self.back_choice] if navigation else choices
        )

    def _select_service(self) -> Dict[str, str]:
        quantities = self.api_service.get_available_quantities()
        services = {}
        for app in ["abc", "def"]:
            for service in self.api_service.get_service_types(app):
                key = service["name"]
                key = key[key.find("(") + 1 : key.find(")")]
                key += f" ({quantities[key.lower()]:,})"
                services[key] = service["id"]

        answers = prompt(
            {
                "type": "list",
                "name": "service",
                "message": "აირჩიეთ ვაქცინა",
                "choices": self._dict_to_choices(services, False),
            },
            style=self.style,
        )

        service = answers.get("service")

        regions = {}
        for region in self.api_service.get_regions(services[service]):
            regions[region["geoName"]] = region["id"]

        return {"service": services[service], "regions": regions}

    def _select_region(
        self, service: str, regions: Dict[str, str]
    ) -> Union[Dict[str, Union[str, Dict[str, str]]], None]:
        answers = prompt(
            {
                "type": "list",
                "name": "region",
                "message": "სერვისის ჩატარების რეგიონი",
                "choices": self._dict_to_choices(regions),
            },
            style=self.style,
        )

        region = answers.get("region")
        if region == self.back_choice:
            return None

        municipalities = {}
        for municipality in self.api_service.get_municipalities(
            regions[region], service
        ):
            municipalities[municipality["geoName"]] = municipality["id"]

        return {
            "service": service,
            "region": regions[region],
            "municipalities": municipalities,
        }

    def _select_municipality(
        self, service: str, region: str, municipalities: Dict[str, str]
    ) -> Union[Dict[str, Union[str, Dict[str, str]]], None]:
        answers = prompt(
            {
                "type": "list",
                "name": "municipality",
                "message": "სერვისის ჩატარების რაიონი",
                "choices": self._dict_to_choices(municipalities),
            },
            style=self.style,
        )

        municipality = answers.get("municipality")
        if municipality == self.back_choice:
            return None

        branches = {}
        for branch in self.api_service.get_municipality_branches(
            service, municipalities[municipality]
        ):
            branches[branch["name"]] = branch["id"]

        return {
            "region": region,
            "service": service,
            "branches": branches,
        }

    def _select_branch(
        self, region: str, service: str, branches: Dict[str, str]
    ) -> Union[Dict[str, Dict[str, List]], None]:
        answers = prompt(
            {
                "type": "list",
                "name": "branch",
                "message": "სერვისის მიმწოდებელი დაწესებულება",
                "choices": self._dict_to_choices(branches),
            },
            style=self.style,
        )

        branch = answers.get("branch")
        if branch == self.back_choice:
            return None

        start_date = date.today()
        end_date = start_date + datetime.timedelta(days=7)

        rooms = {}
        for room in self.api_service.get_slots(
            branches[branch], region, service, start_date, end_date
        ):
            rooms[room["name"]] = room["schedules"]

        return {"rooms": rooms}

    def _select_room(self, rooms: Dict[str, List]) -> Union[Dict[str, List], None]:
        answers = prompt(
            {
                "type": "list",
                "name": "room",
                "message": "აირჩიეთ კაბინეტი",
                "choices": self._dict_to_choices(rooms),
            },
            style=self.style,
        )

        room = answers.get("room")
        if room == self.back_choice:
            return None

        dates = copy.deepcopy(rooms[room][0]["dates"])
        for i, item in enumerate(dates):
            dates[i]["slots"] = list(map(lambda x: x["value"], item["slots"]))

        return {"dates": dates}

    def _print_result_and_ask_to_retry(self, dates: List) -> bool:
        _, columns = os.popen("stty size", "r").read().split()
        header = ["თარიღი", "დღე", "თავისუფალი დროები"]
        table = PrettyTable(
            header,
            hrules=ALL,
            align="l",
            min_width=60,
            max_table_width=int(columns) - 10,
        )
        table.add_rows(
            map(lambda x: [x["dateName"], x["weekName"], ", ".join(x["slots"])], dates)
        )

        print(f"\n{table}\n")

        answers = prompt(
            {
                "type": "confirm",
                "message": "გსურთ სხვა კაბინეტის ნახვა?",
                "name": "repeat",
                "default": False,
            },
            style=self.style,
        )

        return not answers.get("repeat")

    def run(self) -> int:
        """
        Run application.

        :return: Exit code.
        """

        i = 0
        while i < len(self.steps):
            input_data = self.steps[i - 1][1] if i != 0 else {}
            output_data = self.steps[i][0](**input_data)

            if not output_data:
                i = i - 1
                continue

            self.steps[i][1] = output_data
            i = i + 1

        return 0
