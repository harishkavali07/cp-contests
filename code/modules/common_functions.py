import requests
from datetime import datetime,timezone, timedelta
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


async def get_api_response(url: str, request_type: str, headers: dict = None, payload: dict = None) -> tuple:
    """
    Function to get the response from the API
    :param url: The URL of the API
    :param headers: The headers to be sent with the request
    :param payload: The payload to be sent with the request
    :return: The response from the API
    """
    logging.info("Inside get_api_response function")
    try:
        if request_type == "GET":
            logging.info(f"Sending GET request to {url}")
            response = requests.get(url)
        elif request_type == "POST":
            logging.info(f"Sending POST request to {url} with headers: {headers} and payload: {payload}")
            response = requests.post(url, headers = headers, json = payload)
        logging.info("Received response from API")
    except Exception as err_msg:
        raise ValueError("Error while fetching data from api") from err_msg

    if response.status_code == 200:
        logging.info(f"API response successful, status code: {response.status_code}")
        return True, response.json()
    logging.warning(f"API response failed, status code: {response.status_code}")    
    return False, {}

def merge_contests(sources):
    logging.info("Merging contest data from multiple sources.")
    merged_data = {"upcoming": [], "completed": [], "ongoing": []}
    
    for source in sources:
        for category in merged_data.keys():
            merged_data[category].extend(source.get(category, []))
    
    return merged_data

def request_body(data, req_body):
    logging.info(f"Filtering data based on request body: {req_body}")
    positive_infinity = float('inf')
    
    phases = set(req_body.get("phases", ["upcoming", "completed", "ongoing"]))
    min_duration, max_duration = req_body.get("duration", [0, positive_infinity])
    from_date_str = req_body.get("from_date", "2000-01-01T22:00:00+05:30")
    to_date_str = req_body.get("to_date", "2100-01-01T22:00:00+05:30")
    
    from_date = datetime.strptime(from_date_str, '%Y-%m-%dT%H:%M:%S%z')
    to_date = datetime.strptime(to_date_str, '%Y-%m-%dT%H:%M:%S%z')
    modified_data = {"upcoming": [], "completed": [], "ongoing": []}
    
    current_time = datetime.now(timezone.utc)

    for source, values in data.items():
        if source not in phases:
            continue

        for contest in values:
            duration = contest["duration"]
            start_time = datetime.strptime(contest["start_time"], '%Y-%m-%dT%H:%M:%S%z')

            if not (min_duration <= duration <= max_duration and from_date <= start_time <= to_date):
                continue

            end_time = start_time + timedelta(minutes=duration)

            if source == "upcoming":
                if current_time < start_time:
                    modified_data["upcoming"].append(contest)
                else:
                    modified_data["ongoing"].append(contest)
            elif source == "ongoing":
                if start_time <= current_time <= end_time:
                    modified_data["ongoing"].append(contest)
                else:
                    modified_data["completed"].append(contest)
            else: 
                modified_data["completed"].append(contest)
    logging.info("Filtered data")            

    return modified_data               
