from pyspark import pipelines as dp
from pyspark.sql.functions import col, count, countDistinct, max as max_, sum as sum_, first, to_timestamp, datediff, current_date

# Parámetros
catalog_target = "medallion_dev"
bronze_schema_source = "bronze"
silver_schema_source = "silver"
gold_schema_target = "gold"

@dp.materialized_view(
    name=f"{catalog_target}.{gold_schema_target}.vm_churn_feature",
    comment="Capa gold: Vista materializada features con datos enriquecidos y agregados para análisis de abandono (churn) de clientes en modelos ML. Las caracteristicas incluyen estadisticas de usuarios, eventos y ordenes",
    table_properties={
        "quality": "gold",
        "layer": "gold"
    }
)
def vm_churn_feature():
    # DataFrame de eventos agregados por user_id
    events_df = (
        spark.read.table(f"{catalog_target}.{bronze_schema_source}.churn_event_bronze")
        .withColumn("date", to_timestamp(col("date"), "MM-dd-yyyy HH:mm:ss"))
        .groupBy("user_id")
        .agg(
            first("platform").alias("platform"),
            count("*").alias("event_count"),
            countDistinct("session_id").alias("session_count"),
            max_("date").alias("last_event")
        )
    )
    
    # DataFrame de ordenes agregadas por user_id
    orders_df = (
        spark.read.table(f"{catalog_target}.{silver_schema_source}.churn_order_silver")
        .groupBy("user_id")
        .agg(
            count("*").alias("order_count"),
            sum_("amount").alias("total_amount"),
            sum_("item_count").alias("total_item"),
            max_("creation_date").alias("last_transaction")
        )
    )
    
    # Join de usuarios con eventos y ordenes
    return (
        spark.read.table(f"{catalog_target}.{silver_schema_source}.churn_user_silver")
        .withColumnRenamed("id", "user_id")
        .alias("users")
        .join(events_df.alias("events"), col("users.user_id") == col("events.user_id"), "inner")
        .join(orders_df.alias("orders"), col("users.user_id") == col("orders.user_id"), "inner")
        .select(
            col("users.*"),
            col("events.platform"),
            col("events.event_count"),
            col("events.session_count"),
            col("events.last_event"),
            col("orders.order_count"),
            col("orders.total_amount"),
            col("orders.total_item"),
            col("orders.last_transaction"),
            datediff(current_date(), col("users.creation_date")).alias("days_since_creation"),
            datediff(current_date(), col("users.last_activity_date")).alias("days_since_last_activity"),
            datediff(current_date(), col("events.last_event")).alias("days_last_event")
        )
    )