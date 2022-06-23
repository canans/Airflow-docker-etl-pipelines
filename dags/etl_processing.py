from airflow import DAG
from datetime import datetime, timedelta
from airflow.hooks.base_hook import BaseHook
from airflow.decorators import task
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.mysql_operator import MySqlOperator
from airflow.providers.mysql.hooks.mysql import MySqlHook
from airflow.operators.email_operator import EmailOperator
from datetime import datetime,timedelta
import pandas as pd
from airflow.utils.task_group import TaskGroup
from flask import jsonify
from sqlalchemy import create_engine
import psycopg2
from airflow.models import Variable
import numpy as np
from airflow import AirflowException


def get_source_data(**kwargs):
    ti = kwargs['ti']
    source_db_connection = MySqlHook(mysql_conn_id='mysql_con')
    extraction_sql=Variable.get("extraction_sql",deserialize_json=True)
    source_db_store_result = source_db_connection.get_pandas_df(extraction_sql['store_sql'])
    source_db_customer_result=source_db_connection.get_pandas_df(extraction_sql['customer_sql'])
    source_db_store_result=source_db_store_result.to_dict('records')
    source_db_customer_result=source_db_customer_result.to_dict('records')
    print("source_db_store_result", source_db_store_result)
    print("source_db_customer_result", source_db_customer_result)
    ti.xcom_push('extract_data', {"store_result":source_db_store_result,"customer_result":source_db_customer_result})

def transform_data(**kwargs):
    ti = kwargs['ti']
    extract_data = ti.xcom_pull(task_ids='extract', key='extract_data')
    source_db_store_result=extract_data["store_result"]
    source_db_customer_result = extract_data["customer_result"]

    for record in source_db_store_result:
        for key,value in record.items():
        # do something with value
            if value=="None" or value!=value :
                record[key] = None

    for record in source_db_customer_result:
        for key, value in record.items():
            # do something with value
            if value == "None" or value!=value :
                record[key] = None

    ti.xcom_push('extract_data', {"store_result": source_db_store_result, "customer_result": source_db_customer_result})


def load_data(**kwargs):
    ti = kwargs['ti']
    extract_data = ti.xcom_pull(task_ids='transform', key='extract_data')
    source_db_store_result = extract_data["store_result"]
    source_db_customer_result = extract_data["customer_result"]

    target_db_connection = BaseHook.get_connection(conn_id='postgres_conn')
    connection_string = "host={0} user={1} dbname={2} password={3} ".format(target_db_connection.host,
                                                                            target_db_connection.login,
                                                                            target_db_connection.schema,
                                                                            target_db_connection.password)

    db_connection = psycopg2.connect(connection_string)
    target_db_cursor = db_connection.cursor()

    target_db_cursor.execute("Truncate Customer,store_sales;")
    print(source_db_store_result)

    for i in source_db_store_result:

        sql = "INSERT INTO  Store_Sales (STX_ID,STORE_NAME,PAID_PRICE,TRX_STATUS,STORE_STATUS,STORE_LIVE_DATE,SALES_CREATE_DATE) VALUES (%s,%s,%s,%s,%s,%s,%s);"

        #print(sql%tuple(i.values()))
        try:
            target_db_cursor.execute(sql, tuple(i.values()))
            db_connection.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            raise AirflowException(error)



    for j in source_db_customer_result:
        sql = "INSERT INTO customer (ID,NAME,CITY,CREATE_DATE) VALUES (%s,%s,%s,%s);"
        try:
            target_db_cursor.execute(sql, tuple(j.values()))
            db_connection.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            raise AirflowException(error)


    db_connection.close()

with DAG(dag_id='etl-processing',schedule_interval='*/20 * * * *',start_date=datetime(2022, 6, 15),catchup=False) as dag:

    extract = PythonOperator(
            task_id = "extract",
            python_callable = get_source_data,

            )
    transform = PythonOperator(
            task_id = "transform",
            python_callable = transform_data,

            )

    load = PythonOperator(
        task_id="load",
        python_callable=load_data,

    )
    health_check = BashOperator(
        task_id='health_check',
        bash_command='health_check.sh',

    )

    extract>>transform>>load>>health_check