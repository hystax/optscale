#!/bin/bash

# Check if the service name has been passed as an argument
if [ $# -eq 0 ]
then
    echo "No arguments supplied. Please provide the service name as an argument."
    exit 1
fi

SERVICE_NAME=$1

# Get the name of the first pod of the specified service
POD_NAME=$(kubectl get pods -l app=$SERVICE_NAME -o jsonpath="{.items[0].metadata.name}")

# Check if getting the pod name failed
if [ -z "$POD_NAME" ]
then
    echo "Failed to get the pod name. Please check if the service name is correct and the corresponding pods are running."
    exit 1
fi

# Get the container ID
CONTAINER_ID=$(kubectl get pod $POD_NAME -o jsonpath="{.status.containerStatuses[0].containerID}" | cut -d'/' -f3)
echo "Getting you into the pod $POD_NAME, Docker image $CONTAINER_ID"

# Exec sh in the pod
kubectl exec -it $POD_NAME -- /bin/sh

# Ask the user if they want to commit the container and scale the service
read -p "Do you want to commit the container and scale the service $SERVICE_NAME? [y/N] " response
response=${response,,} # convert to lowercase

if [[ $response =~ ^(yes|y)$ ]]
then
    # Create a backup of the previous image version with the current date and time
    BACKUP_IMAGE=$SERVICE_NAME:$(date +"%y%m%d-%H%M%S")
    echo "Backing up $SERVICE_NAME:local as $BACKUP_IMAGE"
    docker tag $SERVICE_NAME:local $BACKUP_IMAGE

    # Use Docker to commit the container to an image
    docker commit $CONTAINER_ID $SERVICE_NAME:local

    # Get the original number of replicas
    ORIG_REPLICAS=$(kubectl get deployment $SERVICE_NAME -o=jsonpath='{.spec.replicas}')

    echo "Rescaling $SERVICE_NAME to 0 and back to $ORIG_REPLICAS to restart all pods"
    # Scale the service to 0
    kubectl scale --replicas=0 deployment/$SERVICE_NAME

    # Scale the service back to the original number of replicas
    kubectl scale --replicas=$ORIG_REPLICAS deployment/$SERVICE_NAME
fi