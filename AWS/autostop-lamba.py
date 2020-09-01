import json
import boto3
import time
from datetime import date 
from datetime import timedelta

#
# Busca todas las instancias EC2 y RDS con:
#    Tag:AutoStop ==['Si' ó 'si']
# 
# Escribe en Cloudwatch Logs (usando print) el número de instancias que encuentre.
#

def lambda_handler(event, context):
    print ('Buscando instancias EC2 que parar ...')
    ec2 = boto3.client('ec2')
    reservations = ec2.describe_instances(
        Filters=[
            {
                'Name': 'tag:AutoStop', 
                'Values': ['Si', 'si']
            },
            {
                'Name' : 'instance-state-name',
                'Values' : [ 'running' ]
            }
            
        ]
    ).get('Reservations', [])

    instances = sum(
        [
            [i for i in r['Instances']]
            for r in reservations
        ], [])

    #print ('Número Instancias EC2 parables encontradas = ', len(instances))

    for instance in instances:
        print ('Parando instancia %s' %(instance['InstanceId']))
        ec2.stop_instances(InstanceIds=[instance['InstanceId']])


    rds = boto3.client('rds')
    print ('Buscando instancias RDS que parar ...')
    all_db_instances = rds.describe_db_instances().get('DBInstances', [])

    for db in all_db_instances:
        if (db['DBInstanceStatus'] == 'available'):
            tags = rds.list_tags_for_resource(
                ResourceName=db['DBInstanceArn'],
            )
            for tag in tags['TagList']:
                if tag['Key'] == 'AutoStop' and tag['Value'] in ['Si', 'si']:
                    print ('Parando DB %s ... ' %(db['DBInstanceIdentifier']))
                    rds.stop_db_instance(
                        DBInstanceIdentifier=db['DBInstanceIdentifier'])

lambda_handler(0,0)