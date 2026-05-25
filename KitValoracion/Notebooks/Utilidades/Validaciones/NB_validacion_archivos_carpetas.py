# Databricks notebook source
from pyspark.sql.functions import col
from pyspark.sql.functions import regexp_replace
import json

# COMMAND ----------

#### TEST ###
#lectura del catalogo
# ruta = '/Volumes/test_data/base/4q23/'
# carpetas = spark.createDataFrame(dbutils.fs.ls(ruta)).withColumn('name', regexp_replace(col('name'), ".$", ""))

# display(carpetas)

# COMMAND ----------

# lectura_carpetas = dbutils.widgets.get('df_base')
# carpetas = spark.createDataFrame(json.loads(lectura_carpetas))
# carpetas = carpetas\
#     .withColumnRenamed('_1','path')\
#     .withColumnRenamed('_2','name')\
#     .withColumnRenamed('_3','Hoja')

# display(carpetas)

# COMMAND ----------

success = True
result = ''
trimestre = dbutils.widgets.get('Trimestre')
ano = dbutils.widgets.get('Anio')
ruta_archivo_destino = dbutils.widgets.get('ruta_kit_origen')
# Remover nombre del archivo
ruta_archivo_destino = f"dbfs:{ruta_archivo_destino.rsplit('/',1)[0]}/"
print(f'Ruta archivo destino: {ruta_archivo_destino}')

try:
    lectura_carpetas = dbutils.widgets.get('df_base')
    carpetas = spark.createDataFrame(json.loads(lectura_carpetas))
    carpetas = carpetas\
        .withColumnRenamed('_1','path')\
        .withColumnRenamed('_2','name')\
        .withColumnRenamed('_3','HojaOrigen')\
        .withColumnRenamed('_4','HojaDestino')

    paths = [row["path"] for row in carpetas.select("path").distinct().collect()]
    df_informacion = spark.createDataFrame([], schema='RutaArchivos STRING, CarpetaArchivos STRING')

    if len(paths) > 0:
        for folder in paths:
            print('')
            print(folder)
            print('*' * 30)
            if folder != ruta_archivo_destino:
                if len(dbutils.fs.ls(folder)) <= 0:
                    msg = f' --- hace falta archivos para la ruta "{folder}" \n '
                    result = result + msg
                    success = False
                    print(msg)
                else:
                    formato_archivo = False
                    for file in dbutils.fs.ls(folder):                    
                        if f'{trimestre}Q_{ano}' in file[1]:
                            formato_archivo = True
                            df_informacion = df_informacion.union(spark.createDataFrame([(str(file[0]),folder)], schema='RutaArchivos STRING, CarpetaArchivos STRING'))
                            break
                    
                if not formato_archivo:
                    msg = f' --- la carpeta {folder} no tiene archivo con el formato <<_"TrimestreEvaluar"Q_"AñoEvaluar".xlsx\n '
                    result = result + msg
                    success = False
                    print(msg)

    if success:
        df_final = df_informacion\
            .join(carpetas, col('CarpetaArchivos') == col('path'), 'inner')\
            .select(col('name'),col('RutaArchivos'),col('HojaOrigen'),col('HojaDestino'))

        dbutils.jobs.taskValues.set(key = 'df_listado_archivos', value = df_final.collect())

        #hugo
        print('df_final')
        display(df_final)
except Exception as ex:
    success = False
    result = 'Task Fail--> ### ' + str(ex) + ' ###'
    print(f'Resul: {result}')

dbutils.jobs.taskValues.set( key = "resultado", value = result)
dbutils.jobs.taskValues.set( key = 'estado', value = success)    
