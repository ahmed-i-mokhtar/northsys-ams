import json


# Function to compute new GPS location given translation and yaw
def compute_new_location(reference_gps, translation):
    """
    Compute a new GPS location given a reference location, translations in meters, and a quaternion rotation.

    :param reference_gps: Dictionary {'lat': latitude, 'lon': longitude, 'alt': altitude}
    :param translation: List [x, y, z] translations in meters.
    :param quaternion: List [w, x, y, z] quaternion representing the rotation.
    :return: Tuple (new_latitude, new_longitude, new_altitude)
    """
    # Unpack reference GPS coordinates
    lat, lon, alt = reference_gps["lat"], reference_gps["lon"], reference_gps["alt"]

    # Unpack translation values
    x, y, z = translation

    # add translation in x and y to the reference GPS coordinates
    new_location = geodesic(meters=y).destination(point=(lat, lon), bearing=0)
    new_location = geodesic(meters=x).destination(
        point=(new_location.latitude, new_location.longitude), bearing=90
    )

    # Compute new altitude
    new_altitude = alt + z

    # Return new latitude, longitude, and altitude
    return new_location.latitude, new_location.longitude, new_altitude


data = json.load(open("AdrUnit.json"))

features = data["features"]

for feature in features:
    num = feature["properties"]["ADRUTNUM"]
    coordinates = feature["geometry"]["coordinates"]
    type = feature["properties"]["ADRSTAT"]
    if num is None:
        continue

    print(num, coordinates, type)
