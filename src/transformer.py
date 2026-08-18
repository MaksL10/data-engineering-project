import os
import yaml
import time
from pymongo import MongoClient
from dotenv import load_dotenv

# 1. Load enviroment variables & config
load_dotenv()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_path = os.path.join(BASE_DIR, "config", "config.yaml")

with open(config_path, "r") as f:
    config = yaml.safe_load(f)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("MONGO_DB", "city_database")
RAW_COLLECTION = os.getenv("MONGO_COLLECTION_RAW", "weather_data")
CLEAN_COLLECTION = os.getenv("MONGO_COLLECTION_PROCESSED", "weather_processed")
VALID_FLAGS = config["quality"]["valid_flags"]
INTERVAL = config["api"]["interval_minutes"]

# 2. Establish connection to Mongo DB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
raw_col = db[RAW_COLLECTION]
clean_col = db[CLEAN_COLLECTION]

def transform_document(raw_doc):
    """Transform one raw GeoSpheredocument into flat record - one per station per timestamp."""
    timestamps = raw_doc.get("timestamps", [])

    records = []

    for feature in raw_doc.get("features", []):
        properties = feature.get("properties", {})
        station_id = properties.get("station")
        parameters = properties.get("parameters", {})

        # one record per timestamp
        for i, timestamp in enumerate(timestamps):
            # Build flat record for this station and timestamp
            record = {
                "station_id": station_id,
                "timestamp": timestamp
            }

            for param_key, param_value in parameters.items():
                data = param_value.get("data", [None])
                value = data[i] if i < len(data) else None
                record[param_key] = value

            records.append(record)

    return records

def transform_unprocessed():
    """Find and transform all raw documents not yet processed"""
    # Only fetch documents where 'processed' field is not True
    # 1. Step: get the newest raw-data document
    unprocessed = raw_col.find({"processed": {"$ne": True}})
    count = 0

    for raw_doc in unprocessed:
        records = transform_document(raw_doc)
    
        for record in records:
            # Avoid duplicates: only insert if station + timestamp not already in clean collection
            exists = clean_col.find_one({
                "station_id": record["station_id"],
                "timestamp": record["timestamp"]
            })

            if not exists:
                clean_col.insert_one(record)
                print(f"[Saved] Station {record['station_id']} | {record['timestamp']}")
            else:
                print(f"[Skipped]  Station {record['station_id']} | {record['timestamp']} already exists")

        # Mark raw document as processed
        raw_col.update_one(
            {"_id": raw_doc["_id"]},
            {"$set": {"processed": True}}
        )
        count += 1

    print("-" * 50)

if __name__ == "__main__":
    print("Transformer started. Exit with CTRL+C.\n")
    try:
        while True:
            transform_unprocessed()
            print(f"Waiting {INTERVAL} minutes... \n")
            time.sleep(INTERVAL * 60)
    except KeyboardInterrupt:
        print("\nTransformer manually stopped.")
    finally:
        client.close()