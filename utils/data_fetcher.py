from utils import processing_utils
import pandas as pd
import altair as alt


def process_request_dict(data_obj, request):
    return process(
        data=data_obj,
        entities=request["entities"],
        metrics=request["metrics"],
        filter_dict=request["filter_dict"],
        threshold_value=request["threshold_val"],
        threshold_metric=request["threshold_metric"],
    )


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
        if len(df) > 0:
            df[processing_utils.CATEGORY_GRAPHING_COL] = df.apply(
                lambda row: row[processing_utils.ENTITY_COL] + ": " + metric_type,
                axis=1,
            )
            dfs.append(df)

    if len(dfs) > 0:
        return pd.concat(dfs), displayable_data
    else:
        return None, displayable_data


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


def generate_data_fetch_request(
    metrics,
    countries,
    states,
    counties,
    overlay_applied,
    overlay_metric,
    overlay_threshold,
):
    request = {}

    request["threshold_metric"] = overlay_metric if overlay_applied else None
    request["threshold_val"] = overlay_threshold if overlay_applied else None
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
        or "threshold_metric" not in request
        or "threshold_val" not in request
        or len(request) > 5
    ):
        return False

    return (
        len(request["entities"]) > 0
        and len(request["metrics"]) > 0
        and len(request["filter_dict"]) > 0
    )


def fetch_streamlit_raw_data_display(displayable_data):
    entities_to_metrics_to_dataframes = {}
    for metric, df in displayable_data.items():
        entities = df[processing_utils.ENTITY_COL].unique().tolist()

        for entity in entities:
            rows = df[df[processing_utils.ENTITY_COL] == entity]

            if len(rows) > 0:
                if entity not in entities_to_metrics_to_dataframes:
                    entities_to_metrics_to_dataframes[entity] = {}

                if metric not in entities_to_metrics_to_dataframes[entity]:
                    entities_to_metrics_to_dataframes[entity][metric] = []

                entities_to_metrics_to_dataframes[entity][metric].append(rows)

    entity_to_metric_to_displayable_df = {}
    entity_to_metric_to_boxplots = {}

    for entity, metric_dict in entities_to_metrics_to_dataframes.items():
        entity_to_metric_to_displayable_df[entity] = {}

        for metric, list_of_dfs in metric_dict.items():
            df = pd.concat(list_of_dfs)

            if processing_utils.DELTA_COL_SUFFIX in metric:
                entity_to_metric_to_boxplots[entity] = {}
                entity_to_metric_to_boxplots[entity][metric] = {}
                last_week = df.sort_values(
                    by=processing_utils.DATE_COL, ascending=False
                ).head(7)

                entity_to_metric_to_boxplots[entity][metric]["Historic"] = {
                    "max": df[processing_utils.MEASUREMENT_COL].max(),
                    "nonzero-min": df[df[processing_utils.MEASUREMENT_COL] > 0][
                        processing_utils.MEASUREMENT_COL
                    ].min(),
                    "mean": df[processing_utils.MEASUREMENT_COL].mean(),
                }
                entity_to_metric_to_boxplots[entity][metric]["Within the last week"] = {
                    "max": last_week[processing_utils.MEASUREMENT_COL].max(),
                    "nonzero-min": last_week[
                        last_week[processing_utils.MEASUREMENT_COL] > 0
                    ][processing_utils.MEASUREMENT_COL].min(),
                    "mean": last_week[processing_utils.MEASUREMENT_COL].mean(),
                }

            columned = df[
                [processing_utils.DATE_COL, processing_utils.MEASUREMENT_COL]
            ].copy()
            entity_to_metric_to_displayable_df[entity][metric] = columned.sort_values(
                by=processing_utils.DATE_COL, inplace=False
            )

    return entity_to_metric_to_displayable_df, entity_to_metric_to_boxplots
