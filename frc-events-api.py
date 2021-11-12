import requests
import json
import sys


def collect_all_pages(sesh, url, opt_args="?"):
    first = sesh.get(url + opt_args).json()
    all = [first]
    for i in range(2, first["pageTotal"] + 1):
        current = sesh.get(url + opt_args + "&page=" + str(i)).json()
        all.append(current)
    return all


def collect_and_merge(sesh, url, opt_args="?"):
    all_pages = collect_and_merge(sesh, url, opt_args)
    result = {}

    for page in all_pages:
        for k in page.keys():
            if "total" in k.lower():
                result[k] = page[k]
            elif "page" in k.lower():
                continue
            else:
                if k not in result:
                    result[k] = []
                result[k].extend(page[k])

    return result


def gather_data(user, password):
    sesh = requests.Session()
    sesh.auth = (user, password)

    data = {}

    data["events"] = collect_and_merge(
        sesh, "https://frc-api.firstinspires.org/v3.0/2022/events"
    )

    data["districts"] = collect_and_merge(
        sesh, "https://frc-api.firstinspires.org/v3.0/2022/districts"
    )

    data["teams"] = collect_and_merge(
        sesh, "https://frc-api.firstinspires.org/v3.0/2022/teams"
    )

    for event in data["events"]["Events"]:
        data["events"][event["code"]] = collect_and_merge(
            sesh,
            "https://frc-api.firstinspires.org/v3.0/2022/teams",
            "?eventCode" + event["code"],
        )

    for district in data["districts"]["districts"]:
        data["districts"][district["code"]] = collect_and_merge(
            sesh,
            "https://frc-api.firstinspires.org/v3.0/2022/teams",
            "?districtCode" + district["code"],
        )


data = gather_data("", "")

if len(sys.argv) == 1:
    print(json.dumps(data))
else:
    with open(sys.argv[1], "w") as f:
        json.dump(data, f)
