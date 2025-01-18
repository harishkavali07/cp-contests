import os
import asyncio
from modules.common_functions import get_api_response
from datetime import datetime, timedelta, timezone
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

LEET_CODE_RAW_DATA = {}
LEET_CODE_DATA = {}
LEET_CODE_LOAD_TIME = None


async def get_default_format(contests: list):
    modified_contests = []
    for contest in contests:
        modified_contest = {}
        modified_contest["platform"] = "leetcode"
        modified_contest["id"] = contest.get("titleSlug", None)
        modified_contest["name"] = contest.get("title", None)
        modified_contest["url"] = os.getenv("leetcode_contest_url") + contest.get("titleSlug", "") + "/"
        start_time = contest.get("startTime", None)
        if start_time:
            dt_utc = datetime.utcfromtimestamp(start_time)
            kolkata_offset = timezone(timedelta(hours=5, minutes=30))
            dt_kolkata = dt_utc.replace(tzinfo=timezone.utc).astimezone(kolkata_offset)
            modified_contest["start_time"] = dt_kolkata.strftime('%Y-%m-%dT%H:%M:%S%z')
        duration = contest.get("duration", 0)
        modified_contest["duration"] = int(duration / 60)

        modified_contests.append(modified_contest)
    return modified_contests

async def process_raw_data():
    logging.info("Processing raw data for LeetCode contests...")
    results = LEET_CODE_RAW_DATA.get("data", {}).get("allContests", [])
    upcoming_contests = []
    completed_contests = []
    ongoing_contests = []
    kolkata_offset = timezone(timedelta(hours=5, minutes=30))
    current_time = datetime.now(kolkata_offset)

    for contest in results:
        start_time = contest.get("startTime", None)
        if start_time:
            dt_start = datetime.utcfromtimestamp(start_time)
            duration_seconds = contest.get("duration", 0)
            duration = timedelta(seconds=duration_seconds)
            dt_end = dt_start + duration
            dt_start_aware = dt_start.replace(tzinfo=timezone.utc).astimezone(kolkata_offset)
            dt_end_aware = dt_end.replace(tzinfo=timezone.utc).astimezone(kolkata_offset)

            if current_time < dt_start_aware:
                upcoming_contests.append(contest)
            elif current_time > dt_end_aware:
                completed_contests.append(contest)
            else:
                ongoing_contests.append(contest)

    process_data = await asyncio.gather(
        get_default_format(upcoming_contests),
        get_default_format(completed_contests),
        get_default_format(ongoing_contests)
    )

    return {
        "upcoming": process_data[0],
        "completed": process_data[1],
        "ongoing": process_data[2]
    }    

async def get_leetcode_contests_data():
    logging.info("Inside get_leetcode_contests_data function...")
    current_time = datetime.now()
    global LEET_CODE_RAW_DATA, LEET_CODE_DATA, LEET_CODE_LOAD_TIME
    if LEET_CODE_LOAD_TIME and (current_time - LEET_CODE_LOAD_TIME) <= timedelta(hours=12):
        logging.info("Using cached LeetCode contest data.")
        return LEET_CODE_DATA
    else:
        logging.info("Fetching fresh data from LeetCode API...")
        status, reponse_json = await get_api_response(os.getenv("leetcode_url"), "GET")
        if not status:
            logging.error("Failed to fetch data from LeetCode API. Response: {response_json}")
            return {}
        LEET_CODE_RAW_DATA = reponse_json
        LEET_CODE_DATA = await process_raw_data()
        LEET_CODE_LOAD_TIME = current_time
        return LEET_CODE_DATA