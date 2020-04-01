from utils import processing_utils
import pandas as pd


def process(
    data, entities, metrics, filter_dict, threshold_value=None, threshold_metric=None
):
    displayable_data = data.CovidDf.get_displayable_data(
        entities=entities,
        measurements=metrics,
        filter_dict=filter_dict,
        threshold_metric=threshold_metric,
        threshold_value=threshold_value,
    )

    dfs = []

    for metric_type, df in displayable_data.items():
        df[processing_utils.CATEGORY_GRAPHING_COL] = df.apply(
            lambda row: row[processing_utils.ENTITY_COL] + ": " + metric_type, axis=1
        )
        dfs.append(df)

    return pd.concat(dfs)


def get_dropdown_options(data):
    options = {}
    all_entities = processing_utils.get_all_entities(data.CovidDf.dataframes)
    # country_to_state = processing_utils.get_countries_to_states(
    #     raw_global_df, us_states_testing_df
    # )
    # state_to_county = processing_utils.get_states_to_counties(us_county_df)

    hierarchy = processing_utils.create_hierarchy(all_entities)

    options[processing_utils.MEASUREMENT_COL] = processing_utils.METRIC_COLS
    options[processing_utils.ENTITY_COL] = hierarchy

    return options


def generate_data_fetch_request(metrics, countries, states, counties):
    request = {}

    print(countries)

    request["filter_dict"] = {}
    request["entities"] = []
    request["metrics"] = metrics

    if len(countries) > 0:
        request["filter_dict"][processing_utils.COUNTRY_COL] = countries
        request["entities"].append(processing_utils.COUNTRY_COL)

    if len(states) > 0:
        request["filter_dict"][processing_utils.STATE_COL] = states
        request["entities"].append(processing_utils.STATE_COL)

    if len(counties) > 0:
        request["filter_dict"][processing_utils.COUNTY_COL] = counties
        request["entities"].append(processing_utils.COUNTY_COL)

    return request


def is_valid_data_fetch_request(request):
    if not isinstance(request, dict):
        return False

    if (
        "entities" not in request
        or "filter_dict" not in request
        or "metrics" not in request
        or len(request) > 3
    ):
        return False

    return (
        len(request["entities"]) > 0
        and len(request["metrics"]) > 0
        and len(request["filter_dict"]) > 0
    )
