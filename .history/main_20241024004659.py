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
origins = ["*"]
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Adjust this to your local development URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

locations_list = []

locations = glob.glob("./data/server_camera_poses/*.json")
for location in locations:
    # use os path to get the file name
    location_name = os.path.basename(location).split(".json")[0]
    locations_list.append(location_name)


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
    ego_pose_path = f"./data/server_camera_poses/{ego_location}.json"
    with open(ego_pose_path, "r") as f:
        ego_pose = json.load(f)
        location_z = float(location.split("_")[0])
        location_x = float(location.split("_")[1])
        location_y = float(location.split("_")[2])
        point_camera = [location_x, location_y, location_z]

        lat, lon, alt = (
            float(ego_location.split("_")[0]),
            float(ego_location.split("_")[1]),
            float(ego_location.split("_")[2]),
        )
        reference_loc = {"lat": lat, "lon": lon, "alt": alt}

        point_camera_hom = np.array(
            point_camera
        )  # Convert to homogeneous coordinates (x, y, z, 1)

        rotation_camera_to_ego = np.array(ego_pose["rotation_matrix"])
        # translation_camera_to_ego = np.array(sensor_calibration["translation"])

        point_ego = np.dot(rotation_camera_to_ego, point_camera)

        # # 2. Transform point from ego vehicle frame to world frame
        # rotation_ego_to_world = np.array(ego_pose["rotation"])
        # translation_ego_to_world = np.array(ego_pose["translation"])

        # point_world = (
        #     np.dot(rotation_ego_to_world, point_ego) + translation_ego_to_world
        # )

        geo_location = compute_new_location(reference_loc, point_ego)
    return geo_location


@app.get("/save_addressing_point/{location}")
async def save_addressing_point(
    ego_location: str, location: str, type: str = "Undefined"
):
    ego_pose_path = f"./data/server_camera_poses/{ego_location}.json"
    addressing_points_path = f"./addressing_points.json"

    addressing_points = {}
    if os.path.exists(addressing_points_path):
        with open(addressing_points_path, "r") as f:
            addressing_points = json.load(f)
    with open(ego_pose_path, "r") as f:
        ego_pose = json.load(f)
        location_x = float(location.split("_")[0])
        location_y = -float(location.split("_")[1])
        location_z = float(location.split("_")[2])
        point_camera = [location_x, location_y, location_z]

        point_camera_hom = np.array(
            point_camera
        )  # Convert to homogeneous coordinates (x, y, z, 1)

        # rotation_camera_to_ego = np.array(ego_pose["rotation_matrix"])
        yaw = ego_pose["yaw"]

        yaw = math.radians(yaw)

        rotation_camera_to_ego = np.array(
            [
                [math.cos(yaw), -math.sin(yaw), 0],
                [math.sin(yaw), math.cos(yaw), 0],
                [0, 0, 1],
            ]
        )

        # translation_camera_to_ego = np.array(sensor_calibration["translation"])
        # log point_camera
        logger.debug(f"point_camera: {point_camera}")
        # point_ego = np.array(point_camera)
        point_ego = np.array(point_camera) @ rotation_camera_to_ego

        point_world = np.array(ego_pose["translation_vector"]) + point_ego

        # # 2. Transform point from ego vehicle frame to world frame
        # rotation_ego_to_world = np.array(ego_pose["rotation"])
        # translation_ego_to_world = np.array(ego_pose["translation"])

        # point_world = (
        #     np.dot(rotation_ego_to_world, point_ego) + translation_ego_to_world
        # )
        # point_world = point_ego - np.array(ego_pose["translation_vector"])

        geo_location = compute_new_location(reference_loc, point_world)
        id = location.split("_")[3]

        geo_location_str = f"{geo_location[0]:.9f}_{geo_location[1]:.9f}_{geo_location[2]:.2f}_{type}_{id}"

        point_world_str = f"{point_world[0]}_{point_world[1]}_{point_world[2]}"
        addressing_points[geo_location_str] = {
            "world": point_world_str,
            "id": location.split("_")[3],
        }

    # Save the addressing points
    with open(addressing_points_path, "w") as f:
        json.dump(addressing_points, f)

    return addressing_points


@app.get("/update_addressing_point_type/{id}")
async def update_addressing_point(id: str, type: str = "Undefined"):
    addressing_points_path = f"./addressing_points.json"
    addressing_points = {}
    if os.path.exists(addressing_points_path):
        with open(addressing_points_path, "r") as f:
            addressing_points = json.load(f)
            x = id.split("_")[0]
            y = id.split("_")[1]
            z = id.split("_")[2]
            location_key = x + "_" + y + "_" + z

            updated_addressing_points = addressing_points.copy()
            # find the key in the addressing points
            for key, value in updated_addressing_points.items():
                current_key = (
                    key.split("_")[0]
                    + "_"
                    + key.split("_")[1]
                    + "_"
                    + key.split("_")[2]
                )
                if current_key == location_key:
                    # remove the old key and add the new key
                    addressing_points.pop(key)
                    addressing_points[location_key + "_" + type] = (
                        value.split("_")[0]
                        + "_"
                        + value.split("_")[1]
                        + "_"
                        + value.split("_")[2]
                    )
                    break

        # Save the addressing points
        with open(addressing_points_path, "w") as f:
            json.dump(addressing_points, f)

    return addressing_points


@app.get("/get_world_addressing_points")
async def get_world_addressing_points():
    addressing_points_path = f"./addressing_points.json"
    addressing_points = {}
    if os.path.exists(addressing_points_path):
        with open(addressing_points_path, "r") as f:
            addressing_points = json.load(f)
    addressing_points_list = []
    for key, value in addressing_points.items():
        id = value["id"]
        key = key + "_" + str(id)
        addressing_points_list.append(key)

    return addressing_points_list


@app.get("/get_camera_addressing_points")
async def get_camera_addressing_points(ego_location: str):
    addressing_points_path = f"./addressing_points.json"
    addressing_points = {}
    if os.path.exists(addressing_points_path):
        with open(addressing_points_path, "r") as f:
            addressing_points = json.load(f)
    camera_addressing_points_dict = {}
    ego_pose_path = f"./data/server_camera_poses/{ego_location}.json"
    with open(ego_pose_path, "r") as f:
        ego_pose = json.load(f)
        for key, value in addressing_points.items():
            # Transform the addressing point from world frame to ego frame
            # rotation_camera_to_ego = np.array(ego_pose["rotation_matrix"])
            world = value["world"]

            id = value["id"]
            point_world = np.array([float(i) for i in world.split("_")])
            if point_world[2] == 0:
                point_world[2] = np.array(ego_pose["translation_vector"])[2] - 1.5
            point_world = point_world - np.array(ego_pose["translation_vector"])
            yaw = ego_pose["yaw"]
            yaw = math.radians(yaw)
            rotation_camera_to_ego = np.array(
                [
                    [math.cos(yaw), -math.sin(yaw), 0],
                    [math.sin(yaw), math.cos(yaw), 0],
                    [0, 0, 1],
                ]
            )

            # Inverse transformation
            point_camera = point_world @ rotation_camera_to_ego.T

            # Transform the addressing point from ego frame to camera frame
            # rotation_camera_to_ego = Quaternion(
            #     sensor_calibration["rotation"]
            # ).rotation_matrix
            # translation_camera_to_ego = np.array(sensor_calibration["translation"])

            # Inverse transformation
            # point_camera = np.dot(
            #     np.linalg.inv(rotation_camera_to_ego),
            #     point_ego - translation_camera_to_ego,
            # )

            distance = math.sqrt(
                point_camera[0] ** 2 + point_camera[1] ** 2 + point_camera[2] ** 2
            )

            if distance < 70:
                camera_addressing_points_dict[key] = (
                    f"{point_camera[0]}_{-point_camera[1]}_{point_camera[2]}_{id}"
                )

    return camera_addressing_points_dict


@app.get("/get_geo_addressing_points")
async def get_addressing_points():
    addressing_points_path = f"./addressing_points.json"
    addressing_points = {}
    if os.path.exists(addressing_points_path):
        with open(addressing_points_path, "r") as f:
            addressing_points = json.load(f)
    geo_list = []
    for key, value in addressing_points.items():
        geo_list.append(key)
    return geo_list


@app.get("/delete_addressing_point")
async def delete_addressing_point(geo_location: str):
    addressing_points_path = f"./addressing_points.json"
    addressing_points = {}
    if os.path.exists(addressing_points_path):
        with open(addressing_points_path, "r") as f:
            addressing_points = json.load(f)
    if geo_location in addressing_points:
        del addressing_points[geo_location]

        # save the addressing points
        with open(addressing_points_path, "w") as f:
            json.dump(addressing_points, f)
        return addressing_points
    else:
        return {"error": "Addressing point not found"}


@app.get("/delete_all_addressing_points")
async def delete_all_addressing_point():
    addressing_points_path = f"./addressing_points.json"
    addressing_points = {}
    if os.path.exists(addressing_points_path):
        with open(addressing_points_path, "r") as f:
            addressing_points = json.load(f)
    addressing_points.clear()

    # save the addressing points
    with open(addressing_points_path, "w") as f:
        json.dump(addressing_points, f)


if __name__ == "__main__":
    unicorn.run(app, port=8000, reload=True)
