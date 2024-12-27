import os
import sys
import json
from pathlib import Path
from fastapi import FastAPI, Body

# Add the parent directory to the sys.path
sys.path.append(str(Path(__file__).parent.parent))

from modules.cp_contests import get_contests_data
# Load the settings from the settings.json file
with open("settings.json", "r") as file:
    settings = json.load(file)

# Update the environment variables with the settings
os.environ.update(settings)

# Create a FastAPI app
app = FastAPI()

@app.post("/cp-contests")
async def get_contests_deatils(request_body : dict = Body(...)):
    print(f"request body: {request_body}")
    response = await get_contests_data(req_body = request_body)
    return response
