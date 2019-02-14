#!/bin/bash
#
# Script pensado para usar desde el cron para descargarse los logs semanalmente.
# Descarga los logs generados por las instancias de los grupo de autoescalado de pre y pro.
#
# Descarga los logs desde 7 dias antes del momento de ejecución hasta el momento de ejecución. 
# Pensado para ejecutarlo todos los lunes a las 00:00 y asi descargar todos los logs de la semana anterior. 
#
# Usa el script python download-logs.py para interactuar con Cloudwatch Logs. Este script necesita 
# $HOME/.aws/credentials para acceder a los servicios de AWS.
#
DESDE=`/bin/date --date="-7 days" +%s`
HASTA=`/bin/date +%s`
NSEMANA=`/bin/date --date="-7 days" +%V`
YEAR=`/bin/date --date="-7 days" +%G`
S3PATH="s3://registros-logs-koibox/autoescalado/${YEAR}/"
# 
# Creamos un dict (associative array) con los nombres de los grupos de logs en cloudwatch a descargar
# y los nombres de ficheros a generar.
declare -A GRP_DICT=(\
	["${NSEMANA}-apache_access_pro.log"]="/aws/elasticbeanstalk/koiboxcrm-prod/var/log/httpd/access_log" \
	["${NSEMANA}-apache_error_pro.log"]="/aws/elasticbeanstalk/koiboxcrm-prod/var/log/httpd/error_log" \
	["${NSEMANA}-symfony_pro.log"]="/aws/elasticbeanstalk/prod/var/app/current/var/logs/prod.log" \
	["${NSEMANA}-eb_activity_pro.log"]="/aws/elasticbeanstalk/koiboxcrm-prod/var/log/eb-activity.log" \
	["${NSEMANA}-apache_access_pre.log"]="/aws/elasticbeanstalk/koiboxcrm-preprod/var/log/httpd/access_log" \
	["${NSEMANA}-apache_error_pre.log"]="/aws/elasticbeanstalk/koiboxcrm-preprod/var/log/httpd/error_log" \
	["${NSEMANA}-symfony_pre.log"]="/aws/elasticbeanstalk/preprod/var/app/current/var/logs/prod.log" \
	["${NSEMANA}-eb_activity_pre.log"]="/aws/elasticbeanstalk/koiboxcrm-preprod/var/log/eb-activity.log")

for filename in "${!GRP_DICT[@]}"
	do 
		/usr/bin/python3 download-logs.py ${GRP_DICT[$filename]} $DESDE $HASTA > $filename | logger -t $0
		aws s3 cp $filename ${S3PATH} | logger -t $0
		rm $filename
	done
