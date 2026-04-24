# Databricks-Medallion
Demo arquitectura Dababricks medallas (medallion)

Este proyecto fue creado por:
Hugo González Olaya
hugo14.gonzalez@gmail.com

Para el demo sera utilizado el conjunto de datos de Databricks en el volumen: Sample, esquema: bakehouse.
Este esquema tiene las tablas:
- media_customer_reviews: Reseña realizada por los clientes
- media_gold_revies_chunked: Detalles de la reseña
- sales_customers: Clientes
- sales_franchises: Franquicias
- sales_suppliers: Proveedores
- sales_transactios: Ventas de la tienda

NOTA: En este proyecto solo va a utilizar las tablas sales_*

## Notebooks
1. Bakehouse_Delete: Borra los objetos
2. bakehouse_create: Crea los objetos
3. bakehouse_grant: Asigna permisos
4. bakehouse_insert_Raw_Bronze: Inserta datos en las tablas del esquema Raw y Bronze
5. bakehouse_Insert_Silver: Inserta datos en las tablas del esquema Silver
6. bakehouse_Insert_Gold: Inserta datos en las tablas del esquema Gold

## Almacenamiento de datos

### Catalogo
Los datos son almacenados en el catalogo indicado en los parametros de los Notebooks.
Por defecto el nombre del catalogo es: bakehouse_dev

### Esquemas
Los cuadernos crean y procesan los datos en los esquemas
- Raw
- Bronze
- Silver
- Gold

### Tablas
Los nombres de las tablas tienen el formato: tabla_{Esquema}
Todas las tablas son cargadas en el esquema Raw y Bronze
En los esquemas Silver y Gold solo será poblada la tabla: Customers

## Transformaciones
1. Raw: 
Esta capa simula un origen de datos, en esta capa, los datos son copiados del origen sin ninguna transformacion.

2. Bronze: 
La capa bronze es la primera capa, los datos son copiados de la capa Raw sin ninguna transformacion.

3. Silver:
En esta capa es realizado proceso de limpieza, calida de datos y algunas transformaciones.

En la tabla de clientes son realizado las siguientes transformaciones:
* Adicionado un capo de metadatos con la fecha y hora de modificación
* Chequear si la columna CustomerID tiene nulos y borrar la fila
* Borrar filas repetidas
* Estandarizar el formato del campo numero telefónico a 14 caracteres: (XXX)-XXX-XXX-XXXXX
* El campo genero cambiar de texto (female, male) a boleano
* Convertir a mayúsculas el campo continente
* En el campo estado, algunos estados aparecen con dos letras o el nombre del estado, las dos letras es remplazado con el nombre del estado usando un diccionario de datos creado para realizar esta transformacion.
* Al finalizar las columnas son organizadas y copiadas de la capa bronze a Silver

4. Gold
Para la tabla de clientes son realizadas las siguientes agrupaciones
* Contar numero de clientes diferentes por pais, y contar número de clientes diferentes por pais y estado.

## Work Flow
El proyecto también cuenta con un WorkFlow que ejecuta todos los notebooks.
Tiene una agenda diaria pero esta deshabilitada.

El orden de ejecución es el siguiente
1. Bakehouse_Delete
2. bakehouse_create
3. bakehouse_grant
3. bakehouse_insert_Raw_Bronze
4. bakehouse_Insert_Silver
5. bakehouse_Insert_Gold

Las tareas de asignar permisos e insertar en raw y bronze corren en paralelo.
La tarea de insertar en silver es ejecutada cuando termina insertan en las capas raw y bronze.

### Licencia
El codigo es de uso libre.
El autor no se hace responsable por el uso del codigo.