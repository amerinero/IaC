import json
import boto3
import time
from datetime import date 
from datetime import timedelta

#
# Busca todas las instancias con:
#    Tag:Proteccion ==['snapshot' ó 'Snapshot']
# y  Tag:Retencion == ['1semana' ó '1Semana' ó '1 semana' ó '1 Semana'] 
# y crea un nuevo snapshot de todos los discos de todas las instancias que encuentre
# a cada snapshot le añade un Tag (Caducidad=%Y-%m-%d) con la fecha del dia de creación 
# snapshot más 7 dias, pensado para que otra funcion lambda lo borre. 
# 
# Escribe en Cloudwatch Logs (usando print) el número de instancias que encuentre
# más una linea por cada volumen del cual haga snapshot.
#

ec = boto3.client('ec2')

def lambda_handler(event, context):
    reservations = ec.describe_instances(
        Filters=[
            {
                'Name': 'tag:Proteccion', 
                'Values': ['snapshot', 'Snapshot']
            },
            {
                'Name': 'tag:Retencion',
                'Values': ['1semana', '1Semana', '1 semana', '1 Semana']
            }
        ]
    ).get('Reservations', [])

    instances = sum(
        [
            [i for i in r['Instances']]
            for r in reservations
        ], [])

    print ('Número Instancias Encontradas=', len(instances))

    for instance in instances:
        for dev in instance['BlockDeviceMappings']:
            if dev.get('Ebs', None) is None:
                continue
            vol_id = dev['Ebs']['VolumeId']
            print ('Found EBS volume', vol_id, 'on instance',instance['InstanceId'])

            snap_description = "Snapshot de %s" % instance['InstanceId']
            hoy = date.today()
            fecha_caducidad = hoy + timedelta(days=7)

            snap = ec.create_snapshot(
            	Description=snap_description,
            	VolumeId=vol_id
            )
            
            ec.create_tags(Resources=[snap['SnapshotId'],
            	],
            	Tags=[{'Key': 'Name', 'Value': 'Auto-bck'},
            	      {'Key': 'Description', 'Value': snap_description},
                      {'Key': 'Caducidad', 'Value': fecha_caducidad.strftime('%Y-%m-%d')} 
                    ]
            )