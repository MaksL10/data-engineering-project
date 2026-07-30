import json
import requests

with open('hohe_warte.json') as HW_response:
    response = json.load(HW_response)

    print(response["features"][0]["properties"]["parameters"]["TL"]["data"][0])

    # temperatur = response[]

    # find all nested keys in the respone:

    keys_list = []
    def get_keys(response, keys_list):
        if isinstance(response, dict):
            for key, value in response.items():
                keys_list.append(key)
                get_keys(value, keys_list)
        elif isinstance(response, list):
            for item in response:
                get_keys(item, keys_list)
    
    get_keys(response, keys_list)
    # print(keys_list)

    # find not nested keys

    # for key, value in response.items():
        # print("Key: ")
        # print(key)
    # for result in response["features"]:
        # print(result["properties"])

    
    HW_response.close()
    print(json.dumps(response, indent=2))

# response_one = requests.get("https://dataset.api.hub.geosphere.at/v1/station/current/tawes-v1-10min?parameters=TL&station_ids=11035")
# print(json.dumps(response_one.json(), indent=2))