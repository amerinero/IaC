#!/bin/bash
yum install httpd -y
yum update -y
mv /etc/localtime /etc/localtime.orig
ln -s /usr/share/zoneinfo/Europe/Madrid /etc/localtime
aws s3 cp s3://webcontentbucket/ /var/www/html/ --recursive
service httpd start
chkconfig httpd on
