import os
from dotenv import load_dotenv
from datetime import datetime, timezone
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("MONGO_DB", "city_database")
HEALTH_COLLECTION = os.getenv("MONGO_COLLECTION_HEALTH", "system_health")
ALERT_COLLECTION = os.getenv("MONGO_COLLECTION_ALERT", "alert_collection")

# 2. install connection to DB

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
alert_col = db[ALERT_COLLECTION]
health_col = db[HEALTH_COLLECTION]

def show_dashboards():

    COMPONENTS = ["producer", "consumer", "transformer", "alert"]
    for component in COMPONENTS:
        entry = health_col.find_one({"component": component})
        if entry is None:
            continue
        elif entry == "last_seen":
            