import requests
import math


async def get_api_response(url: str, request_type: str, headers: dict = None, payload: dict = None) -> tuple:
    """
    Function to get the response from the API
    :param url: The URL of the API
    :param headers: The headers to be sent with the request
    :param payload: The payload to be sent with the request
    :return: The response from the API
    """
    print("inside get_api_response")
    try:
        if request_type == "GET":
            response = requests.get(url)
        elif request_type == "POST":
            response = requests.post(url, headers = headers, json = payload)
        print("received response")
    except Exception as err_msg:
        raise ValueError("Error while fetching data from api") from err_msg

    if response.status_code == 200:
        return True, response.json()
    return False, {}

def merge_contests(sources):
    merged_data = {"upcoming": [], "completed": [], "ongoing": []}
    
    for source in sources:
        for category in merged_data.keys():
            merged_data[category].extend(source.get(category, []))
    
    return merged_data

def request_body(data, req_body):
    positive_infinity = math.inf
    modified_data = {"upcoming": [], "completed": [], "ongoing": []}
    for source, values in data.items():
        if source in req_body.get("phases", ["upcoming", "completed", "ongoing"]):
            for contest in values:
                if (contest["platform"] in req_body.get("sources", ["codechef", "codeforces", "leetcode"]) and 
                req_body.get("duration", [0, positive_infinity])[0] <= contest["duration"] and 
                req_body.get("duration", [0, positive_infinity])[1] >= contest["duration"] and 
                req_body.get("from_date", "2000-01-01T22:00:00+05:30") <= contest["start_time"] and 
                req_body.get("to_date", "2100-01-01T22:00:00+05:30") >= contest["start_time"]):
                    modified_data[source].append(contest)

    return modified_data                
