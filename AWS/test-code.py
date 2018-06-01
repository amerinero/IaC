import boto3
import sys
import time

#
# Globales
#
now = time.strftime("%c")
print (now)

dateformat='%d/%m/%Y-%H:%M'

outfile='/tmp/aws_inventario.txt'
try: 
	fo = open(outfile, 'w')
except Exception as e:
    print(e)
    print("Error: Al intentar abrir el fichero %s...." %(outfile))
    raise e

#
# Funciones
#
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

def show_dict (dic: dict, level=0):
	if not isinstance(dic,dict):
		raise ValueError('Llamada a show_dict con una variable que no es tipo dict')
	tabs=""
	for i in range(0,level):
		tabs = tabs + "\t"
	for clave in dic.keys():
		if isinstance(dic[clave],dict):
			print("%s%s > (dict)" %(tabs,clave))
			show_dict(dic[clave],level+1)
		elif isinstance(dic[clave],list):
			print("%s%s > (list)" %(tabs,clave))
			for index, item in enumerate(dic[clave]):
				if isinstance(item,dict):
					print("%s\tItem[%d] > (dict)" %(tabs,index))
					show_dict(item,level+2)
				else:
					print ("%s\t%s ==> %s" %(tabs,clave, dic[clave]))
		else:
			print ("%s%s ==> %s" %(tabs,clave, dic[clave]))

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



list_ec2('eu-west-1')