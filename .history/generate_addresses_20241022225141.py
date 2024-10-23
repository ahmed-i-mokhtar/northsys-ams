import json


data = json.load(open("AdrUnit.json"))

features = data["features"]

for feature in features:
    num = feature["properties"]["ADRUTNUM"]
    coordinates = feature["geometry"]["coordinates"]
    type = feature["properties"]["ADRSTAT"]
    if num is None:
        continue

    print(num, coordinates, type)
