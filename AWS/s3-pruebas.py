import boto3
import gzip
from io import BytesIO, TextIOWrapper


YEAR="2020"
MONTH=["02"]
BUCKET="registros-logs-lefebvre-pre"
PRE_PREFIX="balanceadores/AWSLogs/966544037023/elasticloadbalancing/eu-west-3/"
LBNAME="357db760-kubesystem-traefi-521f"
#LBNAME="prueba-lexon.c67fbb20b89dbb18"
#LBNAME="default-balalb01p-d401.1f91f03267c1a715"
#LBNAME="default-balalb01p-d401.91b2358d4c51d99a"

s3client = boto3.client('s3', region_name='eu-west-3')

for mes in MONTH:
    for d in range(1,6):
        dia = str(d).zfill(2)
        agregado=""
        PREFIX=PRE_PREFIX+YEAR+"/"+mes+"/"+dia
        OUT_KEY=PRE_PREFIX+YEAR+"/"+mes+"/agregado-"+LBNAME+"-"+YEAR+mes+dia+".gz"
        paginator = s3client.get_paginator('list_objects')
        operation_parameters = {'Bucket': BUCKET,
                        'Prefix': PREFIX}
        page_iterator = paginator.paginate(**operation_parameters)
        ENCONTRADO = False
        borrables = []
        print ("Agregando ficheros de log de %s, para %s/%s/%s...." %(LBNAME,dia,mes,YEAR))
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
            with gzip.open('outfile.gz','wt', encoding="utf-8") as outfile:
                outfile.write(agregado)

            s3client.upload_file('outfile.gz',BUCKET,OUT_KEY)
            print("Subido fichero agregado s3://%s/%s" %(BUCKET,OUT_KEY))
            print("Borrando ficheros agregados ...")
            for file in borrables:
                s3client.delete_object(Bucket=BUCKET, Key=file)

        else:
            print ("No se han encontrado ficheros de logs del balanceador %s en %s/%s" 
                % (LBNAME,BUCKET,PREFIX))