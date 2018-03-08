# Script de creacion de una Nube Privada Virtual con dos subnets una ip publica una nic grupo de seguridad
# con reglas dos maquinas virtuales una publica con instalacion de IIS y otra privada en la segunda subred

#Variables globales al script
  $NombreIpPublica        ='pip-lmt-01'
  $NombreIpPublica02      ='pip-lmt-02'
  $GrupoRecursos          ='rg-lmt-curso'
  $NombreVirtualNet       ='vnet-lmt-curso'
  $RangoDireccionVnet     ='104.45.0.0/16'
  $Dns                    ='lmtcurso'
  $Dns02                  ='lmtcurso02'
  $Lugar                  ='westeurope'
  $NombreNic01            ='nic-lmt-01'
  $NombreNic02            ='nic-lmt-02'
  $NombreSubRed1          ='sn-public-104.45.1.0-we'
  $RangoDireccionSn1      ='104.45.1.0/24'
  $NombreSubRed2          ='sn-private-104.45.2.0-we'
  $RangoDireccionSn2      ='104.45.2.0/24'
  $NombreReglaRDP001      ='nsg-lmt-regla-rdp'
  $NombreReglaRDP002      ='nsg-lmt-regla-rdp002'
  $NombreReglaWWW001      ='nsg-lmt-regla-www'
  $NombreGrupoSeguridad   ='nsg-lmt-curso'
  $NombreGrupoSeguridad02 ='nsg-lmt-curso-02'
  $NombreVm001            ='vm-lmt-win-001'
  $NombreVm002            ='vm-lmt-win-002'

# Peticion de Credenciales para la maquina virtual
$Credenciales = Get-Credential `
    -Message "Introduzca el usuario y password de la maquina virtual."

# Creacion de el grupo de recursos.
$rg = New-AzureRmResourceGroup `
  -Name $GrupoRecursos `
  -Location $Lugar

# Creacion del template con las Subredes de la  Red Privada Virtual, una privada y una publica
$SubRed1 = New-AzureRmVirtualNetworkSubnetConfig `
  -Name $NombreSubRed1 `
  -AddressPrefix $RangoDireccionSn1
$SubRed2 = New-AzureRmVirtualNetworkSubnetConfig `
  -Name $NombreSubRed2 `
  -AddressPrefix $RangoDireccionSn2

# Creacion de la Cloud Privada Virtual.

$Vnet=New-AzureRmVirtualNetwork `
  -ResourceGroupName $rg.ResourceGroupName `
  -Location $Lugar `
  -Name $NombreVirtualNet `
  -AddressPrefix $RangoDireccionVnet `
  -Subnet $SubRed1,$SubRed2

# Creacion de IP Publica .

$publicIp = New-AzureRmPublicIpAddress `
   -Name $NombreIpPublica `
   -ResourceGroupName $rg.ResourceGroupName `
   -AllocationMethod Dynamic `
   -DomainNameLabel $Dns `
   -Location $Lugar `
   -IdleTimeoutInMinutes 4

# Creacion reglas de entrada para puerto 3389 del NSG (network security group) para pubñica
$nsgRuleRDP = New-AzureRmNetworkSecurityRuleConfig `
    -Name $NombreReglaRDP001 `
    -Protocol Tcp `
    -Direction Inbound `
    -Priority 1000 `
    -SourceAddressPrefix * `
    -SourcePortRange * `
    -DestinationAddressPrefix * `
    -DestinationPortRange 3389 `
    -Access Allow

# Creacion reglas de entrada para puerto 80 del NSG (network security group) para publica
$nsgRuleWeb = New-AzureRmNetworkSecurityRuleConfig `
    -Name $NombreReglawww001 `
    -Protocol Tcp `
    -Direction Inbound `
    -Priority 1001 `
    -SourceAddressPrefix * `
    -SourcePortRange * `
    -DestinationAddressPrefix * `
    -DestinationPortRange 80 `
    -Access Allow

# Creacion NSG
$nsg = New-AzureRmNetworkSecurityGroup `
    -ResourceGroupName $rg.ResourceGroupName `
    -Location $Lugar `
    -Name $NombreGrupoSeguridad `
    -SecurityRules $nsgRuleRDP,$nsgRuleWeb

# Creacion de la Tarjeta Virtual de Red y asociacion con subnet la IP publica y NSG
$nic = New-AzureRmNetworkInterface `
    -Name $NombreNic01 `
    -ResourceGroupName $rg.ResourceGroupName `
    -Location $Lugar `
    -SubnetId $VNet.Subnets[0].Id `
    -PublicIpAddressId $PublicIp.Id `
    -NetworkSecurityGroupId $nsg.Id

# Creacion configuracion de la VM de la subnet publica
$vmConfig = New-AzureRmVMConfig `
                -VMName $NombreVm001 `
                -VMSize Standard_B1s | `
            Set-AzureRmVMOperatingSystem `
                -Windows -ComputerName $NombreVm001 `
                -Credential $Credenciales | `
            Set-AzureRmVMSourceImage `
                -PublisherName MicrosoftWindowsServer `
                -Offer WindowsServer `
                -Skus 2012-R2-Datacenter -Version latest | `
            Add-AzureRmVMNetworkInterface -Id $nic.Id

# Creacion de la VM con la configuracion anterior
$Vm1 = New-AzureRmVM -ResourceGroupName $rg.ResourceGroupName -Location $Lugar -VM $vmConfig


#Extension para instalar web server en el arranque de la maquina

$SettingString ='{"commandToExecute":"powershell Add-WindowsFeature Web-Server; powershell Add-Content -Path \"C:\\inetpub\\wwwroot\\Default.htm\" -Value $($env:computername)"}' `

$vm = get-azureRmVm -Name $NombreVm001 -ResourceGroupName $GrupoRecursos

Set-AzureRmVMExtension `
    -ResourceGroupName $rg.ResourceGroupName `
    -ExtensionName IIS `
    -VMName $Vm.Name `
    -Publisher "Microsoft.Compute" `
    -ExtensionType "CustomScriptExtension" `
    -TypeHandlerVersion 1.4 `
    -SettingString $SettingString `
    -Location $Lugar

# ##################
# Creacion de la segunda VM en la subnet privada

# Configuracion reglas de entrada para puerto 3389 del NSG para acceso rdp a la privada
$nsgRuleRDP02 = New-AzureRmNetworkSecurityRuleConfig `
    -Name $NombreReglaRDP002 `
    -Protocol Tcp `
    -Direction Inbound `
    -Priority 1000 `
    -SourceAddressPrefix * `
    -SourcePortRange * `
    -DestinationAddressPrefix * `
    -DestinationPortRange 3389 `
    -Access Allow

# Creacion NSG
$nsg02 = New-AzureRmNetworkSecurityGroup `
    -ResourceGroupName $rg.ResourceGroupName `
    -Location $Lugar `
    -Name $NombreGrupoSeguridad02 `
    -SecurityRules $nsgRuleRDP02

# Creacion de IP Publica .
$publicIp02 = New-AzureRmPublicIpAddress `
   -Name $NombreIpPublica02 `
   -ResourceGroupName $rg.ResourceGroupName `
   -AllocationMethod Dynamic `
   -DomainNameLabel $Dns02 `
   -Location $Lugar `
   -IdleTimeoutInMinutes 4

# Creacion de la Tarjeta Virtual de Red y asociacion NSG y segunda subnet
$nic02 = New-AzureRmNetworkInterface `
    -Name $NombreNic02 `
    -ResourceGroupName $rg.ResourceGroupName `
    -Location $Lugar `
    -SubnetId $VNet.Subnets[1].Id `
    -PublicIpAddressId $PublicIp02.Id `
    -NetworkSecurityGroupId $nsg02.Id

# Creacion configuracion de la VM de la subnet publica
$vmConfig2 = New-AzureRmVMConfig `
                -VMName $NombreVm002 `
                -VMSize Standard_B1s | `
            Set-AzureRmVMOperatingSystem `
                -Windows -ComputerName $NombreVm002 `
                -Credential $Credenciales | `
            Set-AzureRmVMSourceImage `
                -PublisherName MicrosoftWindowsServer `
                -Offer WindowsServer `
                -Skus 2012-R2-Datacenter -Version latest | `
            Add-AzureRmVMNetworkInterface -Id $nic02.Id

# Creacion de la VM con la configuracion anterior
$Vm2 = New-AzureRmVM -ResourceGroupName $rg.ResourceGroupName -Location $Lugar -VM $vmConfig2
