import boto3
import os
from datetime import datetime, timedelta

cloudwatch = boto3.client('cloudwatch')
TABLE_NAME = os.environ.get('TABLE')
HOURS = int(os.environ.get('HOURS', 1))

def format_datapoint(count, average, min, max, ts):
    return f"Count: {count}, Average: {average:.3f} ms, Min: {min:.3f} ms, Max: {max:.3f} ms, Time: {ts}"

response = cloudwatch.get_metric_statistics(
    Namespace='AWS/DynamoDB',
    MetricName='SuccessfulRequestLatency',
    Dimensions=[
        {
            'Name': 'TableName',
            'Value': TABLE_NAME
        },
        {
            'Name': 'Operation',
            'Value': 'GetItem'
        }
    ],
    StartTime=datetime.utcnow() - timedelta(hours=HOURS),
    EndTime=datetime.utcnow(),
    Period=3600 * HOURS,
    Statistics=['SampleCount', 'Average', 'Minimum', 'Maximum']
)

print("**CLOUDWATCH DATA**")
for res_data in response['Datapoints']:
    print(format_datapoint(res_data['SampleCount'], res_data['Average'], res_data['Minimum'], res_data['Maximum'], res_data['Timestamp']))
