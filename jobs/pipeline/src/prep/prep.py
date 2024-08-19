import os
import argparse

import logging
import mlflow
from pathlib import Path

import pandas as pd

from sklearn.model_selection import train_test_split

# input and output arguments
parser = argparse.ArgumentParser()
parser.add_argument("--data", type=str, help="path to input data")
parser.add_argument("--train_data", type=str, help="path to train data")
parser.add_argument("--test_data", type=str, help="path to test data")
args = parser.parse_args()

# Start Logging
mlflow.start_run()

print(" ".join(f"{k}={v}" for k, v in vars(args).items()))

arr = os.listdir(args.data)
print(arr)

# Initialize an empty list to store DataFrames
df = []

for filename in arr:
    print("reading file: %s ..." % filename)
    with open(os.path.join(args.data, filename), "r") as handle:
        input_df = pd.read_csv((Path(args.data) / filename))
        df.append(input_df)

# Concatenate the list of DataFrames into a single DataFrame
df = pd.concat(df)

# Now you can split the DataFrame into train and test sets
train_df, test_df = train_test_split(df, test_size=0.3, random_state=4)

# Save the train and test DataFrames to CSV files
train_df.to_csv((Path(args.train_data) / "train_data.csv"), index=False)
test_df.to_csv((Path(args.test_data) / "test_data.csv"), index=False)

# Stop Logging
mlflow.end_run()
