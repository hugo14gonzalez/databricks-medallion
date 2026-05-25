# Databricks notebook source
from pyspark.sql.functions import col
from pyspark.sql.functions import regexp_replace
#import pandas as pd 

# COMMAND ----------

success = True
result = 'Success'
try:
    # Hugo
    dbutils.widgets.text('ruta_catalogo',"/Volumes/kitvaloracion/base/4q23")

    #dbutils.widgets.text('ruta_catalogo','' )
    ruta = dbutils.widgets.get('ruta_catalogo')
    df = spark.createDataFrame(dbutils.fs.ls(ruta)).withColumn('name', regexp_replace(col('name'), ".$", "")).select(col('path'),col('name'))
    dbutils.jobs.taskValues.set(key = 'df_carpetas_catalogo', value = df.collect())
except Exception as ex:
    success = False
    result = 'Task Fail--> ### ' + str(ex) + ' ###'
    print(f'Resul: {result}')

# Hugo
display(df.collect())

dbutils.jobs.taskValues.set( key = "resultado", value = result)
dbutils.jobs.taskValues.set( key = 'estado', value = success)
