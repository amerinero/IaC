import boto3
from datetime import datetime as dt
import json

# El evento de CloudWatch debe enviar un "Constant (JSON text)" indicando el identificador de rds.
# Se tiene que poner como  en la parte de Target al definir el evento.
# 
# { "dbname":"koiboxpreprod" }

def lambda_handler(event, context):
	db_identifier = event['dbname']
	fecha_hora = dt.now()
	print(db_identifier,fecha_hora.strftime('%Y-%m-%d-%H-%M-%S'))
	rds = boto3.client('rds')
	resp = rds.create_db_snapshot(
		DBSnapshotIdentifier=db_identifier+"-"+fecha_hora.strftime('%Y-%m-%d-%H-%M-%S'),
		DBInstanceIdentifier=db_identifier
	)
	print (resp)

#
# Esto es para pruebas en local. Desde AWS Lambda solo ejecutara lambda_handler
evento='{ "dbname":"koiboxpreprod" }'
lambda_handler(json.loads(evento),"kk")
