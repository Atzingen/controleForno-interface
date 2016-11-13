# -*- coding: latin-1 -*-
'''
Entender quem é quem nessa bagunça
'''

#### do arduino -
void setPinResistencia(int pinR1=2, int pinR2=3,int pinR3=4,int pinR4=5,int pinR5=6,int pinR6=7);
void setPinEsteira(int pinEstEnable=12, int pinEstPwm=11, int pinEstSentido=10);
void setPinSensores(int pinS1=4, int pinS2=3, int pinS3=5, int pinS4=0, int pinS5=2, int pinS6=1);

##### do arquivo tela.py  #############

self.ubee       = '0010'	# primeiros 4 dados que chegam (código do ubee)
self.liga_02    = 'S21\n'	# Resistência 2
self.desliga_02 = 'S22\n'
self.liga_04    = 'S31\n'	# Resistência 4
self.desliga_04 = 'S32\n'
self.liga_06    = 'S41\n'	# Resistência 6
self.desliga_06 = 'S42\n'
self.liga_05    = 'S51\n'	# Resistência 5
self.desliga_05 = 'S52\n'
self.liga_03    = 'S61\n'	# Resistência 3
self.desliga_03 = 'S62\n'
self.liga_01    = 'S71\n'	# Resistência 1
self.desliga_01 = 'S72\n'


##### do arquivo comunicacao_serial.py   #####################################

def resistencia01(self):
    '''
    Função que é chamada quando alguma mudança no controle da GUI relativa a
    resistência 1 ocorre.
    A função verifica o estado da resistência 1 e envia a informação adequada
    para o mc caso seja necessário.
    '''
    # Os dados são enviados apenas se o 'hold' não estiver pressionado.
    if (not self.ui.radioButton_hold.isChecked()):
        # pega o valor (posição) do slider da resistência 1.
        valor = int(self.ui.horizontalSlider_r01.value())
        # envia o dado adequado em função do valor 0, 1..99, 100.
        if valor == 100:
            envia_serial(self,self.liga_02)
        elif valor == 0:
            envia_serial(self,self.desliga_02)
        elif valor > 0 and valor < 100:
            envia_serial(self,'SP2' + str(valor) + '\n')
        # teste de retorno para verificar se os valores foram recebidos pelo mc
        QtCore.QTimer.singleShot(3000, partial(teste_retorno,self))

def resistencia02(self):
    '''  Item a resistencia01 '''
    if (not self.ui.radioButton_hold.isChecked()):
        valor = int(self.ui.horizontalSlider_r02.value())
        if valor == 100:
            envia_serial(self,self.liga_04)
        elif valor == 0:
            envia_serial(self,self.desliga_04)
        elif valor > 0 and valor < 100:
            envia_serial(self,'SP3' + str(valor) + '\n')
        QtCore.QTimer.singleShot(3000, partial(teste_retorno,self))

def resistencia03(self):
    '''  Item a resistencia01 '''
    if (not self.ui.radioButton_hold.isChecked()):
        valor = int(self.ui.horizontalSlider_r03.value())
        if valor == 100:
            envia_serial(self,self.liga_06)
        elif valor == 0:
            envia_serial(self,self.desliga_06)
        elif valor > 0 and valor < 100:
            envia_serial(self,'SP4' + str(valor) + '\n')
        QtCore.QTimer.singleShot(3000, partial(teste_retorno,self))

def resistencia04(self):
    '''  Item a resistencia01 '''
    if (not self.ui.radioButton_hold.isChecked()):
        valor = int(self.ui.horizontalSlider_r04.value())
        if valor == 100:
            envia_serial(self,self.liga_05)
        elif valor == 0:
            envia_serial(self,self.desliga_05)
        elif valor > 0 and valor < 100:
            envia_serial(self,'SP5' + str(valor) + '\n')
        QtCore.QTimer.singleShot(3000, partial(teste_retorno,self))

def resistencia05(self):
    '''  Item a resistencia01 '''
    if (not self.ui.radioButton_hold.isChecked()):
        valor = int(self.ui.horizontalSlider_r05.value())
        if valor == 100:
            envia_serial(self,self.liga_03)
        elif valor == 0:
            envia_serial(self,self.desliga_03)
        elif valor > 0 and valor < 100:
            envia_serial(self,'SP6' + str(valor) + '\n')
        QtCore.QTimer.singleShot(3000, partial(teste_retorno,self))

def resistencia06(self):
    '''  Item a resistencia01 '''
    if (not self.ui.radioButton_hold.isChecked()):
        valor = int(self.ui.horizontalSlider_r06.value())
        if valor == 100:
            envia_serial(self,self.liga_01)
        elif valor == 0:
            envia_serial(self,self.desliga_01)
        elif valor > 0 and valor < 100:
            envia_serial(self,'SP7' + str(valor) + '\n')
        QtCore.QTimer.singleShot(3000, partial(teste_retorno,self))
