import requests
import requests.packages
from typing import List, Dict, Union


class DRHWrite:

    def __init__(
        self,
        hostname: str,
        api_key: str,
        ver: str = "v1",
    ):
        """
        Initializes the API wrapper
        :param hostname: The hostname of the API
        :param api_key: The API key
        :param ver: The version of the API
        """
        self.base_url = "https://{}/{}".format(hostname, ver)
        self._api_key = api_key

    # needs to be tested
    def add_entry(self, data: Dict[str, Union[int, str]]) -> requests.Response:
        """Add a new entry to the database.

        Args:
            data (Dict[str, Union[int, str]]):
                * poll_id (int): Required poll identifier.
                * region_id (int): Required region identifier.
                * secondary_source_id (int): Required secondary source identifier.
                * name (str): Name of the entry.
                * description (str): Required description of the entry.
                * external_url (str <uri>): Required url/uri of the entry.
                * year_from (int): Required starting year of the entry.
                * year_to (int): Required ending year of the entry.
                * tags (List[int]): Optional list of entry tags.
                * data_source_id (int): Optional data source identifier.
                * entry_source (str): Optional source of the entry, values can be "personal_expertise",
                "secondary_source", "expert_source", "supervised_entry".
                * expert_source_id (int): Optional expert source identifier.
                * supervised_by_id (int): Optional supervised by identifier.

        Returns:
            requests.Response: The response from the API.
        """
        url = f"{self.base_url}/entries/"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {self._api_key}",
        }
        response = requests.post(url=url, headers=headers, json=data)
        return response

    # needs to be tested
    # branch_id does not work as expected (waiting on Navid)
    # year_from and year_to do not work as expected (waiting on Navid)
    def add_answer(
        self, entry_id, data: Dict[str, Union[int, str]]
    ) -> requests.Response:
        """Add a new answer to existing entry in the database.

        Args:
            entry_id (int): The entry identifier.
            data (Dict[str, Union[int, str]]):
                * question_id (int): Required question identifier.
                * region_id (int): Optional region identifier.
                * notes (str): Optional notes for the answer.
                * answers (List[Dict[str, Union[int, str]]]):
                    * template_answer_id (int): Required template answer identifier.
                    * tooltip (str): Optional tooltip for the answer.
                    * text_input (str): Optional text input for the answer.
                * branch_ids (List[int]): Optional list of branch identifiers.
                * year_from (int): Optional starting year of the answer.
                * year_to (int): Optional ending year of the answer.

        Returns:
            requests.Response: The response from the API.
        """
        url = f"{self.base_url}/entries/{entry_id}/answersets/"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {self._api_key}",
        }
        response = requests.post(url=url, headers=headers, json=data)
        return response

    def add_entry_tag(self, data: Dict[str, Union[int, str]]) -> requests.Response:
        """Add a new entry tag to the database.

        Args:
            data (Dict[str, Union[int, str]]):
                * name (str): Required name of entry tag (<= 140 characters).
                * parent_tag_id (int): Optional parent tag identifier.

        Returns:
            requests.Response: The response from the API.
        """
        url = f"{self.base_url}/entry_tags/"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {self._api_key}",
        }
        response = requests.post(url=url, headers=headers, json=data)
        return response

    def add_region_tag(self, data: Dict[str, Union[int, str]]) -> requests.Response:
        """Add a new region tag to the database.

        Args:
            data (Dict[str, Union[int, str]]):
                * name (str): Required name of region tag (<= 140 characters).
                * parent_tag_id (int): Optional parent tag identifier.

        Returns:
            requests.Response: The response from the API
        """
        url = f"{self.base_url}/region_tags/"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {self._api_key}",
        }
        response = requests.post(url=url, headers=headers, json=data)
        return response

    def add_region(self, data: Dict[str, Union[int, str]]) -> requests.Response:
        """Add a new region to the database.

        Args:
            data (Dict[str, Union[int, str]]):
                * name (str): Optional name of the region (<= 140 characters).
                * description (str): Optional description of the region.
                * additional_info (str): Optional additional information about the region.
                * geom (List[float]):
                    * type (str): "MultiPolygon"
                    * coordinates (List[float]): Required geometry [[[[x1, y1], [x2, y2], ...]]].
                * tags (List[int]): Optional list of region tags.

        Returns:
            requests.Response: The response from the API.
        """
        url = f"{self.base_url}/regions/"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {self._api_key}",
        }
        response = requests.post(url=url, headers=headers, json=data)
        return response
