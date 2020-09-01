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
    print ('Buscando instancias EC2 que arrancar ...')
    ec2 = boto3.client('ec2')
    reservations = ec2.describe_instances(
        Filters=[
            {
                'Name': 'tag:AutoStart', 
                'Values': ['Si', 'si']
            },
            {
                'Name' : 'instance-state-name',
                'Values' : [ 'stopped' ]
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
        print ('Arrancando instancia %s' %(instance['InstanceId']))
        ec2.start_instances(InstanceIds=[instance['InstanceId']])


    rds = boto3.client('rds')
    print ('Buscando instancias RDS que arrancar ...')
    all_db_instances = rds.describe_db_instances().get('DBInstances', [])

    for db in all_db_instances:
        if (db['DBInstanceStatus'] == 'stopped'):
            tags = rds.list_tags_for_resource(
                ResourceName=db['DBInstanceArn'],
            )
            for tag in tags['TagList']:
                if tag['Key'] == 'AutoStart' and tag['Value'] in ['Si', 'si']:
                    print ('Arrancando DB %s ... ' %(db['DBInstanceIdentifier']))
                    rds.start_db_instance(DBInstanceIdentifier=db['DBInstanceIdentifier'])


lambda_handler(0,0)