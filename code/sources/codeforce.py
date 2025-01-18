import os
import asyncio
from modules.common_functions import get_api_response
from datetime import datetime, timedelta, timezone
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

CODE_FORCES_RAW_DATA = {}
CODE_FORCES_DATA = {}
CODE_FORCES_LOAD_TIME = None


async def get_default_format(contests: list, result: bool):
    modified_contests = []
    for contest in contests:
        modified_contest = {}

        modified_contest["platform"] = "codeforces"
        modified_contest["id"] = str(contest.get("id", None))
        modified_contest["name"] = contest.get("name", None)
        modified_contest["url"] = os.getenv("codeforces_contest_url") + ("/Registration/" if result else "/") + str(contest.get("id", None))
        start_time = contest.get("startTimeSeconds", None)
        if start_time:
            dt_utc = datetime.utcfromtimestamp(start_time)
            kolkata_offset = timezone(timedelta(hours=5, minutes=30))
            dt_kolkata = dt_utc.replace(tzinfo=timezone.utc).astimezone(kolkata_offset)
            modified_contest["start_time"] = dt_kolkata.strftime('%Y-%m-%dT%H:%M:%S%z')
        duration = contest.get("durationSeconds", 0)
        modified_contest["duration"] = int(duration / 60)

        modified_contests.append(modified_contest)
    return modified_contests

async def process_raw_data():
    logging.info("Processing raw data for Codeforces contests...")
    results = CODE_FORCES_RAW_DATA.get("result", [])
    upcoming_contests = []
    completed_contests = []
    ongoing_contests = []
    for contest in results:
        if contest.get("phase","") == "BEFORE":
            upcoming_contests.append(contest)
        elif contest.get("phase","") == "FINISHED":
            completed_contests.append(contest)  
        elif contest.get("phase","") == "CODING":
            ongoing_contests.append(contest)      


    process_data = await asyncio.gather(
        get_default_format(upcoming_contests, True),
        get_default_format(completed_contests, False),
        get_default_format(ongoing_contests, True)
    )

    return {
        "upcoming": process_data[0],
        "completed": process_data[1],
        "ongoing": process_data[2]
    }                 

async def get_codeforces_contests_data():
    logging.info("Inside get_codeforces_contests_data function...")
    current_time = datetime.now()
    global CODE_FORCES_RAW_DATA, CODE_FORCES_DATA, CODE_FORCES_LOAD_TIME
    if CODE_FORCES_LOAD_TIME and (current_time - CODE_FORCES_LOAD_TIME) <= timedelta(hours=12):
        logging.info("Using cached Codeforces contest data.")
        return CODE_FORCES_DATA
    else:
        logging.info("Fetching fresh data from Codeforces API...")
        status, reponse_json = await get_api_response(os.getenv("codeforces_url"), "GET")
        if not status and reponse_json.get("status") != "OK":
            logging.error(f"Failed to fetch data from Codeforces API. Response: {response_json}")
            return {}
        CODE_FORCES_RAW_DATA = reponse_json
        CODE_FORCES_DATA = await process_raw_data()
        CODE_FORCES_LOAD_TIME = current_time
        return CODE_FORCES_DATA