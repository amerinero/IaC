#!/bin/bash
# Probado sobre Debian 8. En otros falla por el nombre del interfaz
# en Debin 8 sale con eth0 (ver linea 13 iptables....)
curl -sSO "https://dl.google.com/cloudagents/install-logging-agent.sh"
bash install-logging-agent.sh
apt-get install -y sysstat
mv /etc/localtime /etc/localtime.orig
ln -s /usr/share/zoneinfo/Europe/Madrid /etc/localtime
mv /etc/default/sysstat /etc/default/sysstat.orig
echo "ENABLED=\"true\"" >> /etc/default/sysstat
systemctl restart sysstat
sysctl -w net.ipv4.ip_forward=1
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf > /dev/null
apt-get install iptables-persistent
