# Databricks notebook source
# MAGIC %sql 
# MAGIC select *
# MAGIC from Delta.`/Volumes/test_data/base/deltatables/participacionempresas`

# COMMAND ----------

# MAGIC %sql 
# MAGIC select *
# MAGIC from test_data.base.capex
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC select Empresa,ValorContable, sum(Valor)
# MAGIC from test_data.base.eeff
# MAGIC group by Empresa,ValorContable

# COMMAND ----------

# MAGIC %sql
# MAGIC select `Año`,Trimestre,Empresa,Estado,ValorContable,TipoCorriente,Descripcion, COUNT(*) AS cantidad 
# MAGIC from test_data.base.EEFF
# MAGIC GROUP BY `Año`,Trimestre,Empresa,Estado,ValorContable,TipoCorriente,Descripcion
# MAGIC HAVING COUNT(*) > 1;

# COMMAND ----------

# MAGIC %sql
# MAGIC use catalog `test_data`; 
# MAGIC
# MAGIC drop table if exists `base`.`capex`;
# MAGIC drop table if exists `base`.`deuda`;
# MAGIC drop table if exists `base`.`eeff`;
# MAGIC drop table if exists `base`.`participacionempresas`;
# MAGIC drop table if exists `base`.`perfildeuda`;
# MAGIC drop table if exists `base`.`proyectos`;
# MAGIC drop table if exists `base`.`trafico_vias`;
# MAGIC
