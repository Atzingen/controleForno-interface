# -*- coding: latin-1 -*-
import ast
from functools import partial
import numpy as np
import time
from PyQt4 import QtGui
import banco.bd_perfil as bd_perfil
import banco.bd_config as bd_config
import banco.bd_sensores as bd_sensores
import graficos, trata_dados
import comunicacao_serial
import controle_pid
import simulacao
try:
    from simulacao.alimento_fortran import *
    print "Usando funcao evolui_tempo Fortran"
except:
    import simulacao.alimento as alimento
    print "Usando funcao evolui_tempo Python"

def novo_perfil_alimento(self):
    print 'novo_perfil_alimento'
    perfil = {}
    flags = QtGui.QMessageBox.Yes
    flags |= QtGui.QMessageBox.No
    mensagem_titulo = 'Novo Alimento - Inserir'
    dialogos = [ 'nome do perfil:', 'Raio do Alimento:', 'Altura Alimento',
                'k Conducao','rho - densidade','Cp - Calor especifico','h_convec',
                'epsilon', 'Temperatura Crosta:', 'Temperatura Centro']
    keys = ['nome','R','H','k','rho','Cp','h_convec','epsilon','Temp-crosta','Temp-centro']
    for i, texto in enumerate(dialogos):
        dado, result = QtGui.QInputDialog.getText(self,mensagem_titulo,texto)
        perfil[keys[i]] = str(dado)
    bd_config.salva_config_alimento(self.caminho_inicial + '/bancoDados',perfil)

def apagar_perfil(self):
    atual = bd_config.retorna_escolha_alimento(self.caminho_inicial + '/bancoDados')
    bd_config.deleta_config_alimento(self.caminho_inicial + '/bancoDados',atual['nome'])
    atualiza_comboBox(self)

def lista_perfil_alimento_update(self):
    escolha = str(self.ui.comboBox_perfilAlimento.currentText())
    #print 'lista antes', escolha
    v = {'qual': escolha, 'nome': 'escolha'}
    bd_config.deleta_config_alimento(self.caminho_inicial + '/bancoDados', 'escolha')
    #print 'depois delatado:', bd_config.retorna_lista_config_alimento(self.caminho_inicial + '/bancoDados')
    bd_config.salva_config_alimento(self.caminho_inicial + '/bancoDados', v)
    #print bd_config.retorna_escolha_alimento(self.caminho_inicial + '/bancoDados')
    atualiza_comboBox(self)
    atuacao_label_alimento(self)

def atualiza_comboBox(self):
    respostas = bd_config.retorna_lista_config_alimento(self.caminho_inicial + '/bancoDados')
    self.ui.comboBox_perfilAlimento.blockSignals(True)
    self.ui.comboBox_perfilAlimento.clear()
    for resposta in respostas:
        if resposta['nome'] != 'escolha':
            self.ui.comboBox_perfilAlimento.addItem(resposta['nome'])
        else:
            escolhido = resposta['qual']
    i = self.ui.comboBox_perfilAlimento.findText(escolhido)
    self.ui.comboBox_perfilAlimento.setCurrentIndex(i)
    self.ui.comboBox_perfilAlimento.blockSignals(False)
    atuacao_label_alimento(self)

def atuacao_label_alimento(self):
    escolha = bd_config.retorna_escolha_alimento(self.caminho_inicial + '/bancoDados').items()
    texto = ""
    for i in range(5):
        texto += str(escolha[i][0]) + ': ' + str(escolha[i][1]) + '\n'
    self.ui.label_alimento_A.setText(texto)
    texto = ""
    for i in range(5,10):
        texto += str(escolha[i][0]) + ': ' + str(escolha[i][1]) + '\n'
    self.ui.label_alimento_B.setText(texto)

def iniciar_perfil_alimento(self):
    if self.ui.pushButton_simAlimento.text() == 'Iniciar':
        self.ui.pushButton_simAlimento.setText('Parar')
        self.status.T_alimento = self.status.T0_alimento()
        perfil = bd_config.retorna_escolha_alimento(self.caminho_inicial + '/bancoDados')
        atuacao_automatico_alimento(self, perfil)
    else:
        self.ui.pushButton_simAlimento.setText('Iniciar')
        print 'parar perfil_alimento'

def atuacao_automatico_alimento(self, perfil):
    inicio = time.time()
    if self.ui.pushButton_simAlimento.text() == 'Parar':
        T_bd = bd_sensores.retorna_dados(self.caminho_banco,1)
        if int(T_bd.shape[0]) > 0:
            T_esteira_bd = T_bd[-1][3]
            T_ar_bd = ( T_bd[-1][6] + T_bd[-1][7] + T_bd[-1][8] )/3
            T_paredes_bd = ( T_bd[-1][4] + T_bd[-1][5] )/2
            print T_esteira_bd, T_ar_bd, T_paredes_bd
            self.status.T_alimento = alimento.evolui_tempo(self.status.dt_alimento,
                self.status.T_alimento, R = float(perfil['R']), H = float(perfil['H']),
                h_convec=float(perfil['h_convec']), epsilon=float(perfil['epsilon']),
                k=float(perfil['k']), rho=float(perfil['rho']), Cp=float(perfil['Cp']),
                T_esteira = T_esteira_bd, T_paredes = T_paredes_bd,
                T_ar = T_ar_bd, T_ambiente = self.status.T_ambiente)
            simulacao.alimento.display_alimento(self, self.status.T_alimento)
            dt = time.time() - inicio
            print dt
            self.timer_alimento.singleShot( (self.status.dt_alimento - dt)*1000,
                partial(atuacao_automatico_alimento,self,perfil))
    else:
        print 'fim timer'

def set_colobarAlimentoLabel(self):
    minimo = self.ui.spinBox_alimento_min.value()
    maximo = self.ui.spinBox_alimento_max.value()
    self.ui.label_alim_13.setText(str( minimo + (maximo-minimo)/3 ))
    self.ui.label_alim_23.setText(str( minimo + 2*(maximo-minimo)/3 ))

def set_colobarFornoLabel(self):
    minimo = self.ui.spinBox_forno_min.value()
    maximo = self.ui.spinBox_forno_max.value()
    self.ui.label_coloerbar13.setText(str( minimo + (maximo-minimo)/3 ))
    self.ui.label_coloerbar23.setText(str( minimo + 2*(maximo-minimo)/3 ))
