import requests


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
