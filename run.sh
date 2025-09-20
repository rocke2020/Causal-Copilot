#!/bin/bash

# Check if first argument is "0" to run directly with python, default is nohup.
# 2024_causal_single_project 1_causal_single_project
data_file="/data/rca-data/tian-qi/v6/1_causal_single_project/photovoltaic_power_station.csv"
dataset_name="光伏发电站运营数据"
initial_query="Do causal discovery on this dataset，核心运营指标是equivalent_operating_hours（等效时长）"
if [ "$1" = "0" ]; then
    echo "Running directly with python..."
    python main.py --data-file "$data_file" --dataset_name "$dataset_name" --initial_query "$initial_query" 2>&1 | tee run.log
else
    echo "Running with nohup in background..."
    nohup python main.py --data-file "$data_file" --dataset_name "$dataset_name" --initial_query "$initial_query" > run-nohup.log 2>&1 &
    echo "Process started in background. Check run-nohup.log for output."
    echo "PID: $!"
fi