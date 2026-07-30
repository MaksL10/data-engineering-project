from pymongo import MongoClient

# 1. Establish connection (Databank: "city_database", Collection: "stations")
client = MongoClient("mongodb://localhost:27017/")
db = client["city_database"]
stations_col = db["stations"]

# 2. List of Dictionaries with all needed stations
# every document should containt {"station_id": "11035", "name": "Wien/Hohe Warte"}

stations_to_add = [
    {"station_id": "11035", "name": "Wien/Hohe Warte"}
]

# 3. Check if stations are already in the DB

for station in stations_to_add:
    search_criterium = {"station_id": station["station_id"]} # search for the same ID in the DB

    new_data = {"$set":{"name": station["name"]}}

    stations_col.update_one(
        filter=search_criterium,
        update=new_data,
        upsert=True
    )

print("Station reconciliation successfully completed!")
client.close()

