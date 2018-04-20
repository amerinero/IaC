import argparse
import os
import time

#
# Antes de nada instalar lo siguientes:
#
# sudo pip3 install -r requirements.txt
#sudo pip3 install googleapiclient google-auth google-auth-httplib2

from google.oauth2 import service_account
import googleapiclient.discovery

SERVICE_ACCOUNT_FILE = 'curso-easynube-b81dac2a14c7.json'


# from oauth2client.client import GoogleCredentials

def get_zone_list (compute,project):
	l_zonas = []
	request = compute.zones().list(project=project)
	if request is not None:
		result = request.execute()
	else:
		print ("Alga ha salido mal")
	
	for item in result['items']:
		l_zonas.append(item['name'])
	return l_zonas



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

# credentials = GoogleCredentials.get_application_default()

project = 'curso-easynube'

credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE)

#
# Lo primero sacar todas las zonas disponibles a una lista
#
compute = googleapiclient.discovery.build('compute', 'v1', \
	credentials=credentials)
zonas = get_zone_list (compute,project)

print (zonas)



