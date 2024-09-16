import os
import sys
import json
from typing import Union
from fastapi import FastAPI
import unicorn
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware
import glob

app = FastAPI()

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
    image_path = f"./data/server_pano_images/{location}.png"
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

    # get file names in the directory
    files = os.listdir("./data/server_pano_images")
    locations = []
    for file in files:
        location = file.split(".png")[0]
        locations.append(location)

    # Return  response
    return locations


if __name__ == "__main__":
    unicorn.run(app, port=8000, reload=True)
