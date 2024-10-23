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


def gps_difference_in_meters(ref_gps, target_gps):
    # Extract latitude and longitude
    lat1, lon1 = ref_gps
    lat2, lon2 = target_gps

    # Calculate north-south distance (y direction)
    north_south_distance = hs.haversine((lat1, lon1), (lat2, lon1), unit=Unit.METERS)

    # Calculate east-west distance (x direction)
    east_west_distance = hs.haversine((lat1, lon1), (lat1, lon2), unit=Unit.METERS)

    # Determine the signs of the distances
    if lat2 < lat1:
        north_south_distance = -north_south_distance
    if lon2 < lon1:
        east_west_distance = -east_west_distance

    return east_west_distance, north_south_distance


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


# target_loc = {"lat": 23.59962966300003, "lon": 58.15737189400005, "alt": 48.25}
loc1 = (reference_loc["lat"], reference_loc["lon"])
# loc2 = (target_loc["lat"], target_loc["lon"])


# x, y = gps_difference_in_meters(loc1, loc2)

# print(x, y)
data = json.load(open("AdrUnit.json"))

features = data["features"]

addressing_points = {}
for feature in features:
    num = feature["properties"]["ADRUTNUM"]
    coordinates = feature["geometry"]["coordinates"]
    type = feature["properties"]["ADRSTAT"]
    if num is None:
        continue
    x, y = gps_difference_in_meters(loc1, (coordinates[1], coordinates[0]))
    geo_str = f"{coordinates[1]}_{coordinates[0]}_0.0_{type}_{num}"
    world_str = f"{x}_{y}_0.0"
    addressing_points[geo_str] = {
        "id": num,
        "world": world_str,
    }

print(addressing_points)
