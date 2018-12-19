#!/usr/bin/python3
import json
import boto3
import time
from datetime import date 
from datetime import timedelta

#
# Elimina los snapshots que tengan:
#   Tag: Caducidad == %Y-%m-%d (dia de hoy)
#

ec = boto3.client('ec2')
hoy = date.today()

snaps = ec.describe_snapshots(
    OwnerIds=['739998647673'],
    Filters=[
        {
          	'Name': 'tag:Caducidad', 
           	'Values': [hoy.strftime('%Y-%m-%d')]
        }         
    ]
).get('Snapshots', [])
print ('Número Snapshots Encontrados=', len(snaps))
for s in snaps:
    ec.delete_snapshot(
        SnapshotId=s['SnapshotId']
    )
    print('Snapshot eliminado:', s['SnapshotId'])
