import os
import mlflow
import argparse
import numpy as np

import pandas as pd

from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import make_pipeline
from sklearn.compose import make_column_transformer

from sklearn.model_selection import train_test_split

from sklearn.ensemble import GradientBoostingRegressor

mlflow.start_run() # Start a new MLflow run

os.makedirs("./outputs", exist_ok=True) # Create the "outputs" directory if it doesn't exist


def select_first_file(path):
    """Selects first file in folder, use under assumption there is only one file in folder
    Args:
        path (str): path to directory or file to choose
    Returns:
        str: full path of selected file
    """
    files = os.listdir(path)
    return os.path.join(path, files[0])


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--train_data", type=str, help="path to train data")
    parser.add_argument("--test_data", type=str, help="path to test data")
    parser.add_argument("--n_estimators", required=False, default=100, type=int)
    parser.add_argument("--learning_rate", required=False, default=0.1, type=float)
    parser.add_argument("--registered_model_name", type=str, help="model name")
    parser.add_argument("--model", type=str, help="path to model file")
    args = parser.parse_args() # Parse the command-line arguments

    car_mpg_train = pd.read_csv(select_first_file(args.train_data))  # Read the training data
    car_mpg_test = pd.read_csv(select_first_file(args.test_data)) # Read the test data

    target = 'mpg'
    numeric_features = ['cyl','disp','hp','wt','acc','yr','origin','car_type',]

    # Extract the features from the training data
    X_train = car_mpg_train.drop(columns=[target]) 
    y_train = car_mpg_train[target]

    # Extract the features from the test data
    X_test = car_mpg_test.drop(columns=[target])
    y_test = car_mpg_test[target]

    # Create a column transformer for preprocessing the numeric features
    preprocessor = make_column_transformer(
        (StandardScaler(), numeric_features)
    )

    # Create a Gradient Boosting Regressor model
    model_gbr = GradientBoostingRegressor(
        n_estimators=args.n_estimators,
        learning_rate=args.learning_rate
    )

    # Create a pipeline with preprocessing and the model
    model_pipeline = make_pipeline(preprocessor, model_gbr)

    model_pipeline.fit(X_train, y_train)

    rmse = model_pipeline.score(X_test, y_test)

    mlflow.log_metric("RMSE", float(rmse))

    print("Registering model pipeline")

    mlflow.sklearn.log_model(
        sk_model=model_pipeline,
        registered_model_name="gbr-car-mpg-predictor",
        artifact_path="gbr-car-mpg-predictor"
    ) # Register the model pipeline in MLflow

    mlflow.end_run()


if __name__ == '__main__':
    main()
