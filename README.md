
# Kubernetes Event Logger

This project captures Kubernetes events and forwards them to a configurable sink.

## Components

- `code/`: Contains the Python code for the event logger.
- `manifests/`: Contains Kubernetes manifests for deployment and Redis StatefulSet.
- `helm_chart/`: Contains a simple Helm Chart for deploying the application.

## How to Use

1. Build a Docker image with the Python code and push it to a registry.
2. Update the `image.repository` in `helm_chart/values.yaml`.
3. Deploy the Redis StatefulSet using `kubectl apply -f manifests/redis_statefulset.yaml`.
4. Deploy the application using the Helm Chart.

## Configuration

- `SINK_TYPE`: The type of sink to use ("Stdout" or "S3").
- `REDIS_HOST`: The hostname of the Redis instance.
- `REDIS_PORT`: The port of the Redis instance.
- `POLLING_FREQUENCY`: The frequency (in seconds) at which to poll for events.

For S3 sink, configure IRSA (IAM Roles for Service Accounts) with the necessary permissions.
