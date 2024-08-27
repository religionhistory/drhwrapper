import requests
import requests.packages
from typing import List, Dict, Union
import pandas as pd
from datetime import datetime
import os
from tqdm import tqdm
import numpy as np
import time
import random
import networkx as nx


class DRHWrapper:
    """
    API access to the Database of Religious History (DRH) data.

    This class provides read access to the Database of Religious History (DRH) API.
    """

    def __init__(
        self,
        hostname: str,
        api_key: str = "",
        ver: str = "v1",
        max_retries=10,
        base_delay=1,
        max_delay=120,
    ):
        """
        Initializes the API wrapper
        :param hostname: The hostname of the API
        :param api_key: The API key
        :param ver: The version of the API
        """
        self.base_url = "https://{}/{}".format(hostname, ver)
        self._api_key = api_key
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

    # this is currently needed.
    def retry_api_call(method):
        def wrapper_api_call(self, *args, **kwargs):
            base_delay = self.base_delay
            max_delay = self.max_delay

            last_exception = None
            for attempt in range(self.max_retries):
                try:
                    return method(self, *args, **kwargs)
                except (requests.exceptions.RequestException, ValueError) as e:
                    print(f"Attempt {attempt + 1} failed with error: {e}")
                    last_exception = e

                    # Calculate the next delay
                    delay = min(base_delay * (2**attempt), max_delay)

                    # Optional: add jitter to prevent storming server in lockstep
                    jitter = random.uniform(
                        0, delay * 0.1
                    )  # Jitter of up to 10% of the delay
                    delay_with_jitter = delay + jitter

                    print(f"Retrying in {delay_with_jitter:.2f} seconds...")
                    time.sleep(delay_with_jitter)

            raise last_exception

        return wrapper_api_call

    # utility for list endpoints
    @staticmethod
    def to_comma_separated_string(value: Union[int, str, List[int]]) -> str:
        """Converts a single value or a list of values into a comma-separated string.

        Args:
            value (Union[int, str, List[int]]): values to convert.

        Returns:
            str: comma-separated string.
        """
        if isinstance(value, list):
            # Convert each element to string and join with commas
            return ",".join(map(str, value))
        # If it's a single value, convert it to string directly
        return str(value)

    # utility for list endpoints
    @staticmethod
    def format_date(date_value) -> str:
        """Format date to 'YYYY-MM-DDTHH:MM:SS'.

        Args:
            date_value (datetime, str): date to format.

        Raises:
            ValueError: raise error if date is not in 'YYYY-MM-DD' or 'YYYY-MM-DDTHH:MM:SS' format.

        Returns:
            str: formatted date as string.
        """
        expected_format = "%Y-%m-%dT%H:%M:%S"
        if isinstance(date_value, datetime):
            return date_value.strftime(expected_format)
        elif isinstance(date_value, str):
            # Check if the string is already in the 'YYYY-MM-DDTHH:MM:SS' format
            try:
                # If parsing succeeds, return as is
                datetime.strptime(date_value, expected_format)
                return date_value
            except ValueError:
                # If parsing fails, assume it's 'YYYY-MM-DD' and append time
                try:
                    date_value = datetime.strptime(date_value, "%Y-%m-%d")
                    return date_value.strftime(expected_format)
                except ValueError:
                    # If the date is not in 'YYYY-MM-DD' format either, raise an error
                    raise ValueError(
                        "Date format must be 'YYYY-MM-DD' or 'YYYY-MM-DDTHH:MM:SS'"
                    )
        return date_value

    # list endpoints
    @retry_api_call
    def list_information(self, endpoint: str, available_params: list, **kwargs) -> dict:
        """General method to fetch information, configurable with parameters.

        Args:
            endpoint (str): API endpoint to fetch information from.
            available_params (list): Specific parameters available for the endpoint.
            **kwargs: Additional parameters to filter the information.
                - expert: <list[int] | str> A list of expert IDs or a comma-separated string of expert IDs.
                - poll: <list[int] | str> A list of poll IDs or a comma-separated string of poll IDs.
                - region: <list[int] | str> A list of region IDs or a comma-separated string of region IDs.
                - start_date: <datetime.datetime | str> Dates can be provided as datetime objects or strings. If strings,
                        they should be in 'YYYY-MM-DD' or 'YYYY-MM-DDTHH:MM:SS' format.
                - end_date: <datetime.datetime | str> Dates can be proided as datetime objects or strings. If strings,
                            they should be in 'YYYY-MM-DD' or 'YYYY-MM-DDTHH:MM:SS' format.
                - limit: <int> Number of results to return (default 25).
                - offset: <int> Initial index from which to return.
                - ordering: <str> Field to order by.

        Returns:
            dict: Dictionary containing the API response.
        """

        params = {"limit": 25}  # Default parameters

        for key, value in kwargs.items():
            if value is not None and key in available_params:
                if key in ["expert", "created_by", "region", "poll"]:
                    params[key] = self.to_comma_separated_string(value)
                elif key in ["start_date", "end_date"]:
                    params[key] = self.format_date(value)
                else:
                    params[key] = value

        response = requests.get(
            url=os.path.join(self.base_url, endpoint), params=params
        )
        return response.json()

    def list_entries(self, to_dataframe=True, **kwargs):
        """Fetches entries. This method supports parameters detailed in `list_information`.
        Includes additional parameters:
        - expert: <list[int] | str> A list of expert IDs or a comma-separated string of expert IDs.
        - region: <list[int] | str> A list of region IDs or a comma-separated string of region IDs.
        - poll: <list[int] | str> A list of poll IDs or a comma-separated string of poll IDs.

        Args:
            to_dataframe (bool, optional): Return as pandas dataframe. Defaults to True.

        Returns:
            pd.DataFrame: Dataframe with entries.
        """
        available_params = [
            "expert",
            "start_date",
            "end_date",
            "limit",
            "offset",
            "ordering",
            "region",
            "poll",
        ]
        entry_information = self.list_information("entries", available_params, **kwargs)
        if to_dataframe:
            entry_information = self.list_entries_to_dataframe(entry_information)
        return entry_information

    @staticmethod
    def list_entries_to_dataframe(entry_dictionary: dict) -> pd.DataFrame:
        """Converts entry dictionary to a DataFrame.

        Args:
            entry_dictionary (dict): Dictionary obtained from .list_entries() method.

        Returns:
            pd.DataFrame: Pandas dataframe with entries.
        """
        entry_dictionary_results = entry_dictionary["results"]
        entry_df = pd.DataFrame(entry_dictionary_results)
        entry_df["entry_id"] = entry_df["id"]
        entry_df["entry_name"] = entry_df["name"].apply(lambda x: x["name"])
        entry_df["expert_id"] = entry_df["expert"].apply(lambda x: x["id"])
        entry_df["expert_name"] = entry_df["expert"].apply(
            lambda x: f"{x['first_name']} {x['last_name']}"
        )
        entry_df["poll_id"] = entry_df["poll"].apply(lambda x: x["id"])
        entry_df["poll_name"] = entry_df["poll"].apply(lambda x: x["name"])
        entry_df["region_id"] = entry_df["region"].apply(lambda x: x["id"])
        entry_df["region_name"] = entry_df["region"].apply(lambda x: x["name"])
        entry_df = entry_df[
            [
                "entry_id",
                "entry_name",
                "expert_id",
                "expert_name",
                "poll_id",
                "poll_name",
                "date_created",
                "year_from",
                "year_to",
                "region_id",
                "region_name",
                "tags",
            ]
        ]
        return entry_df

    def list_entry_tags(self, to_dataframe=True, **kwargs):
        """Fetches entry tags. Supports parameters detailed in `list_information`.
        Includes additional parameters:
        - approved: <bool> Whether to fetch only approved tags.
        - created_by: <list[int] | str> A list of user IDs or a comma-separated string of user IDs.

        Args:
            to_dataframe (bool, optional): Return as pandas dataframe. Defaults to True.

        Returns:
            pd.DataFrame: Dataframe with entry tags.
        """
        available_params = [
            "approved",
            "created_by",
            "start_date",
            "end_date",
            "limit",
            "offset",
            "ordering",
        ]
        entry_tags = self.list_information("entry_tags", available_params, **kwargs)
        if to_dataframe:
            entry_tags = self.list_entry_tags_to_dataframe(entry_tags)
        return entry_tags

    @staticmethod
    def list_entry_tags_to_dataframe(entry_tag_dictionary: dict) -> pd.DataFrame:
        """Converts entry tag dictionary to a DataFrame.

        Args:
            entry_tag_dictionary (dict): dictionary obtained from .list_entry_tags() method.

        Returns:
            pd.DataFrame: Dataframe with entry tags.
        """
        entry_tag_dictionary_results = entry_tag_dictionary["results"]
        entry_tag_df = pd.DataFrame(entry_tag_dictionary_results)
        entry_tag_df["entry_tag_id"] = entry_tag_df["id"]
        entry_tag_df["entry_tag_name"] = entry_tag_df["name"]
        entry_tag_df["approved"] = entry_tag_df["approved"]
        entry_tag_df["parent_tag_id"] = entry_tag_df["parent_tag_id"]
        entry_tag_df["created"] = entry_tag_df["created"]
        entry_tag_df["created_by_id"] = entry_tag_df["created_by"].apply(
            lambda x: x["id"]
        )
        entry_tag_df["created_by_username"] = entry_tag_df["created_by"].apply(
            lambda x: x["username"]
        )
        entry_tag_df["created_by_name"] = entry_tag_df["created_by"].apply(
            lambda x: f"{x['first_name']} {x['last_name']}"
        )
        entry_tag_df = entry_tag_df[
            [
                "entry_tag_id",
                "entry_tag_name",
                "approved",
                "parent_tag_id",
                "created",
                "created_by_id",
                "created_by_username",
                "created_by_name",
            ]
        ]
        return entry_tag_df

    def list_regions(self, to_dataframe=True, **kwargs):
        """Fetches regions from the API. Supports parameters detailed in `list_information`.

        Args:
            to_dataframe (bool, optional): Return as pandas dataframe. Defaults to True.

        Returns:
            pd.DataFrame: Dataframe with regions.
        """
        available_params = [
            "created_by",
            "start_date",
            "end_date",
            "limit",
            "offset",
            "ordering",
        ]
        region_information = self.list_information(
            "regions", available_params, **kwargs
        )
        if to_dataframe:
            region_information = self.list_regions_to_dataframe(region_information)
        return region_information

    @staticmethod
    def list_regions_to_dataframe(region_dictionary: dict) -> pd.DataFrame:
        """Converts region dictionary to a DataFrame.

        Args:
            region_dictionary (dict): dictionary obtained from .list_regions() method.

        Returns:
            pd.DataFrame: Dataframe with regions.
        """
        region_dictionary_results = region_dictionary["results"]
        region_df = pd.DataFrame(region_dictionary_results)
        region_df["region_id"] = region_df["id"]
        region_df["region_name"] = region_df["name"]
        region_df["description"] = region_df["description"]
        region_df["created_by_id"] = region_df["created_by"].apply(lambda x: x["id"])
        region_df["created_by_name"] = region_df["created_by"].apply(
            lambda x: f"{x['first_name']} {x['last_name']}"
        )
        region_df["geom"] = region_df["geom"].apply(lambda x: x["coordinates"])
        region_df = region_df[
            [
                "region_id",
                "region_name",
                "description",
                "created_by_id",
                "created_by_name",
                "geom",
                "tags",
            ]
        ]
        return region_df

    def list_region_tags(self, to_dataframe=True, **kwargs):
        """Fetches region tags from the API. Supports parameters detailed in `list_information`.
        Includes additional parameters:
        - approved: <bool> Whether to fetch only approved tags.
        - created_by: <list[int] | str> A list of user IDs or a comma-separated string of user IDs.

        Args:
            to_dataframe (bool, optional): Return as pandas dataframe. Defaults to True.

        Returns:
            pd.DataFrame: Dataframe with region tags.
        """

        available_params = [
            "approved",
            "created_by",
            "start_date",
            "end_date",
            "limit",
            "offset",
            "ordering",
        ]

        region_tags = self.list_information("region_tags", available_params, **kwargs)
        if to_dataframe:
            region_tags = self.list_region_tags_to_dataframe(region_tags)
        return region_tags

    @staticmethod
    def list_region_tags_to_dataframe(region_tag_dictionary: dict) -> pd.DataFrame:
        """Converts region tag dictionary to a DataFrame.

        Args:
            region_tag_dictionary (dict): dictionary obtained from .list_region_tags() method.

        Returns:
            pd.DataFrame: Dataframe with region tags.
        """
        region_tag_dictionary_results = region_tag_dictionary["results"]
        region_tag_df = pd.DataFrame(region_tag_dictionary_results)
        region_tag_df["region_tag_id"] = region_tag_df["id"]
        region_tag_df["region_tag_name"] = region_tag_df["name"]
        region_tag_df["approved"] = region_tag_df["approved"]
        region_tag_df["parent_tag_id"] = region_tag_df["parent_tag_id"]
        region_tag_df["created"] = region_tag_df["created"]
        region_tag_df["created_by_id"] = region_tag_df["created_by"].apply(
            lambda x: x["id"]
        )
        region_tag_df["created_by_username"] = region_tag_df["created_by"].apply(
            lambda x: x["username"]
        )
        region_tag_df["created_by_name"] = region_tag_df["created_by"].apply(
            lambda x: f"{x['first_name']} {x['last_name']}"
        )
        region_tag_df = region_tag_df[
            [
                "region_tag_id",
                "region_tag_name",
                "approved",
                "parent_tag_id",
                "created",
                "created_by_id",
                "created_by_username",
                "created_by_name",
            ]
        ]
        return region_tag_df

    # questionrelation endpoint
    def get_related_questions(self, to_dataframe=True, simplify=True):
        """Get related questions from the API.

        Args:
            to_dataframe (bool, optional): Return as pandas dataframe. Defaults to True.
            simplify (bool, optional):
                All groups of related questions share a common related question ID.
                This is the lowest Question ID within group.
                Defaults to True.

        Returns:
            pd.DataFrame: Dataframe with question ID (primary key) and related question ID.
        """

        response = requests.get(url=os.path.join(self.base_url, "questionrelation"))
        questionrelation_json = response.json()

        # If not to_dataframe we just return
        if not to_dataframe:
            return questionrelation_json

        # If not simplify we return as is (as DataFrame)
        questionrelation_df = pd.DataFrame(questionrelation_json)
        if not simplify:
            return questionrelation_df.sort_values("id")

        # Else we simplify
        questionrelation_df = questionrelation_df.drop(columns="id")
        questionrelation_df = questionrelation_df.rename(
            columns={
                "first_question_id": "question_id",
                "second_question_id": "related_question_id",
            }
        )

        # Build graph
        G = nx.Graph()
        for _, row in questionrelation_df.iterrows():
            G.add_edge(row["question_id"], row["related_question_id"])

        # Find connected components
        connected_components = list(nx.connected_components(G))

        # Create a new DataFrame for the output with the smallest question_id in each component as the related_question_id
        new_labels = []
        for component in connected_components:
            min_question_id = min(
                component
            )  # Find the minimum question_id in the current component
            for question_id in component:
                new_labels.append(
                    {"question_id": question_id, "related_question_id": min_question_id}
                )

        questionrelation_df = pd.DataFrame(new_labels)
        questionrelation_df = questionrelation_df.sort_values(
            by=["related_question_id", "question_id"]
        ).reset_index(drop=True)
        return questionrelation_df

    # find endpoints
    @retry_api_call
    def find_information(self, endpoint: str, id: Union[int, str]) -> Dict:
        """Fetches a single piece of information from the API.

        Args:
            endpoint (str): Specific API endpoint to fetch information from.
            id (Union[int, str]): ID of the information to fetch

        Returns:
            Dict: Dictionary containing the API response.
        """
        response = requests.get(url=os.path.join(self.base_url, endpoint, str(id)))
        return response.json()

    def find_entry(self, entry_id: Union[int, str]) -> Dict:
        """Fetches a single entry from the API.

        Args:
            entry_id (Union[int, str]): The ID of the entry to fetch.

        Returns:
            Dict: Dictionary containing the API response.
        """
        return self.find_information("entries", entry_id)

    def find_entry_tag(self, entry_tag_id: Union[int, str]) -> Dict:
        """Fetches a single entry tag from the API.

        Args:
            entry_tag_id (Union[int, str]): The ID of the entry tag to fetch.

        Returns:
            Dict: Dictionary containing the API response.
        """
        return self.find_information("entry_tags", entry_tag_id)

    def find_region(self, region_id: Union[int, str]) -> Dict:
        """Fetches a single region from the API.

        Args:
            region_id (Union[int, str]): The ID of the region to fetch.

        Returns:
            Dict: Dictionary containing the API response.
        """
        return self.find_information("regions", region_id)

    def find_region_tag(self, region_tag_id: Union[int, str]) -> Dict:
        """Fetches a single region tag from the API.

        Args:
            region_tag_id (Union[int, str]): The ID of the region tag to fetch.

        Returns:
            Dict: Dictionary containing the API response.
        """
        return self.find_information("region_tags", region_tag_id)

    @staticmethod
    def extract_answerset(response_json: dict) -> pd.DataFrame:
        """Extract answerset from a JSON response from the .get_answerset() method.

        Args:
            response_json (dict): API response from the .get_answerset() method.

        Returns:
            pd.DataFrame: Dataframe with answerset information.
        """
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

    @retry_api_call
    def get_answerset(
        self, question_name: str, to_dataframe=True
    ) -> Union[pd.DataFrame, dict]:
        """Extract answerset for a specific question from the API.

        Args:
            question_name (str): name of the question to fetch answerset for.
            to_dataframe (bool, optional): Return as dataframe. Defaults to True.

        Returns:
            Union[pd.DataFrame, dict]: Return as dataframe (if to_dataframe=True) or dictionary.
        """

        response = requests.get(
            url=os.path.join(self.base_url, "entries-by-question"),
            params={"question_name": question_name},
        )
        answerset_json = response.json()

        if to_dataframe:
            answerset_df = self.extract_answerset(answerset_json)
            return answerset_df

        return answerset_df

    # bmethods below are related to the endpoint (find_entry) that does not scale well #
    def dataframe_from_entry_id_list(self, entry_id_list: list) -> pd.DataFrame:
        """Fetches entries from a list of entry IDs and returns them as a DataFrame.
        Unfortunately, the .find_entry() method does not work well for many entries.
        Consider using the .get_answerset() method instead.

        Args:
            entry_id_list (list): list of integer (entry IDs)

        Returns:
            pd.DataFrame: Dataframe with entries from search
        """
        entry_list = []
        for entry_id in tqdm(entry_id_list):
            entry = self.find_entry(entry_id)  # bottleneck
            entry_list.append(entry)
        df = pd.DataFrame(entry_list)

        df = df.rename(columns={"id": "entry_id"})
        df = df.rename(columns={"name": "entry_name"})
        df["entry_name"] = df["entry_name"].apply(lambda x: x["name"])
        return df

    @staticmethod
    def extract_entry_information(df_entries: pd.DataFrame) -> pd.DataFrame:
        """
        Function to extract basic entry information from a DataFrame of entries.
        Dataframe of entries with answersets should be obtained from the .find_entry() method or the .dataframe_from_entry_id_list() method.

        Args:
            df_entries (pd.DataFrame): DataFrame of entries with answersets.

        Returns:
            pd.DataFrame: DataFrame of basic entry (metadata) information.
        """
        df_entries["region_id"] = df_entries["region"].apply(lambda x: x["id"])
        df_entries["region_name"] = df_entries["region"].apply(lambda x: x["name"])
        df_entries["expert_id"] = df_entries["expert"].apply(lambda x: x["id"])
        df_entries["expert_name"] = df_entries["expert"].apply(
            lambda x: f"{x['first_name']} {x['last_name']}"
        )
        df_entries["poll_id"] = df_entries["poll"].apply(lambda x: x["id"])
        df_entries["poll_name"] = df_entries["poll"].apply(lambda x: x["name"])
        df_entries = df_entries[
            [
                "entry_id",
                "entry_name",
                "description",
                "date_created",
                "year_from",
                "year_to",
                "region_id",
                "region_name",
                "expert_id",
                "expert_name",
                "poll_id",
                "poll_name",
            ]
        ].drop_duplicates()
        return df_entries

    # extract region information
    @staticmethod
    def extract_region_information(df_entries: pd.DataFrame) -> pd.DataFrame:
        """Function to extract region information from a DataFrame of entries.
        Dataframe of entries with answersets should be obtained from the .find_entry() method or the .dataframe_from_entry_id_list() method.

        Args:
            df_entries (pd.DataFrame): DataFrame of entries with answersets.

        Returns:
            pd.DataFrame: Dataframe of region information for entries.
        """
        df_entries["region_id"] = df_entries["region"].apply(lambda x: x["id"])
        df_entries["region_name"] = df_entries["region"].apply(lambda x: x["name"])
        df_entries["region_geom"] = df_entries["region"].apply(
            lambda x: x["geojson"]["coordinates"]
        )
        df_entries["region_description"] = df_entries["region"].apply(
            lambda x: x["description"]
        )
        df_entries = df_entries[
            [
                "entry_id",
                "entry_name",
                "region_id",
                "region_name",
                "region_geom",
                "region_description",
            ]
        ]
        return df_entries

    @staticmethod
    def extract_entry_tags(df_entries: pd.DataFrame) -> pd.DataFrame:
        """Function to extract entry tags from a DataFrame of entries.
        Dataframe of entries with answersets should be obtained from the .find_entry() method or the .dataframe_from_entry_id_list() method.

        Args:
            df_entries (pd.DataFrame): Dataframe of entries with answersets.

        Returns:
            pd.DataFrame: Dataframe of entry tags for entries.
        """
        df_entries = df_entries.explode("tags")
        df_entries[["entry_tag_id", "entry_tag_name"]] = df_entries["tags"].apply(
            pd.Series
        )
        df_entries = df_entries[
            ["entry_id", "entry_name", "entry_tag_id", "entry_tag_name"]
        ].drop_duplicates()
        return df_entries

    def extract_answer_information(self, df_entries: pd.DataFrame) -> pd.DataFrame:
        """Extract answer information from a DataFrame of entries.
        Dataframe of entries with answersets should be obtained from the .find_entry() method or the .dataframe_from_entry_id_list() method.

        Args:
            df_entries (pd.DataFrame): Dataframe of entries with answersets.

        Returns:
            pd.DataFrame: Dataframe of answers for entries.
        """
        information = []
        # loop over entries (rows)
        for _, row in df_entries.iterrows():
            entry_id = row["entry_id"]
            entry_name = row["entry_name"]
            question_sets = row["categories"]
            # loop over question sets
            for question_set in question_sets:
                question_set_id = question_set["id"]  # overall category
                question_set_name = question_set["name"]  # overall category name
                questions = question_set["questions"]
                if questions:
                    answers = self.extract_answers(
                        questions,
                        entry_id,
                        entry_name,
                        question_set_id,
                        question_set_name,
                        question_group_id=np.nan,
                        question_group_name=np.nan,
                    )
                    information.append(answers)
                else:
                    questions_groups = question_set["groups"]
                    for questions_group in questions_groups:
                        questions_group_i = questions_group["questions"]
                        question_group_id = questions_group["id"]
                        question_group_name = questions_group["name"]
                        answers = self.extract_answers(
                            questions_group_i,
                            entry_id,
                            entry_name,
                            question_set_id,
                            question_set_name,
                            question_group_id=question_group_id,
                            question_group_name=question_group_name,
                        )
                        information.append(answers)

        # flatten list
        information = [item for sublist in information for item in sublist]

        # gather dataframe
        df = pd.DataFrame(
            information,
            columns=[
                "entry_id",
                "entry_name",
                "question_set_id",
                "question_set_name",
                "question_group_id",
                "question_group_name",
                "question_id",
                "question_name",
                "parent_question_id",
                "answer_set_id",
                "answer_set_year_from",
                "answer_set_year_to",
                "answer_set_region_id",
                "answer_set_expert_id",
                "answer_set_status_of_participants_value",
                "answer_set_status_of_participants_name",
                "answer_id",
                "answer_name",
                "answer_value",
                "answer_text",
                "notes",
            ],
        )

        # fix introduction of <NA> values
        df["parent_question_id"] = df["parent_question_id"].astype("Int64")
        df["question_group_id"] = df["question_group_id"].astype("Int64")

        return df

    @staticmethod
    def extract_answers(
        answer_dictionary,
        entry_id,
        entry_name,
        question_set_id,
        question_set_name,
        question_group_id,
        question_group_name,
    ):
        """
        Helper function for "extract_answer_information". Extracts answers from a dictionary of questions.
        """
        information = []
        recode_complexity = {
            0: "Elite",
            1: "Religious Specialists",
            2: "Non-elite (common people, general populace)",
        }

        def extract_question_data(question, contextual_data, parent_question_id=None):
            question_id = question["id"]
            question_name = question["name"]
            answer_sets = question["answer_sets"]

            for answer_set in answer_sets:
                answer_set_id = answer_set["id"]
                answer_set_year_from = answer_set["year_from"]
                answer_set_year_to = answer_set["year_to"]
                answer_set_region_id = answer_set["region_id"]
                answer_set_expert_id = answer_set["expert_id"]
                answer_set_status_participants_value = answer_set[
                    "status_of_participants"
                ]
                answer_set_status_participants_name = [
                    recode_complexity[x] for x in answer_set_status_participants_value
                ]
                answers = answer_set["answers"]
                notes = answer_set["notes"]

                for answer in answers:
                    answer_id = answer["id"]
                    answer_name = answer["name"]
                    answer_value = answer["value"]
                    answer_text = answer["text_input"]
                    answer_sub_questions = answer["sub_questions"]

                    # Compile all relevant information for this answer
                    current_data = [
                        entry_id,
                        entry_name,
                        question_set_id,
                        question_set_name,
                        question_group_id,
                        question_group_name,
                        question_id,
                        question_name,
                        parent_question_id,
                        answer_set_id,
                        answer_set_year_from,
                        answer_set_year_to,
                        answer_set_region_id,
                        answer_set_expert_id,
                        answer_set_status_participants_value,
                        answer_set_status_participants_name,
                        answer_id,
                        answer_name,
                        answer_value,
                        answer_text,
                        notes,
                    ]

                    # Add this answer's data to the overall information
                    information.append(current_data)

                    # This fixes a problem with duplication that we should not actually have
                    seen_ids = set()
                    unique_sub_questions = []
                    for sub_question in answer_sub_questions:
                        if sub_question["id"] not in seen_ids:
                            seen_ids.add(sub_question["id"])
                            unique_sub_questions.append(sub_question)

                    # Recursively handle sub-questions, if any, passing current question ID as the parent ID
                    for sub_question in unique_sub_questions:
                        extract_question_data(
                            sub_question, contextual_data, question_id
                        )

        # Initial contextual data for top-level questions
        contextual_data = [
            entry_id,
            entry_name,
            question_set_id,
            question_set_name,
            question_group_id,
            question_group_name,
        ]

        # Start processing each top-level question
        for question in answer_dictionary:
            extract_question_data(question, contextual_data)

        return information
