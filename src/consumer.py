import os
import json
from kafka import KafkaConsumer
from pymongo import MongoClient
from dotenv import load_dotenv

# 1. Kafka Configuration
load_dotenv()
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
TOPIC_NAME = os.getenv("KAFKA_TOPIC", "geosphere-weather")
MONGO_URI = os.getenv("MONGO_DB", "mongodb://localhost:27017/")
DB_NAME = os.getenv("MONGO_DB", "city_database")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION_RAW", "weather_data")

# 2. Install connections
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]
collection = db[COLLECTION_NAME]

# 3. Kafka Consumer
# Is reading bytes from the topic and translates it automaticly into python dict.
consumer = KafkaConsumer(
    TOPIC_NAME,
    bootstrap_servers=[KAFKA_BROKER],
    auto_offset_reset='earliest', # is reading unread messages from the beginning
    enable_auto_commit=True,
    group_id = "geosphere-consumer",    # consumer group for offset management
    value_deserializer = lambda m:json.loads(m.decode("utf-8"))
)

if __name__ == "__main__":
    print(f"Python consumer started. Listening on Topic {TOPIC_NAME}")
    print("Press STRG+C to quit. \n")

    try:
        for message in consumer:
            weather_event = message.value

            # Write the JSON package directly into MongoDB Collection
            result = collection.insert_one(weather_event)

            print(f"[Recieved] new event read from Kafka")
            print(f"[MongoDB] successfully saved with ID: {result.inserted_id}")
            print("-" * 50)
    
    except KeyboardInterrupt:
        print("\nConsumer manually stopped.")
    except Exception as e:
        print(f"Mistake in Consumer: {e}")
    finally:
        mongo_client.close()
