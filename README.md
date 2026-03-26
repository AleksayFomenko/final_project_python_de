# final_project

ETL pipeline на базе Apache Airflow и PySpark для загрузки данных из Parquet (Data Lake) в PostgreSQL (DWH) с поддержкой инкрементальной обработки и нормализации данных. Схемы данных и описание представленны в папке final_project/description/

---

# Структура проекта

<pre>
final_project/
├── airflow
│   ├──logs/
│   └──dags/
│       ├──read_parqet.py
│       ├──marts_dag.py 
│       └──data/
├── postgres_init/
│   └── init.sql
├── Dockerfile
├── docker-compose.yaml
├── requirements.txt
├── .env
└── README.md
</pre>

---

# Запуск

1. Склонируйте репозиторий
2. ```bash echo -e "AIRFLOW_UID=5000" > .env ```
3. ```bash docker compose --build ```
4. ```bash docker compose up -d ```
5. airflow - http://localhost:8080/
6. pg_admin - http://localhost:5050/

---

# Работа с airflow

1. Откройте ссылку http://localhost:8080/
2. Введите логин и пароль (airflow)
3. Перейдите во вкладку DAG
4. Запустите даг read_parquet_dag
5. Дождитесь окончания работы ETL pipeline
6. Запустите build_marts_dag
7. Дождитесь окончания работы ETL pipeline

---

# Результаты работы ETL pipeline в pg_admin

1. Откройте ссылку http://localhost:5050/
2. Добавьте подключение с параметрами:
- Host: `postgres`
- Port: `5432`
- Database: `airflow`
- User: `airflow`
- Password: `airflow`
3. Перейдите в базу airflow

---

# Описание схем БД

- **`dwh`** — слой ядра хранилища, содержащий нормализованные сущности.  
  Включает staging-таблицы (`*_tmp`), используемые для промежуточной загрузки и трансформации данных.

- **`marts`** — слой витрин данных, ориентированный на аналитические задачи.

