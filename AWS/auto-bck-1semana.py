#!/usr/bin/python3
import boto3
import time
from datetime import date 
from datetime import timedelta

ec = boto3.client('ec2')

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
    ).get(
        'Reservations', []
    )

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



       
