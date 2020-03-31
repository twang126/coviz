import pandas as pd

import processing_utils


class CovidData:
    """
    Wrapper for all of our data sources
    """

    def __init__(self, dfs):
        self.dataframes = dfs

    def get_date_start(self, threshold_value, threshold_metric, filter_dict):
        

    def get_displayable_data(self, entities, measurements, filter_dict, threshold_value=None, threshold_metric=None):
        """
        Process a data request to display on a graph.

        Arguments:
            entities {[string]} -- the granularity to return results for
            i.e. County, State/Province..

            measurements {[string]} -- the metrics to display
            i.e. Confirmed, Deaths, etc

        Returns:
            A dictionary mapping a measurement type to a dataframe.

            Each dataframe will have 3 columns:
            [Date, Entity, Metric]
        """

        results = {col: [] for col in measurements}

        for df in self.dataframes:
            matching_entity_cols = [col for col in entities if col in df.columns]

            matching_measurement_cols = [
                col for col in measurements if col in df.columns
            ]

            for measurement_col in matching_measurement_cols:
                for entity_col in matching_entity_cols:
                    if threshold_metric is None or threshold_metric != measurement_col:
                        grouping_cols = [entity_col, processing_utils.DATE_COL]

                        if entity_col in filter_dict:
                            if filter_dict[entity_col] != ["ALL"]:
                                df = df[df[entity_col].isin(filter_dict[entity_col])]

                        aggregated_df = processing_utils.agg_df(
                            df, group_cols=grouping_cols, agg_col=measurement_col
                        )

                        aggregated_df = aggregated_df.rename(
                            columns={
                                entity_col: processing_utils.ENTITY_COL,
                                measurement_col: processing_utils.MEASUREMENT_COL,
                            }
                        )

                        results[measurement_col].append(aggregated_df)

        combined_results = {}
        for measurement, dataframes in results.items():
            if len(dataframes) > 0:
                concat_df = pd.concat(dataframes)

                actual_entities = concat_df[processing_utils.ENTITY_COL].unique()
                combined_results[measurement] = {col: [] for col in actual_entities}

                for entity in actual_entities:
                    relevant_rows = concat_df[
                        concat_df[processing_utils.ENTITY_COL] == entity
                    ][[processing_utils.DATE_COL, processing_utils.MEASUREMENT_COL]]

                    combined_results[measurement][entity] = relevant_rows.to_dict(
                        orient="list"
                    )

        return combined_results