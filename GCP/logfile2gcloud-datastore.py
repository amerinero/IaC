from pyparsing import Word, alphas, alphanums, nums, Combine, Optional, Suppress, Regex
from google.cloud import datastore
import datetime
import pytz

def log2cloud (client,type,line):

    # Primero parseamos la linea y la troceamos

    #logline = MES DD HH:MM:SS HOSTNAME PROC[PID]: MESSAGE
    month = Word(alphas, exact=3)
    ints = Word(nums)
    day = ints
    Horas = ints
    Mins = ints
    Segs = ints
    #timestamp = month + day + Horas + Suppress(":") + Mins + Suppress(":") + Segs
    hour  = Combine(ints + ":" + ints + ":" + ints)
    timestamp = month + day + hour
    hostname = Word(alphas + nums + "_" + "-" + ".")
    appname = Word(alphas + nums + "/" + "-" + "_" + ".") + Optional(Suppress("[") + ints + Suppress("]")) + Suppress(":")
    message = Regex(".*")
    logline = timestamp + hostname + appname + message
    mess_prueba = "Oct 28 08:30:01 MX3750006dc0458 systemd[1]: Started Session 653 of user mfe."
    datefmt = '%Y %b %d %H:%M:%S'
    Year=2017
    timezone=pytz.timezone("CET")
    campos = logline.parseString(line)
    # for i in range(len(campos)):
    #     print ("Campo[",i,"]=",campos[i])

    fechastr="%d %s %02d %s" % (Year,campos[0],int(campos[1]),campos[2])
    # print (fechastr)
    fecha = datetime.datetime.strptime(fechastr,datefmt)
    #fecha.tzinfo=CET
    # print (fecha)
    fechatz = timezone.localize(fecha)
    # print (fechatz)
    # Despues lo inseretamos en la bbdd de la nube

    key = client.key(type)
    logline_db = datastore.Entity(
         key, exclude_from_indexes=['Mensaje'])

    logline_db.update({
         'Fecha': fechatz,
         'Hostname': unicode(campos[3]),
         'Proceso': unicode(campos[4]),
         'PID': int(campos[5]),
         'Mensaje': unicode(campos[6])
     })
    client.put(logline_db)
    return logline_db.key


#print (mess_prueba, "->", campos)
#for i in range(len(campos)):
#    print ("Campo[",i,"]=",campos[i])
Linea ="Oct 30 08:30:01 MX3750006dc0458 systemd[1]: Started Session 653 of user mfe."
client = datastore.Client('unix-logsgraphs')
with open('./hoy.log') as syslogFile:
  for line in syslogFile:
      print line
      log2cloud (client,'LogMensaje',line)
