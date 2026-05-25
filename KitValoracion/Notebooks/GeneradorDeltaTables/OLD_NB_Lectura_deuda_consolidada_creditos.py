# Databricks notebook source
import pyspark.sql.functions as F
from pyspark.sql.functions import col, lit, concat_ws
from pyspark.sql.window import Window
from datetime import datetime 
import unicodedata
import re


# COMMAND ----------

compania_URL = '/Volumes/test_data/base/4q23/Deuda/01 Deuda_Jun2024 - VF.xlsx'
inicio_datos = 1
inicio_datos = 'A10'

# COMMAND ----------

df_inicial = spark.read.format("com.crealytics.spark.excel") \
    .option("header", "false") \
    .option("treatEmptyValuesAsNulls", "true")\
    .option("setErrorCellsToFallbackValues", "true")\
    .option("inferSchema", "false")\
    .option("dataAddress", f"'{hoja}'!{inicio_datos}") \
    .load(compania_URL)

display(df_inicial)

# COMMAND ----------

df_unido = df_inicial\
    .withColumn("_c6", concat_ws('', col('_c6'), col('_c7'), col('_c8')))\
    .drop(col('_c7'),col('_c8'),col('_c9'),col('_c13'),col('_c14'))
display(df_unido)

# COMMAND ----------

nuevos_encabezados = df_unido.head(1)[0]

df_base = df_unido\
    .toDF(*nuevos_encabezados)\
    .filter(
        (col('Filial') != 'Filial') |
        (col('Filial').isNull() == True) 
    )\
    .dropna(how="all")

df_base = df_base\
    .filter(
        (col('Filial') != '(1) Bonos emitidos en PEN y se hizo un SWAP a USD con el Banco BBVA.') |
        (col('Filial').isNull() == True) 
    )

df_base = df_base\
    .filter(
        (col('Filial') != '(2) Bonos emitidos en USD y se hizo un SWAP a UF.') |
        (col('Filial').isNull() == True) 
    )

df_base = df_base\
    .filter(
        (col('Filial') != '(3) Opcion Call') |
        (col('Filial').isNull() == True) 
    )

df_base = df_base\
    .filter(
        (col('Filial') != 'Bonos Verdes') |
        (col('Filial').isNull() == True) 
    )

display(df_base)

# COMMAND ----------

new_cols = ["".join(
    ch for ch in re.sub(
                        r'[^A-Za-z0-9_]', '', unicodedata.normalize("NFD", c).replace("\n", "").replace(" ", "")
                    )  
                    if not unicodedata.combining(ch)
                ) 
                for c in df_base.columns]
                
df_base = df_base.toDF(*new_cols)
display(df_base)

# COMMAND ----------

df_limpio = df_base\
    .withColumn(
        "FechaInicial",
        F.when(
            F.col("FechaInicial").isNotNull(),
            F.expr("date_add('1899-12-30', cast(`FechaInicial` as int))")
        )
    )\
    .withColumn(
        "FechaVencimiento",
        F.when(
            F.col("FechaVencimiento").isNotNull(),
            F.expr("date_add('1899-12-30', cast(`FechaVencimiento` as int))")
        )
    )\
    .withColumn(
        "PlazoAnos",
        F.when(
            F.col("PlazoAnos").isNotNull(),
            F.expr("cast(`PlazoAnos` as int)")
        )
    )\
    .withColumn(
        "Jun2024monedadelcredito",
        F.col("Jun2024monedadelcredito").cast("decimal(20,0)")
    )\
    .withColumn(
        "Jun2024millonesdeCOP",
        F.col("Jun2024millonesdeCOP").cast("decimal(10,0)")
    )\
    .withColumn(
        "Jun2024milesUSD",
        F.col("Jun2024milesUSD").cast("decimal(10,0)")
    )
display(df_limpio)

# COMMAND ----------

# Supongamos que tu DataFrame se llama df y tiene columnas: "Descripcion" (string), "valor" (numérico o null)

# 1) Creamos un ID para preservar el orden original de las filas
df1 = df_limpio.withColumn("row_id", F.monotonically_increasing_id())

# 2) Marcamos filas de país y filas de compañía
#    - Fila de "país": Descripcion != null, valor == null
#    - Fila de "compañía" (o su "marker"): Descripcion != null y valor != null
#      (o, si tu lógica requiere, puede ser Descripcion != null sin importar valor,
#       y luego filtras al final las que tengan valor no nulo)
df2 = df1.withColumn(
    "is_pais",
    (F.col("Filial").isNotNull()) & (F.col("FuentedeFinanciacion").isNull())
).withColumn(
    "is_compania_marker",
    (F.col("Filial").isNotNull()) & (F.col("FuentedeFinanciacion").isNotNull())
)

# 3) Creamos columnas 'pais_marker' y 'compania_marker' con el texto de Descripcion
#    solo en las filas correspondientes
df3 = df2.withColumn(
    "pais_marker",
    F.when(F.col("is_pais"), F.col("Filial"))
).withColumn(
    "compania_marker",
    F.when(F.col("is_compania_marker"), F.col("Filial"))
)

# 4) Definimos una ventana que recorra las filas en orden de row_id
#    y haga un "forward fill" (último valor no nulo) hasta la fila actual
w = Window.orderBy("row_id").rowsBetween(Window.unboundedPreceding, 0)

df4 = df3.withColumn(
    "Pais",
    F.last("pais_marker", ignorenulls=True).over(w)
).withColumn(
    "Compania",
    F.last("compania_marker", ignorenulls=True).over(w)
)

# 5) Filtramos para quedarnos solo con las filas que tengan un valor no nulo
#    (son las filas "compañía" y las filas donde Descripcion era null pero la compañía ya está arrastrada)
df5 = df4.filter(F.col("FuentedeFinanciacion").isNotNull())

# 6) Seleccionamos las columnas finales:

df_ultimo = df5.select(
    "Compania",
    "Pais",
    "FuentedeFinanciacion",
    "MonedaCredito",
    "FechaInicial",
    "FechaVencimiento",
    "PlazoAnos",
    "TasadeInteres",
    "Jun2024monedadelcredito",
    "Jun2024millonesdeCOP",
    "Jun2024milesUSD"
)

display(df_ultimo)


# COMMAND ----------

fecha = datetime.now()
df_ultimo = df_ultimo\
    .withColumn("FECHAPUBLICACION", lit(fecha))
    

display(df_ultimo)

# COMMAND ----------

#Guardamos en el DeltaTable
df_ultimo.write \
    .format("delta") \
    .mode("overwrite") \
    .partitionBy("Pais","Compania") \
    .save("/Volumes/test_data/base/deltatables/Deuda Creditos/")

