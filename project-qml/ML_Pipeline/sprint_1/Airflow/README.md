# [Dockerize] Apache Airflow
## Steps:
Download Airflow yaml file
1. wget https://airflow.apache.org/docs/apache-airflow/stable/docker-compose.yaml

Build container
1. mkdir dags plugins logs
2. echo -e "AIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0" > .env
3. docker-compose up airflow-init

Run
1. docker-compose up
2. http://localhost:8080/

## Result:
![img](result.png)

## Reference:
Build Airflow container
* https://www.youtube.com/watch?v=aTaytcxy2Ck
