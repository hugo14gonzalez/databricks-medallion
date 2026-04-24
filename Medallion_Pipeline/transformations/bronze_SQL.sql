-- SQL en SDP NO soporta variables con interpolación ${} para nombres de tablas o rutas. Solo archivos Python (.py) soporta variables.

-- Variables de configuración
SET catalog_source = 'main';
SET schema_source = 'dbdemos_retail_c360';
SET volume_name_source = "c360";
SET volume_folder_source = f"/Volumes/${catalog_source}/${schema_source}/${volume_name_source}"
SET catalog_target = 'medallion_dev';
SET schema_target = 'bronze';

CREATE OR REFRESH STREAMING TABLE medallion_dev.bronze.churn_user_bronze
(
  CONSTRAINT correct_schema EXPECT (_rescued_data IS NULL)
)
COMMENT "Capa bronze: Datos sin procesar (raw) para el sistema de abandono (churn) de clientes. Datos de usuarios ingestados desde archivos JSON utilizando Auto Loader"
AS SELECT 
  *,
  _metadata.file_name AS ingest_file_name,
  current_timestamp() AS ingest_datetime
FROM STREAM(read_files(
  '/Volumes/main/dbdemos_retail_c360/c360/users',
  format => 'json',
  schemaEvolutionMode => 'addNewColumns'
));
