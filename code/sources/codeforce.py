import os
from modules.common_functions import get_api_response
from datetime import datetime, timedelta
import pytz

CODE_FORCES_RAW_DATA = {}
CODE_FORCES_DATA = {}

DEFAULT_FORMAT = {
    "platform": "codeforces",
    "id": "id",
    "name": "name",
    "url": "id",
    "start_time": "startTimeSeconds",
    "duration": "durationSeconds"
}

async def get_default_format(contests: list, result: bool):
    # print(f"contests: {contests}")
    modified_contests = []
    for contest in contests:
        modified_contest = {}
        for key, value in DEFAULT_FORMAT.items():
            modified_contest[key] = contest.get(value, None)
            if key == "platform":
                modified_contest[key] = "codeforces"
            elif key == "id":
                modified_contest[key] = str(contest.get(value, None))    
            elif key == "duration":
                duration_time_minutes = modified_contest[key]/60
                modified_contest[key] = int(duration_time_minutes)
            elif key == "start_time":
                start_time_seconds = modified_contest[key]
                dt_utc = datetime.utcfromtimestamp(start_time_seconds)
                timezone = pytz.timezone('Asia/Kolkata')
                start_time = pytz.utc.localize(dt_utc).astimezone(timezone)
                modified_contest[key] = start_time.strftime('%Y-%m-%dT%H:%M:%S%z')
            elif key == "url":
                if result:
                    modified_contest[key] = os.getenv("codeforces_contest_url") + "Registration/" + str(contest.get(value, None))
                else:
                    modified_contest[key] = os.getenv("codeforces_contest_url") + "/" + str(contest.get(value, None))          
        # print(modified_contest)
        modified_contests.append(modified_contest)
    return modified_contests

async def process_raw_data():
    results = CODE_FORCES_RAW_DATA.get("result", [])
    # print(f"result: {results}")
    upcoming_contests = []
    completed_contests = []
    ongoing_contests = []
    for contest in results:
        # print(f"contest: {contest}")
        if contest.get("phase","") == "BEFORE":
            upcoming_contests.append(contest)
        elif contest.get("phase","") == "FINISHED":
            completed_contests.append(contest)  
        elif contest.get("phase","") == "CODING":
            ongoing_contests.append(contest)      


    process_data = {}
    process_data["upcoming"] = await get_default_format(upcoming_contests, True)
    process_data["completed"] = await get_default_format(completed_contests, False)
    process_data["ongoing"] = await get_default_format(ongoing_contests, True)
    return process_data                   

async def get_codeforces_contests_data():
    print("inside get_codeforces_contests_data")
    status, reponse_json = await get_api_response(os.getenv("codeforces_url"), "GET")
    if not status and reponse_json.get("status") != "OK":
        return {}
    global CODE_FORCES_RAW_DATA, CODE_FORCES_DATA
    CODE_FORCES_RAW_DATA = reponse_json
    CODE_FORCES_DATA = await process_raw_data()
    return CODE_FORCES_DATA