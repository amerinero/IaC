#!/bin/bash
yum install httpd24 php70 stress awslogs -y
yum update -y
mv /etc/localtime /etc/localtime.orig
ln -s /usr/share/zoneinfo/Europe/Madrid /etc/localtime
aws s3 cp s3://merinerowebbucket001/phpweb /var/www/html/ --recursive
echo "<?php phpinfo(); ?>" > /var/www/html/phpinfo.php
usermod -a -G apache ec2-user
chown -R ec2-user:apache /var/www
chmod 2775 /var/www
find /var/www -type d -exec chmod 2775 {} \;
service httpd start
service awslogs start
chkconfig httpd on
chkconfig awslogs on 

Sobre CentOS 7

#!/bin/bash
yum install php stress awscli -y
yum update -y
mv /etc/localtime /etc/localtime.orig
ln -s /usr/share/zoneinfo/Europe/Madrid /etc/localtime
curl https://s3.amazonaws.com/aws-cloudwatch/downloads/latest/awslogs-agent-setup.py -O
pip install --upgrade s3transfer
aws s3 cp s3://merinerowebbucket001/phpweb /var/www/html/ --recursive
echo "<?php phpinfo(); ?>" > /var/www/html/phpinfo.php
usermod -a -G apache ec2-user
chown -R ec2-user:apache /var/www
chmod 2775 /var/www
find /var/www -type d -exec chmod 2775 {} \;
service httpd start
service awslogs start
chkconfig httpd on
chkconfig awslogs on 