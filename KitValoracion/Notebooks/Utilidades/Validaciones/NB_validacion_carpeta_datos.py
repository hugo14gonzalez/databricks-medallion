# Databricks notebook source
from pyspark.sql.functions import col, coalesce,regexp_replace, lower, when, concat_ws, lit
import json
import pandas as pd

# COMMAND ----------

#### TEST ###
#lectura del catalogo
# ruta = '/Volumes/test_data/base/4q23/'
# #ruta = '/Volumes/brz_lz_crudos/isa_transversal/vol_estructured_files/KitValoracion/2024/3Q24/'
# carpetas = spark.createDataFrame(dbutils.fs.ls(ruta))

# carpetas = carpetas\
#     .withColumn('name', regexp_replace(col('name'), '/', '') )\
#     .select(col('path'),col('name').alias('NombreCatalogo'))

# display(carpetas)

# COMMAND ----------

#Lectura archivo base
# df = pd.read_excel('/Workspace/Users/itco_e_jacevedo@intercolombia.com/NombreCarpetas.xlsx',engine='openpyxl',header=None)
# df_archivo = spark.createDataFrame(df)

# df_archivo = df_archivo\
#         .withColumnRenamed('0','NombreArchivo')\
#         .withColumnRenamed('1','Hoja')

# display(df_archivo)

# COMMAND ----------

success = True
result = 'Success'

try:
    archivo = dbutils.widgets.get('df_excel_base')
    df_archivo = spark.createDataFrame(json.loads(archivo))
    df_archivo = df_archivo\
        .withColumnRenamed('_1','NombreArchivo')\
        .withColumnRenamed('_2','HojaOrigen')\
        .withColumnRenamed('_3','HojaDestino')

    lectura_carpetas = dbutils.widgets.get('df_carpetas_catalogo')
    carpetas = spark.createDataFrame(json.loads(lectura_carpetas))
    carpetas = carpetas\
        .withColumnRenamed('_1','path')\
        .withColumnRenamed('_2','NombreCatalogo')
    

    df_join = carpetas\
            .join(df_archivo, lower(col('NombreCatalogo')) == lower(col('NombreArchivo')), 'full')

    #hugo
    print('df_join')
    display(df_join)

    df_faltantes = df_join\
        .filter(
            (col('NombreArchivo').isNull()) | 
            (col('NombreCatalogo').isNull())
        )\
    .withColumn('Restante',
                when(
                    col('NombreArchivo').isNull(),
                    concat_ws(
                        "",
                        lit('"'),
                        col('NombreCatalogo'),
                        lit('" no existe en el Archivo')
                    )
                )
                .otherwise(
                    concat_ws(
                        "",
                        lit('"'),
                        col('NombreArchivo'),
                        lit('" no existe en el Catálogo')
                    )
                )
            )\
    .select(col('Restante'))

    lista_faltantes = df_faltantes.collect()

    if len(lista_faltantes) > 0:
        result = 'Catalogos y Archivos no coinciden: \n'
        success = False
        for row in lista_faltantes:
            result = result + row[0] + '\n'
        
        print(result)
    else:
        success = True
        df_final = df_join.select(col('path'), col('NombreCatalogo'), col('HojaOrigen'),col('HojaDestino'))        
        dbutils.jobs.taskValues.set(key = 'df_base', value = df_final.collect())
         
except Exception as ex:
    success = False
    result = 'Task Fail--> ### ' + str(ex) + ' ###'
    print(f'Resul: {result}')

dbutils.jobs.taskValues.set( key = "resultado", value = result)
dbutils.jobs.taskValues.set( key = 'estado', value = success)    
