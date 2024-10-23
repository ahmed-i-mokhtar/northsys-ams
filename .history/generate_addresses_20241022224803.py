import json


data = json.load(open("AdrUnit.json"))

features = data["features"]

for feature in features:
    num = feature["properties"]["ADRUTNUM"]
    coordinates = feature["geometry"]["coordinates"]
    print(num, coordinates)
