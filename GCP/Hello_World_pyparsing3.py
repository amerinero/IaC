from pyparsing import Word, alphas, alphanums, nums, Combine, Optional, Suppress, Regex
   # define grammar of a greeting
greet = Word(alphanums) + "," + Word(alphas) + "!"
hello = "Primera123,      Segunda!"
print (hello, "->", greet.parseString(hello))

#logline = MES DD HH:MM:SS HOSTNAME PROC[PID]: MESSAGE
month = Word(alphas, exact=3)
ints = Word(nums)
day = ints
Horas = ints
Mins = ints
Segs = ints
hour  = Combine(Horas + ":" + Mins + ":" + Segs)
timestamp = month + day + Horas + Suppress(":") + Mins + Suppress(":") + Segs
hostname = Word(alphas + nums + "_" + "-" + ".")
appname = Word(alphas + "/" + "-" + "_" + ".") + Optional(Suppress("[") + ints + Suppress("]")) + Suppress(":")
message = Regex(".*")
logline = timestamp + hostname + appname + message
mess_prueba = "Oct 26 08:30:01 MX3750006dc0458 systemd[1]: Started Session 653 of user mfe."
campos = logline.parseString(mess_prueba)
print (mess_prueba, "->", campos)
for i in range(len(campos)):
    print ("Campo[",i,"]=",campos[i])

#print ("Campo[0]=", campos[0])
#print ("Campo[1]=", campos[1])
#print ("Campo[2]=", campos[2])
