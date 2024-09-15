import os
import sys
import json
from typing import Union
from fastapi import FastAPI
import unicorn
from fastapi.responses import FileResponse

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.get("/image")
async def get_image():
    # Path to the image
    image_path = "./data/pano/zzrdBgRfm_S1ov6yLScyjw.jpg"

    # Check if the file exists
    if os.path.exists(image_path):
        return FileResponse(image_path, media_type="image/jpeg")
    else:
        return {"error": "Image not found"}


if __name__ == "__main__":
    unicorn.run(app, port=8000, reload=True)
