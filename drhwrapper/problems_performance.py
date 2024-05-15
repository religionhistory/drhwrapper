"""
vmp 2023-05-14:
shows that too many requests to the API will result in error.
"""

from drhwrapper import DRHWrapper

# initialize
drh = DRHWrapper("staging.religiondatabase.org/public-api")

# get all entries
all_entries = drh.list_entries(to_dataframe=True, limit=1400)
all_entries["entry_id"].nunique()  # n=1392

# filter by poll type
group_polls = all_entries[all_entries["poll_name"].str.contains("Religious Group")][
    ["poll_id", "poll_name"]
].drop_duplicates()
group_entries = all_entries.merge(group_polls, on=["poll_id", "poll_name"], how="inner")
group_entries["entry_id"].nunique()  # n=803
unique_group_entry_IDs = group_entries["entry_id"].unique()

# the call below will fail
group_answer_data = drh.dataframe_from_entry_id_list(unique_group_entry_IDs)
