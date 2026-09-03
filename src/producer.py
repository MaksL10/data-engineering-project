import time
import json
import requests
import os
import yaml
from kafka import KafkaProducer
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from pymongo import MongoClient


# 1. Kafka-Konfigurations
load_dotenv()
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
MONGO_URI = os.getenv("MONGO_DB", "mongodb://localhost:27017/")
DB_NAME = os.getenv("MONGO_DB", "city_database")
TOPIC_NAME = os.getenv("KAFKA_TOPIC", "geosphere-weather")
HEALTH_COLLECTION = os.getenv("MONGO_COLLECTION_HEALTH", "system_health")

# 2. Load config.yaml
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_path = os.path.join(BASE_DIR, "config", "config.yaml")

with open(config_path, "r") as f:
    config = yaml.safe_load(f) # transforms YAML into dict. Config is type[dict]

BASE_URL = config["api"]["base_url"]
ENDPOINT = config["api"]["endpoint"]
API_URL = f"{BASE_URL}/{ENDPOINT}"
INTERVAL = config["api"]["interval_minutes"]

STATION_IDS = ",".join(str(s["id"]) for s in config["stations"])
PARAMETERS = ",".join(config["parameters"])

# 3. Kafka Producer Initialization
# Producer should serialize JSON-Response

producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Install connection to SYSTEM_HEALTH
mongo_client = MongoClient(MONGO_URI)
db = mongo_client(DB_NAME)
health_col = db[HEALTH_COLLECTION]

def fetch_and_send_weather():
    try:
        # Shift time window 1 hour back due to API publication delay (~30 - 40 Minutes)
        end = datetime.now(timezone.utc) -timedelta(hours=1)
        start = end - timedelta(minutes=INTERVAL)

        params = {
            "parameters": PARAMETERS,
            "station_ids": STATION_IDS,
            "start": start.strftime("%Y-%m-%dT%H:%M"),
            "end": end.strftime("%Y-%m-%dT%H:%M")
        }

        print(f"[{time.strftime('%H:%M:%S')}] calling Geosphere API...")
        print(f" Querying: {start.strftime('%H:%M')} -> {end.strftime('%H:%M')} UTC")
        response = requests.get(API_URL, params=params)

        if response.status_code == 200:
            weather_data = response.json()

            # sending complete json-file to kafka
            producer.send(TOPIC_NAME, value=weather_data)
            producer.flush() # securing message has been sent immidiately
            print(f"[{time.strftime('%H:%M:%S')}] Data successfully sent to Topic {TOPIC_NAME}!")
            write_heartbeat("producer")
        else:
            print(f"Error during API retrieval: Status Code: {response.status_code}")

    except Exception as e:
        print(f"An error has occurred: {e}")

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
    print("Python Geosphere Producer has started. Exit with CTRL+C.")
    while True:
        fetch_and_send_weather()
        # we wait 10 Minutes for the next request
        print("Waiting 10 Minutes till the next request... \n")
        time.sleep(600)