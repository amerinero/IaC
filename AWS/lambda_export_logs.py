import boto3
import os
import datetime

# 
# CloudWatchLogs -to- file
# 
# Argumentos:
#   Nombre del grupo de logs
#   Desde --> datetime.datetime
#   Hasta --> datetime.datetime
# Por ejemplo:
#     Hasta = datetime.datetime.now()
#     Desde = datetime.datetime.now() - datetime.timedelta(days=7)

def CWL2file(Log_Group_Name, Desde, Hasta, outfile):
    
    try:
        # 
        # Es necesario usar un paginador para no tener que hacer varias llamadas sucesivas 
        Logs = boto3.client('logs')
        paginator = Logs.get_paginator('describe_log_streams')
        lstreams = []
        pages = paginator.paginate(
            logGroupName = Log_Group_Name,
            orderBy = 'LastEventTime'
            )
        for page in pages:
            lstreams += page.get('logStreams')
    except Logs.exceptions.ResourceNotFoundException as e:
        print("El nombre %s no existe como grupo de Logs" % (Log_Group_Name))
        print(e)
        return 0
    except Exception:
        raise
    
    # Hay que multiplicar por mil los valores que nos hayan pasado en Desde y Hasta para ponerlos
    # en milisegundos.
    miliDesde = int(Desde.timestamp()) * 1000
    miliHasta = int(Hasta.timestamp()) * 1000

    process_streams = []

    for st in lstreams:
        #
        # Las streams cuyo las event timestamp se menor que miliDesde no hace 
        # falta mirarlas, todos los mensajes seran anteriores
        if st.get('lastEventTimestamp') < miliDesde:
            continue
        #
        # Las streams cuyo las event timestamp se mayor que miliHasta no hace 
        # falta mirarlas, todos los mensajes seran posteriores
        if st.get('firstEventTimestamp') > miliHasta:
            continue

        #
        # Todas las demas las tenemos que procesar
        stname = st.get('logStreamName')    
        process_streams.append(stname)
    # 
    # Es necesario usar un paginador para no tener que hacer varias llamadas sucesivas
    if process_streams:
        paginator = Logs.get_paginator('filter_log_events')
        pages = paginator.paginate(
            logGroupName=Log_Group_Name,
            logStreamNames=process_streams,
            startTime=miliDesde,
            endTime=miliHasta,
            )
        print("LogStreams procesadas en grupo: %s" %(Log_Group_Name))
        print(process_streams)
    else:
        print("No hay mensajes para ese intervalo de tiempo")
        return 0
    #
    # Vamos recorriendo las paginas y los eventos dentro de ellas
    # escribimos en el fichero de salida el message de cada evento.
    bytes_out = 0
    with open(outfile, 'a') as f_out:
        for page in pages:
            eventos = page.get('events')
            for ev in eventos:
                bytes_out += f_out.write(ev.get('message') + os.linesep)
    return bytes_out


# El evento de CloudWatch debe enviar algo como esto donde se le diga que grupos de logs 
# y en que bucket debe guardarlos.
# Se tiene que poner como "Constant (JSON text)" en la parte de Target al definir el evento
# 
# {
#     "log_streams": 
#     {
#         "/aws/elasticbeanstalk/koiboxcrm-prod/var/log/httpd/access_log": "apache_access_pro.log",
#         "/aws/elasticbeanstalk/koiboxcrm-prod/var/log/httpd/error_log": "apache_error_pro.log",
#         "/aws/elasticbeanstalk/prod/var/app/current/var/logs/prod.log": "symfony_pro.log",
#         "/aws/elasticbeanstalk/koiboxcrm-prod/var/log/eb-activity.log": "eb_activity_pro.log"
#     },
#     "s3_params":
#     {
#         "S3Bucket": "registros-logs-koibox",
#         "S3Prefix": "autoescalado/pro/"
#     }
# }
# 
# Se pueden definir varios Target en un mismo evento con distinto JSON para poder guardar 
# distintos grupos de logs con un solo evento.
# 
def lambda_handler(event, context):
    Log_streams = event['log_streams']
    S3params = event['s3_params']
    Hasta = datetime.datetime.now()
    Desde = datetime.datetime.now() - datetime.timedelta(days=1)
    Ayer = Desde.strftime('%Y-%m-%d')
    anio = Desde.strftime('%G')
    s3bucket = S3params['S3Bucket']
    s3prefix = S3params['S3Prefix']
    osprefix = "/tmp/"
    
    s3 = boto3.resource('s3')

    for grp in Log_streams.keys():
        os_file = osprefix+Log_streams[grp]
        s3_obj = s3prefix+Ayer+"-"+Log_streams[grp]
        CWL2file(grp, Desde, Hasta, os_file)
        existe = os.path.isfile(os_file)
        if existe:
            s3.meta.client.upload_file(os_file,s3bucket,s3_obj)
            os.remove(os_file)
