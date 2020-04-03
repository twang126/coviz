import numpy as np
import pandas as pd
import altair as alt

from utils import processing_utils


def build_chart(source):
    x_col_str_label = processing_utils.DATE_COL + ":T"
    y_col_str_label = processing_utils.MEASUREMENT_COL + ":Q"
    category_str_label = processing_utils.CATEGORY_GRAPHING_COL + ":N"

    # Create a selection that chooses the nearest point & selects based on x-value
    nearest = alt.selection(
        type="single",
        nearest=True,
        on="mouseover",
        fields=[processing_utils.DATE_COL],
        empty="none",
    )

    # The basic line
    line = (
        alt.Chart(source)
        .mark_line(interpolate="natural")
        .encode(x=x_col_str_label, y=y_col_str_label, color=category_str_label)
    )

    # Transparent selectors across the chart. This is what tells us
    # the x-value of the cursor
    selectors = (
        alt.Chart(source)
        .mark_point()
        .encode(x=x_col_str_label, opacity=alt.value(0),)
        .add_selection(nearest)
    )

    # Draw points on the line, and highlight based on selection
    points = line.mark_point().encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )

    # Draw text labels near the points, and highlight based on selection
    text = line.mark_text(align="left", dx=5, dy=-5).encode(
        text=alt.condition(nearest, y_col_str_label, alt.value(" "))
    )

    # Draw a rule at the location of the selection
    rules = (
        alt.Chart(source)
        .mark_rule(color="limegreen")
        .encode(x=x_col_str_label)
        .transform_filter(nearest)
    )

    # Put the five layers into a chart and bind the data
    chart = alt.layer(line, selectors, points, rules, text).properties(
        width=750, height=600
    )

    return chart