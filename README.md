# Overview
Python wrapper for the Database of Religious History (DRH). 
* Main code in `drhwrapper.py`.
* Example analysis in `demo_analysis.ipynb`.
* To test the write API provide your key in `.env` file
* API documentation: https://staging.religiondatabase.org/public-api/v1/doc/

# Setup
`conda env create -f environment.yml` </br>
`conda activate drhwrapper`

# Known Issues
1. There are duplicated answersets returned from the API (for inconsistent sub-questions). This is fixed on the wrapper side but should be resolved on the API side. See: 
https://basecamp.com/1771727/projects/11075898/todos/492858628 

2. The answerset does not contain all variables that can be unique for an answer. Missing "Status of Participants", but also information on expert and editor. This is documented here: 
https://basecamp.com/1771727/projects/11075898/todos/492858628

This can also be seen in `problems_answerset.py`

3. It should be possible to filter entries (e.g., for `list_entries` method) by whether they have been published (as it is for other endpoints such as the region and entry tags). This is a bit tricky to do for entries. Entries that are published have at least 1 value that is not 0 for the `Published` column in the table `public.polls_pollprogress`. Issue is documented here: 
https://basecamp.com/1771727/projects/11075898/todos/492858628

4. Still some questions that have not been answered for how to use the write API. Documented here: 
https://basecamp.com/1771727/projects/11075898/todos/492858628

5. Currently the API will give an error if too many answersets are requested. I believe that we cannot easily fix this problem, but I would still like this confirmed. This is documented here: 
https://basecamp.com/1771727/projects/11075898/todos/492858628

6. Figure out how we want to handle keys: currently anyone can make read request which can crash our system. We need a system to handle this. Documented here: 
https://basecamp.com/1771727/projects/11075898/todos/495175996

