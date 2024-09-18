import os
import sys
import json
from typing import Union
from fastapi import FastAPI
import unicorn
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware
import glob
from geopy.distance import geodesic
import math
from pyquaternion import Quaternion
import numpy as np
import logging

app = FastAPI()
logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.DEBUG)


locations_list = [
    "42.331515_-83.038699_185.29",
    "42.331553_-83.038734_185.39",
    "42.331593_-83.038761_185.42",
    "42.331634_-83.038786_185.40",
    "42.331675_-83.038811_185.39",
    "42.331718_-83.038832_185.28",
    "42.331762_-83.038841_185.11",
    "42.331805_-83.038826_184.97",
    "42.331838_-83.038785_184.94",
    "42.331862_-83.038734_184.92",
    "42.331882_-83.038681_184.93",
    "42.331894_-83.038623_185.07",
    "42.331881_-83.038568_185.10",
    "42.331853_-83.038523_185.13",
    "42.331816_-83.038491_185.16",
    "42.331777_-83.038463_185.17",
    "42.331737_-83.038438_185.18",
    "42.331697_-83.038413_185.16",
    "42.331658_-83.038388_185.09",
    "42.331618_-83.038369_185.07",
    "42.331576_-83.038381_185.08",
    "42.331547_-83.038424_185.06",
    "42.331524_-83.038475_185.03",
    "42.331501_-83.038526_185.01",
    "42.331477_-83.038577_185.03",
    "42.331454_-83.038628_185.07",
    "42.331431_-83.038680_185.10",
    "42.331408_-83.038732_185.10",
    "42.331386_-83.038783_185.11",
    "42.331363_-83.038835_185.10",
    "42.331341_-83.038887_185.09",
    "42.331318_-83.038938_185.07",
    "42.331296_-83.038990_185.05",
    "42.331274_-83.039042_185.03",
    "42.331251_-83.039094_185.01",
    "42.331229_-83.039146_184.98",
    "42.331207_-83.039197_184.94",
    "42.331184_-83.039248_184.91",
    "42.331162_-83.039300_184.88",
    "42.331139_-83.039351_184.85",
    "42.331116_-83.039402_184.83",
    "42.331094_-83.039454_184.80",
    "42.331071_-83.039506_184.77",
    "42.331049_-83.039558_184.74",
    "42.331027_-83.039610_184.71",
    "42.331005_-83.039663_184.69",
    "42.330983_-83.039716_184.67",
    "42.330962_-83.039768_184.66",
    "42.330940_-83.039821_184.66",
    "42.330918_-83.039874_184.66",
    "42.330896_-83.039926_184.65",
    "42.330873_-83.039979_184.58",
    "42.330850_-83.040031_184.54",
    "42.330827_-83.040083_184.49",
    "42.330804_-83.040135_184.47",
    "42.330780_-83.040186_184.49",
    "42.330757_-83.040238_184.50",
    "42.330734_-83.040290_184.52",
    "42.330711_-83.040342_184.55",
    "42.330688_-83.040394_184.58",
    "42.330666_-83.040446_184.61",
    "42.330643_-83.040499_184.63",
    "42.330621_-83.040551_184.59",
    "42.330599_-83.040604_184.56",
    "42.330576_-83.040657_184.54",
    "42.330554_-83.040709_184.51",
    "42.330531_-83.040762_184.49",
    "42.330509_-83.040814_184.48",
    "42.330486_-83.040867_184.46",
    "42.330464_-83.040919_184.47",
    "42.330441_-83.040971_184.49",
    "42.330418_-83.041024_184.53",
    "42.330395_-83.041076_184.56",
    "42.330371_-83.041127_184.53",
    "42.330347_-83.041179_184.50",
    "42.330323_-83.041230_184.51",
    "42.330299_-83.041281_184.51",
    "42.330275_-83.041332_184.53",
    "42.330253_-83.041385_184.56",
    "42.330232_-83.041438_184.58",
    "42.330211_-83.041492_184.60",
    "42.330190_-83.041546_184.59",
    "42.330169_-83.041599_184.57",
    "42.330147_-83.041652_184.55",
    "42.330125_-83.041705_184.52",
    "42.330103_-83.041757_184.50",
    "42.330080_-83.041810_184.50",
    "42.330057_-83.041862_184.52",
    "42.330040_-83.041918_184.54",
    "42.330036_-83.041978_184.55",
    "42.330051_-83.042035_184.49",
    "42.330083_-83.042077_184.38",
    "42.330121_-83.042108_184.34",
    "42.330160_-83.042135_184.29",
    "42.330197_-83.042162_184.23",
    "42.330238_-83.042190_184.16",
]
reference_loc = {"lat": 42.33402017629453, "lon": -83.04563309009228, "alt": 0.0}


sensor_calibration = {
    "camera_intrinsic": [
        [512, 0.0, 0.512],
        [0.0, 512, 0.512],
        [0.0, 0.0, 1.0],
    ],
    "rotation": [0.7071067811865476, -0.7071067811865475, 0.0, 0.0],
    "sensor_token": "7w7q9c6sp6jzxnixqx7u4h-cs",
    "token": "7w7q9c6sp6jzxnixqx7u4h",
    "translation": [0, 0, 0],
}


# Function to compute new GPS location given translation and yaw
def compute_new_location_with_quaternion(reference_gps, translation, quaternion):
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


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],  # Adjust this to your local development URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.get("/pano_image/{location}")
async def get_pano_image(location: str):
    # Path to the image
    image_path = f"./data/server_pano_images/{location}.jpg"
    # Check if the file exists
    if os.path.exists(image_path):
        return FileResponse(image_path, media_type="image/jpeg")
    else:
        return {"error": "Image not found"}


@app.get("/depth_image/{location}")
async def get_depth_image(location: str):
    # Path to the image
    image_path = f"./data/server_depth_images/{location}.png"
    # Check if the file exists
    if os.path.exists(image_path):
        return FileResponse(image_path, media_type="image/jpeg")
    else:
        return {"error": "Image not found"}


@app.get("/get_locations")
async def get_locations():
    # Return  response
    return locations_list


@app.get("/get_geo_location/{location}")
async def get_geo_location(ego_location: str, location: str):
    ego_pose_path = f"./data/server_ego_poses/{ego_location}.json"
    with open(ego_pose_path, "r") as f:
        ego_pose = json.load(f)
        location_z = float(location.split("_")[0])
        location_x = float(location.split("_")[1])
        location_y = float(location.split("_")[2])
        point_camera = [location_x, location_y, location_z]

        point_camera_hom = np.array(
            point_camera
        )  # Convert to homogeneous coordinates (x, y, z, 1)

        rotation_camera_to_ego = Quaternion(
            sensor_calibration["rotation"]
        ).rotation_matrix
        translation_camera_to_ego = np.array(sensor_calibration["translation"])

        point_ego = (
            np.dot(rotation_camera_to_ego, point_camera) + translation_camera_to_ego
        )

        # 2. Transform point from ego vehicle frame to world frame
        rotation_ego_to_world = Quaternion(ego_pose["rotation"]).rotation_matrix
        translation_ego_to_world = np.array(ego_pose["translation"])

        point_world = (
            np.dot(rotation_ego_to_world, point_ego) + translation_ego_to_world
        )

        geo_location = compute_new_location_with_quaternion(
            reference_loc, point_world, ego_pose["rotation"]
        )
    return geo_location


@app.get("/save_addressing_point/{location}")
async def save_addressing_point(ego_location: str, location: str):
    ego_pose_path = f"./data/server_ego_poses/{ego_location}.json"
    addressing_points_path = f"./addressing_points.json"

    addressing_points = {}
    if os.path.exists(addressing_points_path):
        with open(addressing_points_path, "r") as f:
            addressing_points = json.load(f)
    with open(ego_pose_path, "r") as f:
        ego_pose = json.load(f)
        location_z = float(location.split("_")[0])
        location_x = float(location.split("_")[1])
        location_y = float(location.split("_")[2])
        point_camera = [location_x, location_y, location_z]

        point_camera_hom = np.array(
            point_camera
        )  # Convert to homogeneous coordinates (x, y, z, 1)

        rotation_camera_to_ego = Quaternion(
            sensor_calibration["rotation"]
        ).rotation_matrix
        translation_camera_to_ego = np.array(sensor_calibration["translation"])

        point_ego = (
            np.dot(rotation_camera_to_ego, point_camera) + translation_camera_to_ego
        )

        # 2. Transform point from ego vehicle frame to world frame
        rotation_ego_to_world = Quaternion(ego_pose["rotation"]).rotation_matrix
        translation_ego_to_world = np.array(ego_pose["translation"])

        point_world = (
            np.dot(rotation_ego_to_world, point_ego) + translation_ego_to_world
        )

        geo_location = compute_new_location_with_quaternion(
            reference_loc, point_world, ego_pose["rotation"]
        )

        geo_location_str = (
            f"{geo_location[0]:.9f}_{geo_location[1]:.9f}_{geo_location[2]:.2f}"
        )

        logger.debug(f"geo_location_str: {geo_location_str}")

        point_world_str = f"{point_world[0]}_{point_world[1]}_{point_world[2]}"
        addressing_points[geo_location_str] = point_world_str

    # Save the addressing points
    with open(addressing_points_path, "w") as f:
        json.dump(addressing_points, f)

    return addressing_points


@app.get("/get_world_addressing_points")
async def get_world_addressing_points():
    addressing_points_list = []
    for key, value in addressing_points.items():
        addressing_points_list.append(key)

    return addressing_points_list


@app.get("/get_camera_addressing_points")
async def get_camera_addressing_points(ego_location: str):
    camera_addressing_points_list = []
    ego_pose_path = f"./data/server_ego_poses/{ego_location}.json"
    with open(ego_pose_path, "r") as f:
        ego_pose = json.load(f)
        for key, value in addressing_points.items():
            # Transform the addressing point from world frame to ego frame
            rotation_ego_to_world = Quaternion(ego_pose["rotation"]).rotation_matrix
            translation_ego_to_world = np.array(ego_pose["translation"])
            point_world = np.array([float(i) for i in value.split("_")])

            # Inverse transformation
            point_ego = np.dot(
                np.linalg.inv(rotation_ego_to_world),
                point_world - translation_ego_to_world,
            )

            # Transform the addressing point from ego frame to camera frame
            rotation_camera_to_ego = Quaternion(
                sensor_calibration["rotation"]
            ).rotation_matrix
            translation_camera_to_ego = np.array(sensor_calibration["translation"])

            # Inverse transformation
            point_camera = np.dot(
                np.linalg.inv(rotation_camera_to_ego),
                point_ego - translation_camera_to_ego,
            )

            distance = math.sqrt(
                point_camera[0] ** 2 + point_camera[1] ** 2 + point_camera[2] ** 2
            )

            if distance < 25:
                camera_addressing_points_list.append(
                    f"{point_camera[0]}_{point_camera[1]}_{point_camera[2]}"
                )

    return camera_addressing_points_list


@app.get("/get_geo_addressing_points")
async def get_addressing_points():
    geo_list = []
    for key, value in addressing_points.items():
        geo_list.append(key)
    return geo_list


@app.get("/delete_addressing_point")
async def delete_addressing_point(geo_location: str):
    if geo_location in addressing_points:
        del addressing_points[geo_location]
        return addressing_points
    else:
        return {"error": "Addressing point not found"}


@app.get("/delete_all_addressing_points")
async def delete_all_addressing_point():
    addressing_points.clear()


if __name__ == "__main__":
    unicorn.run(app, port=8000, reload=True)
