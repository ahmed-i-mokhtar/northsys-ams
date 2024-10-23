import json
from geopy.distance import geodesic
import numpy as np


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


reference_loc_str = compute_new_location(
    {"lat": 23.586242, "lon": 58.145658, "alt": 48.25},
    -np.array([146.102, 80.233, 48.25]),
)
reference_loc = {
    "lat": float(reference_loc_str[0]),
    "lon": float(reference_loc_str[1]),
    "alt": float(reference_loc_str[2]),
}

print(reference_loc)

# data = json.load(open("AdrUnit.json"))

# features = data["features"]

# for feature in features:
#     num = feature["properties"]["ADRUTNUM"]
#     coordinates = feature["geometry"]["coordinates"]
#     type = feature["properties"]["ADRSTAT"]
#     if num is None:
#         continue

#     print(num, coordinates, type)
