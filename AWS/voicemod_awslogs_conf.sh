[general]
state_file = /var/awslogs/state/agent-state

[/var/log/messages]
datetime_format = %b %d %H:%M:%S
file = /var/log/messages
buffer_duration = 5000
log_stream_name = {instance_id}
initial_position = start_of_file
log_group_name = centos

[httpd-access_log]
datetime_format = %b %d %H:%M:%S
file = /var/log/httpd/access_log
buffer_duration = 5000
log_stream_name = httpd-access_log
initial_position = start_of_file
log_group_name = centos

[httpd-error_log]
datetime_format = %b %d %H:%M:%S
file = /var/log/httpd/error_log
buffer_duration = 5000
log_stream_name = httpd-error_log
initial_position = start_of_file
log_group_name = centos
