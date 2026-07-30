import json
from pymongo import MongoClient

# establish connection to MongoDB
MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)

# choose DB and collection
db = client["city_database"]
collection = db["weather_data"]

# count amount of documents
count = collection.count_documents({})
print(f"---MongoDB status---")
print(f"Saved documents in total: {count}\n")

if count > 0:
    print("The newest saved document:")
    # picks up the newest document (sorted by from MongoDB generated _ids)
    latest_document = collection.find_one(sort=[('_id', -1)])

    # Nicely formatted output (convert the MongoDB _id into a string so that JSON doesn't complain)
    latest_document["_id"] = str(latest_document["_id"])
    print(json.dumps(latest_document, indent=4, ensure_ascii=False))
else:
    print("Collection is still completely empty")

client.close()