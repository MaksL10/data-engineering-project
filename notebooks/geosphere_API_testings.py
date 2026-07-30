import json
import requests

url = "https://dataset.api.hub.geosphere.at/v1"
type = "station"
mode = ["current", "historical"]
resource_ids = ["klima-v2-10min", "tawes-v1-10min"]
metadata = "metadata"
start = "2026-06-11"
end = "2026-06-12"
params = "?parameters="

metad_url = "https://dataset.api.hub.geosphere.at/v1/station/historical/klima-v2-10min/metadata"

test_url = url + "/" + type + "/" + mode[1] + "/" + resource_ids[0] + params + "tl&station_ids=18225&start=" + start + "&end=" + end
print(test_url)

# metaresponse = requests.get(metad_url)
# meta_obj = metaresponse.json()
# print(json.dumps(meta_obj, indent=2))
response = requests.get(test_url)

obj = response.json()
print(json.dumps(obj, indent=2))