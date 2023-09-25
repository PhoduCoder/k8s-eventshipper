
import logging
import os
import time
import json
import redis
import boto3
from kubernetes import client, config
from retrying import retry

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Redis client
redis_client = redis.StrictRedis(host=os.getenv("REDIS_HOST", "redis"), port=int(os.getenv("REDIS_PORT", 6379)), db=0)

from sinks import Sink, S3Sink, StdoutSink
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

# Initialize Kubernetes client
try:
    config.load_incluster_config()
except config.ConfigException:
    config.load_kube_config()
v1 = client.CoreV1Api()

# Read configuration to select the appropriate Sink
sink_type = os.getenv("SINK_TYPE", "Stdout")
if sink_type == "S3":
    sink = S3Sink()
elif sink_type == "Stdout":
    sink = StdoutSink()
else:
    raise ValueError(f"Unsupported sink type: {sink_type}")

# Fetch last processed event from Redis
last_processed_event = redis_client.get('last_processed_event')
if last_processed_event:
    last_processed_event = last_processed_event.decode('utf-8')

# Get polling frequency from environment variable, default is 300 seconds (5 minutes)
polling_frequency = int(os.getenv("POLLING_FREQUENCY", 300))

# Main loop to capture Kubernetes events and send them to the selected Sink
while True:
    try:
        # Fetch events
        events = v1.list_event_for_all_namespaces().items

        for event in events:
            event_timestamp = event.metadata.creation_timestamp.strftime('%Y-%m-%d %H:%M:%S')

            # Skip events that have already been processed
            if last_processed_event and event_timestamp <= last_processed_event:
                continue

            # Send event to the selected Sink
            sink.send(event)

            # Update last processed event in Redis
            redis_client.set('last_processed_event', event_timestamp)

            # Logging
            logger.info(f"Processed event: {event.metadata.name}")

    except Exception as e:
        logger.error(f"An error occurred: {e}")

    # Sleep for the specified polling frequency to avoid overloading the Kubernetes API server
    time.sleep(polling_frequency)
