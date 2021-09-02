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
from typing import List, Dict

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


def __step_1():
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

    return {"service": services[service]}


def __step_2(service):
    regions = {
        "აჭარა": "31520d88-870e-485e-a833-5ca9e20e84fa",
        "გურია": "27428de4-bb76-47f2-bfac-26700623a05d",
        "თბილისი": "5d129a50-30e9-4b10-8d4d-3febb32ec32c",
        "იმერეთი": "09c1e04c-c664-4252-a30a-2a71ba72c2e2",
        "კახეთი": "d1e285b5-5b60-42c6-9bc2-ac7646a9c96a",
        "მცხეთა-მთიანეთი": "b5a01ce4-bbfc-4b7e-a519-ba11dd7146bb",
        "რაჭა-ლეჩხუმი და ქვემო სვანეთი": "6d893d1f-3851-4d80-b7fc-020179c8a4c0",
        "სამეგრელო და ზემო სვანეთი": "a2a56af7-2f62-4ffa-aa56-038328bd5b32",
        "სამცხე-ჯავახეთი": "acecd83d-fb22-44f9-b69d-3333aceb79a6",
        "ქვემო ქართლი": "f2cf4fc9-7037-4c56-8db7-bd9a6ddadd8a",
        "შიდა ქართლი": "ae3b6e33-6cd7-4b24-bf74-865cfabc2839",
    }
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
    )

    municipalities = {}
    for municipality in municipalities_response.json():
        municipalities[municipality["geoName"]] = municipality["id"]

    return {
        "service": service,
        "region": regions[region],
        "municipalities": municipalities,
    }


def __step_3(service, region, municipalities):
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
    )

    branches = {}
    for branch in branches_response.json():
        branches[branch["name"]] = branch["id"]

    return {
        "region": region,
        "service": service,
        "branches": branches,
    }


def __step_4(region, service, branches):
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
    )

    rooms = {}
    for room in slots_response.json():
        rooms[room["name"]] = room["schedules"]

    return {"rooms": rooms}


def __step_5(rooms):
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


def __step_6(dates):
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


def __print_banner():
    print("__     __             _             _   _             ")
    print(r"\ \   / /_ _  ___ ___(_)_ __   __ _| |_(_) ___  _ __  ")
    print(r" \ \ / / _` |/ __/ __| | '_ \ / _` | __| |/ _ \| '_ \ ")
    print(r"  \ V / (_| | (_| (__| | | | | (_| | |_| | (_) | | | |")
    print(r"   \_/ \__,_|\___\___|_|_| |_|\__,_|\__|_|\___/|_| |_|")
    print(f"\n     v{__version__} {__copyright__} ({__email__})\n")


def __dict_to_choices(raw: Dict[str, any], navigation: bool = True) -> List[str]:
    choices = list(raw.keys())
    return choices + [Separator("-" * 18), BACK_CHOICE] if navigation else choices


def __process():
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
