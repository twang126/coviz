import time
from utils import processing_utils
from utils import api_utils
from utils.covid_dataset import CovidData


class Data:
    def __init__(self):
        self.world_df = None
        self.raw_global_df = None
        self.international_df = None
        self.international_states_df = None
        self.us_testing_df = None
        self.us_states_testing_df = None
        self.us_county_df = None
        self.CovidDf = None
        self.last_update = None

        self.set_up()

    def should_update(self):
        curr_time = time.time()

        if self.last_update is None or curr_time >= self.last_update + 3600:
            print("Please update data.")
            return True

        return False

    def set_up(self):
        # The international COVID dataset, aggregated per country and state
        # Source: Kaggle
        print("Setting up data")
        self.last_update = time.time()
        self.raw_global_df = api_utils.get_international_dataset()

        self.world_df = processing_utils.create_world_df(self.raw_global_df.copy())

        print("Finished world data")

        self.international_df = processing_utils.post_process_international_df(
            self.raw_global_df.copy()
        )

        self.international_states_df = processing_utils.post_process_international_states_df(
            self.raw_global_df.copy(), self.international_df.copy()
        )

        print("Finished international df")

        # US testing dataset
        # Source: https://covidtracking.com/api/
        try:
            self.us_testing_df = processing_utils.post_process_us_testing_df(
                api_utils.get_historical_us_testing_data()
            )
        except Exception as e:
            print("US-wide Experimental failed")
            print(e)

            self.us_testing_df = processing_utils.stable_post_process_us_testing_df(
                api_utils.get_historical_us_testing_data()
            )

        try:
            self.us_states_testing_df = processing_utils.post_process_state_testing_df(
                api_utils.get_historical_states_testing_data()
            )
        except Exception as e:
            print("State-wide Experimental failed")
            print(e)
            self.us_states_testing_df = processing_utils.stable_post_process_state_testing_df(
                api_utils.get_historical_states_testing_data()
            )

        print("Finished US and states DF")

        # (
        #     county_deaths,
        #     county_confirmed,
        # ) = api_utils.get_johns_hopkins_county_level_data()
        # self.us_county_df = processing_utils.post_process_county_df_jhu(
        #     county_deaths, county_confirmed
        # )

        # Covid data per US county
        # Source: NY Times
        self.us_county_df = processing_utils.post_process_county_df(
            api_utils.get_historical_county_level_data()
        )

        print("Finished county df")

        # Wrapper class for all of the different data sources
        self.CovidDf = CovidData(
            [
                self.world_df,
                self.international_df,
                self.international_states_df,
                self.us_testing_df,
                self.us_states_testing_df,
                self.us_county_df,
            ]
        )
