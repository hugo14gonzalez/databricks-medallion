from pyspark import pipelines as dp
from pyspark.sql.functions import current_timestamp, col

# parametros
catalog_source = "main"
schema_source = "dbdemos_retail_c360"
volume_name_source = "c360"
volume_folder_source = f"/Volumes/{catalog_source}/{schema_source}/{volume_name_source}"
catalog_target = "medallion_dev"
bronze_schema_target = "bronze"

@dp.table(
    name=f"{catalog_target}.{bronze_schema_target}.churn_event_bronze",
    comment="Capa bronze: Datos sin procesar (raw) para el sistema de abandono (churn) de clientes. Datos de eventos y sesiones de aplicación ingestados desde archivos CSV utilizando Auto Loader",
    table_properties={
        "quality": "bronze",
        "layer": "bronze",
        "source_format": "csv",
        "delta.autoOptimize.optimizeWrite": "true",
        "delta.autoOptimize.autoCompact": "true"
    }
)
@dp.expect("correct_schema", "_rescued_data IS NULL")
def churn_event_bronze():
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("header", "true")
        .option("cloudFiles.inferColumnTypes", "true")
        .option("cloudFiles.schemaEvolutionMode", "addNewColumns")
        .load(f"{volume_folder_source}/events")
        .withColumn("ingest_file_name", col("_metadata.file_name"))
        .withColumn("ingest_datetime", current_timestamp())
    )

@dp.table(
    name=f"{catalog_target}.{bronze_schema_target}.churn_order_bronze",
    comment="Capa bronze: Datos sin procesar (raw) para el sistema de abandono (churn) de clientes. Datos de ordenes ingestados desde archivos JSON utilizando Auto Loader",
    table_properties={
        "quality": "bronze",
        "layer": "bronze",
        "source_format": "json",
        "delta.autoOptimize.optimizeWrite": "true",
        "delta.autoOptimize.autoCompact": "true"
    }
)
@dp.expect("correct_schema", "_rescued_data IS NULL")
def churn_order_bronze():
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.inferColumnTypes", "true")
        .option("cloudFiles.schemaEvolutionMode", "addNewColumns")
        .load(f"{volume_folder_source}/orders")
        .withColumn("ingest_file_name", col("_metadata.file_name"))
        .withColumn("ingest_datetime", current_timestamp())
    )
