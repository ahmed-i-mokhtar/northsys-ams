import json
from geopy.distance import geodesic
import numpy as np
from math import pi, sin, cos, atan2, sqrt
import haversine as hs
from haversine import Unit


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


def compute_xy(reference_gps, target_gps):
    long1 = reference_gps["lon"]
    lat1 = reference_gps["lat"]
    long2 = target_gps["lon"]
    lat2 = target_gps["lat"]

    lat1 *= pi / 180
    lat2 *= pi / 180
    long1 *= pi / 180
    long2 *= pi / 180

    dlong = long2 - long1
    dlat = lat2 - lat1

    # Haversine formula:
    R = 6371
    a = sin(dlat / 2) * sin(dlat / 2) + cos(lat1) * cos(lat2) * sin(dlong / 2) * sin(
        dlong / 2
    )
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    d = R * c

    x = d * cos(lat1) * cos(dlong) * 1000
    y = d * cos(lat1) * sin(dlong) * 1000

    return x, y


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
target_loc = {"lat": 23.58785381400003, "lon": 58.14583060000007, "alt": 48.25}
loc1 = (reference_loc["lat"], reference_loc["lon"])
loc2 = (target_loc["lat"], target_loc["lon"])

result = hs.haversine(loc1, loc2, unit=Unit.METERS)
bearing = hs.haversine(loc1, loc2, unit=Unit.DEGREES)
delta_x = result * cos(bearing)
delta_y = result * sin(bearing)
print("The distance calculated is:", result, bearing)
print("The delta x and y are:", delta_x, delta_y)
# data = json.load(open("AdrUnit.json"))

# features = data["features"]

# for feature in features:
#     num = feature["properties"]["ADRUTNUM"]
#     coordinates = feature["geometry"]["coordinates"]
#     type = feature["properties"]["ADRSTAT"]
#     if num is None:
#         continue

#     print(num, coordinates, type)
