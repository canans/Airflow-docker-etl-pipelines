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

from airflow.utils.task_group import TaskGroup
from sqlalchemy import create_engine

@task
def get_source_data(ti=None):
    xy={"x":"y"}
    ti.xcom_push(key='value from pusher 1', value=xy)


with DAG(dag_id='xcom-canan',schedule_interval="0 9 * * *",start_date=datetime(2022, 6, 15),catchup=False) as dag:
    task=PythonOperator(
        task_id="test",
        python_callable=get_source_data,
        dag=dag
    )
    task