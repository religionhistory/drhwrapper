import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from datetime import datetime
from drhwrapper import DRHWrapper
import requests
import os

drh = DRHWrapper("staging.religiondatabase.org/public-api")

### NB: include this in "demo_analysis.ipynb"

# default
x = drh.get_questionrelations()

# without simplifying
y = drh.get_questionrelations(simplify=False)

# as the json object
z = drh.get_questionrelations(to_dataframe=False)


### getting the answer value
### this also seems to work
df_entries = drh.dataframe_from_entry_id_list([775])
df_answers = drh.extract_answer_information(df_entries)
df_answers[df_answers["answer_name"] == "I don't know"]
