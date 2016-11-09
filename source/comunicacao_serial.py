# -*- coding: latin-1 -*-
from __future__ import division
import sys, os, serial, time, glob
import numpy as np
from functools import partial
from PyQt4 import QtCore
# Imports Locais
import exporta_experimentos, bd_sensores, modulo_global, trata_dados
def conecta(self):
    '''
    Evento ocorre quando o botao de conectar/desconectar é pressionado
    '''
    # s é o objeto serial que será criado/destruido/usado
    global s
    texto_botao = self.ui.pushButton_conectar.text()
    if ( texto_botao == 'Conectar' ):
        # Configurações da comunicação serial:
        baudrate = int(self.ui.comboBox_baudRate.currentText())
        porta    = str(self.ui.comboBox_portaSerial.currentText())
        # Caso os dados de conf. tenham sido selecionados (porta não é vazio)
        if ( porta > 1 and baudrate is not '' ):
            try:
                s.port = porta
                s.baudrate = baudrate
                s.timeout=0
                # caso a porta esteja aberta, feche e abre de novo.
                if s.is_open:
                    s.close()
                    time.sleep(0.05)
                s.open()
                # altera as informações da ui para conectado.
                self.enabled_disabled(True)
                self.ui.pushButton_conectar.setText('Desconectar')
                self.timer_serial.singleShot(500,partial(serial_read,self))
            except:
                self.alerta_toolbar('erro ao conectar')
    elif ( texto_botao == 'Desconectar'):
        self.enabled_disabled(False)
        try:
            s.close()
        except:
            pass
        self.ui.pushButton_conectar.setText('Conectar')

def envia_serial(dado):
    ''' Método que envia uma string pela serial '''
    global s
    try:
        if s.is_open:
            s.write(dado)
    except:
        self.alerta_toolbar('Erro ao enviar dado pela serial')
        pass

def serial_read(self):
    global texto
    if s.is_open:
        texto += s.read(s.in_waiting)
        if '\r\n' in texto:
            # separa a string recebida (caso haja mais de um dado recebido)
            texto_depois = texto.split('\r\n')
            # if: verificar se o ultimo elemento da lista não é vazio e portanto
            # ainda existe parta do dao a ser recebida (salvar a parte recebida)
            if texto_depois[-1] != '':
                texto = texto_depois[-1]
            else:
                # caso os dados tenham chegado por compelto, apaga o buffer
                texto = ''
            # remove o ultimo elemento da lista ( '' ou dado parcial)
            texto_depois = texto_depois[:-1]
            for item in texto_depois:
                self.alerta_toolbar('Dado Recebido: ' + item)
                self.ui.textEdit_dadosSerial.insertPlainText(item + '\n')
                tipo, d = trata_dados.verifica_dado(item,self)
                trata_dados.resultado_dado(self, tipo, d)
        self.timer_serial.singleShot(50,partial(serial_read,self))

def envia_setpwm(self):
    texto = self.ui.lineEdit_periodoPWM.text()
    print 'SU' + str(texto) + '\n'
    envia_serial('SU' + str(texto) + '\n')

def envia_setanalog(self):
    texto_nLeituras = str(self.ui.lineEdit_analogicaNleituras.text())
    if len(texto_nLeituras) > 2:
        texto_nLeituras = texto_nLeituras[0:2]
    elif len(texto_nLeituras) == 1:
        texto_nLeituras = '0' + texto_nLeituras
    elif len(texto_nLeituras) < 1:
        self.alerta_toolbar('erro textbox nLeituras (2 caracteres)')
        return None
    texto_delay = self.ui.lineEdit_analogicaDelayms.text()
    print 'SL' + texto_nLeituras + str(texto_delay) + '\n'
    envia_serial('SL' + texto_nLeituras + str(texto_delay) + '\n')

def envia_manual(self):
    '''
    Envia os dados da string contida na lineEdit (envio manual) '''
    # captura o texto da lineEdit
    texto = self.ui.lineEdit_serialManual.text()
    print "envia serial: ", texto
    envia_serial(str(texto) + '\n')
    # Apaga a string enviada da lineEdit
    self.ui.lineEdit_serialManual.setText('')

def auto_ST(self):
    ''' Método recursivo.
    É chamado quando a checkbox de receber a temperatura dos sensores
    automaticamente é ativada.
    A função ativa uma thread do QT no modo singleShot após a quantidad de tempo
    escolhida no spinBox_serialUpdate da GUI. caso a checkbox continue ativada,
    a função se chamará novamente de forma recursiva até que a checkbox seja
    desabilitada ou a conecção seja desfeita.
    '''
    # Executa apenas quando a checkbox está ativada
    if self.ui.checkBox_serialAuto.isChecked():
        # Função que envia o pedido de temperatura para o microcontrolador
        envia_serial('ST\n')
        # tempo para chamar a função de forma recursiva.
        tempo = 1000*self.ui.spinBox_serialUpdate.value()
        self.timer_ST.singleShot(tempo,partial(auto_ST,self))

def serial_ports():
    '''
    Retorna uma lista as possíveis portas seriais (reais ou virtuais) diponíveis no
    sistema operacional
    '''
    # windows:
    if sys.platform.startswith('win'):
        ports = ['COM' + str(i + 1) for i in range(256)]
    # Linux
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = glob.glob('/dev/tty[A-Za-z]*')
    # Mac OS
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')
    # Retorna a lista com as portas seriais encontradas
    return ports

###################################################################################################################
#################################   Comandos forno   ##############################################################

def teste_retorno(self):
    ''' Função que é chamada apés alteração no estado da esteira resistências.
    Esta função é chamada t segundos após o envio do comando para o microcontrolador,
    com o objetivo de rerificar se este recebeu corretamente o comando (quando isto ocorre
    o mc devolve o mesmo comando em uma string (eco), que é verificada pela
    função de leitura serial, alterando o estado das variáveis de controle da
    esteira e das resistências 1 a 6).
    Para esta verificação, é comparado o estado da variável de controle com o
    estado dos sliders de controle, que são alterados quando recebem o sinal de
    volta do microcontrolador '''

    global valor_resistencia01
    global valor_resistencia02
    global valor_resistencia03
    global valor_resistencia04
    global valor_resistencia05
    global valor_resistencia06
    global valor_esteira

    #print 'funcao retorno' # debug
    #print valor_resistencia01, valor_resistencia02, valor_resistencia03
    #print valor_resistencia04, valor_resistencia05, valor_resistencia06, valor_esteira

    self.ui.horizontalSlider_esteira.setValue(valor_esteira)
    self.ui.lcdNumber_esteiraVelocidade.display(valor_esteira)
    self.ui.radioButton_esteiraFrente.setChecked(valor_esteira == 100)
    self.ui.radioButton_esteiraTras.setChecked(valor_esteira == -100)

    self.ui.horizontalSlider_r01.setValue(valor_resistencia01)
    self.ui.progressBar_r01.setValue(valor_resistencia01)

    self.ui.horizontalSlider_r02.setValue(valor_resistencia02)
    self.ui.progressBar_r02.setValue(valor_resistencia02)

    self.ui.horizontalSlider_r03.setValue(valor_resistencia03)
    self.ui.progressBar_r03.setValue(valor_resistencia03)

    self.ui.horizontalSlider_r04.setValue(valor_resistencia04)
    self.ui.progressBar_r04.setValue(valor_resistencia04)

    self.ui.horizontalSlider_r05.setValue(valor_resistencia05)
    self.ui.progressBar_r05.setValue(valor_resistencia05)

    self.ui.horizontalSlider_r06.setValue(valor_resistencia06)
    self.ui.progressBar_r06.setValue(valor_resistencia06)

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
            envia_serial(liga_02)
        elif valor == 0:
            envia_serial(desliga_02)
        elif valor > 0 and valor < 100:
            envia_serial('SP2' + str(valor) + '\n')
        # teste de retorno para verificar se os valores foram recebidos pelo mc
        QtCore.QTimer.singleShot(3000, partial(teste_retorno,self))

def resistencia02(self):
    '''  Item a resistencia01 '''
    if (not self.ui.radioButton_hold.isChecked()):
        valor = int(self.ui.horizontalSlider_r02.value())
        if valor == 100:
            envia_serial(liga_04)
        elif valor == 0:
            envia_serial(desliga_04)
        elif valor > 0 and valor < 100:
            envia_serial('SP3' + str(valor) + '\n')
        QtCore.QTimer.singleShot(3000, partial(teste_retorno,self))

def resistencia03(self):
    '''  Item a resistencia01 '''
    if (not self.ui.radioButton_hold.isChecked()):
        valor = int(self.ui.horizontalSlider_r03.value())
        if valor == 100:
            envia_serial(liga_06)
        elif valor == 0:
            envia_serial(desliga_06)
        elif valor > 0 and valor < 100:
            envia_serial('SP4' + str(valor) + '\n')
        QtCore.QTimer.singleShot(3000, partial(teste_retorno,self))

def resistencia04(self):
    '''  Item a resistencia01 '''
    if (not self.ui.radioButton_hold.isChecked()):
        valor = int(self.ui.horizontalSlider_r04.value())
        if valor == 100:
            envia_serial(liga_05)
        elif valor == 0:
            envia_serial(desliga_05)
        elif valor > 0 and valor < 100:
            envia_serial('SP5' + str(valor) + '\n')
        QtCore.QTimer.singleShot(3000, partial(teste_retorno,self))

def resistencia05(self):
    '''  Item a resistencia01 '''
    if (not self.ui.radioButton_hold.isChecked()):
        valor = int(self.ui.horizontalSlider_r05.value())
        if valor == 100:
            envia_serial(liga_03)
        elif valor == 0:
            envia_serial(desliga_03)
        elif valor > 0 and valor < 100:
            envia_serial('SP6' + str(valor) + '\n')
        QtCore.QTimer.singleShot(3000, partial(teste_retorno,self))

def resistencia06(self):
    '''  Item a resistencia01 '''
    if (not self.ui.radioButton_hold.isChecked()):
        valor = int(self.ui.horizontalSlider_r06.value())
        if valor == 100:
            envia_serial(liga_01)
        elif valor == 0:
            envia_serial(desliga_01)
        elif valor > 0 and valor < 100:
            envia_serial('SP7' + str(valor) + '\n')
        QtCore.QTimer.singleShot(3000, partial(teste_retorno,self))

def hold(self):
    '''
    Função que é chamada quando o estado do checkbox 'hold' é alterado.
    Caso o hold seja desligado (solto). São chamadas as funções de todas as
    esteiras para enviar os dados caso haja diferença entre o estado da variável
    e do slider.
    Caso o hold tenha sido pressionado nada ocorre.
    '''
    # Caso o 'hold' tenha sido desligado:
    if ( self.ui.radioButton_hold.isChecked() == False ):
        resistencia01(self)
        QtCore.QTimer.singleShot(50,  partial(resistencia02,self))
        QtCore.QTimer.singleShot(100, partial(resistencia03,self))
        QtCore.QTimer.singleShot(150, partial(resistencia04,self))
        QtCore.QTimer.singleShot(200, partial(resistencia05,self))
        QtCore.QTimer.singleShot(250, partial(resistencia06,self))
        # teste de retorno para verificar se os valores foram recebidos pelo mc
        QtCore.QTimer.singleShot(3000, partial(teste_retorno,self))

def esteira(parametros):
    '''
    Função que é acionada ao alterar o valor do slider da esteira. Envia para o
    mc o comando adequado
    O sinal pode ter sido disparado por 4 eventos: alteração no slider da
    esteira, botao frente ou botao tras ou botao parada. A informação de quem
    disparou o sinal é enviada como uma string sinal em parâmetros.
    '''
    self, sinal = parametros
    # Caso o sinal não seja do slider, atualizar o valor deste de acordo
    # com quem enviou o sinal: (botão parada, frente o tras)
    if sinal == 'frente':
        self.ui.horizontalSlider_esteira.setValue(100)
    elif sinal == 'tras':
        self.ui.horizontalSlider_esteira.setValue(-100)
    elif sinal == 'parar':
        self.ui.horizontalSlider_esteira.setValue(0)
    valor = self.ui.horizontalSlider_esteira.value()
    if valor > 0 and valor < 100:
        s.write('SH' + str(valor) + '\n')
        self.ui.radioButton_esteiraFrente.setChecked(False)
        self.ui.radioButton_esteiraTras.setChecked(False)
    elif valor < 0 and valor > -100:
        self.ui.radioButton_esteiraFrente.setChecked(False)
        self.ui.radioButton_esteiraTras.setChecked(False)
        s.write('SA' + str(abs(valor)) + '\n')
    elif valor == -100:
        self.ui.radioButton_esteiraFrente.setChecked(False)
        self.ui.radioButton_esteiraTras.setChecked(True)
        s.write('SA' + str(abs(valor)) + '\n')
    elif valor == 100:
        self.ui.radioButton_esteiraFrente.setChecked(True)
        self.ui.radioButton_esteiraTras.setChecked(False)
        s.write('SH' + str(abs(valor)) + '\n')
    else:
        s.write('SD\n')
    # teste de retorno para verificar se os valores foram recebidos pelo mc
    QtCore.QTimer.singleShot(3000, partial(teste_retorno,self))

def emergencia(self):
    ''' Função de Emergência. Para a esteira e desliga todas as resistências '''
    s.write('SD\n')
    QtCore.QTimer.singleShot(50, partial(envia_serial,'SD' + '\n'))
    for i in range(2,8):
        QtCore.QTimer.singleShot((i-1)*200, partial(envia_serial,'S' + str(i) + '2\n'))
    # teste de retorno para verificar se os valores foram recebidos pelo mc
    QtCore.QTimer.singleShot(4000, partial(teste_retorno,self))
