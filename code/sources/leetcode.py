import os
from modules.common_functions import get_api_response
from datetime import datetime, timedelta
import pytz

LEET_CODE_RAW_DATA = {}
LEET_CODE_DATA = {}

DEFAULT_FORMAT = {
    "platform": "leetcode",
    "id": "titleSlug",
    "name": "title",
    "url": "titleSlug",
    "start_time": "startTime",
    "duration": "duration"
}

async def get_default_format(contests: list):
    # print(f"contests: {contests}")
    modified_contests = []
    for contest in contests:
        modified_contest = {}
        for key, value in DEFAULT_FORMAT.items():
            modified_contest[key] = contest.get(value, None)
            if key == "platform":
                modified_contest[key] = "leetcode"
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
                modified_contest[key] = os.getenv("leetcode_contest_url") + (contest.get(value, None)) + "/"         
        # print(modified_contest)
        modified_contests.append(modified_contest)
    return modified_contests

async def process_raw_data():
    results = LEET_CODE_RAW_DATA.get("data", {}).get("allContests", [])
    # print(f"result: {results}")
    upcoming_contests = []
    completed_contests = []
    ongoing_contests = []
    for contest in results:
        start_time = contest.get("startTime", None)
        dt_start = datetime.utcfromtimestamp(start_time)
        duration_seconds = contest.get("duration", 0)
        duration = timedelta(seconds=duration_seconds)
        dt_end = dt_start + duration
        timezone = pytz.timezone('Asia/Kolkata')
        dt_start_aware = timezone.localize(dt_start)
        dt_end_aware = timezone.localize(dt_end)
        current_time = datetime.now(timezone)
        if current_time < dt_start_aware:
            upcoming_contests.append(contest)
        elif current_time > dt_end_aware:
            completed_contests.append(contest)
        else:
            ongoing_contests.append(contest)

    process_data = {}
    process_data["upcoming"] = await get_default_format(upcoming_contests)
    process_data["completed"] = await get_default_format(completed_contests)
    process_data["ongoing"] = await get_default_format(ongoing_contests)
    return process_data      

async def get_leetcode_contests_data():
    print("inside get_leetcode_contests_data")
    status, reponse_json = await get_api_response(os.getenv("leetcode_url"), "GET")
    if not status :
        return {}
    global LEET_CODE_RAW_DATA, LEET_CODE_DATA
    LEET_CODE_RAW_DATA = reponse_json
    LEET_CODE_DATA = await process_raw_data()
    return LEET_CODE_DATA