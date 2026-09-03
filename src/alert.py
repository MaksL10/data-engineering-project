import time
import os
import yaml
from datetime import datetime, timezone
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
HEALTH_COLLECTION = os.getenv("MONGO_COLLECTION_HEALTH", "system_health")
THRESHOLDS = {
    "tl": {"max": config["alerts"]["temperature"]["max"],
           "min": config["alerts"]["temperature"]["min"]},
    "ffam": {"max": config["alerts"]["wind"]["ffam_max"]},
    "ffx": {"max": config["alerts"]["wind"]["ffx_max"]},
    "rr": {"max": config["alerts"]["precipitation"]["rr_max"]},
    "sh": {"max": config["alerts"]["snow"]["sh_max"]}
}
STATION_NAMES = {str(s["id"]): s["name"] for s in config["stations"]}
PARAMETER_NAMES = {
    "tl": "Lufttemperatur",
    "ffam": "Windgeschwindigkeit",
    "ffx": "Windböen",
    "rr": "Niederschlag",
    "sh": "Schneehöhe"
}
PARAMETER_UNITS = {
    "tl": "°C",
    "ffam": "km/h",
    "ffx": "km/h",
    "rr": "mm",
    "sh": "cm"
}

# 2. Establish connection to Mongo DB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
clean_col = db[CLEAN_COLLECTION]
alert_col = db[ALERT_COLLECTION]
health_col = db[HEALTH_COLLECTION]

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

            if value is None:
                continue

            is_alert = is_threshold_exceeded(value, limits)

            active_alert = alert_col.find_one({
                "station_id": station_id,
                "parameter": parameter,
                "active": True
            })

            if is_alert and active_alert:
                continue

            elif is_alert and not active_alert:
                send_alarm(station_id, parameter, value, limits)

            elif not is_alert and active_alert:
                send_resolved(station_id, parameter, active_alert)

            write_heartbeat("alert")

def is_threshold_exceeded(value, limits) -> bool:
    """Checks if the value is over or under max/min alert limit"""
    if value > limits.get("max", float("inf")):
        return True 
    if value < limits.get("min", float("-inf")):
        return True
    return False

def send_alarm(station, parameter, value, limit):
    max = limit.get("max", float("inf"))
    min = limit.get("min", float("-inf"))
    limit_type = "max" if value > max else "min"

    station_name = STATION_NAMES.get(station, station)
    param_name = PARAMETER_NAMES.get(parameter, parameter)
    unit = PARAMETER_UNITS.get(parameter, "")

    alert_col.insert_one({
                "station_id": station,
                "parameter": parameter,
                "value": value,
                "limit_type": limit_type,
                "active": True,
                "timestamp": datetime.now(timezone.utc)
            })

    if value > max:
        
        print(f'[WARNUNG]: {station_name}. {param_name} beträgt {value}{unit} '
              f'(Grenzwert: {max}{unit})')

    else:
        print(f'[WARNUNG]: {station_name}. {param_name} beträgt {value}{unit} '
                      f'(Grenzwert: {min}{unit})')

def send_resolved(station, parameter, active_alert):
    station_name = STATION_NAMES.get(station, station)
    param_name = PARAMETER_NAMES.get(parameter, parameter)

    alert_col.update_one(
        {"_id": active_alert["_id"]},
        {"$set": {
            "active": False,
            "resolved_at": datetime.now(timezone.utc)
        }}
    )

    print(f'[ENTWEARNUNG]: {station_name}: {param_name} wieder im Normalbereich')

def write_heartbeat(component: str):
    health_col.update_one(
        {"component": component},
        {"$set": {
            "status": "ok",
            "last_seen": datetime.now(timezone.utc)
        }},
        upsert = True
    )
        

if __name__ == "__main__":
    print(f'Allert system started. Exit with CTRL+C\n')
    try:
        while True:
            check_alerts()
            time.sleep(INTERVAL * 60)
    except KeyboardInterrupt:
        print(f'\nAlert system stopped')
    finally:
        client.close()