"""
vmp 2023-06-12:
shows that too many requests to the API will result in error.
"""

# okay, manually try new endpoint #
import os
import requests
import pandas as pd

#### try with a super-question ####
params = {"question_name": "Is supernatural monitoring present:"}
base_url = "https://staging.religiondatabase.org/public-api/v1"
endpoint = "entries-by-question"
response = requests.get(url=os.path.join(base_url, endpoint), params=params)
response_json = response.json()

## seems unstable (error codes) ##
# error 500
# error 500
# response 200
# error 502
# response 200

# need something that actually builds this document;
response_df = pd.DataFrame(response_json)

# gather all of the information into a dataframe
information = []
for json_entry in response_json:
    entry_id = json_entry["id"]
    entry_name = json_entry["title"]
    date_created = json_entry["date_created"]
    poll_id = json_entry["poll"]["id"]
    poll_name = json_entry["poll"]["name"]
    for answer in json_entry["answers"]:
        answer_name = answer["name"]
        answer_value = answer["value"]
        answer_text = answer["text_input"]
        year_from = answer["year_from"]
        year_to = answer["year_to"]
        expert_id = answer["expert"]["expert_id"]
        expert_name = (
            answer["expert"]["first_name"] + " " + answer["expert"]["last_name"]
        )
        region_id = answer["region_id"]
        status_participants = answer["status_of_participants"]["name"]
        information.append(
            [
                entry_id,
                entry_name,
                date_created,
                poll_id,
                poll_name,
                answer_name,
                answer_value,
                answer_text,
                year_from,
                year_to,
                expert_id,
                expert_name,
                region_id,
                status_participants,
            ]
        )
df = pd.DataFrame(
    information,
    columns=[
        "entry_id",
        "entry_name",
        "date_created",
        "poll_id",
        "poll_name",
        "answer_name",
        "answer_value",
        "answer_text",
        "year_from",
        "year_to",
        "expert_id",
        "expert_name",
        "region_id",
        "status_participants",
    ],
)

# so now we do have some cases with multiple answers
# look into these cases
# also compare with the data dump potentially
len(df)
df["entry_id"].nunique()
duplication = (
    df.groupby("entry_id")
    .size()
    .reset_index(name="count")
    .sort_values("count", ascending=False)
)
duplication = duplication[duplication["count"] > 1]
duplication
df[df["entry_id"] == 929]  # good

""" tested 
176 (good) -- but all yes
342 (good) -- but all yes 
1381 (staging)
570 -- maybe good -- both yes but 2 different experts (one should be history maybe?)
416 (good) -- yes and don't know
929 ()
"""

"""
Check how this works with a sub-question;
can we actually infer what we need in that case? 
Also try to build up a workflow analysis for this. 
"""


# convert to dataframe
def convert_dataframe(response_json):
    df = pd.DataFrame(response_json)
    df = df.rename(
        columns={
            "id": "entry_id",
            "title": "entry_name",
            "region": "region_id",
        }
    )
    df["poll_id"] = df["poll"].apply(lambda x: x["id"])
    df["poll_name"] = df["poll"].apply(lambda x: x["name"])
    df["answer_name"] = df["answers"].apply(
        lambda x: x[0]["name"] if len(x) > 0 else None
    )
    df["answer_value"] = df["answers"].apply(
        lambda x: x[0]["value"] if len(x) > 0 else None
    )
    return df


# maybe we do have to loop over records:
def extract_dataframe(response_json):
    information = []
    for json_entry in response_json:
        entry_id = json_entry["id"]
        entry_name = json_entry["title"]
        date_created = json_entry["date_created"]
        poll_id = json_entry["poll"]["id"]
        poll_name = json_entry["poll"]["name"]
        question_id = json_entry["question_id"]
        for answer in json_entry["answers"]:
            answer_name = answer["name"]
            answer_value = answer["value"]
            answer_text = answer["text_input"]
            year_from = answer["year_from"]
            year_to = answer["year_to"]
            expert_id = answer["expert"]["expert_id"]
            expert_name = (
                answer["expert"]["first_name"] + " " + answer["expert"]["last_name"]
            )
            region_id = answer["region_id"]
            status_participants = answer["status_of_participants"]["name"]
            information.append(
                [
                    entry_id,
                    entry_name,
                    poll_id,
                    poll_name,
                    question_id,
                    answer_name,
                    answer_value,
                    answer_text,
                    year_from,
                    year_to,
                    region_id,
                    status_participants,
                    expert_id,
                    expert_name,
                    date_created,
                ]
            )
    df = pd.DataFrame(
        information,
        columns=[
            "entry_id",
            "entry_name",
            "poll_id",
            "poll_name",
            "question_id",
            "answer_name",
            "answer_value",
            "answer_text",
            "year_from",
            "year_to",
            "region_id",
            "status_participants",
            "expert_id",
            "expert_name",
            "date_created",
        ],
    )
    return df


df2 = extract_dataframe(response_json)
df2

df = convert_dataframe(response_json)
df["answers"][0]

# how many do we have here?
len(df)  # 1100 (so has to be more than just groups)

# now test whether this works as expected.
df.groupby("answer_name", dropna=False).size()
df[df["answer_name"].isnull()]  # poll not answswered so that makes sense.

# okay so they all have count = 1 which is a bit weird
# there should be some that are inconsistent I feel.
df.groupby("entry_id").size().reset_index(name="count").sort_values("count")
df.groupby(
    "poll_id"
).size()  # 35, 43, 44, 45, 50 (might be better to have the poll name).

# try to figure out why this is the case.
answerset = pd.read_csv("../../drh-sosis-replication/data/raw/answerset.csv")
answerset_monitoring = answerset[
    answerset["question_name"] == "Is supernatural monitoring present:"
]
len(answerset_monitoring)  # 1175 (so longer than 1100)

""" to-do 
Figure out whether it makes sense not to have the poll name and the entry name.
i.e., how natural is this to merge on other objects?
Also would be really nice to have the question ID. 

* We definitely need branching questions (Elite, Religious Specialist, etc.)
* We definitely need expert ID (and/or name). 
"""

# figure out why we have less observations
answerset_monitoring_branching = answerset_monitoring[
    [
        "question_id",
        "question_name",
        "answer",
        "answer_value",
        "entry_id",
        "entry_name",
        "region_id",
        "year_from",
        "year_to",
        "poll_id",
        "expert_id",
        "date_modified",  # this gives a couple of extra ones but they are not useful
        "date_created",  # this gives a couple of extra ones but they are not useful
        "branching_question",
    ]
].drop_duplicates()
len(answerset_monitoring_branching)  # 1172

# 1172 instead of 1175 because of date modified and date created.
# these are probably not useful but double check this.
answerset_monitoring.groupby(["entry_id", "date_modified"]).size().reset_index(
    name="count"
).sort_values("count", ascending=False)
# 2013, 929, 739

answerset_monitoring[answerset_monitoring["entry_id"] == 2013]  # no, no
answerset_monitoring[answerset_monitoring["entry_id"] == 929]  # no, yes
answerset_monitoring[answerset_monitoring["entry_id"] == 739]  # doesnt know, yes

df[df["entry_id"] == 2013]["answers"][
    990
]  # has no, no (both there and correct: but should be removed)
df[df["entry_id"] == 929]["answers"][420]  # yes, no (both there and correct)
df[df["entry_id"] == 739]["answers"][
    289
]  # yes, field doesnt know (both there and correct)

"""
We probably do not need the date columns.
But we need to be careful to actually process this. 
So first we would blow up the data based on the branching questions. 
And then we would need to check for additional inconsistencies. 
"""


# check other questions that branch answers
def find_inconsistency(df, column):
    df_sub = df[["entry_id", column]].drop_duplicates()
    return (
        df_sub.groupby("entry_id")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )


branching = find_inconsistency(answerset_monitoring_branching, "branching_question")
branching  # a lot of inconsistency here.
expert_id = find_inconsistency(answerset_monitoring_branching, "expert_id")
expert_id  # correct 1805 has inconsistency
year_from = find_inconsistency(answerset_monitoring_branching, "year_from")
year_from  # no inconsistency here.
year_to = find_inconsistency(answerset_monitoring_branching, "year_to")
year_to  # no inconsistency here.
region_id = find_inconsistency(answerset_monitoring_branching, "region_id")
region_id  # no inconsistency here.

df[df["entry_id"] == 176]["answers"][3]

""" things so far: 
# weird columns
- name column? what does this correspond to? this is not the entry name.

# things that we need 
- branching_question 
- expert_id and expert name (at least one)

# additional columns that would be nice but are not necessary
- question ID
- poll name 
"""

### try a sub-question ###
params = {
    "question_name": "There is supernatural monitoring of prosocial norm adherence in particular:"
}
base_url = "https://staging.religiondatabase.org/public-api/v1"
endpoint = "entries-by-question"
response = requests.get(url=os.path.join(base_url, endpoint), params=params)

response_json = response.json()

df_sub = convert_dataframe(response_json)

len(df[df["answer_value"] == 1])  # 645 have this but only 450
df_sub_polls = df_sub[df_sub["poll_id"].isin([35, 43])]
len(df_sub_polls)

"""
450 so now it matches n yes answers. 
Meaning that for sub-questions you only get the ones where parent is "Yes".
This makes sense as well. 
"""

# find something where we have inconsistency in year or region
answerset_test = answerset[
    ["entry_id", "question_name", "region_id", "answer_value"]
].drop_duplicates()
grouped_answers = (
    answerset_test.groupby(["entry_id", "question_name"])
    .size()
    .reset_index(name="count")
    .sort_values("count", ascending=False)
)
grouped_answers = grouped_answers[grouped_answers["count"] == 2]
grouped_answers.head(20)
test = answerset.groupby(["entry_id", "region_id"]).size().reset_index(name="count")
test.groupby("entry_id").size().reset_index(name="count").sort_values(
    "count", ascending=False
)

# 1324
answers_test = answerset[answerset["entry_id"] == 1324]
answers_test = answers_test[answers_test["answer"].isin(["Yes", "No"])]
answers_region = answers_test[
    answers_test["region_id"] != 1132
]  # one thing to check is whether we do have different regions here for each answer
answers_region[answers_region["question_id"] == 7690]["region_id"]

# test this immmediately
params = {"question_name": "Inspired by high god?"}
base_url = "https://staging.religiondatabase.org/public-api/v1"
endpoint = "entries-by-question"
response = requests.get(url=os.path.join(base_url, endpoint), params=params)

response_json = response.json()

df_region = convert_dataframe(response_json)
df_region.groupby(["entry_id", "region_id"]).size().reset_index(
    name="count"
).sort_values("count", ascending=False)
df_region[df_region["entry_id"] == 1324]  # 1132 is not correct; that is for the entry.
