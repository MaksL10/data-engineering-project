import json
import requests
import os
import yaml
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import date, timedelta, datetime
from typing import Literal

# 1. Loading env
load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_path = os.path.join(BASE_DIR, "config", "config.yaml")

with open(config_path, "r") as f:
    config = yaml.safe_load(f)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("MONGO_DB", "city_database")
RAW_COLLECTION = os.getenv("MONGO_COLLECTION_RAW", "weather_data")
VALID_FLAGS = config["quality"]["valid_flags"]

BASE_URL = config["api"]["base_url"]
ENDPOINT = config["api"]["endpoint"]
API_URL = f"{BASE_URL}/{ENDPOINT}"

STATION_IDS = ",".join(str(s["id"]) for s in config["stations"]) # is a String with all station ids in it. Example: "6, 10, 11"
PARAMETERS = ",".join(config["parameters"])

# 2. Establish connection to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
raw_col = db[RAW_COLLECTION]

def get_all_data():
    try:
        dates = get_period()
        start = dates[0]
        end = dates[1]

        api_limit_check = get_limits(start, end, 
                                     len(config["stations"]),
                                     len(config["parameters"]),
                                     config["api"]["interval_minutes"])
        if api_limit_check == "good":

            params = {
                "parameters": PARAMETERS,
                "station_ids": STATION_IDS,
                "start": start_point,
                "end": end_point
            }

            print(f'Calling GeoSphere Austra for backfill')
            response = requests.get(API_URL, params=params)

            if response.status_code == 200:
                weather_data = response.json()

                raw_col.insert_one(weather_data)

            else:
                print(f"Error during API retrieval: Status Code: {response.status_code}")

        else:
            current = start_point
            call_count = 0
            while current < end_point:
                chunk_end = min(current + timedelta(days=30), end_point)
                print(f'Calling GeoSphere Austra for backfill for the {call_count} time(s)')
                params = {
                    "parameters": PARAMETERS,
                    "station_ids": STATION_IDS,
                    "start": current.strftime("%Y-%m-%dT%H:%M"),
                    "end": chunk_end.strftime("%Y-%m-%dT%H:%M")
                }

                response = requests.get(API_URL, params=params)

                if response.status_code == 200:
                    weather_data = response.json()

                    raw_col.insert_one(weather_data)
                    current = chunk_end + timedelta(days=1)

                    call_count += 1

                else:
                    print(f'[Error] {response.status_code}')
                    break

    except Exception as e:
        print(f"An error has occurred: {e}")

def get_period():
    end_point = date.today()
    start_point = end_point - timedelta(days=180)
    dates = [start_point, end_point]
    return dates

def get_limits(start, end, count_stations, count_parameters, req_interval) -> Literal["good", "bad"]:
    req_limit = 1000000
    timestamps_per_day = (24 * 60) / req_interval
    count_days = (end - start).days
    req_count = count_stations * count_parameters * count_days * timestamps_per_day

    if req_count > req_limit:
        return "bad"
    else:
        return "good"

if __name__ == "__main__":
    print("Getting backfill data from GeoSphere Austria")
    get_all_data()
    print("All data saved")
    client.close()
