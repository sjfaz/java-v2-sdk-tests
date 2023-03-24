import boto3
from datetime import datetime, timedelta
import os

client = boto3.client('logs')
LOG_GROUP = os.environ.get('LOG_GROUP')
HOURS = int(os.environ.get('HOURS', 1))
FILTER = os.environ.get('FILTER', '?"ApiCallTimeout" ?"ApiCallAttemptTimeout" ?"Exception:"')

# Get the logs matching for a time period with filter pattern
def get_log_group(start_time, end_time):
    print("**LOG ERRORS**")
    events = []
    
    response = client.filter_log_events(
        logGroupName=LOG_GROUP,
        startTime=start_time,
        endTime=end_time,
        filterPattern=FILTER
    )
    events.extend(response['events'])
    # If there is a next token, get the next batch of log events
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
    # Loop through each log event and extract the desired section using regex
    attempt_count = 0
    total_count = 0
    for event in events:
        message = event['message']
        # print(message)
        if 'ApiCallAttemptTimeout' in message:
            attempt_count += 1
        if 'ApiCallTimeout' in message:
            total_count += 1
    print(f"attempt count: {attempt_count}")
    print(f"total count: {total_count}")

# Get logs for the last x hours
if __name__ == '__main__':
    end_time = int(datetime.now().timestamp() * 1000)
    start_time = int((datetime.now() - timedelta(hours=HOURS)).timestamp() * 1000)
    get_log_group(start_time, end_time)