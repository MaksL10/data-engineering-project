import time
import os
import yaml
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_path = os.path.join(BASE_DIR, "config", "config.yaml")

with open(config_path, "r") as f:
    config = yaml.safe_load(f)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("MONGO_DB", "city_database")
CLEAN_COLLECTION = os.getenv("MONGO_COLLECTION_PROCESSED", "weather_processed")
ALERT_COLLECTION = os.getenv("MONGO_COLLECTION_ALERT", "alert_collection")
THRESHOLDS = {
    "tl": {"max": config["alerts"]["temperature"]["max"],
           "min": config["alerts"]["temperature"]["min"]},
    "ffam": {"max": config["alerts"]["wind"]["ffam_max"]},
    "ffx": {"max": config["alerts"]["wind"]["ffx_max"]},
    "rr": {"max": config["alerts"]["precipitation"]["rr_max"]},
    "sh": {"max": config["alerts"]["snow"]["sh_max"]}
}

# 2. Establish connection to Mongo DB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
clean_col = db[CLEAN_COLLECTION]
alert_col = db[ALERT_COLLECTION]

def check_alerts():
    for station in config["stations"]:
        station_id = str(station["id"])
        latest = clean_col.find_one(
            {"station_id": station_id},
            sort = [("timestamp", -1)]
        )

        if latest is None:
            continue

        for parameter, limits in THRESHOLDS.items():
            value = latest.get(parameter)

            is_alert = False

            if value is None:
                continue

            elif value > limits["max"]:
                is_alert = True

            if is_alert is True:
                send_alarm(parameter, limits["max"], value)
    

if __name__ == "__main__":
    check_alerts()
    client.close