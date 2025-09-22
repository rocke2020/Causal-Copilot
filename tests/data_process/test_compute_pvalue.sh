export PYTHONPATH='.'
# 
file=app/tests/test_data.py
python $file \
    2>&1 | tee $file.log