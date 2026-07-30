import time
from pymongo import MongoClient

# 1. Configuration
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "city_database"
RAW_COLLECTION = "weather_data"
CLEAN_COLLECTION = "cleaned_weather"
STATIONS = "stations"

# 2. Establish connection to DB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
raw_col = db[RAW_COLLECTION]
clean_col = db[CLEAN_COLLECTION]


stations_col = db[STATIONS]

def get_station_lookup():
    # get all documents from stations-collection in MongoDB
    db_stations = stations_col.find()

    lookup = {}

    for doc in db_stations:
        station_id = doc.get("station_id")
        station_name = doc.get("name")

        lookup[station_id] = station_name

    return lookup

def transform_latest_data():
    # 1. Step: get the newest raw-data document
    latest_raw = raw_col.find_one(sort=[('_id', -1)])

    if not latest_raw:
        print("No raw data found in MongoDB. Please start the producer first!")
        return
    
    # extracting timestamps of the last file
    timestamps = latest_raw.get("timestamps", [])

    records = []

    for feature in latest_raw.get("features", []):
        properties = feature.get("properties", [])
        
        # extract station ID, where the key is "station"
        station = properties.get("station", [])
        
        # extract the next Dict layer
        parameters = properties.get("parameters", {})
        
        # getting data for Temperature, Temperature Unis and Name
        for key, value in parameters.items():
            temp_list = value.get("data", [])
            temp_unit = value.get("unit")
            temp_name = value.get("name")

            temp = temp_list[0]

            print(temp_name, ":", temp, temp_unit)

        new_file = create_cleaned_data(timestamps, temp, station, temp_unit, temp_name)
        print(new_file)

    
    #return(features)

    # 2. Step: search stations for certain station (here for example: Wien/Hohe Warte)
    # target_station = "Wien/Hohe Warte"
    # wien_data = None

# def check():
    #_

def create_cleaned_data(timestamps, temp, station_id, temp_unit, temp_name):
    record = {
        "station": station_id,
        "timestamp": timestamps,
        "name": temp_name,
        "unit": temp_unit,
        "temp": temp
    }

    return record


if __name__ == "__main__":
    my_lookup = get_station_lookup()
    raw_data = transform_latest_data()
    client.close()