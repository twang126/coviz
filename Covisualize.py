import numpy as np
import pandas as pd
import streamlit as st

import altair as alt

from utils import site_data_abstraction
from utils import data_fetcher
from utils import processing_utils
from utils import graphing
from utils import streamlit_ui
from utils import session_state

import time
import random

hide_menu_style = """
        <style>
            #MainMenu {visibility: hidden;}
        </style>"""

hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
"""

open_graph_style = """
<head>
    <meta property="og:site_name" content="Coviz-19"/>
    <meta property="og:title" content="The Covid Analysis Project"/>
    <meta property="og:description" content="A comprehensive tool to plot and explore any combination of Covid-19 metrics and locations. Backed by all of the world's available, most reliable data."/>
    <meta property="og:type" content="website" />
    <meta property="og:image" content="https://i.imgur.com/rm14BZI.png"/>
    <link rel="shortcut icon" href="static/favicon/favicon.ico">
    <link rel="icon" href="static/favicon/favicon.ico">
</head>
"""

### Hide annoying built-in Streamlit HTML ###
st.markdown(open_graph_style, unsafe_allow_html=True)
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
st.markdown(hide_menu_style, unsafe_allow_html=True)

state = session_state.get(
    data=None,
    key=0,
    dropdown_options=None,
    metrics=streamlit_ui.default_metrics,
    country=streamlit_ui.default_country,
    states=streamlit_ui.default_states,
    county=streamlit_ui.default_county,
    overlay_metric=streamlit_ui.default_overlay_metric,
    overlay_threshold=streamlit_ui.default_overlay_threshold,
    overlay=False,
    chart=None,
)


def get_hours_from_epoch():
    return int(time.time() // (60 * 60))


@st.cache
def load_data(curr_time):
    data = site_data_abstraction.Data()
    dropdown_options = data_fetcher.get_dropdown_options(data)

    return (data, dropdown_options)


# We need to grab the curr time as a way to smartly cache
curr_time = get_hours_from_epoch()

streamlit_ui.add_header_and_title(st)

if st.checkbox("Show instructions"):
    streamlit_ui.load_instructions(st)

if st.checkbox("Show Entity to Metrics mapping"):
    streamlit_ui.load_entity_to_metrics_mapping(st)

if state.data is None:
    state.data, state.dropdown_options = load_data(curr_time)

### Build a placeholder cell ###
st.markdown("""## Graph ## """)
graph_cell = st.empty()

data_cell = st.empty()

### Set up the side bar ###
### Use lots of Empty place holders to support reset button
st.sidebar.markdown("""**QueryBuilder [v1.1](https://github.com/twang126/coviz)**""")

st.sidebar.markdown("""### Select Metric(s): """)
metrics_selector = st.sidebar.empty()
st.sidebar.markdown("""### Select Entities: """)
st.sidebar.text("Note: You can leave options empty.")
countries_selector = st.sidebar.empty()

states_selector = st.sidebar.empty()

counties_selector = st.sidebar.empty()

st.sidebar.markdown("""### Overlay (optional):""")

overlay_box = st.sidebar.empty()
overlay_metric_selector = st.sidebar.empty()
overlay_threshold_box = st.sidebar.empty()

plot_button = st.sidebar.button("Plot")

reset_button = st.sidebar.button("Reset")
graph_alerts_cell = st.sidebar.empty()

#### Define the reset button
if reset_button:
    state.key = state.key + 1
    state.country = streamlit_ui.default_country
    state.county = streamlit_ui.default_county
    state.states = streamlit_ui.default_states
    state.metrics = streamlit_ui.default_metrics
    state.overlay_metric = streamlit_ui.default_overlay_metric
    state.overlay_threshold = streamlit_ui.default_overlay_threshold

    state.chart = None
    state.overlay = False

### Actually implement the selector menus
metrics = metrics_selector.multiselect(
    "Type(s) of data to plot",
    state.dropdown_options[processing_utils.MEASUREMENT_COL],
    # default=state.metrics,
    key=state.key,
)

countries = countries_selector.multiselect(
    processing_utils.COUNTRY_COL + "s:",
    state.dropdown_options[processing_utils.ENTITY_COL][processing_utils.COUNTRY_COL],
    # default=state.country,
    key=state.key,
)

states = states_selector.multiselect(
    processing_utils.STATE_COL + "s:",
    state.dropdown_options[processing_utils.ENTITY_COL][processing_utils.STATE_COL],
    # default=state.states,
    key=state.key,
)

counties = counties_selector.multiselect(
    "US Counties:",
    state.dropdown_options[processing_utils.ENTITY_COL][processing_utils.COUNTY_COL],
    # default=state.county,
    key=state.key,
)

overlay_checkbox = overlay_box.checkbox(
    "Add overlay", key=state.key, value=state.overlay
)


if overlay_checkbox:
    overlay_metric = overlay_metric_selector.selectbox(
        label="Overlay Metric:",
        options=state.dropdown_options[processing_utils.MEASUREMENT_COL],
        key=state.key,
        index=state.overlay_metric,
    )

    overlay_threshold = overlay_threshold_box.number_input(
        label="Overlay Threshold:", key=state.key, value=state.overlay_threshold
    )

    if not state.overlay:
        state.country = countries
        state.county = counties
        state.states = states
        state.metrics = metrics
else:
    overlay_metric = None
    overlay_threshold = None

state.overlay_metric = (
    streamlit_ui.get_default_index(
        overlay_metric, state.dropdown_options[processing_utils.MEASUREMENT_COL]
    )
    if overlay_metric is not None
    else streamlit_ui.default_overlay_metric
)
state.overlay_threshold = (
    overlay_threshold
    if overlay_threshold is not None
    else streamlit_ui.default_overlay_threshold
)
state.overlay = overlay_checkbox

## Add the default plot
if state.chart is None:
    default_source_df, default_displayable_dict = data_fetcher.process_request_dict(
        data_obj=state.data, request=streamlit_ui.get_default_request()
    )
    default_chart = graphing.build_chart(source=default_source_df)
    state.chart = default_chart

graph_cell.altair_chart(state.chart)

### Upon the 'plot' button being pressed, plot the graph if the parameters are valid ###
if plot_button:
    request = data_fetcher.generate_data_fetch_request(
        metrics,
        countries,
        states,
        counties,
        overlay_checkbox,
        overlay_metric,
        overlay_threshold,
    )

    # state.country = countries
    # state.county = counties
    # state.states = states
    # state.metrics = metrics

    # if overlay_checkbox:
    #     state.overlay_metric = streamlit_ui.get_default_index(
    #         overlay_metric, state.dropdown_options[processing_utils.MEASUREMENT_COL]
    #     )
    #     state.overlay_threshold = overlay_threshold
    #     state.overlay = True
    # else:
    #     state.overlay_metric = streamlit_ui.default_overlay_metric
    #     state.overlay_threshold = streamlit_ui.default_overlay_threshold
    #     state.overlay = False

    successfully_updated_chart = False

    if data_fetcher.is_valid_data_fetch_request(request):
        df, displayable_data = data_fetcher.process_request_dict(
            data_obj=state.data, request=request
        )

        if df is not None:
            with st.spinner("Fetching results..."):
                chart = graphing.build_chart(source=df)

                graph_cell.altair_chart(chart)
                successfully_updated_chart = True

                # Set the default plot
                (
                    all_dataframes,
                    all_plots,
                ) = data_fetcher.fetch_streamlit_raw_data_display(displayable_data)

                state.chart = chart

                # Pretend like we are processing
                time.sleep(float(random.randint(50, 115)) / 100)

            st.markdown("""## Data ## """)

            if len(all_dataframes) > 0:
                for entity, df in all_dataframes.items():
                    st.subheader(entity)
                    st.write(df)

            if len(all_plots) > 0:
                st.markdown("### Descriptive statistics for rate of change metrics ###")

                for entity, metric_to_plot in all_plots.items():
                    st.subheader(entity)

                    for metric, stats_dict in metric_to_plot.items():
                        st.markdown(metric)
                        st.write(stats_dict)

    if not successfully_updated_chart:
        graph_alerts_cell.warning("Failed to update: no data returned for that query.")
    else:
        graph_alerts_cell.success("Query succeeded!")
