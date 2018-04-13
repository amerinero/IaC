import boto3
import sys
import time

now = time.strftime("%c")
print (now)
#
# Vamos ahora con el S3
#
s3 = boto3.resource('s3')
s3c = boto3.client('s3')
#
print ("Listado de buckets en S3:")

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

def sumarize_s3_bucket(bucket):
	TOTALSIZE=0
	OBJECTCOUNT=0
	Truncado = True
	ctoken=""
	while Truncado:
		if ctoken == "":
			contenido = s3c.list_objects_v2(Bucket=bucket)
		else:
			contenido = s3c.list_objects_v2(Bucket=bucket,ContinuationToken=ctoken)
		if contenido['IsTruncated']:
			ctoken = contenido['NextContinuationToken']
		else:
			Truncado = False
		OBJECTCOUNT = OBJECTCOUNT + contenido['KeyCount']
		if contenido['KeyCount'] > 0:
			for item in contenido['Contents']:
				TOTALSIZE = TOTALSIZE + item['Size']
			
	return TOTALSIZE / (1024*1024), OBJECTCOUNT



for bucket in s3.buckets.all():
	print ("\t",bucket.name,bucket.creation_date)

kk = s3c.list_buckets()

#show_dict(kk)

bucks = kk['Buckets']

for b in bucks:
	Tamaño, nobjs = sumarize_s3_bucket(b['Name'])
	print("Bucket=%s CreationDate=%s %dMB %d Objectos" %(b['Name'],b['CreationDate'], Tamaño, nobjs))
	
	#show_dict(contenido,1)
	#print ("********************************************")

# buckets, owners, respons = s3c.list_buckets()
# print (owners)
# print ("*** Siguiente ***")
# print (buckets)
