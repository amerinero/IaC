from pyparsing import Word, alphas, alphanums, nums, Combine, Optional, Suppress, Regex
from google.cloud import datastore
import datetime
import pytz
import argparse

def log2cloud (client,type,logfile):

    # Primero parseamos la linea y la troceamos ....

    # logline = MES DD HH:MM:SS HOSTNAME PROC[PID]: MESSAGE

    month = Word(alphas, exact=3)
    ints = Word(nums)
    day = ints
    hour  = Combine(ints + ":" + ints + ":" + ints)

    # Definimos las 4 partes de la linea de log (Ubuntu)
    timestamp = month + day + hour
    hostname = Word(alphas + nums + "_" + "-" + ".")
    appname = Word(alphas + nums + "/" + "-" + "_" + ".") + Optional(Suppress("[") + ints + Suppress("]")) + Suppress(":")
    message = Regex(".*")

    # Componemos la plantilla con la que se hara el parseo
    logline = timestamp + hostname + Optional(appname) + message

    # La fecha en los logs de linux (Ubuntu) viene asi
    datefmt = '%Y %b %d %H:%M:%S'

    # Necesitamos saber en que anio estamos porque no viene en el fichero
    Year = datetime.date.today().year

    # Tambien tenemos que poner la zona horaria. No vale con anadir CET y ya
    # Usaremos esto luego con la hora que saquemos de la linea
    timezone=pytz.timezone("CET")

    # A partir de aqui viene lo que tenemos que repetir por cada linea del fichero
    linecounter = 0
    with open(logfile) as syslogFile:
      for line in syslogFile:
          linecounter += 1
          print line
          # Realizamos el parseo de la linea de log para sacar todos los campos separaditos
          campos = logline.parseString(line)

           # DEBUG
        #   for i in range(len(campos)):
        #     print ("Campo[",i,"]=",campos[i])

          # Componemos una cadena con el timestamp sacado de la linea de log
          fechastr="%d %s %02d %s" % (Year,campos[0],int(campos[1]),campos[2])

          # A partir de la cadena antiior creamos un objeto datetime
          fecha = datetime.datetime.strptime(fechastr,datefmt)

          # Anadimos la zona horaria al objeto datetime creado anteriormente
          fechatz = timezone.localize(fecha)

          # Despues lo inseretamos en la bbdd de la nube

          key = client.key(type)
          logline_db = datastore.Entity(
          key, exclude_from_indexes=['Mensaje'])

        #   print ("Numero de campos:",len(campos))

          if (len(campos)<5):
              print ("Linea no procesable")
              print (line)
          elif (len(campos)==5):
              proceso = unicode('-Empty-')
              pid = 0
              Mensaje = unicode(campos[4])
          elif (len(campos)==6):
              proceso = unicode(campos[4])
              pid = 0
              Mensaje = unicode(campos[5])
          else:
              proceso = unicode(campos[4])
              pid = int(campos[5])
              Mensaje = unicode(campos[6])



          logline_db.update({
              'Fecha': fechatz,
              'Hostname': unicode(campos[3]),
              'Proceso': proceso,
              'PID': pid,
              'Mensaje': Mensaje
           })
          client.put(logline_db)

    print ("Total lineas procesadas: ",linecounter)
    return linecounter


# Python main

cmdparser = argparse.ArgumentParser()
cmdparser.add_argument("Project", help="The GCP Project where the datastore is created")
cmdparser.add_argument("Type", help="The datastore type")
cmdparser.add_argument("Logfile", help="The logfile to be stored in cloud datastore")
args = cmdparser.parse_args()

print args

client = datastore.Client(args.Project)
log2cloud(client,args.Type,args.Logfile)

# with open('./pre2gst.log') as syslogFile:
#   for line in syslogFile:
#       print line
#       log2cloud (client,'LogMensaje',line)
