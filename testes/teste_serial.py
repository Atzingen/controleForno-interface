import serial, time

s = serial.Serial()
s.port = "/dev/ttyAMA0"
s.baudrate = 9600
s.timeout=10

ligado = False

s.open()
texto = ""
contador = 1

while s.is_open:
    if contador % 20 == 0:
        if ligado:
            s.write("S21\n")
        else:
            s.write("S22\n")
        ligado = not(ligado)
    if contador % 30 == 0:
        s.write("ST\n")
        print "enviado pedido"
    print s.in_waiting
    if (s.in_waiting > 0):
        texto += s.read(s.in_waiting)
    print "parcial", texto
    if '\r\n' in texto:
        print texto
        texto = ""
    time.sleep(0.1)
    print "sleep ", contador
    contador += 1
print "fim da funcao serial"
