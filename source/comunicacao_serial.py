# -*- coding: latin-1 -*-
from __future__ import division
import sys, os, serial, time
import numpy as np
from functools import partial
from PyQt4 import QtCore
# Imports Locais
from banco_dados import *
from exporta_experimentos import *
from modulo_global import *

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
            print texto_depois
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
                tipo, d = verifica_dado(item,self)
                resultado_dado(self, tipo, d)
        self.timer_serial.singleShot(50,partial(serial_read,self))


def verifica_dado(dado,self):
    '''
    Função que verifica o tipo de dado retornado pela serial para o software
    de controle. Retorna dois parâmetros, o tipo do dado recebido e o valor
    caso este tipo de dado tenha valor.

    Tipo_de_dado, valor <- verifica_dado(dado)

    Tipo_de_dado:.
    1 ->  Dado de Temperatura ('S0001aaaabbbbccccddddeeeeffff') com
            aaaa = 4 digitos do sensor 1, bbbb do sensor 2 e etc.
    2 ->  Liga ou desliga completamente uma das resistências do forno.
            Comandos: S'x''y', com x inteiro = 2 ... 7 e y = 1 ou
            2 (liga ou desliga a esteira).
    3 ->  Para a Esteira. Comando 'SD'.
    4 ->  Esteira para Frente(?) SH'xxx', onde xxx são 1 a 3 digitos
            de 1 a 100 - velocidade da esteira.
    5 ->  Item ao item 4, porém para tras SA.
    6 ->  'Erro' recebido do microcontrolador - Pedido enviao ao arduino não
            estava no formato esperado, portanto o microcontrolador retorna
            a string 'Erro'.
    7 ->  Resposta desconhecida.
    8 ->  Liga parcialmente (pwm) uma das resistências.
            SP'x''y''z'. x: indica a esteira (de 2a7)y e z: o valor de 1 a 99.
    9 ->  Retorno do Pedido de informação das resistencias e esteira (SK).
            formato: S,aaa,bbb,ccc,ddd,eee,fff,ggg
            Onde os dados, a..f são o estado das resistencias e ggg é a
            velocidade da esteira.
    '''
    try:
        if dado[0] == 'S':
            # tipo 1, pedido temperatura - 'S0001aaaabbbbccccddddeeeeffff'
            if len(dado) == 29 and dado[1:29].isdigit() and dado[1:5] == '0001':
                d = converte_dado(dado,self)
                if d[0]:
                    return 1, d
            # tipo 2, ligar ou desligar alguma resistencia - S'x''y'
            elif len(dado) == 3 and dado[1].isdigit() and (dado[2] == '1' or dado[2] == '2'):
                if ( int(dado[1]) > 1 and int(dado[1]) < 8):
                    return 2, dado[1:]
            # tipo 3, parada da esteira
            elif dado == 'SD':
                return 3, dado
            # tipo 4, esteira para frente 0 a 100 - SH'xxx'
            elif dado[0:2] == 'SH' and dado[2:].isdigit() and len(dado) < 6:
                if len(dado) == 4 or dado == "SH100":
                    return 4, dado.strip('SH')
            # tipo 5, esteira para tras 0 a 100 - SA'xxx'
            elif dado[0:2] == 'SA' and dado[2:].isdigit() and len(dado) < 6:
                if len(dado) == 4 or dado == "SA100":
                    return 5, dado.strip('SA')
            # tipo 8, pwd esteira - SP'x''y''z'
            elif dado[0:2] == 'SP' and len(dado) > 3 and len(dado) < 6:
                if ( dado[2:].isdigit() and int(dado[3:]) < 101 ):
                    return 8, dado[2:]
            # tipo 9, retorno de informacao da esteira e resistencias
            elif dado[1] == ',':
                valores = dado.split(',')
                # rerifica se todos os dados chegaram corretamente:
                if len(dado) > 7:
                    return 9, valores
        # tipo 6: Erro - envio de string incorreta ao microcontrolador
        elif 'Erro -' in dado:
            return 6, dado
    except:
        return False, False
    # Caso não seja nenhum dos tipos esperados: erro, tipo 7
    return 7, False

def resultado_dado(self, tipo, d):
    '''
    Função que recebe como entrada o tipo (tipo) de dado recebido e o dado (d)
    pré-processado.
    Com estas informações, as alterações da GUI e nas variáveis de controle
    são feitas para mosrtar o recebimento dos dados.
    '''
    global valor_resistencia01
    global valor_resistencia02
    global valor_resistencia03
    global valor_resistencia04
    global valor_resistencia05
    global valor_resistencia06
    global valor_esteira
    # tipo 1: retono de dados de temperatura.
    if tipo == 1:
        # Altera os valores dos displays de temperatura.
        #temperatura = [None, d[4], d[], d[], d[], d[], d[]]
        self.ui.lcdNumber_s1.display(d[1])
        self.ui.lcdNumber_s2.display(d[2])
        self.ui.lcdNumber_s3.display(d[3])
        self.ui.lcdNumber_s4.display(d[4])
        self.ui.lcdNumber_s5.display(d[5])
        self.ui.lcdNumber_s6.display(d[6])
        # Coloca os dados da temperatura em ums string
        data = str(["%i" % x for x in d])
        # Adiciona um caracter de fim de linha a string
        data = data + '\n'
        self.ui.textEdit_temperatura.insertPlainText(data)
        atuadores = str(valor_resistencia01) + "," + str(valor_resistencia02) + "," + \
        str(valor_resistencia03) + "," + str(valor_resistencia04) + "," + \
        str(valor_resistencia05) + "," + str(valor_resistencia06) + "," + \
        str(valor_esteira)
        calibracao = str(retorna_dados_config_calibracao())
        print atuadores, calibracao
        # Adicionando os dados ao bd:
        # 'Sem nome': padrão para quando ainda não foi dado nome ao experimento
        if str(self.ui.label_nomeExperimento.text()) == 'Sem Nome':
            adiciona_dado(float(d[0]),float(d[1]),float(d[2]),
                          float(d[3]),float(d[4]),float(d[5]),float(d[6]),
                          calibracao=calibracao,atuadores=atuadores)
        else:
            adiciona_dado(float(d[0]),float(d[1]),
                          float(d[2]),float(d[3]),float(d[4]),float(d[5]),
                          float(d[6]),
                          experimento=str(self.ui.label_nomeExperimento.text()),
                          calibracao=calibracao,atuadores=atuadores)
    # Tipo 2 - Liga ou desliga alguma resistência.
    elif tipo == 2:
        # d[0] - Valores de 2 a 7 = as 6 resistências
        if d[0] == '2':
            # d[1] : 1 para ligar e 0 para desligar
            if d[1] == '1':
                # Altera o valor da variável de controle da resistência
                valor_resistencia01 = 100
                # Altera a barra da GUI para a respectiva resistência
                self.ui.progressBar_r01.setValue(100)
            else:
                valor_resistencia01 = 0
                self.ui.progressBar_r01.setValue(0)
        # Idem para as outras 5 resistências
        elif d[0] == '3':									# Resustência 2
            if d[1] == '1':
                valor_resistencia02 = 100
                self.ui.progressBar_r02.setValue(100)
            else:
                valor_resistencia02 = 0
                self.ui.progressBar_r02.setValue(0)
        elif d[0] == '4':									# Resustência 3
            if d[1] == '1':
                valor_resistencia03 = 100
                self.ui.progressBar_r03.setValue(100)
            else:
                valor_resistencia03 = 0
                self.ui.progressBar_r03.setValue(0)
        elif d[0] == '5':									# Resustência 4
            if d[1] == '1':
                valor_resistencia04 = 100
                self.ui.progressBar_r04.setValue(100)
            else:
                valor_resistencia04 = 0
                self.ui.progressBar_r04.setValue(0)
        elif d[0] == '6':									# Resustência 5
            if d[1] == '1':
                valor_resistencia05 = 100
                self.ui.progressBar_r05.setValue(100)
            else:
                valor_resistencia05 = 0
                self.ui.progressBar_r05.setValue(0)
        elif d[0] == '7':									# Resustência 6
            if d[1] == '1':
                valor_resistencia06 = 100
                self.ui.progressBar_r06.setValue(100)
            else:
                valor_resistencia06 = 0
                self.ui.progressBar_r06.setValue(0)

    # tipo 8 - Potência parcial de uma resistência
    elif tipo == 8:
        # d[0] - Valores de 2 a 7 - respectivo a cada resistência
        if d[0] == '2':
            # Altera o valor da variável de controle da resistência
            valor_resistencia01 = int(d[1:])
            # Altera a barra da GUI para a respectiva resistência
            self.ui.progressBar_r01.setValue(int(d[1:]))
        # Idem para as outas 5 resistências
        elif d[0] == '3':
            valor_resistencia02 = int(d[1:])
            self.ui.progressBar_r02.setValue(int(d[1:]))
        elif d[0] == '4':
            valor_resistencia03 = int(d[1:])
            self.ui.progressBar_r03.setValue(int(d[1:]))
        elif d[0] == '5':
            valor_resistencia04 = int(d[1:])
            self.ui.progressBar_r04.setValue(int(d[1:]))
        elif d[0] == '6':
            valor_resistencia05 = int(d[1:])
            self.ui.progressBar_r05.setValue(int(d[1:]))
        elif d[0] == '7':
            valor_resistencia06 = int(d[1:])
            self.ui.progressBar_r06.setValue(int(d[1:]))
    # Tipo 3 - Para completamente a esteira
    elif tipo == 3:
        valor_esteira = 0
    # tipo 4 - Velocidade da esteira para frente (1 a 99)
    elif tipo == 4:
        valor_esteira = int(d)
    # Tipo 5 - Velocidade da esteira para tras (1 a 99)
    elif tipo == 5:
        valor_esteira = -1*int(d)
    elif tipo == 9:
        # Atualiza o valor das variaveis globais
        valor_resistencia01 = int(d[1])
        valor_resistencia02 = int(d[2])
        valor_resistencia03 = int(d[3])
        valor_resistencia04 = int(d[4])
        valor_resistencia05 = int(d[5])
        valor_resistencia06 = int(d[6])
        valor_esteira = int(x=d[7])
        # Atualiza os slides e controles da GUI
        QtCore.QTimer.singleShot(10, partial(teste_retorno,self))
    else:
        print "erro no recebimento !!!!!!!"

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

def converte_dado(dado,self):
    '''
    Função que recebe o dado como string e particiona em um vetor com 7 pos.
    A primeira posição é o tempo atual e as outras 6 são os dados dos sensores
    '''
    try:
        dado = dado.strip('S')
        d = np.zeros([7,1])
        # captura a instante em que a coleta foi feita
        d[0] = time.time()
        # sensores 1,..,6
        d[1] = float(self.S_01_A) + (float(self.S_01_B) * int(dado[4:8]))
        d[2] = float(self.S_02_A) + (float(self.S_02_B) * int(dado[8:12]))
        d[3] = float(self.S_03_A) + (float(self.S_03_B) * int(dado[24:28]))
        d[4] = float(self.S_04_A) + (float(self.S_04_B) * int(dado[12:16]))
        d[5] = float(self.S_05_A) + (float(self.S_05_B) * int(dado[20:24]))
        d[6] = float(self.S_06_A) + (float(self.S_06_B) * int(dado[16:20]))
        return d
    except:
        return False

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

def converte_numero(s):
    '''
    Retorna True caso o valor passado seja um int ou float na string
    '''
    try:
        return float(s)
    except ValueError:
        return False
