from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import os

# Step 1: Extract
def extract():
    url = "https://people.sc.fsu.edu/~jburkardt/data/csv/airtravel.csv"
    df = pd.read_csv(url)
    df.to_csv("/tmp/raw.csv", index=False)

# Step 2: Transform
def transform():
    df = pd.read_csv("/tmp/raw.csv")
    df["TOTAL"] = df.iloc[:, 1:].sum(axis=1)
    df.to_csv("/tmp/processed.csv", index=False)

# Step 3: Load (just print for now)
def load():
    with open("/tmp/processed.csv") as f:
        print(f.read())

# DAG definition
with DAG(
    dag_id="simple_etl_demo",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["demo"]
) as dag:

    t1 = PythonOperator(task_id="extract", python_callable=extract)
    t2 = PythonOperator(task_id="transform", python_callable=transform)
    t3 = PythonOperator(task_id="load", python_callable=load)

    t1 >> t2 >> t3

