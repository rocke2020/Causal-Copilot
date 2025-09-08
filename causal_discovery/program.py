import json
import causal_discovery.wrappers as wrappers
from causal_discovery.wrappers.utils.tab_utils import (
    remove_highly_correlated_features,
    add_correlated_nodes_to_graph,
    restore_original_node_indices,
)
from utils.logger import logger
from pathlib import Path
from pandas import DataFrame


class Programming(object):
    def __init__(self, args, enable_save_data=1):
        self.args = args
        self.enable_save_data = enable_save_data
        self.data_file = Path(args.data_file)

    def save_data(self, global_state, processed_data: DataFrame):
        if not self.enable_save_data:
            return
        out_dir = Path(f"output/{global_state.algorithm.selected_algorithm}")
        out_dir.mkdir(parents=True, exist_ok=True)
        algorithm_arguments_file = out_dir / "algorithm_arguments.json"
        arguments = global_state.algorithm.algorithm_arguments
        with open(algorithm_arguments_file, "w", encoding="utf-8") as f:
            json.dump(arguments, f, ensure_ascii=False, indent=4)
        data_file = out_dir / f"processed_{self.data_file.stem}.csv"
        with open(data_file, "w", encoding="utf-8") as f:
            processed_data.to_csv(f, index=False)

    def forward(self, global_state):
        """handle_correlated_features默认开启；时序模型，如果有lag_matrix，额外处理"""
        # Check if we should automatically find and handle correlated features
        logger.info(f"{global_state.algorithm.selected_algorithm = }")
        correlation_threshold = getattr(global_state.algorithm, "correlation_threshold")
        logger.info(
            f"Checking for correlated features with threshold {global_state.algorithm.handle_correlated_features = }, {correlation_threshold = }"
        )
        if global_state.algorithm.handle_correlated_features:
            threshold = getattr(global_state.algorithm, "correlation_threshold", 0.99)
            # Automatically find and remove highly correlated features
            # processed_data is DataFrame
            reduced_data, adjusted_mapping, original_indices = (
                remove_highly_correlated_features(
                    global_state.user_data.processed_data, threshold=threshold
                )
            )

            # Only proceed with reduced dataset if we found correlated features
            orig_data_shape = global_state.user_data.processed_data.shape
            logger.info(
                f"{orig_data_shape = }, {reduced_data.shape = }, {original_indices = }"
            )
            # 初步应用，人工选择的特征，大概率相关性较低不会被移除。
            if len(original_indices) < global_state.user_data.processed_data.shape[1]:
                # Run algorithm on reduced dataset
                logger.info("Running algorithm on reduced dataset...")
                self.save_data(global_state, reduced_data)
                algo_func = getattr(wrappers, global_state.algorithm.selected_algorithm)
                graph, info, raw_result = algo_func(
                    global_state.algorithm.algorithm_arguments
                ).fit(reduced_data)

                # Restore original indices in the mapping if needed
                restored_graph, restored_mapping = restore_original_node_indices(
                    graph, original_indices, adjusted_mapping
                )

                # Add back the highly correlated features to the graph
                final_graph = add_correlated_nodes_to_graph(
                    restored_graph,
                    data=global_state.user_data.processed_data,
                    threshold=threshold,
                    original_indices=original_indices,
                )

                # Store original and expanded results
                global_state.results.raw_result = raw_result
                global_state.results.converted_graph = final_graph
                info["original_graph"] = (
                    graph  # Store the original graph before adding correlated nodes
                )
                info["high_corr_features_removed"] = original_indices
            else:
                # No correlated features found, run algorithm on the full dataset
                logger.info("No correlated features found, running on full dataset...")
                algo_func = getattr(wrappers, global_state.algorithm.selected_algorithm)
                self.save_data(global_state, global_state.user_data.processed_data)

                """graph, info, raw_result from algo_func
                info = {
                    'edges': edges,
                    'graph': graph,
                    }
                adj_matrix, info, (graph, edges)
                """
                graph, info, raw_result = algo_func(
                    global_state.algorithm.algorithm_arguments
                ).fit(global_state.user_data.processed_data)
                logger.info(f"{type(raw_result[0]) = }, {type(raw_result[1]) = }")
                global_state.results.raw_result = raw_result
                global_state.results.converted_graph = graph
        else:
            # Run algorithm on the full dataset
            logger.info("No correlated features found, running on full dataset...")
            algo_func = getattr(wrappers, global_state.algorithm.selected_algorithm)
            self.save_data(global_state, global_state.user_data.processed_data)
            graph, info, raw_result = algo_func(
                global_state.algorithm.algorithm_arguments
            ).fit(global_state.user_data.processed_data)
            logger.info(f"{type(raw_result[0]) = }, {type(raw_result[1]) = }")
            global_state.results.raw_result = raw_result
            global_state.results.converted_graph = graph

        # Handle time-series specific data
        if global_state.statistics.time_series:
            if "lag_matrix" in info:
                # Store the original lag matrix
                original_lag_matrix = info["lag_matrix"]
                global_state.results.lagged_graph = original_lag_matrix

                # If we have correlated features, add them to the lag graph as well
                if global_state.algorithm.handle_correlated_features:
                    threshold = getattr(
                        global_state.algorithm, "correlation_threshold", 0.99
                    )
                    # Add correlated nodes to the lag graph
                    enhanced_lag_matrix = add_correlated_nodes_to_graph(
                        original_lag_matrix,
                        data=global_state.user_data.processed_data,
                        threshold=threshold,
                        original_indices=original_indices,
                    )
                    global_state.results.lagged_graph = enhanced_lag_matrix
                    info["lag_matrix"] = enhanced_lag_matrix
            else:
                global_state.results.lagged_graph = None

        global_state.results.raw_info = info

        return global_state
