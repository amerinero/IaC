from pyparsing import Word, alphas, alphanums, nums, Combine, Optional, Suppress, Regex
from google.cloud import datastore

def log2cloud (client,type,line):

    # Primero parseamos la linea y la troceamos

    #logline = MES DD HH:MM:SS HOSTNAME PROC[PID]: MESSAGE
    month = Word(alphas, exact=3)
    ints = Word(nums)
    day = ints
    hour  = Combine(ints + ":" + ints + ":" + ints)
    timestamp = month + day + hour
    hostname = Word(alphas + nums + "_" + "-" + ".")
    appname = Word(alphas + "/" + "-" + "_" + ".") + Optional(Suppress("[") + ints + Suppress("]")) + Suppress(":")
    message = Regex(".*")
    logline = timestamp + hostname + appname + message
    mess_prueba = "Oct 26 08:30:01 MX3750006dc0458 systemd[1]: Started Session 653 of user mfe."
    #campos = logline.parseString(mess_prueba)
    campos = logline.parseString(line)
    for i in range(len(campos)):
        print ("Campo[",i,"]=",campos[i])

    # Despues lo inseretamos en la bbdd de la nube

    key = client.key(type)
    logline_db = datastore.Entity(
        key, exclude_from_indexes=['Mensaje'])

    logline_db.update({
        'Fecha': campos[0]+campos[1]+campos[2],
        'Hostname': campos[3],
        'Mensaje': campos[4]+campos[5]+campos[6]
    })
    client.put(logline_db)
    return logline_db.key


#print (mess_prueba, "->", campos)
#for i in range(len(campos)):
#    print ("Campo[",i,"]=",campos[i])
Linea ="Oct 26 08:30:01 MX3750006dc0458 systemd[1]: Started Session 653 of user mfe."
client = datastore.Client('unix-logsgraphs')
log2cloud (client,'LogMensaje',Linea)
