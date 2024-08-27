import unittest
from unittest.mock import patch
import pandas as pd
from drhwrapper import DRHWrapper  # Import your class from your package


class TestDRHWrapper(unittest.TestCase):
    @patch("drhwrapper.api.requests.get")
    def test_get_related_questions(self, mock_get):
        # Setup mock response
        mock_response_data = [
            {"first_question_id": 1, "second_question_id": 2},
            {"first_question_id": 2, "second_question_id": 3},
            {"first_question_id": 3, "second_question_id": 1},
        ]
        mock_get.return_value.json.return_value = mock_response_data

        # Expected DataFrame setup
        expected_data = {
            "question_id": [1, 2, 3],
            "related_question_id": [
                1,
                1,
                1,
            ],  # Assume all are related (simplified example)
        }
        expected_df = pd.DataFrame(expected_data)
        expected_df = expected_df.sort_values(
            by=["related_question_id", "question_id"]
        ).reset_index(drop=True)

        # Create an instance of your class
        instance = DRHWrapper()

        # Invoke the method under test
        result_df = instance.get_related_questions()

        # Assert that the DataFrame is as expected
        pd.testing.assert_frame_equal(result_df, expected_df)

    def test_simplify_logic(self):
        data = {"first_question_id": [1, 1, 2], "second_question_id": [2, 3, 3]}
        input_df = pd.DataFrame(data)
        expected_data = {"question_id": [1, 2, 3], "related_question_id": [1, 1, 1]}
        expected_df = (
            pd.DataFrame(expected_data)
            .sort_values(by=["related_question_id", "question_id"])
            .reset_index(drop=True)
        )
        instance = DRHWrapper()
        result_df = instance.simplify_question_relations(input_df)  # test networkx
        pd.testing.assert_frame_equal(result_df, expected_df)


# Run the tests
if __name__ == "__main__":
    unittest.main()
