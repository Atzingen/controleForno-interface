# -*- coding: latin-1 -*-
from __future__ import division
import sys, os, serial, time, glob
import numpy as np
from functools import partial
from PyQt4 import QtCore
# Imports Locais
from modulo_global import *
import exporta_experimentos, trata_dados
import banco.bd_sensores as bd_sensores
import banco.bd_config as bd_config

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

def conecta(self):
    '''
    Evento ocorre quando o botao de conectar/desconectar é pressionado
    '''
    texto_botao = self.ui.pushButton_conectar.text()
    if ( texto_botao == 'Conectar' ):
        # Configurações da comunicação serial:
        baudrate = int(self.ui.comboBox_baudRate.currentText())
        porta    = str(self.ui.comboBox_portaSerial.currentText())
        # Caso os dados de conf. tenham sido selecionados (porta não é vazio)
        if ( porta > 1 and baudrate is not '' ):
            try:
                self.s.port = porta
                self.s.baudrate = baudrate
                self.s.timeout=0
                # caso a porta esteja aberta, feche e abre de novo.
                if self.s.is_open:
                    self.s.close()
                    time.sleep(0.05)
                self.s.open()
                # altera as informações da ui para conectado.
                self.enabled_disabled(True)
                self.ui.pushButton_conectar.setText('Desconectar')
                self.timer_serial.singleShot(100,partial(serial_read,self))
                self.timer_serial.singleShot(500,partial(envia_serial,self,self.CHR_check))
                self.timer_serial.singleShot(600,partial(envia_setanalog,self,atualiza=False))
                self.timer_serial.singleShot(700,partial(envia_setpwm,self,atualiza=False))
            except:
                self.alerta_toolbar('erro ao conectar')
    elif ( texto_botao == 'Desconectar'):
        self.enabled_disabled(False)
        try:
            self.s.close()
        except:
            self.alerta_toolbar('erro ao desconectar')
        self.ui.pushButton_conectar.setText('Conectar')

def serial_read(self):
    if self.s.is_open:
        self.texto += self.s.read(self.s.in_waiting)
        if '\r\n' in self.texto:
            # separa a string recebida (caso haja mais de um dado recebido)
            texto_depois = self.texto.split('\r\n')
            # if: verificar se o ultimo elemento da lista não é vazio e portanto
            # ainda existe parta do dao a ser recebida (salvar a parte recebida)
            if texto_depois[-1] != '':
                self.texto = texto_depois[-1]
            else:
                # caso os dados tenham chegado por compelto, apaga o buffer
                self.texto = ''
            # remove o ultimo elemento da lista ( '' ou dado parcial)
            texto_depois = texto_depois[:-1]
            for item in texto_depois:
                self.alerta_toolbar('Dado Recebido: ' + item)
                self.ui.textEdit_dadosSerial.insertPlainText(item + '\n')
                tipo, d = trata_dados.verifica_dado(item,self)
                print 'DEBUG: tratado:', item, tipo, d
                trata_dados.resultado_dado(self, tipo, d)
        self.timer_serial.singleShot(50,partial(serial_read,self))

def envia_serial(self,dado):
    '''
    Método que envia uma string pela serial
    '''
    print "DEBUG: enviando:", self.CHR_inicioDado + dado
    try:
        if self.s.is_open:
            self.s.write(self.CHR_inicioDado + dado + '\n')
    except:
        self.alerta_toolbar('Erro ao enviar dado pela serial')
        pass

def auto_ST(self):
    '''
    Método recursivo.
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
        envia_serial(self,self.CHR_pedidoTemperaturas)
        # tempo para chamar a função de forma recursiva.
        tempo = 1000*self.ui.spinBox_serialUpdate.value()
        self.timer_ST.singleShot(tempo,partial(auto_ST,self))

def envia_setpwm(self, atualiza):
    try:
        if atualiza:
            self.tempo_pwm = int(self.ui.lineEdit_periodoPWM.text())
            bd_config.salva_config_pwm(self.tempo_pwm)
        else:
            self.tempo_pwm = bd_config.retorna_dados_config()[9]
        envia_serial(self,self.CHR_tempoPWM + str(self.tempo_pwm))
    except:
        self.alerta_toolbar('Erro envia_setpwm - int')

def envia_setanalog(self, atualiza):
    try:
        if atualiza:
            texto_nLeituras = str(self.ui.lineEdit_analogicaNleituras.text())
            texto_delay = str(self.ui.lineEdit_analogicaDelayms.text())
            bd_config.salva_config_ad(int(texto_nLeituras),int(texto_delay))
        else:
            resposta_bd = bd_config.retorna_dados_config()[9]
            texto_nLeituras, texto_delay = resposta_bd[10], resposta_bd[11]
        if len(texto_nLeituras) > 2:
            texto_nLeituras = texto_nLeituras[0:2]
        elif len(texto_nLeituras) == 1:
            texto_nLeituras = '0' + texto_nLeituras
        elif len(texto_nLeituras) < 1:
            self.alerta_toolbar('erro textbox nLeituras (2 caracteres)')
            return None
        texto_delay = self.ui.lineEdit_analogicaDelayms.text()
        envia_serial(self,self.CHR_setADC + texto_nLeituras + str(texto_delay))
    except:
        self.alerta_toolbar('Erro envia_setanalog')

def envia_manual(self):
    '''
    Envia os dados da string contida na lineEdit (envio manual)
    '''
    # captura o texto da lineEdit
    texto = self.ui.lineEdit_serialManual.text()
    try:
        if self.s.is_open:
            self.s.write(str(texto) + '\n')
    except:
        self.alerta_toolbar('Erro ao enviar dado pela serial')
        pass
    # Apaga a string enviada da lineEdit
    self.ui.lineEdit_serialManual.setText('')

def envia_resistencia(self,n):
    '''
    Função que é chamada quando alguma mudança no controle da GUI relativa a
    uma das resistências (1 a 6) ocorre.
    A função verifica o estado da resistência n e envia a informação adequada
    para o mc caso seja necessário.
    '''
    # Os dados são enviados apenas se o 'hold' não estiver pressionado.
    if (not self.ui.radioButton_hold.isChecked()):
        # pega o valor (posição) do slider da resistência 1.
        if n == 1:
            str_pin = self.pinR1
            valor = int(self.ui.horizontalSlider_r01.value())
        elif n == 2:
            str_pin = self.pinR2
            valor = int(self.ui.horizontalSlider_r02.value())
        elif n == 3:
            str_pin = self.pinR3
            valor = int(self.ui.horizontalSlider_r03.value())
        elif n == 4:
            str_pin = self.pinR4
            valor = int(self.ui.horizontalSlider_r04.value())
        elif n == 5:
            str_pin = self.pinR5
            valor = int(self.ui.horizontalSlider_r05.value())
        elif n == 6:
            str_pin = self.pinR6
            valor = int(self.ui.horizontalSlider_r06.value())
        else:
            self.alerta_toolbar(self,"n fora do range (1..6)")
            return None
        # envia o dado adequado em função do valor 0, 1..99, 100.
        if valor == 100:
            envia_serial(self,str_pin + self.CHR_ligaForno)
        elif valor == 0:
            envia_serial(self,str_pin + self.CHR_desligaForno)
        elif valor > 0 and valor < 100:
            envia_serial(self,self.CHR_setPotenciaPWM + str_pin + str(valor))
        else:
            self.alerta_toolbar(self,"valor fora do range (0..100)")
            return None
        print 'DEBUG:', 'envia_serial', str_pin, valor
        # teste de retorno para verificar se os valores foram recebidos pelo mc
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
        for i in range(1,7):
            QtCore.QTimer.singleShot(100*i, partial(envia_resistencia,self,i))
        # teste de retorno para verificar se os valores foram recebidos pelo mc
        QtCore.QTimer.singleShot(3000, partial(teste_retorno,self))

def esteira(self,sinal):
    '''
    Função que é acionada ao alterar o valor do slider da esteira. Envia para o
    mc o comando adequado
    O sinal pode ter sido disparado por 4 eventos: alteração no slider da
    esteira, botao frente ou botao tras ou botao parada. A informação de quem
    disparou o sinal é enviada como uma string sinal em parâmetros.
    '''
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
        envia_serial(self,self.CHR_esteiraFrente + str(valor))
        self.ui.radioButton_esteiraFrente.setChecked(False)
        self.ui.radioButton_esteiraTras.setChecked(False)
    elif valor < 0 and valor > -100:
        self.ui.radioButton_esteiraFrente.setChecked(False)
        self.ui.radioButton_esteiraTras.setChecked(False)
        envia_serial(self,self.CHR_esteiraTras + str(abs(valor)))
    elif valor == -100:
        self.ui.radioButton_esteiraFrente.setChecked(False)
        self.ui.radioButton_esteiraTras.setChecked(True)
        envia_serial(self,self.CHR_esteiraTras + str(abs(valor)))
    elif valor == 100:
        self.ui.radioButton_esteiraFrente.setChecked(True)
        self.ui.radioButton_esteiraTras.setChecked(False)
        envia_serial(self,self.CHR_esteiraFrente + str(abs(valor)))
    else:
        envia_serial(self,self.CHR_esteiraParada)
    # teste de retorno para verificar se os valores foram recebidos pelo mc
    QtCore.QTimer.singleShot(3000, partial(teste_retorno,self))

def emergencia(self):
    '''
    Função de Emergência. Para a esteira e desliga todas as resistências
    '''
    envia_serial(self,self.STR_emergencia)
    # teste de retorno para verificar se os valores foram recebidos pelo mc
    QtCore.QTimer.singleShot(4000, partial(teste_retorno,self))

def teste_retorno(self):
    '''
    Função que é chamada após alteração no estado da esteira resistências.
    Esta função é chamada t segundos após o envio do comando para o microcontrolador,
    com o objetivo de rerificar se este recebeu corretamente o comando (quando isto ocorre
    o mc devolve o mesmo comando em uma string (eco), que é verificada pela
    função de leitura serial, alterando o estado das variáveis de controle da
    esteira e das resistências 1 a 6).
    Para esta verificação, é comparado o estado da variável de controle com o
    estado dos sliders de controle, que são alterados quando recebem o sinal de
    volta do microcontrolador
    '''
    print 'DEBUG: funcao retorno', self.valor_resistencia01, self.valor_resistencia02,\
    self.valor_resistencia03, self.valor_resistencia04, \
    self.valor_resistencia05,self.valor_resistencia06, self.valor_esteira

    self.ui.horizontalSlider_esteira.setValue(self.valor_esteira)
    self.ui.lcdNumber_esteiraVelocidade.display(self.valor_esteira)
    self.ui.radioButton_esteiraFrente.setChecked(self.valor_esteira == 100)
    self.ui.radioButton_esteiraTras.setChecked(self.valor_esteira == -100)

    self.ui.horizontalSlider_r01.setValue(self.valor_resistencia01)
    self.ui.progressBar_r01.setValue(self.valor_resistencia01)

    self.ui.horizontalSlider_r02.setValue(self.valor_resistencia02)
    self.ui.progressBar_r02.setValue(self.valor_resistencia02)

    self.ui.horizontalSlider_r03.setValue(self.valor_resistencia03)
    self.ui.progressBar_r03.setValue(self.valor_resistencia03)

    self.ui.horizontalSlider_r04.setValue(self.valor_resistencia04)
    self.ui.progressBar_r04.setValue(self.valor_resistencia04)

    self.ui.horizontalSlider_r05.setValue(self.valor_resistencia05)
    self.ui.progressBar_r05.setValue(self.valor_resistencia05)

    self.ui.horizontalSlider_r06.setValue(self.valor_resistencia06)
    self.ui.progressBar_r06.setValue(self.valor_resistencia06)
