import json
from fastapi import Response
from http import HTTPStatus
from modules.common_functions import merge_contests, request_body
from sources.codechef import get_codechef_contests_data
from sources.codeforce import get_codeforces_contests_data
from sources.leetcode import get_leetcode_contests_data

async def get_contests_data(req_body: dict):
    try:
        # print("inside get_contests_data")
        codechef_data = await get_codechef_contests_data()
        # print("data fetched from codechef")
        codeforce_data = await get_codeforces_contests_data()
        leetcode_data = await get_leetcode_contests_data()
        contest_data_sources = [codechef_data, codeforce_data, leetcode_data]
        test_data = merge_contests(contest_data_sources)
        data = request_body(test_data, req_body)
        return Response(
            json.dumps(data),
            status_code = HTTPStatus.OK.value,
            media_type = "application/json"
        )
    except Exception as err_msg:
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
