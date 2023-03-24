#!/usr/bin/python3

import subprocess

# List of test details (change names as needed)
tests_details = [ 
    {'table': 'ecs-javav2-netty-cmk', 'log_group': 'ecs-javav2-netty-cmk-loggroup'},
    {'table': 'ecs-javav2-crt-cmk', 'log_group': 'ecs-javav2-crt-cmk-loggroup'},
]

# Loop through all test to get the last x hours of metrics / logs
for test_detail in tests_details:
    env_vars = {
        'TABLE': test_detail['table'],
        'LOG_GROUP': test_detail['log_group'],
        'HOURS': '1',
    }
    print("***Starting: " + test_detail['table'] + "***")
    print(f"***Env: {env_vars}***")
    result_logs = subprocess.run(['python3', './utils/log-timings.py'], env=env_vars, capture_output=True, text=True)
    result_cw = subprocess.run(['python3', './utils/cw-metrics.py'], env=env_vars, capture_output=True, text=True)
    result_errors = subprocess.run(['python3', './utils/log-errors.py'], env=env_vars, capture_output=True, text=True)
    print(result_logs.stdout)
    print(result_cw.stdout)
    print(result_errors.stdout)
    print("***Finished: " + test_detail['table'] + "***")