import json

with open("metadaten_hourly.json") as df:
    file = json.load(df)
    print(json.dumps(file, indent=2))
    file.close()