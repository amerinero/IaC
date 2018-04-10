#
# Pequeño programa para ir recorriendo las distintas regiones
# de AWS y listando los objetos que tenemos en ellas.
#
import boto3
import sys

def list_ec2_region(region):
	ec2_r = boto3.resource('ec2', region_name=region)
	print ("**** Region:",region,"****")
	print ("")
	print ("\tVPCs:")
	for vpc in ec2_r.vpcs.all():
		print ("\t\t",vpc, vpc.cidr_block, vpc.tags)
	print ("")
	print ("\tInstancias EC2:")
	for instance in ec2_r.instances.all():
		print ("\t\t",instance, instance.state, instance.tags)
	print ("")
	print ("\tVolumenes EBS:")
	for volume in ec2_r.volumes.all():
		print("\t\t",volume, volume.size,"gb", volume.tags)
	#print ("")
	#print ("\tSnapshots:")
	#for snap in ec2_r.snapshots.all():
	#	print("\t\t",snap,snap.volume_id,snap.start_time,snap.tags)
	print ("")
	print ("\tClassic Addresses:")
	for addr in ec2_r.classic_addresses.all():
		print("\t\t",addr)	
	print ("")


sts = boto3.client('sts')
current_identity = sts.get_caller_identity()
print ("Listado generado para cuenta AWS:", current_identity['Account'])
print ("Por el usuario:",current_identity['Arn'])
print ("")

#
# Vamos primero con los objetos EC2
#
ec2 = boto3.client('ec2')

# Retrieves all regions/endpoints that work with EC2
#
print ("Listado de objetos EC2 por region:")
response = ec2.describe_regions()
#print('Regions:', response['Regions'])
for listItem in response['Regions']:
	#print (listItem['RegionName'])
	list_ec2_region(listItem['RegionName'])
print ("")
#
# Vamos ahora con el S3
#
s3 = boto3.resource('s3')
#
print ("Listado de buckets en S3:")
for bucket in s3.buckets.all():
	print ("\t",bucket,bucket.creation_date)

