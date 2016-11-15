# -*- coding: latin-1 -*-
from PyQt4 import QtGui
import banco.bd_calibracao as bd_calibracao
import banco.bd_config as bd_config
import automatico


def salva_calibracao(self):
    '''
    Função que salva o valor da calibração linear para a conversao do valor
    de tensao obtido pelo termopar para temperatura.
    '''
    # Retira os dados da ui.
    s_01_A = float(self.ui.lineEdit_S01A.text())
    s_02_A = float(self.ui.lineEdit_S02A.text())
    s_03_A = float(self.ui.lineEdit_S03A.text())
    s_04_A = float(self.ui.lineEdit_S04A.text())
    s_05_A = float(self.ui.lineEdit_S05A.text())
    s_06_A = float(self.ui.lineEdit_S06A.text())
    s_01_B = float(self.ui.lineEdit_S01B.text())
    s_02_B = float(self.ui.lineEdit_S02B.text())
    s_03_B = float(self.ui.lineEdit_S03B.text())
    s_04_B = float(self.ui.lineEdit_S04B.text())
    s_05_B = float(self.ui.lineEdit_S05B.text())
    s_06_B = float(self.ui.lineEdit_S06B.text())
    text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog',
        'Digite o nome da calibracao')
    self.alerta_toolbar("Salvando cal: " + text)
    if ok:
        nomes = bd_calibracao.nomes_calibracao()
        for nome in nomes:
            if nome[0] == text:
                igual = True
                break
            else:
                igual = False
        if igual:
            self.alerta_toolbar("nome ja existe")
            print "nome já existe"
        else:
            bd_calibracao.insere_calibracao(str(text), s_01_A, s_02_A, s_03_A, s_04_A, s_05_A, s_06_A, s_01_B, s_02_B, s_03_B, s_04_B, s_05_B, s_06_B)

def deleta_calibracao(self, tipo):
    print 'inicio', tipo
    try:
        if tipo == 'Fit':
            numero_escolha = self.ui.comboBox_fitLinear.currentIndex()
            escolha = self.ui.comboBox_fitLinear.itemText(numero_escolha)
        elif tipo == 'potencia':
            numero_escolha = self.ui.comboBox_perfilPotencia.currentIndex()
            escolha = self.ui.comboBox_perfilPotencia.itemText(numero_escolha)
        elif tipo == 'temperatura':
            numero_escolha = self.ui.comboBox_perfilTemperatura.currentIndex()
            escolha = self.ui.comboBox_perfilTemperatura.itemText(numero_escolha)
        else:
            self.alerta_toolbar("Tipo" + str(tipo) + " nao existe")
            return None
        reply = QtGui.QMessageBox.question(self,'Mensagem',"Tem certeza que deletar a calibracao" + escolha + " ?",
    										QtGui.QMessageBox.Yes |QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            print escolha, tipo
            bd_calibracao.deleta_calibracao_bd(str(escolha),tipo)
            if (str(escolha)==bd_config.retorna_dados_config_calibracao()):
                primeiro_nome = self.ui.comboBox_fitLinear.itemText(0)
                bd_config.salva_config_calibracao(primeiro_nome)
            lista_calibracoes(self)
            automatico.lista_perfil_potencia(self)
            automatico.lista_perfil_resistencia(self)
    except Exception as e:
        print e
        pass

def atualiza_lineEdit_calibracao(self):
    self.ui.lineEdit_S01A.setText(str(self.S_01_A))
    self.ui.lineEdit_S02A.setText(str(self.S_02_A))
    self.ui.lineEdit_S03A.setText(str(self.S_03_A))
    self.ui.lineEdit_S04A.setText(str(self.S_04_A))
    self.ui.lineEdit_S05A.setText(str(self.S_05_A))
    self.ui.lineEdit_S06A.setText(str(self.S_06_A))
    self.ui.lineEdit_S01B.setText(str(self.S_01_B))
    self.ui.lineEdit_S02B.setText(str(self.S_02_B))
    self.ui.lineEdit_S03B.setText(str(self.S_03_B))
    self.ui.lineEdit_S04B.setText(str(self.S_04_B))
    self.ui.lineEdit_S05B.setText(str(self.S_05_B))
    self.ui.lineEdit_S06B.setText(str(self.S_06_B))


def lista_calibracoes(self):
    self.ui.comboBox_portaSerial.blockSignals(True)
    nomes = bd_calibracao.nomes_calibracao()
    numero_escolha = self.ui.comboBox_fitLinear.currentIndex()
    escolha = bd_config.retorna_dados_config_calibracao()
    self.ui.comboBox_fitLinear.clear()
    i = 0
    for nome in nomes:
        self.ui.comboBox_fitLinear.addItem(str(nome[0]))
        if escolha == nome[0] and numero_escolha == -1:
            numero_escolha = i
        i = i + 1
    self.ui.comboBox_fitLinear.setCurrentIndex(numero_escolha)
    self.ui.comboBox_fitLinear.blockSignals(False)
    escolha = unicode(self.ui.comboBox_fitLinear.currentText())
    valores = bd_calibracao.leitura_calibracao(escolha)
    bd_config.salva_config_calibracao(escolha)
    atualiza_valores_calibracoes(self,valores)
    atualiza_lineEdit_calibracao(self)

def atualiza_valores_calibracoes(self, valores):
    '''Pega os valores dos campos da calibra��o linear para fazer a convers�o entre tens�o e temperatura'''
    self.S_01_A = valores[2]
    self.S_02_A = valores[3]
    self.S_03_A = valores[4]
    self.S_04_A = valores[5]
    self.S_05_A = valores[6]
    self.S_06_A = valores[7]
    self.S_01_B = valores[8]
    self.S_02_B = valores[9]
    self.S_03_B = valores[10]
    self.S_04_B = valores[11]
    self.S_05_B = valores[12]
    self.S_06_B = valores[13]
