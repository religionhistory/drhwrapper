from drhwrapper import DRHWrapper
from datetime import datetime

drh = DRHWrapper("staging.religiondatabase.org/public-api")

### problems answerset ###

"""
The two calls below should give distinct sub-questions.
They give the same sub-question however, which is a problem (this should never happen).

Note: 
We also have the problem that we do not get all the information that we need for answersets. 
1. branching question (status of participants).
2. expert id
3. editor id 

Note: 
We also have the problem that we are only getting answer "name" and not "value".
"""

entry_775 = drh.find_entry(775)
entry_775["categories"][1]["groups"][0]["questions"][0]["answer_sets"][0]["answers"][0][
    "sub_questions"
][0]
entry_775["categories"][1]["groups"][0]["questions"][0]["answer_sets"][0]["answers"][0][
    "sub_questions"
][1]

# I have fixed this here now:
entry_df = drh.dataframe_from_entry_id_list([775])  # still has the issue
entry_answers = drh.extract_answer_information(entry_df)  # this fixes it
entry_answers[
    entry_answers["question_name"].str.contains("Is the cultural contact competitive")
]

# another problem (expert for "Expert Source" entries (e.g. 23))
entry_information = drh.find_entry(23)
entry_information["expert"]  # not correct

# test new functionality
entry_df = drh.dataframe_from_entry_id_list([775])
answerset = drh.extract_answer_information(entry_df)
answerset[
    [
        "answer_set_year_to",
        "answer_set_region_id",
        "answer_set_status_of_participants_value",
        "answer_set_status_of_participants_name",
        "answer_set_expert_id",
    ]
]

# need to consider whether this should be a list or a string
# also need to check this in cases where we have different values.
