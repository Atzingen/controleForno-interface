# -*- coding: latin-1 -*-
import ast
from functools import partial
import numpy as np
from PyQt4 import QtGui
import banco.bd_perfil as bd_perfil
import banco.bd_config as bd_config
import graficos, trata_dados

def automatico_perfil_update(self,tipo,estados):
    '''
    Função que é chamada ao início de um novo controle de perfil
    automático. Esta função se chamará de forma recursiva até que
    o controle termine.

    tipo -> { resistencia , forno}
    estados -> || ponto, passo |    (R1)
                | ...  , ...   |    (R2)
                ...
                | ponto, passo ||   (R6)

            ponto: mostra qual o ultimo ponto* que o perfil passou,
            sendo o instante atual um tempo entre ponto e ponto + 1

            passo: quantos elementos discretos o tempo atual está entre o
            ponto e ponto + 1. A separação em elementos discretos é feita
            separando o tempo entre ponto e ponto + 1 entre pwm segundos,
            que é o período completo.

    '''
    if tipo == 'resistencia':
        nome = unicode(self.ui.comboBox_perfilResistencia.currentText())
    elif tipo == 'potencia':
        nome = unicode(self.ui.comboBox_perfilPotencia.currentText())
    else:
        print "DEBUG: erro tipo "
        self.alerta_toolbar("Erro - tipo perfil automatico")
        return None
    perfil = bd_perfil.leitura_perfil(nome,tipo)
    n_terminos = 0
    # r 0..5 para passar pela info de todas as resistencias
    for r in range(6):
        # perfir[i+2] -> +2 pois as duas primeiras linhas recebidas
        # do bd são a chave primária e o nome.
        perfil_r = ast.literal_eval(perfil[r+2])
        # pega o número de pontos para a resistencia r:
        numero_pontos = len(perfil_r)
        # pega em que ponto específico o controle do perfil está:
        # ponto e passo antes de agir
        ponto_atual = int(estados[r,0])
        passo = estados[r,1]
        if ( numero_pontos  > ponto_atual + 1):
            #informacao dos pontos Pn e Pn+1
            t_inicial = perfil_r[ponto_atual][0]
            t_final = perfil_r[ponto_atual+1][0]
            r_inicial = perfil_r[ponto_atual][1]
            r_final = perfil_r[ponto_atual+1][1]
            delta_r = r_final - r_inicial
            delta_t = (t_final - t_inicial)*60.0 # convertendo para segundos
            numero_passos = delta_t//self.tempo_pwm
            if numero_passos > 0:
                pwm = r_inicial + float(passo*delta_r)/float(numero_passos)
                t_atual = t_inicial + float(passo*delta_t)/float(numero_passos)
            else:
                pwm = r_inicial
                t_atual = t_inicial
            if (r+1)%6 == 0:
                print pwm, t_atual
            # if - condição de mudança abrusca (slope 90 graus)
            if t_final <= t_inicial:
                # zera o passo
                estados[r,1] = 0
                # incrementa 1 no ponto atual
                estados[r,0] += 1
            else: # condição normal de incremento (passo)
                # caso ainda esteja entre um ponto e outro (não chegou o
                # final do passo):
                if (numero_passos > passo + 1):
                    # incrementa o passo e não altera o ponto
                    estados[r,1] += 1
                else: # fim de passo entre um ponto e outro
                    # zera o passo
                    estados[r,1] = 0
                    # incrementa o ponto
                    estados[r,0] += 1
        else:
            n_terminos += 1
            pwm = 0
    if n_terminos < 6:
        dt = t_final - t_inicial
        graficos.plota_perfil(self,tipo,(t_inicial + passo*dt/numero_passos,
                                t_inicial + passo*dt/numero_passos,
                                0  ,100 ))
        if self.ui.pushButton_perfilResistencia.text() == "Cancelar" or \
        self.ui.pushButton_perfilPotencia.text() == "Cancelar":
            self.timer_serial.singleShot(self.tempo_pwm*100,
                                         partial(automatico_perfil_update,
                                                self,tipo,estados))
    else:
        if tipo == 'resistencia':
            self.ui.pushButton_perfilResistencia.setText("Iniciar")
        elif tipo == 'potencia':
            self.ui.pushButton_perfilPotencia.setText("Iniciar")
        print "DEBUG: fim do controle automatico"
        self.alerta_toolbar("fim do controle automatico")

def inicia_perfil(self, tipo):
    '''
    Função acionada pelo sinal do botão Inicia/Fim do perfil_resistencia
    ou perfil_potencia.
    Altera o texto do botão inicia/fim e chama a função
    automatico_perfil_update
    '''
    if tipo == 'resistencia':
        if self.ui.pushButton_perfilResistencia.text() == "Iniciar":
            self.ui.pushButton_perfilResistencia.setText("Cancelar")
            # variavel estado: vetor 6,2 com as informações de indice e
            # passo de cada resistencia
            estados = np.zeros([6,2])
            automatico_perfil_update(self,'resistencia',estados)
        elif self.ui.pushButton_perfilResistencia.text() == "Cancelar":
            reply = QtGui.QMessageBox.question(self,'Mensagem',
                                "Tem certeza que terminar ?",
    							QtGui.QMessageBox.Yes |QtGui.QMessageBox.No,
                                QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                self.ui.pushButton_perfilResistencia.setText("Iniciar")
                self.alerta_toolbar("Fim perfil Automatico")
            else:
                self.alerta_toolbar("Perfil Automatico continua")
                pass
        else:
            self.alerta_toolbar("Erro IniciaPerfil")
            return None
    elif tipo == 'potencia':
        if self.ui.pushButton_perfilPotencia.text() == "Iniciar":
            self.ui.pushButton_perfilPotencia.setText("Cancelar")
            estados = np.zeros([6,2])
            automatico_perfil_update(self,'potencia',estados)
        elif self.ui.pushButton_perfilPotencia.text() == "Cancelar":
            reply = QtGui.QMessageBox.question(self,'Mensagem',
                                "Tem certeza que terminar ?",
    							QtGui.QMessageBox.Yes |QtGui.QMessageBox.No,
                                QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                self.ui.pushButton_perfilPotencia.setText("Iniciar")
                self.alerta_toolbar("Fim perfil Automatico")
            else:
                self.alerta_toolbar("Perfil Automatico continua")
                pass
        else:
            self.alerta_toolbar("Erro IniciaPerfil")
            return None
    else:
        self.alerta_toolbar("Erro IniciaPerfil")
        return None

def novo_perfil(self,tipo):
    '''
    Abre um Dialog box para o usuário preencher as informações sobre
    um novo perfil, com os dados tempo e velor para todas as resistencias
    ou tempo e valor comum (caso de todas as resistencias iguais).
    '''
    flags = QtGui.QMessageBox.Yes
    flags |= QtGui.QMessageBox.No
    question = "As potencias das resistencias r1...r6 serao iguais ?"
    response = QtGui.QMessageBox.question(self, "Question",question,flags)
    sim = (response == QtGui.QMessageBox.Yes)
    n, i, sair = 1, 1, False
    R =  [ [], [], [], [], [], [] ]
    mensagem = "Digite o tempo e potencia separados por ',': t,p"
    if sim:
        while  not sair:
            dado, result = QtGui.QInputDialog.getText(self,
                    "Toras Resistencias: Inserir ponto " + str(n),mensagem)
            if result:
                try:
                    v1_str, v2_str = dado.split(',')
                    v1 = trata_dados.converte_numero(v1_str)
                    v2 = trata_dados.converte_numero(v2_str)
                    for i in range(6):
                        R[i].append([v1,v2])
                except:
                    QtGui.QMessageBox.warning(self, "Erro",
                                "O valor digitado nao esta no formato (numero,numero)",
                                QtGui.QMessageBox.Cancel, QtGui.QMessageBox.NoButton,
                                QtGui.QMessageBox.NoButton)
                    sair = True
                    break
            else:
                sair = True
                break
            n += 1
    else:
        for i in range(6):
            n = 1
            sair = False
            while  not sair:
                dado, result = QtGui.QInputDialog.getText(self,
                        "Inserir ponto " + str(n),
                        "R" + str(i+1) + " " + mensagem)
                if result:
                    try:
                        v1_str, v2_str = dado.split(',')
                        v1 = trata_dados.converte_numero(v1_str)
                        v2 = trata_dados.converte_numero(v2_str)
                        R[i].append([v1,v2])
                    except:
                        QtGui.QMessageBox.warning(self, "Erro",
                                    "O valor digitado nao esta no formato (numero,numero)",
                                    QtGui.QMessageBox.Cancel, QtGui.QMessageBox.NoButton,
                                    QtGui.QMessageBox.NoButton)
                        sair = True
                        break
                else:
                    sair = True
                n += 1
    text = "Verifique o perfil digitado: \n"
    for i in range(6):
        text += "R" + str(i) + ": " + str(R[i]) +  "\n"
    nome, result = QtGui.QInputDialog.getText(self,"Digitar nome do perfil",text)
    if result:
        bd_perfil.insere_perfil(tipo,str(nome),str(R[0]),str(R[1]),str(R[2]),
                                str(R[3]),str(R[4]),str(R[5]),"1")

def lista_perfil_resistencia(self):
    self.ui.comboBox_perfilResistencia.blockSignals(True)
    nomes = bd_perfil.nomes_perfil_resistencia()
    numero_escolha = self.ui.comboBox_perfilResistencia.currentIndex()
    escolha = bd_config.retorna_dados_config_resistencia()
    self.ui.comboBox_perfilResistencia.clear()
    i = 0
    for nome in nomes:
        self.ui.comboBox_perfilResistencia.addItem(str(nome[0]))
        if escolha == nome[0] and numero_escolha == -1:
            numero_escolha = i
        i = i + 1
    self.ui.comboBox_perfilResistencia.setCurrentIndex(numero_escolha)
    self.ui.comboBox_perfilResistencia.blockSignals(False)
    escolha = unicode(self.ui.comboBox_perfilResistencia.currentText())
    bd_config.salva_config_perfil_resistencia(escolha)
    graficos.plota_perfil(self,'resistencia',None)


def lista_perfil_potencia(self):
    self.ui.comboBox_perfilPotencia.blockSignals(True)
    nomes = bd_perfil.nomes_perfil_potencia()
    numero_escolha = self.ui.comboBox_perfilPotencia.currentIndex()
    escolha = bd_config.retorna_dados_config_potencia()
    self.ui.comboBox_perfilPotencia.clear()
    i = 0
    for nome in nomes:
        self.ui.comboBox_perfilPotencia.addItem(str(nome[0]))
        if escolha == nome[0] and numero_escolha == -1:
            numero_escolha = i
        i = i + 1
    self.ui.comboBox_perfilPotencia.setCurrentIndex(numero_escolha)
    self.ui.comboBox_perfilPotencia.blockSignals(False)
    escolha = unicode(self.ui.comboBox_perfilPotencia.currentText())
    bd_config.salva_config_perfil_potencia(escolha)
    graficos.plota_perfil(self,'potencia',None)
