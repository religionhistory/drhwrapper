"""
Testing write API. 
Mostly this works, but see REAEDME.md. 
There are still some unresolved questions.
The main discussion thread is here: 
https://basecamp.com/1771727/projects/11075898/todos/492858628
"""

import requests
import requests.packages
from typing import List, Dict
import pandas as pd
from drhwrapper import DRHWrapper
from dotenv import load_dotenv
import os
import json
import shapely
import logging
import geopandas as gpd

# trying write endpoints
n = 4
load_dotenv("../.env")
api_key = os.getenv("API_KEY")
url = "https://staging.religiondatabase.org/public-api/v1/entries/"

# construct headers
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Api-Key {api_key}",
}


logging.basicConfig(filename="add_region_error.log", level=logging.ERROR)


def logging_call(url, headers, data):
    try:
        response = requests.post(url=url, headers=headers, json=data)
        if response.status_code == 200 or response.status_code == 201:
            return response
        else:
            logging.error(response.status_code)
            logging.error(response.text)
    except ValueError as e:
        # This block catches JSON decoding errors
        logging.error(response.text)
    except Exception as e:
        # This block catches any other exceptions
        print(f"other error")


# find information to even make the request
drh = DRHWrapper("staging.religiondatabase.org/public-api")

### 1. Add a new entry ### (works except "entry_source")
data = {
    # required arguments
    "poll_id": 35,  # Religious Group (v5)
    "region_id": 7,  # Middle and Lower Yellow River Valley
    "secondary_source_id": 2,  # multiple references
    "name": f"Test entry by Victor Poulsen (name) -{n}",
    "description": f"Test entry by Victor Poulsen (description) -{n}",
    "external_url": "https://victorpoulsen.com",
    "year_from": -2000,  # testing negative here
    "year_to": 2000,  # testing positive here
    # optional arguments
    "tags": [8, 123],  # [8, 123],  # religious group, chinese religion
    "data_source_id": 1,  # database of religious history
    "entry_source": f"Test entry 2 by Victor Poulsen (source) -{n}",  # this gives an error
    "expert_source_id": 93,  # David Keightley
    "supervised_by_id": 93,  # David Keightley
}
response = logging_call(url=url, headers=headers, data=data)

### 2. Add a new answer ###
# find an entry that is already bogus
entry_id = 2238  # on staging this is a bogus entry
entry = drh.find_entry(entry_id=2238)
entry["categories"][2]

url = (
    f"https://staging.religiondatabase.org/public-api/v1/entries/{entry_id}/answersets/"
)

data = {
    # required arguments
    "question_id": 4814,  # Are grave goods present:
    "answers": [
        {
            "template_answer_id": 915,  # Yes
            "tooltip": f"VMP test answer tooltip -{n}",  # hvad er det her tooltip?
            "text_input": f"VMP test answer text input -{n}",
        }
    ],
    # optional arguments
    "region_id": 7,  # Middle and Lower Yellow River Valley
    "notes": f"VMP test notes -{n}",
    # "branch_ids": xxxx,
    "year_from": -2000,  # testing negative here
    "year_to": 2000,  # testing positive here
}

response = logging_call(url=url, headers=headers, data=data)
entry_modified = drh.find_entry(entry_id=2238)
entry_modified["categories"][2]["groups"][0]["questions"][5]  # works

### 3. Add a new entry tag ###
url = "https://staging.religiondatabase.org/public-api/v1/entry_tags/"
data = {
    # required
    "name": "Test entry tag 2 by Victor Poulsen",
    # optional
    "parent_tag_id": 8,  # religious group
}
response = requests.post(url=url, headers=headers, json=data)
response.json()  # created as id=43612 and in the database
drh.find_entry_tag(43612)  # good
drh.find_entry_tag(8)  # good

### 4. add a new region tag (works) ###
region_df = drh.list_regions(to_dataframe=True)
region_df.head(5)
url = "https://staging.religiondatabase.org/public-api/v1/region_tags/"
data = {
    # required
    "name": "Test region tag by Victor Poulsen, Parent Europe",
    # optional
    "parent_tag_id": 3,  # Europe
}
response = requests.post(url=url, headers=headers, json=data)
response.status_code
response.json()  # okay this is done now.
drh.find_region_tag(1154)  # good

### 5. add a new region ###
url = "https://staging.religiondatabase.org/public-api/v1/regions/"

geojson_multipolygon = {
    "type": "MultiPolygon",
    "coordinates": [
        [  # First polygon
            [
                [25.70651273057507, 20.12936899454739],
                [24.32176423177748, 17.261722744599297],
                [27.491512622239952, 16.77415243774415],
                [30.76157694295469, 19.57211004319896],
                [
                    25.70651273057507,
                    20.12936899454739,
                ],  # Closing point same as the starting point
            ]
        ],
        [  # Second polygon
            [
                [31.881646726537753, 18.302173686027928],
                [28.00573118090847, 15.320971606580741],
                [31.491367829995255, 13.258935177635806],
                [33.75422354326557, 16.59398262827223],
                [
                    31.881646726537753,
                    18.302173686027928,
                ],  # Closing point same as the starting point
            ]
        ],
    ],
}

print(json.dumps(geojson_multipolygon, indent=4))  # this is valid

data = {
    # required arguments
    "name": f"Test region by Victor Poulsen -{n}",
    "geom": geojson_multipolygon,
    # optional arguments below
    "description": f"Test region description VMP -{n}",
    "tags": [938, 505],
    "additional_info": f"Test region additional info VMP -{n}",
}

response = logging_call(url=url, headers=headers, data=data)
drh.list_regions(to_dataframe=True, offset=1750)
