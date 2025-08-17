python main.py --data-file data/dataset/Abalone/Abalone.csv \
    --initial_query "Do causal discovery on this dataset" \
    2>&1 | tee app/runs/quick_run.sh.log