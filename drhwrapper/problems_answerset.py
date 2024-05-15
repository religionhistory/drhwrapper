from drhwrapper import DRHWrapper
from datetime import datetime

# test
drh = DRHWrapper("staging.religiondatabase.org/public-api")

# extract entry data ("find_entry" does no preprocessing)
entry_clean = drh.find_entry(775)

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

entry_clean["categories"][1]["groups"][0]["questions"][0]["answer_sets"][0]["answers"][
    0
]["sub_questions"][0]
entry_clean["categories"][1]["groups"][0]["questions"][0]["answer_sets"][0]["answers"][
    0
]["sub_questions"][1]

# I have fixed this here now:
entry_df = drh.dataframe_from_entry_id_list([775])  # still has the issue
entry_answers = drh.extract_answer_information(entry_df)  # this fixes it
entry_answers[
    entry_answers["question_name"].str.contains("Is the cultural contact competitive")
]
