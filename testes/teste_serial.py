import serial, time

s = serial.Serial()
s.port = "/dev/tty.usbserial-A50285BI"
s.baudrate = 9600
s.timeout=0

s.open()
texto = ""
contador = 1

while s.isOpen():
    if contador % 50 == 0:
        s.write("ST\n")
        print "enviado pedido"
    if (s.inWaiting() > 0):
        texto += s.read(s.inWaiting())
    print "parcial", texto
    if '\r\n' in texto:
        print texto
        texto = ""
    time.sleep(0.1)
    print "sleep ", contador
    contador += 1
print "fim da funcao serial"
