from pyspark import pipelines as dp
from pyspark.sql.functions import current_timestamp, col, to_timestamp, initcap

# Parámetros
catalog_target = "medallion_dev"
bronze_schema_source = "bronze"
silver_schema_target = "silver"

@dp.table(
    name=f"{catalog_target}.{silver_schema_target}.churn_user_silver",
    comment="Capa silver: Datos limpios y transformados del sistema de abandono (churn) de clientes. Datos de usuarios con tipos corregidos y validaciones aplicadas",
    table_properties={
        "quality": "silver",
        "layer": "silver",
        "delta.enableChangeDataFeed": "true",
        "delta.autoOptimize.optimizeWrite": "true",
        "delta.autoOptimize.autoCompact": "true"
    }
)
@dp.expect_or_drop("id_valid", "id IS NOT NULL")
def churn_user_silver():
    return (
        spark.readStream.table(f"{catalog_target}.{bronze_schema_source}.churn_user_bronze")
        .drop("ingest_datetime", "ingest_file_name", "_rescued_data")
        .withColumn("creation_date", to_timestamp(col("creation_date"), "MM-dd-yyyy HH:mm:ss"))
        .withColumn("last_activity_date", to_timestamp(col("last_activity_date"), "MM-dd-yyyy HH:mm:ss"))
        .withColumn("firstname", initcap(col("firstname")))
        .withColumn("lastname", initcap(col("lastname")))
        .withColumn("gender", col("gender").cast("int"))
        .withColumn("age_group", col("age_group").cast("int"))
        .withColumn("churn", col("churn").cast("int"))
        .withColumn("ingest_datetime_silver", current_timestamp())
    )

# Vista staging temporal para transformaciones antes de CDC
@dp.temporary_view(
    name="v_churn_order_silver_staging",
    comment="Vista temporal staging: Transformaciones de órdenes antes de aplicar CDC upsert"
)
@dp.expect_or_drop("user_id_valid", "user_id IS NOT NULL")
@dp.expect_or_drop("order_id_valid", "order_id IS NOT NULL")
def v_churn_order_silver_staging():
    return (
        spark.readStream.table(f"{catalog_target}.{bronze_schema_source}.churn_order_bronze")
        .drop("ingest_datetime", "ingest_file_name", "_rescued_data")
        .withColumnRenamed("id", "order_id")
        .withColumnRenamed("transaction_date", "creation_date")
        .withColumn("creation_date", to_timestamp(col("creation_date"), "MM-dd-yyyy HH:mm:ss"))
        .withColumn("amount", col("amount").cast("int"))
        .withColumn("item_count", col("item_count").cast("int"))
        .withColumn("ingest_datetime_silver", current_timestamp())
    )

# Tabla destino para CDC con capacidades de upsert (SCD Type 1)
dp.create_streaming_table(
    name=f"{catalog_target}.{silver_schema_target}.churn_order_silver",
    comment="Capa silver: Datos limpios y transformados del sistema de abandono (churn) de clientes. Datos de ordenes con CDC upsert (SCD Type 1)",
    table_properties={
        "quality": "silver",
        "layer": "silver",
        "delta.enableChangeDataFeed": "true",
        "delta.autoOptimize.optimizeWrite": "true",
        "delta.autoOptimize.autoCompact": "true",
    },
)

# Flujo CDC con SCD Type 1 (upserts: inserts + updates)
dp.create_auto_cdc_flow(
    target=f"{catalog_target}.{silver_schema_target}.churn_order_silver",
    source="v_churn_order_silver_staging",
    keys=["order_id", "user_id"],
    sequence_by="ingest_datetime_silver",
    stored_as_scd_type=1
)
