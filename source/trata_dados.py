# -*- coding: latin-1 -*-
import time
import numpy as np
from PyQt4 import QtCore
from functools import partial
from modulo_global import *
import comunicacao_serial, automatico
import banco.bd_sensores as bd_sensores
import banco.bd_config as bd_config

def converte_numero(s):
    '''
    Retorna True caso o valor passado seja um int ou float na string
    '''
    try:
        return float(s)
    except ValueError:
        return False


def converte_dado(dado,self):
    '''
    Função que recebe o dado como string e particiona em um vetor com 7 pos.
    A primeira posição é o tempo atual e as outras 6 são os dados dos sensores

    Return:
        d[0] -> timestamp do instante em que o dado foi recebido
        d[1] -> float sensor_esteira
        d[2] -> float sensor_teto1
        d[3] -> float sensor_teto2
        d[4] -> float sensor_lateral1
        d[5] -> float sensor_lateral2
        d[6] -> float sensor_lateral3
    '''
    try:
        dado = dado.strip('S')
        d = np.zeros([7,1])
        # captura a instante em que a coleta foi feita
        d[0] = time.time()
        # sensores 1,..,6
        d[1] = float(self.S_01_A) + (float(self.S_01_B) * \
               int(dado[self.pos_sensor_esteira :self.pos_sensor_esteira + 4]))
        d[2] = float(self.S_02_A) + (float(self.S_02_B) * \
               int(dado[self.pos_sensor_teto1 :self.pos_sensor_teto1 + 4]))
        d[3] = float(self.S_03_A) + (float(self.S_03_B) * \
               int(dado[self.pos_sensor_teto2 :self.pos_sensor_teto2 + 4]))
        d[4] = float(self.S_04_A) + (float(self.S_04_B) * \
               int(dado[self.pos_sensor_lateral1 :self.pos_sensor_lateral1 + 4]))
        d[5] = float(self.S_05_A) + (float(self.S_05_B) * \
               int(dado[self.pos_sensor_lateral2 :self.pos_sensor_lateral2 + 4]))
        d[6] = float(self.S_06_A) + (float(self.S_06_B) * \
               int(dado[self.pos_sensor_lateral3 :self.pos_sensor_lateral3 + 4]))
        try:
            self.status.forno(self,d[1:])
            #self.status.alimento(self,d[1:])
            self.status.incrementaContador()
        except Exception as e:
            print e
        return d
    except:
        self.alerta_toolbar('Erro converte_dado')
        return False

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
            formato: S,aaa,bbb,ccc,ddd,eee,fff,ggg,h,i,j
            Onde os dados, a..f são o estado das resistencias e ggg é a
            velocidade da esteira.
            h é o delayAnalog,
            i é o _nLeituras (número de leituras analogicas para a média)
            j é o período total do pwm
          Ou 'SK' - Parada total r1,..r6 = 0 e esteira parada
    10 -> SU ou SL, confirmacao de recebimento de alteracao de valor do pwm ou
          da leitura analógica.
    '''
    try:
        #print "DEBUG: recebido:", dado
        if dado[0] == self.CHR_inicioDado:
            # tipo 1, pedido temperatura - 'S0001aaaabbbbccccddddeeeeffff'
            if len(dado) == 29 and dado[1:29].isdigit() \
            and dado[1:5] == self.STR_inicioTemperatura:
                d = converte_dado(dado,self)
                if d[0]:
                    return 1, d
            # tipo 2, ligar ou desligar alguma resistencia - S'x''y'
            elif len(dado) == 3 and dado[1].isdigit() and \
            (dado[2] == self.CHR_ligaForno or dado[2] == self.CHR_desligaForno):
                if ( dado[1] in self.pinResistencias):
                    return 2, dado[1:]
            # tipo 3, parada da esteira
            elif dado == self.CHR_inicioDado + self.CHR_esteiraParada:
                return 3, dado
            # tipo 4, esteira para frente 0 a 100 - SH'xxx'
            elif dado[1] == self.CHR_esteiraFrente \
            and dado[2:].isdigit() and len(dado) < 6:
                if len(dado) == 4 or dado[2:] == "100":
                    return 4, dado.strip(self.CHR_inicioDado + self.CHR_esteiraFrente)
            # tipo 5, esteira para tras 0 a 100 - SA'xxx'
            elif dado[1] == self.CHR_esteiraTras \
            and dado[2:].isdigit() and len(dado) < 6:
                if len(dado) == 4 or dado[2:] == "100":
                    return 5, dado.strip(self.CHR_inicioDado + self.CHR_esteiraTras)
            # tipo 8, pwd esteira - SP'x''y''z'
            elif dado[1] == self.CHR_setPotenciaPWM and len(dado) > 3 \
            and len(dado) < 6:
                if ( dado[2:].isdigit() and int(dado[3:]) < 101 ):
                    return 8, dado[2:]
            # tipo 9, retorno de informacao da esteira e resistencias
            elif dado[1] == ',':
                valores = dado.split(',')
                # rerifica se todos os dados chegaram corretamente:
                if len(dado) > 7:
                    return 9, valores
            elif dado[1] == self.STR_emergencia and len(dado) == 2:
                return 9, [0,0,0,0,0,0,0,0]
            elif dado[1] == self.CHR_tempoPWM or self.CHR_setADC:
                return 10, None
        # tipo 6: Erro - envio de string incorreta ao microcontrolador
        elif 'Erro -' in dado:
            return 6, dado
    except:
        self.alerta_toolbar('Erro verifica_dado-except')
        return False, False
    # Caso não seja nenhum dos tipos esperados: erro, tipo 7
    self.alerta_toolbar('Erro verifica_dado-7')
    return 7, False

def resultado_dado(self, tipo, d):
    '''
    Função que recebe como entrada o tipo (tipo) de dado recebido e o dado (d)
    pré-processado.
    Com estas informações, as alterações da GUI e nas variáveis de controle
    são feitas para mosrtar o recebimento dos dados.
    '''
    try:
        print tipo
        # tipo 1: retono de dados de temperatura.
        if tipo == 1:
            # Altera os valores dos displays de temperatura.
            #temperatura = [None, d[4], d[], d[], d[], d[], d[]]
            self.ui.sensor_esteira.setText("{0:0.1f}".format(float(d[1])))
            self.ui.sensor_teto1.setText("{0:0.1f}".format(float(d[2])))
            self.ui.sensor_teto2.setText("{0:0.1f}".format(float(d[3])))
            self.ui.sensor_lateral1.setText("{0:0.1f}".format(float(d[4])))
            self.ui.sensor_lateral2.setText("{0:0.1f}".format(float(d[5])))
            self.ui.sensor_lateral3.setText("{0:0.1f}".format(float(d[6])))
            # Coloca os dados da temperatura em ums string
            data = str(["%i" % x for x in d])
            # Adiciona um caracter de fim de linha a string
            data = data + '\n'
            self.ui.textEdit_temperatura.insertPlainText(data)
            atuadores = str(self.valor_resistencia01) + "," + str(self.valor_resistencia02) + "," + \
            str(self.valor_resistencia03) + "," + str(self.valor_resistencia04) + "," + \
            str(self.valor_resistencia05) + "," + str(self.valor_resistencia06) + "," + \
            str(self.valor_esteira)
            calibracao = str(bd_config.retorna_dados_config_calibracao())
            # Adicionando os dados ao bd:
            # 'Sem nome': padrão para quando ainda não foi dado nome ao experimento
            if str(self.ui.label_nomeExperimento.text()) == 'Sem Nome':
                bd_sensores.adiciona_dado(float(d[0]),float(d[1]),float(d[2]),
                              float(d[3]),float(d[4]),float(d[5]),float(d[6]),
                              calibracao=calibracao,atuadores=atuadores)
            else:
                bd_sensores.adiciona_dado(float(d[0]),float(d[1]),
                              float(d[2]),float(d[3]),float(d[4]),float(d[5]),
                              float(d[6]),
                              experimento=str(self.ui.label_nomeExperimento.text()),
                              calibracao=calibracao,atuadores=atuadores)
        # Tipo 2 ou 8 - Liga ou desliga alguma resistência (total o pwm).
        elif tipo == 2 or tipo == 8:
            # tipo 2 liga ou desliga completamente uma resistência
            if tipo == 2:
                if d[1] == self.CHR_ligaForno:
                    valor_resistencia = 100
                elif d[1] == self.CHR_desligaForno:
                    valor_resistencia = 0
                else:
                    self.alerta_toolbar('Erro resultado_dado-tipo2')
                    return None
            # tipo 8 - Potência parcial de uma resistência
            elif tipo == 8:
                valor_resistencia = int(d[1:])
            else:
                self.alerta_toolbar('Erro resultado_dado-tipo8')
                return None
            # d[0] - Valor do numero das resistencia
            if d[0] == self.pinR1:
                self.valor_resistencia01 = valor_resistencia
                self.ui.progressBar_r01.setValue(valor_resistencia)
            elif d[0] == self.pinR2:
                self.valor_resistencia02 = valor_resistencia
                self.ui.progressBar_r02.setValue(valor_resistencia)
            elif d[0] == self.pinR3:
                self.valor_resistencia03 = valor_resistencia
                self.ui.progressBar_r03.setValue(valor_resistencia)
            elif d[0] == self.pinR4:
                self.valor_resistencia04 = valor_resistencia
                self.ui.progressBar_r04.setValue(valor_resistencia)
            elif d[0] == self.pinR5:
                self.valor_resistencia05 = valor_resistencia
                self.ui.progressBar_r05.setValue(valor_resistencia)
            elif d[0] == self.pinR6:
                self.valor_resistencia06 = valor_resistencia
                self.ui.progressBar_r06.setValue(valor_resistencia)
        # Tipo 3 - Para completamente a esteira
        elif tipo == 3:
            self.valor_esteira = 0
        # tipo 4 - Velocidade da esteira para frente (1 a 99)
        elif tipo == 4:
            self.valor_esteira = int(d)
        # Tipo 5 - Velocidade da esteira para tras (1 a 99)
        elif tipo == 5:
            self.valor_esteira = -1*int(d)
        elif tipo == 9:
            # Atualiza o valor das variaveis globais
            self.valor_resistencia01 = int(d[1])
            self.valor_resistencia02 = int(d[2])
            self.valor_resistencia03 = int(d[3])
            self.valor_resistencia04 = int(d[4])
            self.valor_resistencia05 = int(d[5])
            self.valor_resistencia06 = int(d[6])
            self.valor_esteira = int(d[7])
            if len(d) > 8:
                delayAnalog = int(d[8])
                nLeituras = int(d[9])
                self.tempo_pwm = int(d[10])
                bd_config.salva_config_pwm(self.tempo_pwm)
                bd_config.salva_config_ad(nLeituras,delayAnalog)
                automatico.atualiza_label_microcontrolador(self)
            QtCore.QTimer.singleShot(10, partial(comunicacao_serial.teste_retorno,self))
        elif tipo == 10:
            pass
        else:
            self.alerta_toolbar('Erro resultado_dado-else')
    except:
        self.alerta_toolbar('except resultado_dado')
