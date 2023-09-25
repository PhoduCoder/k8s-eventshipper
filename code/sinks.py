
import json
import boto3
from retrying import retry
import os

# Initialize S3 client if S3 sink is selected
if os.getenv("SINK_TYPE") == "S3":
    s3_client = boto3.client('s3', region_name=os.getenv("AWS_REGION"))
    s3_bucket = os.getenv("S3_BUCKET")

# Sink Interface
class Sink:
    def send(self, event):
        pass

# S3 Sink Implementation
class S3Sink(Sink):
    @retry(stop_max_attempt_number=3)
    def send(self, event):
        event_json = json.dumps(event.metadata.to_dict())
        s3_client.put_object(Body=event_json, Bucket=s3_bucket, Key=f"events/{event.metadata.name}.json")

# Stdout Sink Implementation
class StdoutSink(Sink):
    def send(self, event):
        event_json = json.dumps(event.metadata.to_dict(), indent=4)
        print(event_json)
