import boto3
import gzip
from io import BytesIO, TextIOWrapper
from datetime import date, timedelta

def lambda_handler(event, context):
    
    LBNAME=event["LBNAME"]
    
    yesterday = date.today() - timedelta(days=1)
    dia = yesterday.strftime('%d')
    mes = yesterday.strftime('%m')
    YEAR = yesterday.strftime('%Y')
    print ("Agregando ficheros de log de %s, para %s/%s/%s...." %(LBNAME,dia,mes,YEAR))
    
    s3client = boto3.client('s3', region_name='eu-west-3')
    
    agregado=""
    BUCKET="registros-logs-lefebvre-pre"
    PRE_PREFIX="balanceadores/AWSLogs/966544037023/elasticloadbalancing/eu-west-3/"
    PREFIX=PRE_PREFIX+YEAR+"/"+mes+"/"+dia
    OUT_KEY=PRE_PREFIX+YEAR+"/"+mes+"/agregado-"+LBNAME+"-"+YEAR+mes+dia+".gz"
    paginator = s3client.get_paginator('list_objects')
    operation_parameters = {'Bucket': BUCKET,
                    'Prefix': PREFIX}
    page_iterator = paginator.paginate(**operation_parameters)
    ENCONTRADO = False
    borrables = []
    for page in page_iterator:
        if 'Contents' in page:
            for item in page['Contents']:
                if LBNAME in item['Key']:
                    ENCONTRADO = True
                    obj = s3client.get_object(Bucket=BUCKET, Key=item['Key'])
                    with gzip.GzipFile(fileobj=obj["Body"],mode='ra') as gzipfile, TextIOWrapper(gzipfile, encoding="utf-8") as wrapper:
                        content = wrapper.read()
                    agregado = agregado + str(content)
                    borrables.append(item['Key'])
        else:
            print ("No hay contenido el la página del iterable")

    if ENCONTRADO:
        with gzip.open('/tmp/outfile.gz','wt', encoding="utf-8") as outfile:
            outfile.write(agregado)

        s3client.upload_file('/tmp/outfile.gz',BUCKET,OUT_KEY)
        print("Subido fichero agregado s3://%s/%s" %(BUCKET,OUT_KEY))
        print("Borrando ficheros agregados ...")
        for file in borrables:
            s3client.delete_object(Bucket=BUCKET, Key=file)
    else:
        print ("No se han encontrado ficheros de logs del balanceador %s en %s/%s" 
            % (LBNAME,BUCKET,PREFIX))