import os
from modules.common_functions import get_api_response

CODE_CHEF_RAW_DATA = {}
CODE_CHEF_DATA = {}


DEFAULT_FORMAT = {
    "platform": "codechef",
    "id": "contest_code",
    "name": "contest_name",
    "start_time": "contest_start_date_iso",
    "duration": "contest_duration"
}


async def get_default_format(contests: list):
    print(f"heelo {contests}")
    modified_contests = []
    for contest in contests:
        modified_contest = {}
        for key, value in DEFAULT_FORMAT.items():
            modified_contest[key] = contest.get(value, None)
            if key == "platform":
                modified_contest[key] = "codechef"
        print(modified_contest)
        modified_contests.append(modified_contest)
    return modified_contests


async def process_raw_data():
    upcoming_contests = CODE_CHEF_RAW_DATA.get("future_contests", [])
    completed_contests = CODE_CHEF_RAW_DATA.get("past_contests", [])
    process_data = {}
    process_data["upcoming"] = await get_default_format(upcoming_contests)
    process_data["completed"] = await get_default_format(completed_contests)
    return process_data

async def get_codechef_contests_data():
    print("inside get_codechef_contests_data")
    status, reponse_json = await get_api_response(os.getenv("codechef_url"), "GET")
    if not status and reponse_json.get("status") != "success":
        return {}
    global CODE_CHEF_RAW_DATA, CODE_CHEF_DATA
    CODE_CHEF_RAW_DATA = reponse_json
    CODE_CHEF_DATA = await process_raw_data()
    return CODE_CHEF_DATA
