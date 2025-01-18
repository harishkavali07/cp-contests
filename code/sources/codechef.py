import os
import asyncio
from modules.common_functions import get_api_response
from datetime import datetime, timedelta
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

CODE_CHEF_RAW_DATA = {}
CODE_CHEF_DATA = {}
CODE_CHEF_LOAD_TIME = None


async def get_default_format(contests: list):
    modified_contests = []
    for contest in contests:
        modified_contest = {
            "platform": "codechef",
            "id": contest.get("contest_code", None),
            "name": contest.get("contest_name", None),
            "url": os.getenv("codechef_contest_url") + contest.get("contest_code", "contests"),
            "start_time": contest.get("contest_start_date_iso", None),
            "duration": int(contest.get("contest_duration", 0))
        }
        modified_contests.append(modified_contest)
    return modified_contests


async def process_raw_data():
    logging.info("Processing raw data for contests...")
    upcoming_contests = CODE_CHEF_RAW_DATA.get("future_contests", [])
    completed_contests = CODE_CHEF_RAW_DATA.get("past_contests", [])
    ongoing_contests = CODE_CHEF_RAW_DATA.get("present_contests", [])

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

async def get_codechef_contests_data():
    logging.info("Inside get_codechef_contests_data function...")
    current_time = datetime.now()
    global CODE_CHEF_RAW_DATA, CODE_CHEF_DATA, CODE_CHEF_LOAD_TIME
    if CODE_CHEF_LOAD_TIME and (current_time - CODE_CHEF_LOAD_TIME) <= timedelta(hours=12):
        logging.info("Using cached CodeChef contest data.")
        return CODE_CHEF_DATA
    else:
        logging.info("Fetching fresh data from CodeChef API...")
        status, reponse_json = await get_api_response(os.getenv("codechef_url"), "GET")
        if not status and reponse_json.get("status") != "success":
            logging.error(f"Failed to fetch data from CodeChef API. Response: {reponse_json}")
            return {}
        CODE_CHEF_RAW_DATA = reponse_json
        CODE_CHEF_DATA = await process_raw_data()
        CODE_CHEF_LOAD_TIME = current_time
        return CODE_CHEF_DATA    
