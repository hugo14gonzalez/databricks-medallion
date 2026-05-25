# Databricks notebook source
import requests
import json

# resultado = dbutils.widgets.get('resultado')
# Hugo
try:    
  resultado = dbutils.widgets.get('resultado')
except:
    resultado = 'default_value'

# URL del trigger HTTP de tu Logic App

#PRB
# logic_app_url = "https://prod-57.eastus.logic.azure.com:443/workflows/1213c5d97a3a49cfa700b053d516a4ba/triggers/When_a_HTTP_request_is_received/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2FWhen_a_HTTP_request_is_received%2Frun&sv=1.0&sig=uHzFRJdUNXLuEr81BSVQUjbqIkk9gTpnQgejZz7k4SM"

#PRD
logic_app_url= 'https://trv-la-prd-notificaciones-001.azurewebsites.net:443/api/Notificaciones/triggers/When_a_HTTP_request_is_received/invoke?api-version=2022-05-01&sp=%2Ftriggers%2FWhen_a_HTTP_request_is_received%2Frun&sv=1.0&sig=GUEnYrvV64dDITB9lWdFUqTI7y0VO3ApRJzftcoBrvM'
# Datos que deseas enviar (ajusta el payload a tus necesidades)
cuerpo = {
  "Estado": "Fallido",
  "mensaje": f"{resultado}"
}
headers = {"Content-Type": "application/json"}

# Enviar la solicitud POST
#response = requests.post(logic_app_url, data=json.dumps(cuerpo), headers=headers)

print(cuerpo)
