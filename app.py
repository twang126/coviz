import json

from flask import Flask
from flask import render_template
from flask import request
from flask import Response

from utils import api_utils
from utils import processing_utils
from utils.covid_dataset import CovidData

import time

app = Flask(__name__)


class Data:
    def __init__(self):
        self.raw_global_df = None
        self.international_df = None
        self.international_states_df = None
        self.us_testing_df = None
        self.us_states_testing_df = None
        self.us_county_df = None
        self.CovidDf = None
        self.last_update = None

        self.set_up()

    def set_up(self):
        # The international COVID dataset, aggregated per country and state
        # Source: Kaggle
        print("Set up data")
        self.last_update = time.time()
        self.raw_global_df = api_utils.get_international_dataset()
        self.international_df = processing_utils.post_process_international_df(
            self.raw_global_df
        )

        self.international_states_df = processing_utils.post_process_international_states_df(
            self.raw_global_df
        )

        # US testing dataset
        # Source: https://covidtracking.com/api/
        self.us_testing_df = processing_utils.post_process_us_testing_df(
            api_utils.get_historical_us_testing_data()
        )
        self.us_states_testing_df = processing_utils.post_process_state_testing_df(
            api_utils.get_historical_states_testing_data()
        )

        # Covid data per US county
        # Source: NY Times
        self.us_county_df = processing_utils.post_process_county_df(
            api_utils.get_historical_county_level_data()
        )

        # Wrapper class for all of the different data sources
        self.CovidDf = CovidData(
            [
                self.international_df,
                self.international_states_df,
                self.us_testing_df,
                self.us_states_testing_df,
                self.us_county_df,
            ]
        )


data = Data()


@app.route("/r/process")
def process():
    entities = request.args.get("entity", type=str, default="").split(",")
    metrics = request.args.get("metric", type=str, default="").split(",")
    filters = request.args.get("filters", type=str, default="ALL").split("_")

    filter_dict = {}
    for filter_str in filters:
        split_arr = filter_str.split(":")
        key = split_arr[0]
        values = split_arr[1].split(",")

        filter_dict[key] = values

    displayable_data = data.CovidDf.get_displayable_data(
        entities=entities, measurements=metrics, filter_dict=filter_dict
    )

    response_json = {}
    for k, v in displayable_data.items():
        response_json[k] = json.dumps(displayable_data[k])

    return Response(json.dumps(response_json), status=200, mimetype="application/json")


@app.route("/")
def index():
    curr_time = time.time()

    if curr_time > 7200 + data.last_update:
        data.set_up()

    return render_template("index.html")


@app.route("/r/get_dropdown_options")
def get_dropdown_options():
    options = {}
    all_entities = processing_utils.get_all_entities(data.CovidDf.dataframes)
    # country_to_state = processing_utils.get_countries_to_states(
    #     raw_global_df, us_states_testing_df
    # )
    # state_to_county = processing_utils.get_states_to_counties(us_county_df)

    hierarchy = processing_utils.create_hierarchy(all_entities)

    options[processing_utils.MEASUREMENT_COL] = processing_utils.METRIC_COLS
    options[processing_utils.ENTITY_COL] = hierarchy

    return Response(json.dumps(options), status=200, mimetype="application/json")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
