# Databricks notebook source
#Hugo
#%pip install openpyxl
#dbutils.library.restartPython()

# COMMAND ----------

import pandas as pd
#dbutils.widgets.removeAll()

# COMMAND ----------

#Hugo
dbutils.widgets.text('ruta_excel_base', "/Volumes/kitvaloracion/base/config/NombreCarpetas.xlsx")

#dbutils.widgets.text('ruta_excel_base','' )
parametro_ruta = dbutils.widgets.get('ruta_excel_base')

# COMMAND ----------

success = True
result = 'Success'

try:
    df = pd.read_excel(parametro_ruta,engine='openpyxl',header=None)
    df = spark.createDataFrame(df)
    dbutils.jobs.taskValues.set(key = 'df_excel_base', value = df.collect())
except Exception as ex:
    success = False
    result = 'Task Fail--> ### ' + str(ex) + ' ###'
    print(f'Resul: {result}')

# Hugo
print(f"success: {success}")
print(f"result: {result}")
display(df.collect())

dbutils.jobs.taskValues.set( key = "resultado", value = result)
dbutils.jobs.taskValues.set( key = 'estado', value = success)
