# Overview
Python wrapper for the Database of Religious History (DRH). 
* Main code in `drhwrapper.py`.
* Example analysis in `demo_analysis.ipynb`.
* To test the write API provide your key in `.env` file
* API documentation: https://staging.religiondatabase.org/public-api/v1/doc/

# To-do
1. I have fixed duplication of inconsistent sub-questions in the API. However, this should still be fixed on the API side. This is documented here: 
https://basecamp.com/1771727/projects/11075898/todos/492858628 

2. The answerset does not contain all variables that can be unique for an answer. Missing "Status of Participants", but also information on expert and editor. This is documented here: 
https://basecamp.com/1771727/projects/11075898/todos/492858628

This can also be seen in `problems_answerset.py`

3. The answerset now includes the answer "value" in addition to the answer "name". The `drhwrapper.py` has been updated. Updated this in `demo_read_api.ipynb` but need to update in `demo_analysis.ipynb` as well. 

4. Related question ID endpoint now added and functionality made to extract in useful format. Documented this in `demo_read_api.ipynb` but should use this in `demo_analysis.ipynb` as well.

5. It should be possible to filter entries (e.g., for `list_entries`) by whether they have been published (as it is for other endpoints such as the region and entry tags). This is a bit tricky to do for entries. Entries that are published have at least 1 value that is not 0 for the `Published` column in the table `public.polls_pollprogress`. Issue is documented here: 
https://basecamp.com/1771727/projects/11075898/todos/492858628

6. Still some questions that have not been answered for how to use the write API. Documented here: 
https://basecamp.com/1771727/projects/11075898/todos/492858628

7. Currently the API will give an error if too many answersets are requested. I believe that we cannot easily fix this problem, but I would still like this confirmed. This is documented here: 
https://basecamp.com/1771727/projects/11075898/todos/492858628

8. Figure out how we want to handle keys: currently anyone can make read request which can crash our system. We need a system to handle this. Asked Mike on 2024-05-16. 

9. Consider whether write API functionality should be integrated into same base class as the read API or whether to keep these distinct. They will most likely have different users. 

10. Organize the code and the examples such that this can be turned into a Python package that can be installed through pip. I would prefer to fix most of the problems that we currently have before proceeding with this. 


# Notes

1. Do we have the level of tags (e.g., "Christian Traditions" is level 2) from the API? Looks like we do not. I am not sure how important this is. We do have "parent", but I think "level" might be helpful as well. 

2. Consider transformations (e.g., dates to date-time, regions to geopandas). Either leave to user or have as optional arguments. 