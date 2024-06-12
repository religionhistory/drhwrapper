"""
vmp 2023-06-12:
testing write API.

problems: 
--> add new answer (branch id, default date range)
"""

from drhwrite import DRHWrite
from dotenv import load_dotenv
import os

# trying write endpoints
n = 6
load_dotenv("../.env")
api_key = os.getenv("API_KEY")

# find information to even make the request
drh = DRHWrite(hostname="staging.religiondatabase.org/public-api", api_key=api_key)

## 1. Add a new entry
data = {
    # required arguments
    "poll_id": 43,  # Religious Group (v6)
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
    "entry_source": f"personal_expertise",  # should be one of ['personal_expertise', 'secondary_source', 'expert_source', 'supervised_entry']"
    "expert_source_id": 93,  # David Keightley
    "supervised_by_id": 93,  # David Keightley
}

drh.add_entry(data)  # <Response [201]>

"""
We cannot load this new entry yet, because it has no questions answered.
"""

## 2. Add a new answer
entry_id = 2263

# try with specific arguments (e.g. dates, region).
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
    "region_id": 467,  # Taken from Warring States (China)
    "notes": f"VMP not specified",
    # "branch_ids": [0, 1, 2],
    "year_from": -2000,  # testing negative here
    "year_to": 2000,  # testing positive here
}

drh.add_answer(entry_id, data)  # <Response [201]>

"""
We can now fetch the entry and see the answer.
This looks correct.
"""

from drhwrapper import DRHWrapper

drhread = DRHWrapper(hostname="staging.religiondatabase.org/public-api")
entry_df = drhread.dataframe_from_entry_id_list([2263])
answer_df = drhread.extract_answer_information(entry_df)
answer_df.head()

## 3. Add a new entry tag
data = {
    # required
    "name": f"Test entry tag -{n} by Victor Poulsen",
    # optional
    "parent_tag_id": 8,  # religious group
}
drh.add_entry_tag(data)  # <Response [201]>

drhread.find_entry_tag(43613)  # good

## 4. add a new region tag
data = {
    # required
    "name": f"Test region tag -{n} by Victor Poulsen, Parent Europe",
    # optional
    "parent_tag_id": 3,  # Europe
}

drh.add_region_tag(data)  # <Response [201]>
drhread.find_region_tag(1156)  # good

## 5. add a new region
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

data = {
    # required arguments
    "name": f"Test region by Victor Poulsen -{n}",
    "geom": geojson_multipolygon,
    # optional arguments below
    "description": f"Test region description VMP -{n}",
    "tags": [938, 505],
    "additional_info": f"Test region additional info VMP -{n}",
}

drh.add_region(data)  # <Response [201]>
drhread.list_regions(to_dataframe=True, offset=1760)  # also works
