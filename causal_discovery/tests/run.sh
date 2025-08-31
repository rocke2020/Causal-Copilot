#!/bin/bash

# Check if first argument is "0" to run directly with python, default is nohup.
if [ "$1" = "0" ]; then
    echo "Running directly with python..."
    python main.py --data-file data/dataset/Abalone/Abalone.csv --initial_query "Do causal discovery on this dataset" 2>&1 | tee run.log
else
    echo "Running with nohup in background..."
    nohup python main.py --data-file data/dataset/Abalone/Abalone.csv --initial_query "Do causal discovery on this dataset" > run-nohup.log 2>&1 &
    echo "Process started in background. Check run-nohup.log for output."
    echo "PID: $!"
fi