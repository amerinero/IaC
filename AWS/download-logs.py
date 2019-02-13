import boto3
import sys
import time
import argparse

#
# Programilla para descargar los logs de un grupo de CloudWatch Logs.
#
# El grupo puede tener multiples streams de logs dentro.
#
# Argumentos:
#	Nombre del grupo de logs
#	Desde --> Fecha en segundos (date +%%s) desde la cual queremos los logs
#	Hasta --> Fecha en segundos (date +%%s) hasta la cual queremos los logs
# Por ejemplo:
# Desde = 1546297200 <-- `date --date="2019-01-01 00:00:00" +%s`
# Hasta = 1548975599 <-- `date --date="2019-01-31 23:59:59" +%s`
#
# Para saber los grupos de log que tenemos en una region:
# aws logs describe-log-groups --output json | grep logGroupName

#
# Salidas:
#	Por la salida estandard todos los mensajes de log encontrados
#	Por stderr mensajes de progreso y debug

#
# Lo primero parseamos los argumentos. 
# Si no encuentra tres, falla. 
#
parser = argparse.ArgumentParser()
parser.add_argument("Log_Group_Name", \
	help="Nombre del grupo de logs")
parser.add_argument("Desde", \
	help="Fecha en segundos (date +%%s) desde la cual queremos los logs")
parser.add_argument("Hasta", \
	help="Fecha en segundos (date +%%s) hasta la cual queremos los logs")

argumentos = parser.parse_args()

print ("Nombre del grupo = ",argumentos.Log_Group_Name, file=sys.stderr)
print ("Desde = ",argumentos.Desde, file=sys.stderr)
print ("Hasta = ",argumentos.Hasta, file=sys.stderr)

#
# Construimos el objeto para gestionar los logs
# 
# Recordar que usara lo que haya en $HOME/.aws para acceder a AWS
#
Logs = boto3.client('logs')

grupos = Logs.describe_log_groups().get('logGroups')
ctoken = Logs.describe_log_groups().get('nextToken')

# FIX ME --- Por si hay muchos grupos de log (+1000) para paginar
#print ("Next Token para grupos = ",ctoken)

#
# Creamos una lista con todos los grupos de logs que hayamos encontrado.
#
group_names = []
for gr in grupos:
	group_names.append(gr.get('logGroupName'))

#
# Miramos si el nombre de grupo que nos han pasado por argumentos esta en la lista.
# Si no esta salimos con error. 
#
if argumentos.Log_Group_Name not in group_names:
	print ("Error: No existe un grupo de logs llamado ", argumentos.Log_Group_Name)
	sys.exit(1)

#
# Vale, ya tenemos claro que el grupo existe. 
# Ahora vamos a ir mirando todas las streams de logs que haya en ese grupo
# 

lstreams = Logs.describe_log_streams(
	logGroupName=argumentos.Log_Group_Name,
	orderBy='LastEventTime').get('logStreams')

# Primero nos fijamos en el lastEventTimestamp del stream, si es menor que argumenteos.Desde
# entonces todos los mensajes de ese stream son anteriores al intervalo que buscamos y no hace
# falta mirar en ese stream. 
#
# Despues nos fijamos en el firstEventTimestamp del stream, si es mayor que argumentos.Hasta
# entonces todos los mensajes de ese stream son posteriores al intervalo que buscamos y no hace
# falta mirar en ese stream.
# 
# Hay que multiplicar por mil los valores que nos hayan pasado en Desde y Hasta para ponerlos
# en milisegundos.

miliDesde = int(argumentos.Desde) * 1000
miliHasta = int(argumentos.Hasta) * 1000

for st in lstreams:
	if st.get('lastEventTimestamp') < miliDesde:
		#print ("Stream %s todos los mensajes anteriores" % (st.get('logStreamName')))
		continue

	if st.get('firstEventTimestamp') > miliHasta:
		#print ("Stream %s todos los mensajes posteriores" % (st.get('logStreamName')))
		continue

	# Por cada stream tenemos que ir extrayendo los mensajes de log. Devuelve aprox. 1MB de 
	# mensajes cada vez. Hay que hacer varias llamadas con nextToken para sacarlos todos.
	# (ver https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.get_log_events )

	stname = st.get('logStreamName')	
	print ("Procesando %s" % (stname), file=sys.stderr)

	setevents = Logs.get_log_events(
			logGroupName=argumentos.Log_Group_Name,
			logStreamName=stname,
			startTime=miliDesde,
			endTime=miliHasta,
			startFromHead=True)

	ftoken = setevents.get('nextForwardToken')
	btoken = setevents.get('nextBackwardToken')
	eventos = setevents.get('events')

	print ("Numero de mensajes %d" % (len(eventos)), file=sys.stderr)

	# Aqui es donde sacamos por la salida estandard los mensajes de log
	for ev in eventos:
		print (ev.get('message'))

	# Bucle para hacer cuantas llamadas sean necesarias con nextToken hasta sacar todos
	# los mensajes
	while (ftoken != 'None'):
		setevents = Logs.get_log_events(
			logGroupName=argumentos.Log_Group_Name,
			logStreamName=stname,
			startTime=miliDesde,
			endTime=miliHasta,
			startFromHead=True,
			nextToken=ftoken)
		eventos = setevents.get('events')

		print ("(in loop) Numero de mensajes %d" %(len(eventos)), file=sys.stderr)

		for ev in eventos:
			print (ev.get('message'))
		
		oldtoken = ftoken
		ftoken = setevents.get('nextForwardToken')
		if ftoken == oldtoken:
			ftoken = 'None'