# Pequeño programa para ir recorriendo las distintas regiones
# de AWS y listando los objetos que tenemos en ellas.
#
import boto3
import sys
import time

default_region='eu-west-1'
outfile='/tmp/aws_inventario.txt'
try: 
	fo = open(outfile, 'w')
except Exception as e:
    print(e)
    print("Error: Al intentar abrir el fichero %s...." %(outfile))
    raise e

def list_ec2(region):
	ec2_r = boto3.resource('ec2', region_name=region)
	print ("\tVPCs:")
	fo.write("\tVPCs:\n")
	for vpc in ec2_r.vpcs.all():
		if not vpc.is_default:
			print ("\t\t",vpc.vpc_id, vpc.cidr_block, vpc.tags)
			fo.write("\t\t%s %s %s\n" %(vpc.vpc_id, vpc.cidr_block, vpc.tags))
	
	print ("\tInstancias EC2:")
	fo.write("\tInstancias EC2:\n")
	for instance in ec2_r.instances.all():
		print ("\t\t",instance.instance_id, instance.state, instance.tags)
		fo.write("\t\t%s %s %s\n" %(instance.instance_id, instance.state, instance.tags))
	
	print ("\tVolumenes EBS:")
	fo.write("\tVolumenes EBS:\n")
	for volume in ec2_r.volumes.all():
		print("\t\t",volume.volume_id, volume.size,"gb", volume.tags)
		fo.write("\t\t%s %sGB %s\n" %(volume.volume_id, volume.size,volume.tags))
		
	
	print ("\tSnapshots:")
	fo.write("\tSnapshots:\n")
	sts = boto3.client('sts')
	current_identity = sts.get_caller_identity()
	Account = current_identity['Account']
	for snap in ec2_r.snapshots.filter(OwnerIds=[Account]):
		print("\t\t",snap.snapshot_id,snap.volume_id,snap.start_time,snap.tags)
		fo.write("\t\t%s %s %s %s\n" %(snap.snapshot_id,snap.volume_id,snap.start_time,snap.tags))

	# print ("\tClassic Addresses:")
	# for addr in ec2_r.classic_addresses.all():
	# 	print("\t\t",addr)	

def list_rds(region):
	print ("\tInstancias RDS:")
	fo.write("\tInstancias RDS:\n")
	rds = boto3.client('rds', region_name=region)
	desc_instances = rds.describe_db_instances()
	db_instances = desc_instances['DBInstances']
	for db in db_instances:
		print ("\t\t",db['DbiResourceId'],db['DBName'],db['Engine'],\
			db['EngineVersion'], db['DBInstanceStatus'], db['InstanceCreateTime'])
		fo.write ("\t\t%s %s %s %s %s %s\n" %(db['DbiResourceId'],db['DBName'],db['Engine'],\
			db['EngineVersion'], db['DBInstanceStatus'], db['InstanceCreateTime']))

def list_dynamodb(region):
	print ("\tTablas DynamoDB:")
	fo.write("\tTablas DynamoDB:\n")
	dynamo = boto3.client('dynamodb', region_name=region)
	for table in dynamo.list_tables()['TableNames']:
		info_table = dynamo.describe_table(TableName=table)['Table']
		print ("\t\t",info_table['TableName'], info_table['TableStatus'],\
		 info_table['CreationDateTime'])
		fo.write ("\t\t%s %s %s" %(info_table['TableName'], info_table['TableStatus'],\
		 info_table['CreationDateTime']))

sts = boto3.client('sts')
current_identity = sts.get_caller_identity()
now = time.strftime("%c")
print (now)
fo.write("%s\n"%(now))
print ("Listado generado para cuenta AWS:", current_identity['Account'])
fo.write("Listado generado para cuenta AWS: %s\n" %(current_identity['Account']))
print ("Por el usuario:",current_identity['Arn'])
fo.write("Por el usuario: %s\n" %(current_identity['Arn']))
print ("")
fo.write("\n")


#
# Vamos primero con las cosas regionales:
# 	a) objetos EC2
#	b) Bases de datos RDS
#	c) Tablas DynamoDB
#
ec2 = boto3.client('ec2', region_name='eu-west-1')
#
print ("Listado de regionales:")
fo.write ("Listado de regionales:\n")
response = ec2.describe_regions()
for listItem in response['Regions']:
	print ("**** Region:",listItem['RegionName'],"****")
	fo.write("**** Region: %s ****\n" %(listItem['RegionName']))
	print ("")
	fo.write("\n")
	list_ec2(listItem['RegionName'])
	list_rds(listItem['RegionName'])
	list_dynamodb(listItem['RegionName'])
	print ("")
	fo.write("\n")
#
# Vamos ahora con el S3
#
s3 = boto3.resource('s3')
#
print ("Listado de buckets en S3:")
fo.write("Listado de buckets en S3:\n")
for bucket in s3.buckets.all():
	print ("\t",bucket,bucket.creation_date)
	fo.write("\t %s %s\n" %(bucket,bucket.creation_date))
fo.close()