import json

from flask import Flask
from flask import render_template
from flask import request
from flask import Response

import api_utils
import processing_utils
from covid_dataset import CovidData

app = Flask(__name__)

# The international COVID dataset, aggregated per country and state
# Source: Kaggle

raw_global_df = api_utils.get_international_dataset()
international_df = processing_utils.post_process_international_df(raw_global_df)

international_states_df = processing_utils.post_process_international_states_df(
    raw_global_df
)

# US testing dataset
# Source: https://covidtracking.com/api/
us_testing_df = processing_utils.post_process_us_testing_df(
    api_utils.get_historical_us_testing_data()
)
us_states_testing_df = processing_utils.post_process_state_testing_df(
    api_utils.get_historical_states_testing_data()
)

# Covid data per US county
# Source: NY Times
us_county_df = processing_utils.post_process_county_df(
    api_utils.get_historical_county_level_data()
)

# Wrapper class for all of the different data sources
CovidDf = CovidData(
    [
        international_df,
        international_states_df,
        us_testing_df,
        us_states_testing_df,
        us_county_df,
    ]
)


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

    displayable_data = CovidDf.get_displayable_data(
        entities=entities, measurements=metrics, filter_dict=filter_dict
    )

    response_json = {}
    for k, v in displayable_data.items():
        response_json[k] = json.dumps(displayable_data[k])

    return Response(json.dumps(response_json), status=200, mimetype="application/json")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/r/get_dropdown_options")
def get_dropdown_options():
    options = {}
    all_entities = processing_utils.get_all_entities(CovidDf.dataframes)
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
