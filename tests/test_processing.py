import unittest

import pandas as pd
from utils.covid_dataset import CovidData
from utils import processing_utils

dummy_confirmed_data = {
    processing_utils.DATE_COL: [
        "2020-03-01",
        "2020-03-02",
        "2020-03-03",
        "2020-03-01",
        "2020-03-04",
    ],
    processing_utils.COUNTRY_COL: ["US", "US", "China", "Canada", "China"],
    processing_utils.CONFIRMED_COL: [10, 12, 4, 9, 16],
}

dummy_deaths_data = {
    processing_utils.DATE_COL: [
        "2020-03-01",
        "2020-03-02",
        "2020-03-03",
        "2020-03-01",
        "2020-03-04",
    ],
    processing_utils.COUNTRY_COL: ["US", "US", "China", "Canada", "China"],
    processing_utils.DEATHS_COL: [4, 5, 19, 10, 18],
}

dummy_confirmed_states_data = {
    processing_utils.DATE_COL: [
        "2020-03-01",
        "2020-03-02",
        "2020-03-03",
        "2020-03-01",
        "2020-03-04",
    ],
    processing_utils.STATE_COL: [
        "Maryland",
        "Maryland",
        "Alaska",
        "Alaska",
        "New York",
    ],
    processing_utils.CONFIRMED_COL: [10, 12, 4, 9, 16],
}


class ProcessingUtilsTestCase(unittest.TestCase):
    def setUp(self):
        self.dfs = [
            pd.DataFrame.from_dict(dummy_confirmed_data),
            pd.DataFrame.from_dict(dummy_deaths_data),
            pd.DataFrame.from_dict(dummy_confirmed_states_data),
        ]

    def test_no_filter(self):
        CovidDf = CovidData(self.dfs)

        filtered_dfs = CovidDf.get_scaled_dataframes(
            threshold_value=9,
            threshold_metric=processing_utils.CONFIRMED_COL,
            filter_dict={
                processing_utils.COUNTRY_COL: ["US", "China", "Canada"],
                processing_utils.STATE_COL: ["Maryland", "Alaska", "New York"],
            },
        )

        for i, df in enumerate(filtered_dfs):
            print("Original: ------------")
            print(self.dfs[i])
            print("New: ----------")
            print(df.head())
