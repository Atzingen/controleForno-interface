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
    ''' Evento ocorre quando o botao de conectar/desconectar é pressionado
    '''
    texto_botao = self.ui.pushButton.text()
    if ( texto_botao == 'Conectar' ):
        baudrate = int(self.ui.comboBox_2.currentText())			# Configurações da comunicação serial
        porta    = str(self.ui.comboBox.currentText())
        if ( porta > 1 and baudrate is not '' ):					# Caso os dados de conf. tenham sido selecionados
            try:
                s.port = porta
                s.baudrate = baudrate
                s.timeout=self.serial_timeout
                #s = serial.Serial(porta,baudrate,timeout=self.serial_timeout)
                if s.isOpen():
                    s.close()
                    time.sleep(0.1)
                s.open()											# abre a comunicação
                self.enabled_disabled(True)							# altera as informações da ui para conectado
                self.ui.pushButton.setText('Desconectar')
                serial_read(self)
            except:
                self.alerta_toolbar('erro ao conectar')
    elif ( texto_botao == 'Desconectar'):							# idem ao desconectar
        self.enabled_disabled(False)
        try:
            s.close()												# fecha a conecção
        except:
            pass
        self.ui.pushButton.setText('Conectar')

def envia_serial(dado):
    ''' Método que envia uma string pela serial '''
    try:
        if s.isOpen():
            s.write(dado)
    except:
        self.alerta_toolbar('Erro ao enviar dado pela serial')
        pass

def serial_read(self):
    try:
        texto = s.readline()										# Quando os dados do forno chegam com quebra de linha '\n'
        if texto is not '':											# Caso tenham dados na pilha
            texto = texto.rstrip('\r\n')							# remove o caractere de fim de linha.
            self.alerta_toolbar('Dado Recebido: ' + texto) 			# Debug - Remover
            self.ui.textEdit.insertPlainText(texto + '\n')    		# Tempo para o delay
            tipo, d = verifica_dado(texto,self)						# Envia a string recebida para a função que trata os dados
            ################## Seleção dos tipos de 1 a 8 (ver função verifica_dado)###########################################
            # Tipo 1 - Recebe os dados de temperatura dos 6 sensores
            if tipo == 1:
                self.ui.lcdNumber.display(d[1])						# Altera os valores dos displays de temperatura
                self.ui.lcdNumber_2.display(d[2])
                self.ui.lcdNumber_3.display(d[3])
                self.ui.lcdNumber_4.display(d[4])
                self.ui.lcdNumber_5.display(d[5])
                self.ui.lcdNumber_6.display(d[6])
                data = str(["%i" % x for x in d])					# Coloca os dados da temperatura em ums string
                data = data + '\n'									# Adiciona um caracter de fim de linha a string
                self.ui.textEdit_2.insertPlainText(data)			# Insere o texto na textbox da GUI
                # Adicionando os dados ao bd
                if self.experimento_nome == 'Sem Nome':				# 'Sem nome': padrão para quando ainda não foi dado nome ao experimento
                    adiciona_dado(float(d[0]),float(d[1]),float(d[2]),
                                                        float(d[3]),float(d[4]),float(d[5]),float(d[6]))
                else:
                    adiciona_dado(float(d[0]),float(d[1]),
                                                        float(d[2]),float(d[3]),float(d[4]),float(d[5]),
                                                        float(d[6]),experimento=str(self.experimento_nome))
            # Tipo 2 - Liga ou desliga alguma resistência.
            elif tipo == 2:
                if d[0] == '2':										# d[0] - Valores de 2 a 7 = as 6 resistências
                    if d[1] == '1':									# d[1] : 1 para ligar e 0 para desligar
                        self.resitencia01 = 100						# Altera o valor da variável de controle da resistência
                        self.ui.progressBar_r01.setValue(100)		# Altera a barra da GUI para a respectiva resistência
                    else:
                        self.resitencia01 = 0
                        self.ui.progressBar_r01.setValue(0)			# Idem para as outras 5 resistências
                elif d[0] == '3':									# Resustência 2
                    if d[1] == '1':
                        self.resitencia02 = 100
                        self.ui.progressBar_r02.setValue(100)
                    else:
                        self.resitencia02 = 0
                        self.ui.progressBar_r02.setValue(0)
                elif d[0] == '4':									# Resustência 3
                    if d[1] == '1':
                        self.resitencia03 = 100
                        self.ui.progressBar_r03.setValue(100)
                    else:
                        self.resitencia03 = 0
                        self.ui.progressBar_r03.setValue(0)
                elif d[0] == '5':									# Resustência 4
                    if d[1] == '1':
                        self.resitencia04 = 100
                        self.ui.progressBar_r04.setValue(100)
                    else:
                        self.resitencia04 = 0
                        self.ui.progressBar_r04.setValue(0)
                elif d[0] == '6':									# Resustência 5
                    if d[1] == '1':
                        self.resitencia05 = 100
                        self.ui.progressBar_r05.setValue(100)
                    else:
                        self.resitencia05 = 0
                        self.ui.progressBar_r05.setValue(0)
                elif d[0] == '7':									# Resustência 6
                    if d[1] == '1':
                        self.resitencia06 = 100
                        self.ui.progressBar_r06.setValue(100)
                    else:
                        self.resitencia06 = 0
                        self.ui.progressBar_r06.setValue(0)
            # tipo 8 - Potência parcial de uma resist6encia
            elif tipo == 8:
                if d[0] == '2':										# d[0] - Valores de 2 a 7 - respectivo a cada resistência
                    self.resitencia01 = int(d[1:])					# Altera o valor da variável de controle da resistência
                    self.ui.progressBar_r01.setValue(int(d[1:])) 	# Altera a barra da GUI para a respectiva resistência
                elif d[0] == '3':									# Idem para as outas 5 resistências
                    self.resitencia02 = int(d[1:])
                    self.ui.progressBar_r02.setValue(int(d[1:]))
                elif d[0] == '4':
                    self.resitencia03 = int(d[1:])
                    self.ui.progressBar_r03.setValue(int(d[1:]))
                elif d[0] == '5':
                    self.resitencia04 = int(d[1:])
                    self.ui.progressBar_r04.setValue(int(d[1:]))
                elif d[0] == '6':
                    self.resitencia05 = int(d[1:])
                    self.ui.progressBar_r05.setValue(int(d[1:]))
                elif d[0] == '7':
                    self.resitencia06 = int(d[1:])
                    self.ui.progressBar_r06.setValue(int(d[1:]))
            # Tipo 3 - Para completamente a esteira
            elif tipo == 3:
                self.esteira = 0
            # tipo 4 - Velocidade da esteira para frente (1 a 99)
            elif tipo == 4:
                self.esteira = int(d)
            # Tipo 5 - Velocidade da esteira para tras (1 a 99)
            elif tipo == 5:
                self.esteira = -1*int(d)
    except Exception as e:
        self.alerta_toolbar('except - função serial_read ' + str(e))
    if s.isOpen() and self.ui.pushButton.text() == 'Desconectar':
        self.timer_serial.singleShot(self.tempo_update_serial,partial(serial_read,self))

def envia_manual(self):
    ''' Envia manualmente dados pela serial. A string contida na lineEdit é capturada e eniada '''
    texto = self.ui.lineEdit.text()						# captura o texto da lineEdit
    s.write(str(texto))									# envia a string pela serial
    s.write('\n')										# envia um caracter de fim de linha
    self.ui.lineEdit.setText('')						# Apaga a string enviada da lineEdit

def auto_ST(self):
    ''' Método recursivo.
    É chamado quando a checkbox de receber a temperatura dos sensores automaticamente é ativada.
    A função ativa uma thread do QT no modo singleShot após a quantidad de tempo escolhida no
    spinBox da GUI. caso a checkbox continue ativada, a função se chamará novamente de forma recursiva
    até que a checkbox seja desabilitada ou a conecção seja desfeita.
    '''
    if self.ui.checkBox_9.isChecked():					# Executa apenas quando a checkbox está ativada
        atualiza_temp(self)							# Função que envia o pedido de temperatura para o microcontrolador
        tempo = 1000*self.ui.spinBox.value()			# *1000 pois o tempo da do método singleshot é em milissegundos
        self.timer_ST.singleShot(tempo,partial(auto_ST,self))   # Thread recursiva única que se chamará.

def verifica_dado(dado,self):
    '''	Função que verifica o tipo de dado retornado pela serial para o software de controle
        Tipo_de_dado, valor <- verifica_dado(dado)
        Retorna dois parâmetros, o tipo do dado recebido e o valor caso este tipo de dado tenha valor
        Tipo_de_dado:
                1 ->  Dado de Temperatura ('S0001aaaabbbbccccddddeeeeffff') com aaaa = 4 digitos do sensor 1,
                                                                                bbbb do sensor 2 e etc
                2 ->  Liga ou desliga completamente uma das resistências do forno. Comandos: S'x''y', com
                        x inteiro = 2 ... 7 e y = 1 ou 2 (liga ou desliga a esteira)
                3 ->  Para a Esteira. Comando 'SD'
                4 ->  Esteira para Frente(?) SH'xx', onde xx são dois (ou 1) digito de 1 a 99 - velocidade
                        da esteira
                5 ->  Item ao item 4 porém para tras(?) SA
                6 ->  'Erro' recebido do microcontrolador - Pedido enviao ao arduino não estava no formato esperado
                7 ->  Resposta desconhecida
                8 ->  Liga parcialmente (pwm) uma das resistências. SP'x''y''z'. x: indica a esteira (de 2 a 7)
                        y e z: o valor de 1 a 99.
    '''
    try:
        if dado[0] == 'S':															# Todo dado sempre começa com o caractere 'S'
            if len(dado) == 29 and dado[1:29].isdigit() and dado[1:5] == '0001':	# Checa se é pedido de temperatura (1)
                d = converte_dado(dado,self)										# Chama a função para retirar os dados e converter
                                                                                    # em temperatura.
                if d[0]:															# Caso a conversão tenha ocorrido com sucesso:
                    return 1, d														# retorna o tipo de dado e os valores
                else:
                    return False, False 											# retorna falso caso haja erro no formato dos dados
            elif len(dado) == 3 and dado[1].isdigit() and (dado[2] == '1' or dado[2] == '2'): # Testa a condição 2 (S'x''y')
                if ( int(dado[1]) > 1 and int(dado[1]) < 8):						# Ainda na condição 2, verifica se 'x' esta entre 2 e 7
                    return 2, dado[1:] 												# retorna o tipo de dado e os valores
            elif dado[0:2] == 'SP' and len(dado) > 3 and len(dado) < 6:				# Testa o tipo 8 (SP...)
                if ( dado[2:].isdigit() and int(dado[3:]) < 101 ):					# Verifica se tudo após os 2 primeiros caracteres
                                                                                    # são dígitos (0..9)
                    return 8, dado[2:]												# Retorna o valor numérico e o código 8
                else:																# Retorna falso não seja apenas digidos aós SP
                    return False, False
            elif dado == 'SD':														# Verifica o tipo 3
                return 3, dado  													# Retorna o valor numérico e o código 3
            elif dado[0:2] == 'SH' and dado[2:].isdigit() and len(dado) < 5:		# verifica o tipo 4
                return 4, dado.strip('SH')											# Retorna o valor numérico e o código 4
            elif dado[0:2] == 'SA' and dado[2:].isdigit() and len(dado) < 5:		# Verifica o tipo 5
                return 5, dado.strip('SA')											# Retorna o valor numérico e o código 5
            elif 'Erro -' in dado:													# Caso haja algum erro captado no microcontrolador
                return 6, dado
            else:
                return 7, False
        else:
            return False, False
    except:
        return False, False

def converte_dado(dado,self):	
    '''Função que recebe o dado como stringo e particiona em um vetor com 7 posições.
    A primeira posição é o tempo atual e as outras 6 são os 6 dados do sensor (int de 0 a 1023)'''
    try:
        dado = dado.strip('S')
        d = np.zeros([7,1])
        d[0] = time.time() 															# tempo_coleta
        d[1] = float(self.S_01_A) + (float(self.S_01_B) * int(dado[4:8]))		# Sensor 1
        d[2] = float(self.S_02_A) + (float(self.S_02_B) * int(dado[8:12]))		# Sensor 2
        d[3] = float(self.S_03_A) + (float(self.S_03_B) * int(dado[24:28]))  	# Sensor 3
        d[4] = float(self.S_04_A) + (float(self.S_04_B) * int(dado[12:16]))		# Sensor 4
        d[5] = float(self.S_05_A) + (float(self.S_05_B) * int(dado[20:24]))		# Sensor 5
        d[6] = float(self.S_06_A) + (float(self.S_06_B) * int(dado[16:20]))		# Sensor 6
        return d 																	# retorna o vetor numpyarray
    except:
        return False

def serial_ports():
    '''Lista as possíveis portas seriais (reais ou virtuais) diponíveis no sistema operacional'''
    if sys.platform.startswith('win'):							# Caso o SO seja windows (apenas para debug)
        ports = ['COM' + str(i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'): 	# Linux
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):						# Caso o SO seja Mac OS (apenas para debug)
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')
    return ports  												# Retorna a lista com as portas seriais encontradas



###################################################################################################################
#################################   Comandos forno   ##############################################################

def teste_retorno(self):
    ''' Função que é chamada após alteração no estado da esteira ou das resistências.
    Esta função é chamada t segundos após o envio do comando para o microcontrolador,
    com o objetivo de rerificar se este recebeu corretamente o comando (quando isto ocorre
    o mc devolve o mesmo comando em uma string, que é verificada pela funçao de leitura serial,
    alterando o estado das variáveis de controle da esteira e das resistências 1 a 6).
    Para esta verificação, é comparado o estado da variável de controle com o estado dos sliders
    de controle, que são alterados quando recebem o sinal de volta do microcontrolador '''
    if not(int(self.ui.horizontalSlider.value()) == self.esteira):				# verifica se há diferença entre a variável e a esteira
        self.ui.lcdNumber_7.display(self.esteira)								# Altera o valor do LCD da GUI
        self.ui.horizontalSlider.setValue(self.esteira)							# Altera o valor do slider

    if not(int(self.ui.horizontalSlider_r01.value()) == self.resitencia01):		# verifica se há diferença entre a variável e a resistência 1
        self.ui.horizontalSlider_r01.setValue(self.resitencia01)				# Altera o valor do slider
        self.ui.progressBar_r01.setValue(self.resistencia01)					# Altera o valor da progressbar

    if not(int(self.ui.horizontalSlider_r02.value()) == self.resitencia02):		# Idem para resistências 2 a 6
        self.ui.horizontalSlider_r02.setValue(self.resitencia02)
        self.ui.progressBar_r02.setValue(self.resistencia02)

    if not(int(self.ui.horizontalSlider_r03.value()) == self.resitencia03):
        self.ui.horizontalSlider_r03.setValue(self.resitencia03)
        self.ui.progressBar_r03.setValue(self.resistencia03)

    if not(int(self.ui.horizontalSlider_r04.value()) == self.resitencia04):
        self.ui.horizontalSlider_r04.setValue(self.resitencia04)
        self.ui.progressBar_r04.setValue(self.resistencia04)

    if not(int(self.ui.horizontalSlider_r05.value()) == self.resitencia05):
        self.ui.horizontalSlider_r05.setValue(self.resitencia05)
        self.ui.progressBar_r05.setValue(self.resistencia05)

    if not(int(self.ui.horizontalSlider_r06.value()) == self.resitencia06):
        self.ui.horizontalSlider_r06.setValue(self.resitencia06)
        self.ui.progressBar_r06.setValue(self.resistencia06)

def atualiza_temp(self):
    ''' Envia o pedid de atualização da temperatura (o mc retornará os dados da temperatura dos 6 sensores) '''
    s.write('ST\n')

def resistencia01(self):
    ''' Função que é chamada quando alguma mudança no controle da GUI relativa a resistência 1 ocorre
    A função verifica o estado da resistência 1 e envia para o mc caso seja necessário '''
    if (not self.ui.radioButton.isChecked()):									# Os dados são enviados apenas se o 'hold' não estiver pressionado
        valor = int(self.ui.horizontalSlider_r01.value())						# Pega o valor do slider relativo a resistência 1
        if valor == 100:														# envia o dado adequado em função do valor 0, 1..99, 100
            envia_serial(liga_02)
        elif valor == 0:
            envia_serial(desliga_02)
        elif valor > 0 and valor < 100:
            envia_serial('SP2' + str(valor) + '\n')
        QtCore.QTimer.singleShot(3000, partial(teste_retorno,self))				# Chama a função teste_retorno em t segundos para verificar se o mc recebeu
                                                                                # o comando e retornou a string esperada.

def resistencia02(self):														# Idem para as resistências 2 a 6
    if (not self.ui.radioButton.isChecked()):
        valor = int(self.ui.horizontalSlider_r02.value())
        if valor == 100:
            envia_serial(liga_04)
        elif valor == 0:
            envia_serial(desliga_04)
        elif valor > 0 and valor < 100:
            envia_serial('SP3' + str(valor) + '\n')
        QtCore.QTimer.singleShot(3000, partial(teste_retorno,self))				# Chama a função teste_retorno em t segundos para verificar se o mc recebeu

def resistencia03(self):
    if (not self.ui.radioButton.isChecked()):
        valor = int(self.ui.horizontalSlider_r03.value())
        if valor == 100:
            envia_serial(liga_06)
        elif valor == 0:
            envia_serial(desliga_06)
        elif valor > 0 and valor < 100:
            envia_serial('SP4' + str(valor) + '\n')
        QtCore.QTimer.singleShot(3000, partial(teste_retorno,self))				# Chama a função teste_retorno em t segundos para verificar se o mc recebeu

def resistencia04(self):
    if (not self.ui.radioButton.isChecked()):
        valor = int(self.ui.horizontalSlider_r04.value())
        if valor == 100:
            envia_serial(liga_05)
        elif valor == 0:
            envia_serial(desliga_05)
        elif valor > 0 and valor < 100:
            envia_serial('SP5' + str(valor) + '\n')
        QtCore.QTimer.singleShot(3000, partial(teste_retorno,self))				# Chama a função teste_retorno em t segundos para verificar se o mc recebeu

def resistencia05(self):
    if (not self.ui.radioButton.isChecked()):
        valor = int(self.ui.horizontalSlider_r05.value())
        if valor == 100:
            envia_serial(liga_03)
        elif valor == 0:
            envia_serial(desliga_03)
        elif valor > 0 and valor < 100:
            envia_serial('SP6' + str(valor) + '\n')
        QtCore.QTimer.singleShot(3000, partial(teste_retorno,self))				# Chama a função teste_retorno em t segundos para verificar se o mc recebeu

def resistencia06(self):
    if (not self.ui.radioButton.isChecked()):
        valor = int(self.ui.horizontalSlider_r06.value())
        if valor == 100:
            envia_serial(liga_01)
        elif valor == 0:
            envia_serial(desliga_01)
        elif valor > 0 and valor < 100:
            envia_serial('SP7' + str(valor) + '\n')
        QtCore.QTimer.singleShot(3000, partial(teste_retorno,self))				# Chama a função teste_retorno em t segundos para verificar se o mc recebeu

def hold(self):
    ''' Função que é chamada quando o estado do checkbox 'hold' é alterado.
    Caso o hold seja deslicado. São chamadas as funções de todas as esteiras
    para enviar os dados caso haja diferença entre o estado da variável e do
    slider.'''
    if ( self.ui.radioButton.isChecked() == False ):							# Caso o 'hold' tenha sido desligado:
        resistencia01(self)														# Chama a função da resistência 1
        time.sleep(0.1)															# Espera um pequeno tempo por precaução de sobrecarregar a serial
        resistencia02(self)														# Idem para as resistências 2 .. 6
        time.sleep(0.1)
        resistencia03(self)
        time.sleep(0.1)
        resistencia04(self)
        time.sleep(0.1)
        resistencia05(self)
        time.sleep(0.1)
        resistencia06(self)

def esteira(self):
    ''' Função que é acionada ao alterar o valor do slider da esteira. Envia para o mc o comando adequado '''
    valor = self.ui.horizontalSlider.value()
    if valor > 0:																# SH'xy' para frente (valores maiores que zero)
        s.write('SH' + str(valor) + '\n')
    elif valor < 0:																# SA'xy' para tras (valores menores que zero)
        s.write('SA' + str(abs(valor)) + '\n')
    else:
        s.write('SD\n')															# Parar a esteira (0)
    QtCore.QTimer.singleShot(3000, partial(teste_retorno,self))					# Chama a função teste_retorno em t segundos para verificar se o mc recebeu

def para_esteira(self):
    ''' Função de parada total da esteira. Envia o comando para o mc e altera o valor do slider. '''
    self.ui.horizontalSlider.setValue(0)
    s.write('SD\n')
    QtCore.QTimer.singleShot(3000, partial(teste_retorno,self))					# Chama a função teste_retorno em t segundos para verificar se o mc recebeu

def emergencia(self):
    ''' Função de Emergência. Para a esteira e desliga todas as resistências '''
    s.write('SD\n')
    for i in range(2,8):
        s.write('S' + str(i) + '2\n')
        time.sleep(0.1)
    QtCore.QTimer.singleShot(5000, partial(teste_retorno,self))