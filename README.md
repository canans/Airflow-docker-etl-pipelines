
ETL PROCESSING--->/dags/etl_processing.py


---airflow init command

docker-compose up airflow-init

--docker-compose up

docker-compose up

---mysql---
docker-compose -f stack.yaml up
docker exec -it b7d87e5f4405 /bin/bash

--postgre schema
\dn  
\c
\ı
------
docker exec -it 8569ceda9b8b psql -U airflow -d postgres
select * from store_sales 
select * from Customer 

---mysql---
docker-compose down stack.yaml
docker-compose -f stack.yaml up
docker exec -it b7d87e5f4405 /bin/bash
mysql -uroot -p




psql -u airflow -h localhost -d airflow -p 5432

createuser -U postgres -s root

createdb -h localhost -p 5432 -U postgres testdb 

ALTER USER airflow WITH PASSWORD '1234';


docker inspect 309c3150971b# Airflow-docker-etl-pipelines
