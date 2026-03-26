from airflow import DAG
from datetime import datetime
from airflow.operators.python import PythonOperator
from pyspark.sql import SparkSession
import pyspark.sql.functions as F

POSTGRES_URL = "jdbc:postgresql://postgres:5432/airflow"
POSTGRES_PROPERTIES = {
    "user": "airflow",
    "password": "airflow",
    "driver": "org.postgresql.Driver"
}


def get_spark():
    return SparkSession.builder \
        .appName("build_marts") \
        .master("local[*]") \
        .config("spark.jars.packages", "org.postgresql:postgresql:42.7.3") \
        .getOrCreate()


def read_table(spark, table):
    return spark.read.jdbc(POSTGRES_URL, table, properties=POSTGRES_PROPERTIES)


def write_mart(df, table):
    df.write \
        .format("jdbc") \
        .option("url", POSTGRES_URL) \
        .option("dbtable", table) \
        .option("user", POSTGRES_PROPERTIES["user"]) \
        .option("password", POSTGRES_PROPERTIES["password"]) \
        .option("driver", POSTGRES_PROPERTIES["driver"]) \
        .option("truncate", "true") \
        .mode("overwrite") \
        .save()


def build_dm_orders_stats():
    spark = get_spark()

    orders = read_table(spark, "dwh.orders")
    order_items = read_table(spark, "dwh.order_items")
    stores = read_table(spark, "dwh.stores").withColumnRenamed("address", "store_address")

    items_agg = order_items.groupBy("order_id").agg(
        F.sum(F.col("price") * F.col("quantity") - F.col("item_discount")).alias("items_turnover"),
        F.sum(F.when(F.col("item_replaced_id").isNotNull(), 1).otherwise(0)).alias("has_replacement")
    )

    df = orders \
        .join(items_agg, "order_id", "left") \
        .join(stores, "store_id", "left") \
        .withColumn("dt", F.to_date("created_at")) \
        .withColumn("year", F.year("created_at")) \
        .withColumn("month", F.month("created_at")) \
        .withColumn("turnover",
            F.coalesce(F.col("items_turnover"), F.lit(0))) \
        .withColumn("revenue",
            F.coalesce(F.col("items_turnover"), F.lit(0)) - F.coalesce(F.col("order_discount"), F.lit(0))) \
        .withColumn("profit",
            F.coalesce(F.col("items_turnover"), F.lit(0))
            - F.coalesce(F.col("order_discount"), F.lit(0))
            - F.coalesce(F.col("delivery_cost"), F.lit(0))) \
        .withColumn("is_delivered",
            F.when(F.col("delivered_at").isNotNull(), 1).otherwise(0)) \
        .withColumn("is_canceled",
            F.when(F.col("canceled_at").isNotNull(), 1).otherwise(0)) \
        .withColumn("is_canceled_after_delivery",
            F.when(
                F.col("canceled_at").isNotNull() & F.col("delivered_at").isNotNull(), 1
            ).otherwise(0)) \
        .withColumn("is_service_error",
            F.when(
                F.col("order_cancellation_reason").isin("Ошибка приложения", "Проблемы с оплатой"), 1
            ).otherwise(0))

    dm = df.groupBy("dt", "year", "month", "store_id", "store_address") \
        .agg(
            F.sum("turnover").alias("turnover"),
            F.sum("revenue").alias("revenue"),
            F.sum("profit").alias("profit"),
            F.count("order_id").alias("orders_count"),
            F.sum("is_delivered").alias("delivered_count"),
            F.sum("is_canceled").alias("canceled_count"),
            F.sum("is_canceled_after_delivery").alias("canceled_after_delivery"),
            F.sum("is_service_error").alias("service_error_cancels"),
            F.countDistinct("user_id").alias("buyers_count"),
            F.avg("revenue").alias("avg_check"),
            F.countDistinct("driver_id").alias("active_couriers"),
            F.sum("has_replacement").alias("courier_changes")
        ) \
        .withColumn("orders_per_buyer",
            F.col("orders_count") / F.col("buyers_count")) \
        .withColumn("revenue_per_buyer",
            F.col("revenue") / F.col("buyers_count"))

    write_mart(dm, "marts.dm_orders_stats")
    spark.stop()


def build_dm_items_stats():
    spark = get_spark()

    orders = read_table(spark, "dwh.orders")
    order_items = read_table(spark, "dwh.order_items")
    items = read_table(spark, "dwh.items").withColumnRenamed("title", "item_title")
    stores = read_table(spark, "dwh.stores").withColumnRenamed("address", "store_address")

    df = order_items \
        .join(
            orders.select("order_id", "store_id", "created_at", "canceled_at"),
            "order_id", "left"
        ) \
        .join(items, "item_id", "left") \
        .join(stores, "store_id", "left") \
        .withColumn("dt", F.to_date("created_at")) \
        .withColumn("year", F.year("created_at")) \
        .withColumn("month", F.month("created_at")) \
        .withColumn("item_turnover_row",
            F.col("price") * F.col("quantity") - F.col("item_discount")) \
        .withColumn("is_canceled_item",
            F.when(F.col("canceled_quantity") > 0, 1).otherwise(0))

    dm = df.groupBy("dt", "year", "month", "store_id", "store_address", "item_id", "item_title", "item_category") \
        .agg(
            F.sum("item_turnover_row").alias("item_turnover"),
            F.sum("quantity").alias("ordered_quantity"),
            F.sum("canceled_quantity").alias("canceled_quantity"),
            F.countDistinct("order_id").alias("orders_with_item"),
            F.sum("is_canceled_item").alias("orders_with_cancel")
        )

    write_mart(dm, "marts.dm_items_stats")
    spark.stop()


with DAG(
    dag_id="build_marts_dag",
    start_date=datetime(2026, 3, 22),
    schedule_interval="@daily",
    catchup=False,
    tags=["spark", "marts"]
) as dag:

    dm_orders_task = PythonOperator(
        task_id="dm_orders_stats",
        python_callable=build_dm_orders_stats
    )

    dm_items_task = PythonOperator(
        task_id="dm_items_stats",
        python_callable=build_dm_items_stats
    )

    dm_orders_task >> dm_items_task
