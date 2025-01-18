import json
import asyncio
from fastapi import Response
from http import HTTPStatus
from modules.common_functions import merge_contests, request_body
from modules.common_functions import merge_contests, request_body
from sources.codechef import get_codechef_contests_data

async def get_contests_data(req_body: dict):
    try:
        tasks = []
        # print("inside get_contests_data")
        if "codechef" in req_body.get("sources", ["codechef", "codeforces", "leetcode"]):
            tasks.append(get_codechef_contests_data())
        # print("data fetched from codechef")
        if "codeforces" in req_body.get("sources", ["codechef", "codeforces", "leetcode"]):
            tasks.append(get_codeforces_contests_data())
        if "leetcode" in req_body.get("sources", ["codechef", "codeforces", "leetcode"]):
            tasks.append(get_leetcode_contests_data())
        results = await asyncio.gather(*tasks)    
        contest_data_sources = [result for result in results if result]
        test_data = merge_contests(contest_data_sources)
        logging.info("Merged contest data")
        data = request_body(test_data, req_body)
        return Response(
            json.dumps(data),
            status_code = HTTPStatus.OK.value,
            media_type = "application/json"
        )
    except Exception as err_msg:
        logging.error(f"Error occurred while fetching contests data: {err_msg}")
        return Response(
            json.dumps(
                {
                    "message": "Internal Server Error",
                    "error": str(err_msg)
                }
            ),
            status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value,
            media_type = "application/json"
        )
