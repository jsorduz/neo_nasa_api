import json
import os
from datetime import datetime, timedelta

import requests

from logger import logger
from utils import create_file_if_not_exists

API_KEY = os.getenv("API_KEY", "DEMO_KEY")
STORE_FILE = bool(os.getenv("STORE_FILE", False))
BASE_URL = "https://api.nasa.gov/neo/rest/v1"
DATA_FOLDER = "data"

if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)


def get_nasa_data(url):
    response = requests.get(url)
    # logger.debug(f"{response.status_code} - {response.content}")
    logger.warning(f"Rate limit remaining: {response.headers['X-RateLimit-Remaining']}")
    return json.loads(response.content)


def get_data_from_file(file_path):
    if STORE_FILE is not True:
        return
    if os.path.exists(file_path):
        logger.debug(f"Loading from file '{file_path}'")
        with open(file_path, "r") as file:
            data = json.load(file)
            return data


def store_data_in_file(file_path, data):
    if STORE_FILE is not True:
        return

    create_file_if_not_exists(file_path)
    with open(file_path, "w") as outfile:
        json_object = json.dumps(data, indent=4)
        outfile.write(json_object)


def get_neo(start_date: datetime = None, end_date: datetime = None):
    if not end_date:
        end_date = datetime.today()
    if not start_date:
        start_date = end_date - timedelta(days=7)

    DATA_OUT = os.path.join(
        DATA_FOLDER,
        f"neo_list_{start_date.strftime('%Y_%m_%d')}_{end_date.strftime('%Y_%m_%d')}.json",
    )
    file_data = get_data_from_file(DATA_OUT)
    if file_data is not None:
        return file_data

    url = f"{BASE_URL}/feed?api_key={API_KEY}"
    url += f"&end_date={end_date.strftime('%Y-%m-%d')}"
    url += f"&start_date={start_date.strftime('%Y-%m-%d')}"
    data = get_nasa_data(url)

    store_data_in_file(DATA_OUT, data)

    return data


def get_neo_by_id(neo_id):

    DATA_OUT = os.path.join(DATA_FOLDER, f"neo_id_{neo_id}.json")
    file_data = get_data_from_file(DATA_OUT)
    if file_data is not None:
        return file_data

    url = f"{BASE_URL}/neo/{neo_id}?api_key={API_KEY}"
    url += f"&asteroid_id={neo_id}"

    data = get_nasa_data(url)

    store_data_in_file(DATA_OUT, data)
    return data
