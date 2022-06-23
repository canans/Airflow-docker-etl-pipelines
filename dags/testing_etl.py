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
from sqlalchemy import create_engine
import psycopg2


def get_source_data(**context):

    source_db_connection=MySqlHook(mysql_conn_id='mysql_con')
    sql="""SELECT 
            stx.ID AS STX_ID, 
            st.NAME as STORE_NAME,
            s.PAID_PRICE,
            stx.STATUS as TRX_STATUS,
            st.STATUS as STORE_STATUS ,
            st.LIVE_DATE as STORE_LIVE_DATE,
            s.CREATE_DATE AS SALES_CREATE_DATE
            FROM Sales_TX_T AS stx 
            LEFT JOIN Sales_T  AS s  ON stx.SALES_ID = s.ID
            LEFT JOIN Store_T AS st ON stx.STORE_ID = st.ID;"""
    source_db_result=source_db_connection.get_pandas_df(sql)
    tbl_dict = source_db_result.to_dict('dict')


    source_db_result["STORE_LIVE_DATE"] = pd.to_datetime(source_db_result["STORE_LIVE_DATE"])
    source_db_result["STORE_LIVE_DATE"] = pd.to_datetime(source_db_result["SALES_CREATE_DATE"])

    target_db_connection=BaseHook.get_connection(conn_id='postgres_conn')
    engine = create_engine(f'postgresql://{target_db_connection.login}:{target_db_connection.password}@{target_db_connection.host}:{target_db_connection.port}/{target_db_connection.schema}')
    connection_string = "host={0} user={1} dbname={2} password={3} ".format(target_db_connection.host,
                                                                            target_db_connection.login,
                                                                            target_db_connection.schema,
                                                                            target_db_connection.password)

    db_connection=psycopg2.connect(connection_string)
    cursor=db_connection.cursor()
    datas=source_db_result.values.tolist()

    for i in datas:
        sql = "INSERT INTO STORE_SALES  VALUES (%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(sql, tuple(i))
        db_connection.commit()



with DAG(dag_id='testing',schedule_interval="0 9 * * *",start_date=datetime(2022, 6, 15),catchup=False) as dag:


       task=PythonOperator(
           task_id="test",
           python_callable=get_source_data,
           provide_context=True,
           do_xcom_push=True,
           dag=dag
       )

       task




