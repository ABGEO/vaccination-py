"""
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

import requests
from PyInquirer import prompt, style_from_dict, Token, Separator
from prettytable import PrettyTable, ALL

from vaccination import __version__, __copyright__, __email__

BASE_URL = "https://booking.moh.gov.ge/abc/API/api"
DEFAULT_STYLE = style_from_dict(
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
BACK_CHOICE = "<< უკან დაბრუნება"
SECURITY_CODES = []


def __step_1() -> Dict[str, str]:
    services = {
        "Pfizer": "efc7f5d4-f4b1-4095-ad53-717389ea8258",
        "Sinovac": "f0a99555-7873-4b61-9dbc-545622278233",
        "Sinopharm": "d1eef49b-00b9-4760-9525-6100c168e642",
        "AstraZeneca": "4bb6c283-3afb-436c-9974-6730cd2a18bd",
    }
    answers = prompt(
        {
            "type": "list",
            "name": "service",
            "message": "აირჩიეთ ვაქცინა",
            "choices": __dict_to_choices(services, False),
        },
        style=DEFAULT_STYLE,
    )

    service = answers.get("service")

    regions_response = requests.get(
        f"{BASE_URL}/CommonData/GetRegions",
        {"serviceId": services[service], "onlyFree": True},
        headers={"SecurityNumber": __get_security_number()},
    )

    regions = {}
    for region in regions_response.json():
        regions[region["geoName"]] = region["id"]

    return {"service": services[service], "regions": regions}


def __step_2(
    service: str, regions: Dict[str, str]
) -> Union[Dict[str, Union[str, Dict[str, str]]], None]:
    answers = prompt(
        {
            "type": "list",
            "name": "region",
            "message": "სერვისის ჩატარების რეგიონი",
            "choices": __dict_to_choices(regions),
        },
        style=DEFAULT_STYLE,
    )

    region = answers.get("region")
    if region == BACK_CHOICE:
        return None

    municipalities_response = requests.get(
        f"{BASE_URL}/CommonData/GetMunicipalities/{regions[region]}",
        {"serviceId": service, "onlyFree": True},
        headers={"SecurityNumber": __get_security_number()},
    )

    municipalities = {}
    for municipality in municipalities_response.json():
        municipalities[municipality["geoName"]] = municipality["id"]

    return {
        "service": service,
        "region": regions[region],
        "municipalities": municipalities,
    }


def __step_3(
    service: str, region: str, municipalities: Dict[str, str]
) -> Union[Dict[str, Union[str, Dict[str, str]]], None]:
    answers = prompt(
        {
            "type": "list",
            "name": "municipality",
            "message": "სერვისის ჩატარების რაიონი",
            "choices": __dict_to_choices(municipalities),
        },
        style=DEFAULT_STYLE,
    )

    municipality = answers.get("municipality")
    if municipality == BACK_CHOICE:
        return None

    branches_response = requests.get(
        f"{BASE_URL}/CommonData/GetMunicipalityBranches/{service}/{municipalities[municipality]}",
        {"onlyFree": True},
        headers={"SecurityNumber": __get_security_number()},
    )

    branches = {}
    for branch in branches_response.json():
        branches[branch["name"]] = branch["id"]

    return {
        "region": region,
        "service": service,
        "branches": branches,
    }


def __step_4(
    region: str, service: str, branches: Dict[str, str]
) -> Union[Dict[str, Dict[str, List]], None]:
    answers = prompt(
        {
            "type": "list",
            "name": "branch",
            "message": "სერვისის მიმწოდებელი დაწესებულება",
            "choices": __dict_to_choices(branches),
        },
        style=DEFAULT_STYLE,
    )

    branch = answers.get("branch")
    if branch == BACK_CHOICE:
        return None

    start_date = date.today()
    end_date = start_date + datetime.timedelta(days=7)
    slots_response = requests.post(
        f"{BASE_URL}/PublicBooking/GetSlots/",
        json={
            "branchID": branches[branch],
            "startDate": start_date.strftime("%Y-%m-%d"),
            "endDate": end_date.strftime("%Y-%m-%d"),
            "regionID": region,
            "serviceID": service,
        },
        headers={"SecurityNumber": __get_security_number()},
    )

    rooms = {}
    for room in slots_response.json():
        rooms[room["name"]] = room["schedules"]

    return {"rooms": rooms}


def __step_5(rooms: Dict[str, List]) -> Union[Dict[str, List], None]:
    answers = prompt(
        {
            "type": "list",
            "name": "room",
            "message": "აირჩიეთ კაბინეტი",
            "choices": __dict_to_choices(rooms),
        },
        style=DEFAULT_STYLE,
    )

    room = answers.get("room")
    if room == BACK_CHOICE:
        return None

    dates = copy.deepcopy(rooms[room][0]["dates"])
    for i, item in enumerate(dates):
        dates[i]["slots"] = list(map(lambda x: x["value"], item["slots"]))

    return {"dates": dates}


def __step_6(dates: List) -> bool:
    _, columns = os.popen("stty size", "r").read().split()
    header = ["თარიღი", "დღე", "თავისუფალი დროები"]
    table = PrettyTable(
        header, hrules=ALL, align="l", min_width=60, max_table_width=int(columns) - 10
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
        style=DEFAULT_STYLE,
    )

    return not answers.get("repeat")


def __print_banner() -> None:
    print("__     __             _             _   _             ")
    print(r"\ \   / /_ _  ___ ___(_)_ __   __ _| |_(_) ___  _ __  ")
    print(r" \ \ / / _` |/ __/ __| | '_ \ / _` | __| |/ _ \| '_ \ ")
    print(r"  \ V / (_| | (_| (__| | | | | (_| | |_| | (_) | | | |")
    print(r"   \_/ \__,_|\___\___|_|_| |_|\__,_|\__|_|\___/|_| |_|")
    print(f"\n     v{__version__} {__copyright__} ({__email__})\n")


def __dict_to_choices(raw: Dict[str, any], navigation: bool = True) -> List[str]:
    choices = list(raw.keys())
    return choices + [Separator("-" * 18), BACK_CHOICE] if navigation else choices


def __get_security_number() -> str:
    # pylint: disable=W0603
    global SECURITY_CODES

    if not SECURITY_CODES:
        SECURITY_CODES = requests.get(
            "https://vaccination.abgeo.dev/api/numbers?count=100"
        ).json()

    return SECURITY_CODES.pop(0)


def __process() -> int:
    steps = [
        [__step_1, {}],
        [__step_2, {}],
        [__step_3, {}],
        [__step_4, {}],
        [__step_5, {}],
        [__step_6, {}],
    ]

    i = 0
    while i < len(steps):
        input_data = steps[i - 1][1] if i != 0 else {}
        output_data = steps[i][0](**input_data)

        if not output_data:
            i = i - 1
            continue

        steps[i][1] = output_data
        i = i + 1

    return 0


def main() -> int:
    """
    Main function.
    :return: Exit code.
    """

    __print_banner()
    return __process()


if __name__ == "__main__":
    import sys

    sys.exit(main())
