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
];

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
        # Read the binary content of the PNG file directly
        with open(image_path, "rb") as image_file:
            file_data = image_file.read()

        # Return the binary content as a response
        headers = {
            "Content-Type": "application/octet-stream",  # Indicates binary data
            "Content-Disposition": f"attachment; filename={location}.png",
        }

        return Response(content=file_data, headers=headers)

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
