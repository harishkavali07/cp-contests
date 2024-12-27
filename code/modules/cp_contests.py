import json
from fastapi import Response
from http import HTTPStatus
from sources.codechef import get_codechef_contests_data

async def get_contests_data(req_body: dict):
    try:
        print("inside get_contests_data")
        data = await get_codechef_contests_data()
        print("data fetched from codechef")
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
