
#!/bin/bash
# Para GCP  (probado en VM Ubuntu 17.0)
curl -sSO "https://dl.google.com/cloudagents/install-logging-agent.sh"
bash install-logging-agent.sh
apt-get install -y sysstat
apt-get install -y nginx
apt-get install -y stress
mv /etc/localtime /etc/localtime.orig
ln -s /usr/share/zoneinfo/Europe/Madrid /etc/localtime
mv /etc/default/sysstat /etc/default/sysstat.orig
echo "ENABLED=\"true\"" >> /etc/default/sysstat
systemctl restart sysstat
systemctl enable nginx
systemctl start nginx
