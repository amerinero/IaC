# Página manual. No ha man aws
# Esta es la página man principal.
$> aws help

# Pero tambien existen páginas man para los modulos
$> aws configre help
$> aws ec2 help

# Listar configuración actual
$> aws configure list 

# Para configurar la primera vez
$> aws configure

# Lista de regiones formato tabla
$> aws ec2 describe-regions --output table

# Listar instancias ec2
$> aws ec2 describe-instances

# Lo mismo pero la salida en forma tabla
$> aws ec2 describe-regions --output table

# Creación de un vpc. Esto devuelve el json del nuevo vpc. 
# Lo mismo conviene redirigir la salida a un fichero. En esta salida
# figura el vpc-id que tendremos que usar para crear consas dentro de 
# este vpc.
$> aws ec2 create-vpc --cidr-block 13.0.0.0/16
$> aws ec2 create-vpc --cidr-block 13.0.0.0/16 > new-vpc.json

# Asignar Internet Gateway
$> aws ec2 attach-internet-gateway \
	--internet-gateway-id igw-ecd8b68b \
	--vpc-id vpc-a2cd5dc4

# Crear una subnet en un vpc.
# Mejor guardar la salida
$> aws ec2 create-subnet --vpc-id vpc-a2cd5dc4 \
	--cidr-block 13.0.100.0/24
$> aws ec2 create-subnet --vpc-id vpc-a2cd5dc4 \
	--cidr-block 13.0.200.0/24 > new-subnet.json

# Crear tabla de rutas
$> aws ec2 create-route-table --vpc-id vpc-a2cd5dc4

# Añadir ruta a la tabla. (igw-ecd8b68b es el id de un IGW)
$> aws ec2 create-route --route-table-id rtb-2843ea51 \
	--destination-cidr-block 0.0.0.0/0 \
	--gateway-id igw-ecd8b68b

# Asociar tabla de rutas a subnet
$> aws ec2 associate-route-table  \
	--subnet-id subnet-7d258c35  \
	--route-table-id rtb-2843ea51

# Crear Security-Group
aws ec2 create-security-group \
	--group-name cli-sg \
	--vpc-id vpc-a2cd5dc4 \
	--description "security group from CLI"

# Crear Reglas dentro de un Security Group
aws ec2 authorize-security-group-ingress \
	--group-name cli-sg \
	--protocol tcp --port 22 --cidr 0.0.0.0/0

# Listar "key pairs"
$> aws ec2 describe-key-pairs --output text

# Crear instancia privada (sin IP Publica)
aws ec2 run-instances --image-id ami-3bfab942 \
	--subnet-id subnet-5456ff1c \
	--security-group-ids sg-c34942b9 \
	--count 1 --instance-type t2.micro \
	--key-name Merinero 

# Crear instancia publica (con IP Publica)
aws ec2 run-instances --image-id ami-3bfab942 \
	--subnet-id subnet-5456ff1c \
	--security-group-ids sg-c34942b9 \
	--count 1 --instance-type t2.micro \
	--associate-public-ip-address \
	--key-name Merinero 






