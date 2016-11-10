# -*- coding: latin-1 -*-
import time
import numpy as np
from modulo_global import *
import comunicacao_serial, bd_sensores, bd_config

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
        atuadores = str(self.valor_resistencia01) + "," + str(self.valor_resistencia02) + "," + \
        str(self.valor_resistencia03) + "," + str(self.valor_resistencia04) + "," + \
        str(self.valor_resistencia05) + "," + str(self.valor_resistencia06) + "," + \
        str(self.valor_esteira)
        calibracao = str(bd_config.retorna_dados_config_calibracao())
        print atuadores, calibracao
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
    # Tipo 2 - Liga ou desliga alguma resistência.
    elif tipo == 2:
        # d[0] - Valores de 2 a 7 = as 6 resistências
        if d[0] == '2':
            # d[1] : 1 para ligar e 0 para desligar
            if d[1] == '1':
                # Altera o valor da variável de controle da resistência
                self.valor_resistencia01 = 100
                # Altera a barra da GUI para a respectiva resistência
                self.ui.progressBar_r01.setValue(100)
            else:
                self.valor_resistencia01 = 0
                self.ui.progressBar_r01.setValue(0)
        # Idem para as outras 5 resistências
        elif d[0] == '3':									# Resustência 2
            if d[1] == '1':
                self.valor_resistencia02 = 100
                self.ui.progressBar_r02.setValue(100)
            else:
                self.valor_resistencia02 = 0
                self.ui.progressBar_r02.setValue(0)
        elif d[0] == '4':									# Resustência 3
            if d[1] == '1':
                self.valor_resistencia03 = 100
                self.ui.progressBar_r03.setValue(100)
            else:
                self.valor_resistencia03 = 0
                self.ui.progressBar_r03.setValue(0)
        elif d[0] == '5':									# Resustência 4
            if d[1] == '1':
                self.valor_resistencia04 = 100
                self.ui.progressBar_r04.setValue(100)
            else:
                self.valor_resistencia04 = 0
                self.ui.progressBar_r04.setValue(0)
        elif d[0] == '6':									# Resustência 5
            if d[1] == '1':
                self.valor_resistencia05 = 100
                self.ui.progressBar_r05.setValue(100)
            else:
                self.valor_resistencia05 = 0
                self.ui.progressBar_r05.setValue(0)
        elif d[0] == '7':									# Resustência 6
            if d[1] == '1':
                self.valor_resistencia06 = 100
                self.ui.progressBar_r06.setValue(100)
            else:
                self.valor_resistencia06 = 0
                self.ui.progressBar_r06.setValue(0)

    # tipo 8 - Potência parcial de uma resistência
    elif tipo == 8:
        # d[0] - Valores de 2 a 7 - respectivo a cada resistência
        if d[0] == '2':
            # Altera o valor da variável de controle da resistência
            self.valor_resistencia01 = int(d[1:])
            # Altera a barra da GUI para a respectiva resistência
            self.ui.progressBar_r01.setValue(int(d[1:]))
        # Idem para as outas 5 resistências
        elif d[0] == '3':
            self.valor_resistencia02 = int(d[1:])
            self.ui.progressBar_r02.setValue(int(d[1:]))
        elif d[0] == '4':
            self.valor_resistencia03 = int(d[1:])
            self.ui.progressBar_r03.setValue(int(d[1:]))
        elif d[0] == '5':
            self.valor_resistencia04 = int(d[1:])
            self.ui.progressBar_r04.setValue(int(d[1:]))
        elif d[0] == '6':
            self.valor_resistencia05 = int(d[1:])
            self.ui.progressBar_r05.setValue(int(d[1:]))
        elif d[0] == '7':
            self.valor_resistencia06 = int(d[1:])
            self.ui.progressBar_r06.setValue(int(d[1:]))
    # Tipo 3 - Para completamente a esteira
    elif tipo == 3:
        self.valor_esteira = 0
    # tipo 4 - Velocidade da esteira para frente (1 a 99)
    elif tipo == 4:
        print "alterando esteira (4)", d
        self.valor_esteira = int(d)
        print "valor_esteira", self.valor_esteira
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
        self.valor_esteira = int(x=d[7])
        # Atualiza os slides e controles da GUI
        QtCore.QTimer.singleShot(10, partial(comunicacao_serial.teste_retorno,self))
    else:
        print "erro no recebimento !!!!!!!"
