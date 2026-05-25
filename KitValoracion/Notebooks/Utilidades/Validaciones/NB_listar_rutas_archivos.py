# Databricks notebook source
from pyspark.sql.functions import col, count, element_at, regexp_replace, split,row_number
from pyspark.sql import Row
from datetime import datetime
from pyspark.sql.window import Window
import json


# COMMAND ----------

archivo = dbutils.widgets.get('df_excel_base')
df_base = spark.createDataFrame(json.loads(archivo))
df_base = df_base\
    .withColumnRenamed('_1','Carpeta')\
    .withColumnRenamed('_2','Hoja')

# COMMAND ----------

lectura_carpetas = dbutils.widgets.get('df_carpetas_catalogo')
carpetas = spark.createDataFrame(json.loads(lectura_carpetas))
carpetas = carpetas\
    .withColumnRenamed('_1','path')\
    .withColumnRenamed('_2','name')


# COMMAND ----------

paths = [row["path"] for row in carpetas.select("path").distinct().collect()]
df_informacion = spark.createDataFrame([], schema='NombreCarpeta STRING, RutaArchivos STRING')
for data in paths:
    nombre_dato = carpetas.select('name').where(col('path') == data).first()['name']
    for file in dbutils.fs.ls(data):
        df_informacion = df_informacion.union(spark.createDataFrame([(nombre_dato, file[0])], schema='NombreCarpeta STRING, RutaArchivos STRING'))
    #print('-' * 100)

#display(df_informacion)

# COMMAND ----------

df_join =  df_base.join(df_informacion, df_base.Carpeta == df_informacion.NombreCarpeta, 'inner').select(col('NombreCarpeta'), col('Hoja'), col('RutaArchivos'))

# COMMAND ----------

df_completo = df_join.withColumn(
    "Archivo",
    element_at(
        split(
            # 1) Elimina el slash final (si lo hay)
            regexp_replace(col("RutaArchivos"), "/$", ""),
            "/"
        ),
        -1  # 2) Toma el último elemento del array resultante
    )
)


# COMMAND ----------

df_individual_data = (
    df_completo.groupBy("NombreCarpeta")
      .agg(count("Archivo").alias("num_archivos"))
      .filter(col("num_archivos") == 1)
      .join(df_completo, on="NombreCarpeta", how="inner")
      .select(col('NombreCarpeta'),col('Hoja'),col('RutaArchivos'),col('Archivo'))
)


# COMMAND ----------


ano_actual = '2023' #f'{datetime.now().year}'
mes_actual = f'{datetime.now().month}'

trimestre_actual = '3'#f'{(mes_actual - 1) // 3 + 1}

df_trimestre_actual = df_completo.filter(
    (col('Archivo').like(f'%Q{trimestre_actual}%')) |
    (col('Archivo').like(f'%{trimestre_actual}Q%')) |
    (col('Archivo').like(f'%T{trimestre_actual}%')) |
    (col('Archivo').like(f'%{trimestre_actual}T%')) 
    
    
)


# COMMAND ----------

df_union = df_individual_data.union(df_trimestre_actual).distinct()

# COMMAND ----------

df_carpetas = df_completo.groupBy(col('NombreCarpeta')).count().select('NombreCarpeta')

# COMMAND ----------


# Join df_carpetas and df_union using left anti join and select 'NombreCarpeta'
df_filtered = df_carpetas.join(
    df_union,
    df_union.NombreCarpeta == df_carpetas.NombreCarpeta,
    'left_anti'
).select('NombreCarpeta')

# Filter df_completo based on the result of the join
df_diff = df_completo.filter(col('NombreCarpeta').isin([row.NombreCarpeta for row in df_filtered.collect()]))

# Further filter df_diff based on 'Archivo' column
df_diff = df_diff.filter(
    (col('Archivo').like('%2023%')) |
    (col('Archivo').like('%23%'))
)

display(df_diff)

# COMMAND ----------

# Define una ventana que particiona por 'nombre'
window_spec = Window.partitionBy("NombreCarpeta").orderBy("Archivo")

# Asigna un número a cada fila dentro del grupo
df_con_indices = df_diff.withColumn("row_num", row_number().over(window_spec))

df_primeros = df_con_indices.filter("row_num = 1").drop("row_num")

# COMMAND ----------

df_final = df_union.union(df_primeros)

dbutils.jobs.taskValues.set(key = 'df_listado_archivos', value = df_final.collect())
