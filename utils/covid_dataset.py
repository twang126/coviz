import pandas as pd

from utils import processing_utils


class CovidData:
    """
    Wrapper for all of our data sources
    """

    def __init__(self, dfs):
        self.dataframes = dfs

    def get_scaled_dataframes(self, threshold_value, threshold_metric, filter_dict):
        entity_type_to_entity_to_min_date = {}

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
            if threshold_metric in df.columns:
                for entity_type, values in filter_dict.items():
                    if entity_type in df.columns:
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

                                if entity_type not in entity_type_to_entity_to_min_date:
                                    entity_type_to_entity_to_min_date[entity_type] = {}

                                if (
                                    entity_definition
                                    not in entity_type_to_entity_to_min_date[
                                        entity_type
                                    ]
                                ):
                                    entity_type_to_entity_to_min_date[entity_type][
                                        entity_definition
                                    ] = this_min
                                else:
                                    prev_min = entity_type_to_entity_to_min_date[
                                        entity_type
                                    ][entity_definition]

                                    if this_min < prev_min:
                                        entity_type_to_entity_to_min_date[entity_type][
                                            entity_definition
                                        ] = this_min

        if global_min_date is None:
            return []

        filtered_dfs = []
        for i, df in enumerate(date_serialized_dataframes):
            filtered_df = df
            filtered_df = filtered_df[
                filtered_df[processing_utils.DATE_COL] >= global_min_date
            ]

            scaled_dfs = []

            for entity_type, entity_defs in entity_type_to_entity_to_min_date.items():
                for entity_def, min_date in entity_defs.items():
                    if entity_type in filtered_df.columns:
                        scaled_df = filtered_df[filtered_df[entity_type] == entity_def]
                        scaled_df = scaled_df[
                            scaled_df[processing_utils.DATE_COL] >= min_date
                        ]

                        if threshold_metric in scaled_df.columns:
                            scaled_df = scaled_df[
                                scaled_df[threshold_metric] >= threshold_value
                            ]

                        if len(scaled_df) < 0:
                            continue

                        days_scale = min_date - global_min_date

                        scaled_df[processing_utils.DATE_COL] = scaled_df[
                            processing_utils.DATE_COL
                        ].apply(lambda d: d - days_scale)
                        scaled_dfs.append(scaled_df)

            if len(scaled_dfs) > 0:
                filtered_dfs.append(pd.concat(scaled_dfs))

        for i, df in enumerate(filtered_dfs):
            if processing_utils.DATE_COL in df.columns:
                re_written_df = df
                re_written_df[processing_utils.DATE_COL] = re_written_df[
                    processing_utils.DATE_COL
                ].apply(lambda x: x.strftime("%Y-%m-%d"))
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
        dfs_to_use = self.dataframes

        if threshold_value is not None and threshold_metric is not None:
            dfs_to_use = self.get_scaled_dataframes(
                threshold_value=threshold_value,
                threshold_metric=threshold_metric,
                filter_dict=filter_dict,
            )

        results = {col: [] for col in measurements}

        for df in dfs_to_use:
            matching_entity_cols = [col for col in entities if col in df.columns]

            matching_measurement_cols = [
                col for col in measurements if col in df.columns
            ]

            for measurement_col in matching_measurement_cols:
                for entity_col in matching_entity_cols:
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

                combined_results[measurement] = concat_df

        return combined_results
