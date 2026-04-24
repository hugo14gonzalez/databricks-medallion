from pyspark import pipelines as dp
from pyspark.sql.functions import col, count, countDistinct, max as max_, sum as sum_, first, to_timestamp, datediff, current_date

# Parámetros
catalog_target = "medallion_dev"
bronze_schema_source = "bronze"
silver_schema_source = "silver"
gold_schema_target = "gold"
model_predict_churn = "predict_customer_churn"

# Pendiete: crear modelo ML
# ----------------------------------
# Cargar modelos ML y registrarlos como UDF. 
# Cargar el modelo de predición de abandono (churn) del cientes desde el registro MLflow y registrarlo para usos en predicciones.
# ----------------------------------
#import mlflow
#mlflow.set_registry_uri('databricks-uc')

## @prod: version del modelo
#predict_churn_udf = mlflow.pyfunc.spark_udf(spark, "models:/{catalog_target}.{gold_schema_target}.{model_predict_churn}@prod", #"long", env_manager='virtualenv')
#spark.udf.register("predict_churn", predict_churn_udf)

# ----------------------------------
# Aplicar modelo ML model para predecir abandono (churn) de clientes
# Utilice predict_churn UDF para puntear cada cliente.
# Identificar clientes en riesgo de abandono (churn) basado en sus características de comportamiento y demográficas.
# ----------------------------------
#model_features = predict_churn_udf.metadata.get_input_schema().input_names()

#@dp.materialized_view(comment="Predicción de clientes en riesgo de abandono (churn)")
#def vm_churn_prediction():
#  return (
#          spark.read.table(f"{catalog_target}.{gold_schema_target}.vm_churn_feature")
#          .withColumn('churn_prediction', predict_churn_udf(*model_features)))