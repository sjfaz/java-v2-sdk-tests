import boto3
from datetime import datetime, timedelta
import re
import os
from statistics import mean

client = boto3.client('logs')
LOG_GROUP = os.environ.get('LOG_GROUP')
HOURS = int(os.environ.get('HOURS', 1))
FILTER = os.environ.get('FILTER', '"Time taken (ms):"')

def get_log_group(start_time, end_time):
    print("**LOG TIMING DATA**")
    events = []
    # Get the log events matching the filter expression
    response = client.filter_log_events(
        logGroupName=LOG_GROUP,
        startTime=start_time,
        endTime=end_time,
        filterPattern=FILTER
    )
    events.extend(response['events'])
    #if there is a next token, get the next batch of log events
    while 'nextToken' in response:
        next_token = response['nextToken']
        response = client.filter_log_events(
            logGroupName=LOG_GROUP,
            startTime=start_time,
            endTime=end_time,
            filterPattern=FILTER,
            nextToken=next_token
        )
        events.extend(response['events'])
    process_response(events)

def process_response(events):
    regex_pattern = r"Time taken \(ms\): (\d+)"
    times = []
    # Loop through each log event and extract the desired section using regex
    for event in events:
        message = event['message']
        match = re.search(regex_pattern, message)
        number = int(match.group(1))
        times.append(number)

    # Print the averages, percentiles, range counts, and absolute tail
    print(f"count: {len(times)}")
    avg_response_time = mean(times)
    sortedtimes = sorted(times)
    print(f"average: {avg_response_time}")
    percentiles = {}
    for percentile in [50, 90, 95, 99, 99.5, 99.9]:
        index = int(len(times) * percentile / 100)
        percentiles[f'P{percentile}'] = sortedtimes[index]

    max = sortedtimes[-1]
    min = sortedtimes[0]
    print('Response time percentiles:')
    print(f"min: {min}")
    for percentile, value in percentiles.items():
        print(f'{percentile}: {value:.0f} ms')
    print(f"max: {max}")

    ranges = list(range(0, 110, 10))
    ranges.append(250)
    ranges.append(float('inf'))
    counts = []
    for i in range(len(ranges) - 1):
        start_range = ranges[i]
        end_range = ranges[i + 1]
        count = sum(start_range <= time < end_range for time in sortedtimes)
        counts.append(count)
    
    for i in range(len(ranges) - 1):
        if i < len(ranges) - 2:
            print(f"{ranges[i]}-{ranges[i+1]}: {counts[i]}")
        else:
            print(f"{ranges[i]}+: {counts[i]}")
    print(f"Absolute tail: {sortedtimes[-100:]}")

# Get logs for the last x hours
if __name__ == '__main__':
    end_time = int(datetime.now().timestamp() * 1000)
    start_time = int((datetime.now() - timedelta(hours=HOURS)).timestamp() * 1000)
    get_log_group(start_time, end_time)