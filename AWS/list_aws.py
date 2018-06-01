# Pequeño programa para ir recorriendo las distintas regiones
# de AWS y listando los objetos que tenemos en ellas.
#
import boto3
import sys
import time

default_region='eu-west-1'
dateformat='%d/%m/%Y-%H:%M'
outfile='/tmp/aws_inventario.txt'
try: 
	fo = open(outfile, 'w')
except Exception as e:
    print(e)
    print("Error: Al intentar abrir el fichero %s...." %(outfile))
    raise e

def tags2str(tag_dict: list):
	TAGLIST = ""
	if not isinstance(tag_dict, list):
		#print ("DEBUG: No es list es %s" %(type(tag_dict)))
		return TAGLIST
	#if tag_dict == "":
	#	return TAGLIST
	for item in tag_dict:
		TAGLIST = TAGLIST + "%s=%s " %(item['Key'], item['Value'])
	return TAGLIST

def sumarize_s3_bucket(bucket):
	TOTALSIZE=0
	OBJECTCOUNT=0
	s3cli = boto3.client('s3')
	Truncado = True
	ctoken=""
	while Truncado:
		if ctoken == "":
			contenido = s3cli.list_objects_v2(Bucket=bucket)
		else:
			contenido = s3cli.list_objects_v2(Bucket=bucket,ContinuationToken=ctoken)
		if contenido['IsTruncated']:
			ctoken = contenido['NextContinuationToken']
		else:
			Truncado = False
		OBJECTCOUNT = OBJECTCOUNT + contenido['KeyCount']
		if contenido['KeyCount'] > 0:
			for item in contenido['Contents']:
				TOTALSIZE = TOTALSIZE + item['Size']
	LOCATION = s3cli.get_bucket_location(Bucket=bucket)['LocationConstraint']
	try:
		TAGS = s3cli.get_bucket_tagging(Bucket=bucket)['TagSet']
	except Exception as inst:
		TAGS = ""

	return TOTALSIZE / (1024*1024), OBJECTCOUNT, LOCATION, TAGS

def list_ec2(region):
	ec2_r = boto3.resource('ec2', region_name=region)
	print ("\tVPCs:")
	fo.write("\tVPCs:\n")
	for vpc in ec2_r.vpcs.all():
		if not vpc.is_default:
			print ("\t\t%s %s %s" %(vpc.vpc_id, vpc.cidr_block, tags2str(vpc.tags)))
			fo.write("\t\t%s %s %s\n" %(vpc.vpc_id, vpc.cidr_block, tags2str(vpc.tags)))
	
	print ("\tInstancias EC2:")
	fo.write("\tInstancias EC2:\n")
	for instance in ec2_r.instances.all():
		fecha = instance.launch_time.strftime(dateformat)
		print ("\t\t%s %s %s %s" %(instance.instance_id, instance.state['Name'], fecha, tags2str(instance.tags)))
		fo.write("\t\t%s %s %s %s\n" %(instance.instance_id, instance.state['Name'], fecha, tags2str(instance.tags)))
	
	print ("\tVolumenes EBS:")
	fo.write("\tVolumenes EBS:\n")
	for volume in ec2_r.volumes.all():
		fecha = volume.create_time.strftime(dateformat)
		print("\t\t%s %sGB %s %s" %(volume.volume_id, volume.size, fecha, tags2str(volume.tags)))
		fo.write("\t\t%s %sGB %s %s\n" %(volume.volume_id, volume.size, fecha, tags2str(volume.tags)))
		
	
	print ("\tSnapshots:")
	fo.write("\tSnapshots:\n")
	sts = boto3.client('sts')
	current_identity = sts.get_caller_identity()
	Account = current_identity['Account']
	for snap in ec2_r.snapshots.filter(OwnerIds=[Account]):
		fecha=snap.start_time.strftime(dateformat)
		print("\t\t%s %s %s %s" %(snap.snapshot_id,snap.volume_id,fecha,tags2str(snap.tags)))
		fo.write("\t\t%s %s %s %s\n" %(snap.snapshot_id,snap.volume_id,fecha,tags2str(snap.tags)))
		
def list_rds(region):
	print ("\tInstancias RDS:")
	fo.write("\tInstancias RDS:\n")
	rds = boto3.client('rds', region_name=region)
	desc_instances = rds.describe_db_instances()
	db_instances = desc_instances['DBInstances']
	for db in db_instances:
		fecha=db['InstanceCreateTime'].strftime(dateformat)
		print ("\t\t%s %s %s %s %s %s" %(db['DbiResourceId'],db['DBName'],db['Engine'],\
			db['EngineVersion'], db['DBInstanceStatus'], fecha))
		fo.write ("\t\t%s %s %s %s %s %s\n" %(db['DbiResourceId'],db['DBName'],db['Engine'],\
			db['EngineVersion'], db['DBInstanceStatus'], fecha))
		
def list_dynamodb(region):
	print ("\tTablas DynamoDB:")
	fo.write("\tTablas DynamoDB:\n")
	dynamo = boto3.client('dynamodb', region_name=region)
	for table in dynamo.list_tables()['TableNames']:
		info_table = dynamo.describe_table(TableName=table)['Table']
		fecha=info_table['CreationDateTime'].strftime(dateformat)
		print ("\t\t%s %s %s" %(info_table['TableName'], info_table['TableStatus'],\
		 fecha))
		fo.write ("\t\t%s %s %s\n" %(info_table['TableName'], info_table['TableStatus'],\
		 fecha))

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
	fecha=bucket.creation_date.strftime(dateformat)
	Tamaño, nobjs, loc, tags = sumarize_s3_bucket(bucket.name)
	print("\t%s\t%s %dMB %d Objetos %s %s" %(bucket.name, fecha, Tamaño, nobjs, loc, tags2str(tags)))
	fo.write("\t%s\t%s %dMB %d Objetos %s %s\n" %(bucket.name, fecha, Tamaño, nobjs, loc, tags2str(tags)))
fo.close()