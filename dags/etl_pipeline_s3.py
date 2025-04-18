from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import boto3
import pandas as pd
import os

# Paramètres Object Storage
ACCESS_KEY = os.getenv("SCW_ACCESS_KEY")
SECRET_KEY = os.getenv("SCW_SECRET_KEY")
REGION = "fr-par"
ENDPOINT = f"https://s3.{REGION}.scw.cloud"
RAW_BUCKET = "raw-zone"
PROCESSED_BUCKET = "processed-zone"
RAW_FILE_KEY = "airtravel.csv"
PROCESSED_FILE_KEY = "processed.csv"

# Step 1: Extract depuis Object Storage
def extract():
    s3 = boto3.client(
        "s3",
        endpoint_url=ENDPOINT,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
    )
    s3.download_file(RAW_BUCKET, RAW_FILE_KEY, "/tmp/raw.csv")

# Step 2: Transform
def transform():
    df = pd.read_csv("/tmp/raw.csv")
    df["TOTAL"] = df.iloc[:, 1:].sum(axis=1)
    df.to_csv("/tmp/processed.csv", index=False)

# Step 3: Load dans Object Storage
def load():
    s3 = boto3.client(
        "s3",
        endpoint_url=ENDPOINT,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
    )
    s3.upload_file("/tmp/processed.csv", PROCESSED_BUCKET, PROCESSED_FILE_KEY)

# DAG definition
with DAG(
    dag_id="etl_s3_scaleway",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["scw", "etl"]
) as dag:

    t1 = PythonOperator(task_id="extract", python_callable=extract)
    t2 = PythonOperator(task_id="transform", python_callable=transform)
    t3 = PythonOperator(task_id="load", python_callable=load)

    t1 >> t2 >> t3
