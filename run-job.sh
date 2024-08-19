#!/bin/bash

# Get the job file and optional parameters
job=$1
experiment_name=$2
option=$3

# Ensure the job file is provided
if [[ -z "$job" ]]; then
  echo "Error: Job file is not specified."
  exit 1
fi

# Create the job
if [[ -z "$experiment_name" ]]; then
  if [[ "$job" =~ pipeline.yml ]]; then
    run_id=$(az ml job create -f "$job" --query name -o tsv --set settings.force_rerun=True)
  else
    run_id=$(az ml job create -f "$job" --query name -o tsv)
  fi
else
  run_id=$(az ml job create -f "$job" --query name -o tsv --set experiment_name="$experiment_name" --set settings.force_rerun=True)
fi

# Check if the run ID is obtained
if [[ -z "$run_id" ]]; then
  echo "Job creation failed."
  exit 3
fi

# Option to wait or not
if [[ "$option" == "nowait" ]]; then
  az ml job show -n "$run_id" --query services.Studio.endpoint
  exit 0
fi

# Monitor the job status
status=$(az ml job show -n "$run_id" --query status -o tsv)
if [[ -z "$status" ]]; then
  echo "Failed to retrieve job status."
  exit 4
fi

# Retrieve the job URI
job_uri=$(az ml job show -n "$run_id" --query services.Studio.endpoint)
if [[ -z "$job_uri" ]]; then
  echo "Failed to retrieve job URI."
  exit 5
fi

echo "Job URI: $job_uri"

# Define status states
running=("Queued" "NotStarted" "Starting" "Preparing" "Running" "Finalizing")
while [[ " ${running[@]} " =~ " ${status} " ]]; do
  echo "Job Status: $status"
  echo "Job URI: $job_uri"
  sleep 8
  status=$(az ml job show -n "$run_id" --query status -o tsv)
  if [[ -z "$status" ]]; then
    echo "Failed to retrieve job status."
    exit 4
  fi
done

# Check final job status
if [[ "$status" == "Completed" ]]; then
  echo "Job completed successfully."
  exit 0
elif [[ "$status" == "Failed" ]]; then
  echo "Job failed."
  exit 1
else
  echo "Job not completed or failed. Status is $status"
  exit 2
fi