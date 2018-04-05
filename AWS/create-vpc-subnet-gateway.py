import boto3
import sys

ec2 = boto3.resource('ec2')
vpc = ec2.create_vpc(CidrBlock='12.0.0.0/24')
tag = vpc.create_tags(
	Tags=[
		{
			'Key': 'Name',
			'Value': 'vpc-boto3'	
		},
		{
			'Key': 'Creador',
			'Value': str(sys.argv[0])
		},
	]
	)	
subnet = vpc.create_subnet(
	CidrBlock='12.0.0.0/25')
tag2 = subnet.create_tags(
	Tags=[
		{
			'Key': 'Name',
			'Value': 'subnet-boto3'	
		},
		{
			'Key': 'Creador',
			'Value': str(sys.argv[0])
		},
	]
	)
gateway = ec2.create_internet_gateway()