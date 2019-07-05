import boto3
from datetime import datetime as dt
from datetime import timedelta as td
import json

# El evento de CloudWatch debe enviar un "Constant (JSON text)" indicando el identificador de rds (dbname) 
# el minimo de dias que deben tener los snapshots a borrar (retencion).
# Se tiene que poner como  en la parte de Target al definir el evento.
# 
# { "dbname":"koiboxpreprod","retencion":8 }

def lambda_handler(event, context):
	db_identifier = event['dbname']
	dias = event['retencion']
	limite = dt.utcnow()-td(days=dias)
	rds = boto3.client('rds')
	resp = rds.describe_db_snapshots(
		DBInstanceIdentifier=db_identifier,
		SnapshotType='manual',
	)
	for snap in resp['DBSnapshots']:
		snap_id=snap['DBSnapshotIdentifier']
		snap_time=snap['SnapshotCreateTime'].replace(tzinfo=None)
		print(limite,snap_time)
		if (limite > snap_time):
			print ("Borramos: %s" % (snap_id))
			resp = rds.delete_db_snapshot(
				DBSnapshotIdentifier=snap_id
			)

#
# Esto es para pruebas en local. Desde AWS Lambda solo ejecutara lambda_handler
evento='{ "dbname":"koiboxpreprod","retencion":14 }'
lambda_handler(json.loads(evento),"kk")