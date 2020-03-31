import pandas as pd

from utils import processing_utils


class CovidData:
    """
    Wrapper for all of our data sources
    """

    def __init__(self, dfs):
        self.dataframes = dfs

    def get_scaled_dataframes(self, threshold_value, threshold_metric, filter_dict):
        df_to_entity_to_min_date = {}

        global_min_date = None
        date_serialized_dataframes = []

        for i, df in enumerate(self.dataframes):
            new_df = df.copy()
            if processing_utils.DATE_COL in new_df:
                new_df[processing_utils.DATE_COL] = pd.to_datetime(
                    new_df[processing_utils.DATE_COL]
                )

            date_serialized_dataframes.append(new_df)

        for i, df in enumerate(date_serialized_dataframes):
            df_to_entity_to_min_date[i] = {}

            if threshold_metric in df.columns:
                for entity_type, values in filter_dict.items():
                    if entity_type in df.columns:
                        df_to_entity_to_min_date[i][entity_type] = {}
                        for entity_definition in values:
                            matching_rows = df[
                                (df[entity_type] == entity_definition)
                                & (df[threshold_metric] >= threshold_value)
                            ]

                            if len(matching_rows) > 0:
                                this_min = matching_rows[
                                    processing_utils.DATE_COL
                                ].min()

                                if (
                                    global_min_date is None
                                    or global_min_date > this_min
                                ):
                                    global_min_date = this_min

                                df_to_entity_to_min_date[i][entity_type][
                                    entity_definition
                                ] = this_min

        if global_min_date is None:
            return []

        filtered_dfs = []
        for i, df in enumerate(date_serialized_dataframes):
            entities_to_entity_to_min_date = df_to_entity_to_min_date[i]
            filtered_df = df
            filtered_df = filtered_df[
                filtered_df[processing_utils.DATE_COL] >= global_min_date
            ]

            if len(entities_to_entity_to_min_date) > 0:
                scaled_dfs = []
                for (
                    entity_col,
                    entity_def_dict,
                ) in entities_to_entity_to_min_date.items():
                    for entity_def, min_date in entity_def_dict.items():
                        scaled_df = filtered_df[filtered_df[entity_col] == entity_def]
                        days_scale = min_date - global_min_date

                        scaled_df[processing_utils.DATE_COL] = scaled_df[
                            processing_utils.DATE_COL
                        ].apply(lambda d: d - days_scale)
                        scaled_dfs.append(scaled_df)

                filtered_df = pd.concat(scaled_dfs)

            filtered_dfs.append(filtered_df)

        for i, df in enumerate(filtered_dfs):
            if processing_utils.DATE_COL in df.columns:
                re_written_df = df
                re_written_df[processing_utils.DATE_COL] = re_written_df[
                    processing_utils.DATE_COL
                ].apply(lambda x: str(x))
                filtered_dfs[i] = re_written_df

        return filtered_dfs

    def get_displayable_data(
        self,
        entities,
        measurements,
        filter_dict,
        threshold_value=None,
        threshold_metric=None,
    ):
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
