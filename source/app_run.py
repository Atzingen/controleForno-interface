# -*- coding: latin-1 -*-
from __future__ import division
# Bibliotecas
import numpy as np
import sys, os, serial, glob, thread, time, datetime, sqlite3, PIL, scipy, csv, smtplib, shutil, platform
from functools import partial
from threading import Thread
from PyQt4 import QtGui, QtCore
from PIL import Image, ImageQt

try:
    import picamera
except:
    pass
# Importanto objetos e fun��es locais
from forno_gui import Ui_MainWindow
from banco_dados import *
from comunicacao_serial import *
from exporta_experimentos import *
from matplotlibwidgetFile import *
from camera_rp import *
from modulo_global import *


class Main(QtGui.QMainWindow):
    '''
	Classe principal da tela.
	a ui usa as propriedades da classe Ui_MainWindow,
	feita com o Qt Designer, e mantida separadamente no
	arquivo gui_forno_gui, compilada com o pyuic4
	'''
    def __init__(self):
        ''' Construtor do objeto da tela principal. Executa quando o programa inicia'''
        # Iniciando a ui
        QtGui.QMainWindow.__init__(self)  # Interface Gr�fica
        self.ui = Ui_MainWindow()  # Qtdesigner
        self.ui.setupUi(self)
        ###     Vari�veis da calibração        ################################
        nomes_calibracao = retorna_dados_config()
        cal = leitura_calibracao(str(nomes_calibracao))
        self.atualiza_valores_calibracoes(cal)
        self.atualiza_lineEdit_calibracao()

        if (platform.system() == 'Darwin'):
            self.ui.horizontalSlider_r01.setStyle(QtGui.QStyleFactory.create("macintosh"))
            self.ui.horizontalSlider_r02.setStyle(QtGui.QStyleFactory.create("macintosh"))
            self.ui.horizontalSlider_r03.setStyle(QtGui.QStyleFactory.create("macintosh"))
            self.ui.horizontalSlider_r04.setStyle(QtGui.QStyleFactory.create("macintosh"))
            self.ui.horizontalSlider_r05.setStyle(QtGui.QStyleFactory.create("macintosh"))
            self.ui.horizontalSlider_r06.setStyle(QtGui.QStyleFactory.create("macintosh"))
            self.ui.horizontalSlider_esteira.setStyle(QtGui.QStyleFactory.create("macintosh"))
            self.ui.horizontalSlider_graficoPeriodo.setStyle(QtGui.QStyleFactory.create("macintosh"))
        else:
            self.ui.horizontalSlider_r01.setStyle(QtGui.QStyleFactory.create("windows"))
            self.ui.horizontalSlider_r02.setStyle(QtGui.QStyleFactory.create("windows"))
            self.ui.horizontalSlider_r03.setStyle(QtGui.QStyleFactory.create("windows"))
            self.ui.horizontalSlider_r04.setStyle(QtGui.QStyleFactory.create("windows"))
            self.ui.horizontalSlider_r05.setStyle(QtGui.QStyleFactory.create("windows"))
            self.ui.horizontalSlider_r06.setStyle(QtGui.QStyleFactory.create("windows"))
            self.ui.horizontalSlider_esteira.setStyle(QtGui.QStyleFactory.create("windows"))
            self.ui.horizontalSlider_graficoPeriodo.setStyle(QtGui.QStyleFactory.create("windows"))

        ######## Caminho para os experimentos salvos #########################
        source_parent, _ = local_parent()
        self.ui.label_caminho.setText(source_parent + "dadosExperimento")

        ####### Banco de dados ################################################
        tempo_coleta = time.time()
        cria_tabela()
        #####  QTimers ########################################################
        self.timer_foto = QtCore.QTimer()
        self.timer_grafico = QtCore.QTimer()
        self.timer_serial = QtCore.QTimer()
        self.timer_ST = QtCore.QTimer()
        self.timer_status = QtCore.QTimer()

        #####  Acertando a hora do experimento (datetimeedit) #################
        agora = QtCore.QDateTime.currentDateTime()
        antes = agora.addDays(-5)
        self.ui.dateTimeEdit_inicio.setDateTime(antes)
        self.ui.dateTimeEdit_fim.setDateTime(agora)
        #####  testes #########################################################

        #######  Atualizando os valores das portas no inicio do programa #####
        self.add_portas_disponiveis()

        #######################################################################
        # Adicionando a foto do layout do forno
    	self.ui.label_layoutForno.setScaledContents(True)
    	self.ui.label_layoutForno.setPixmap(QtGui.QPixmap("forno_layout.png"))
        ## Remover depois				- Porta serial com4 pc de casa
        if sys.platform.startswith('win'):
            self.ui.comboBox_portaSerial.setCurrentIndex(4)
        ####### Connexões #####################################################
        # Slider do tempo de intervalo grafico
        self.ui.horizontalSlider_graficoPeriodo.sliderReleased.connect(partial(tempo_grafico, self))
        self.ui.horizontalSlider_r01.sliderReleased.connect(partial(resistencia01, self))
        self.ui.horizontalSlider_r02.sliderReleased.connect(partial(resistencia02, self))
        self.ui.horizontalSlider_r03.sliderReleased.connect(partial(resistencia03, self))
        self.ui.horizontalSlider_r04.sliderReleased.connect(partial(resistencia04, self))
        self.ui.horizontalSlider_r05.sliderReleased.connect(partial(resistencia05, self))
        self.ui.horizontalSlider_r06.sliderReleased.connect(partial(resistencia06, self))
        self.ui.horizontalSlider_esteira.sliderReleased.connect(partial(esteira, [self, 'slider']))
        self.ui.radioButton_esteiraTras.pressed.connect(partial(esteira, [self,'tras']))
        self.ui.radioButton_esteiraFrente.pressed.connect(partial(esteira, [self,'frente']))
        self.ui.pushButton_esteiraParar.pressed.connect(partial(esteira, [self,'parar']))
        self.ui.pushButton_conectar.pressed.connect(partial(conecta, self))
        self.ui.pushButton_emergencia.pressed.connect(partial(emergencia, self))
        self.ui.pushButton_serialAtualiza.pressed.connect(partial(envia_serial, 'ST\n'))
        self.ui.pushButton_updateInfo.pressed.connect(partial(envia_serial, 'SK\n'))
        self.ui.pushButton_limpaTexto.pressed.connect(self.limpa_texto)
        self.ui.pushButton_serialEnviaLinha.pressed.connect(partial(envia_manual, self))
        self.ui.pushButton_periodoPWM.pressed.connect(partial(envia_setpwm, self))
        self.ui.pushButton_leituraAnalogica.pressed.connect(partial(envia_setanalog, self))
        self.ui.comboBox_portaSerial.activated.connect(self.add_portas_disponiveis)
        self.ui.comboBox_fitLinear.activated.connect(self.lista_calibracoes)
        self.ui.radioButton_hold.clicked.connect(partial(hold, self))
        self.ui.pushButton_tiraFoto.pressed.connect(partial(tira_foto, self))
        self.ui.checkBox_cameraAutoUpdate.stateChanged.connect(partial(foto_update, self))
        self.ui.checkBox_graficoAuto.stateChanged.connect(partial(grafico_update, self))
        self.ui.checkBox_serialAuto.stateChanged.connect(partial(auto_ST, self))
        self.ui.pushButton_gerarArquivo.pressed.connect(partial(gera_arquivo, self))
        self.ui.pushButton_enviarEmail.pressed.connect(partial(envia_email, self))
        self.ui.pushButton_pendrive.pressed.connect(partial(pendrive, self))
        self.ui.pushButton_zerarBanco.pressed.connect(partial(zerabd_gui, self))
        self.ui.pushButton_limpaSenha.pressed.connect(partial(limpa_senha, self))
        self.ui.pushButton_experimento.pressed.connect(partial(novo_exp, self))
        self.ui.pushButton_localArquivo.pressed.connect(partial(local_arquivo, self.ui))
        self.ui.pushButton_salvarFit.pressed.connect(self.salva_calibracao)
        self.ui.pushButton_deletarFit.pressed.connect(self.deleta_calibracao)
        self.lista_calibracoes(False)

    #########################  Calibracao linear ###########################
    def salva_calibracao(self):
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
        print text, ok
        if ok:
            nomes = nomes_calibracao()
            for nome in nomes:
                if nome[0] == text:
                    igual = True
                    break
                else:
                    igual = False
            if igual:
                print "nome já existe"
            else:
                insere_calibracao(str(text), s_01_A, s_02_A, s_03_A, s_04_A, s_05_A, s_06_A, s_01_B, s_02_B, s_03_B, s_04_B, s_05_B, s_06_B)

    def deleta_calibracao(self):
        try:
            numero_escolha = self.ui.comboBox_fitLinear.currentIndex()
            escolha = self.ui.comboBox_fitLinear.itemText(numero_escolha)
            reply = QtGui.QMessageBox.question(self,'Mensagem',"Tem certeza que deletar a calibracao" + escolha + " ?",
        										QtGui.QMessageBox.Yes |QtGui.QMessageBox.No, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                deleta_calibracao_bd(str(escolha))
                if ( str(escolha) == retorna_dados_config() ):
                    primeiro_nome = self.ui.comboBox_fitLinear.itemText(0)
                    salva_config_calibracao(primeiro_nome)
                self.lista_calibracoes()
        except:
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

    def lista_calibracoes(self,tipo=0):
        self.ui.comboBox_portaSerial.blockSignals(True)
        nomes = nomes_calibracao()
        numero_escolha = self.ui.comboBox_fitLinear.currentIndex()
        self.ui.comboBox_fitLinear.clear()
        for nome in nomes:
            self.ui.comboBox_fitLinear.addItem(str(nome[0]))
        self.ui.comboBox_fitLinear.setCurrentIndex(numero_escolha)
        self.ui.comboBox_fitLinear.blockSignals(False)
        escolha = unicode(self.ui.comboBox_fitLinear.currentText())
        if ( tipo is False):
            padrao = retorna_dados_config()
            valores = leitura_calibracao(padrao)
        else:
            valores = leitura_calibracao(escolha)
            salva_config_calibracao(escolha)
        self.atualiza_valores_calibracoes(valores)
        self.atualiza_lineEdit_calibracao()

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

    #####################  Fun��es da GUI #################################
    def alerta_toolbar(self, texto):
    	'''
		Fun��o que coloca o texto na statusbar. O texto passado como par�metro na fun��o � anexado
		ao texto j� existente.
		Ao final da fun��o, um Qtimer � acionado, chamando a fun��o apaga_alterta, que retirar� o aviso
		da statusbar.
    	'''
        texto_inicial = str(self.statusBar().currentMessage())
        texto_append = texto + ' | '
        self.statusBar().showMessage(texto_inicial + texto_append)
        self.timer_status.singleShot(5000,partial(self.apaga_alterta,texto_append))

    def apaga_alterta(self, texto):
    	'''
		Fun��o que apaga o texto passado como par�metro da statusbar.
    	'''
        mensagem_total = str(self.statusBar().currentMessage())
        try:
            mensagem_total = mensagem_total.replace(texto,'')
            self.statusBar().clearMessage()
            self.statusBar().showMessage(mensagem_total)
        except:
            pass


    def enabled_disabled(self, estado):
        ''' Habilita ou desabilita as fun��es de controle da esteira (caso esteja ou n�o conectado ao forno) '''
        if (not estado):  # Caso esteja conectado:
            self.ui.horizontalSlider_r01.setValue(0)  # Volta os sliders para a opsi��o inicial
            self.ui.horizontalSlider_r02.setValue(0)
            self.ui.horizontalSlider_r04.setValue(0)
            self.ui.horizontalSlider_r03.setValue(0)
            self.ui.horizontalSlider_r06.setValue(0)
            self.ui.horizontalSlider_r05.setValue(0)
        self.ui.horizontalSlider_esteira.setEnabled(estado)  # Habilita/desabilita os controles
        self.ui.horizontalSlider_r01.setEnabled(estado)
        self.ui.horizontalSlider_r02.setEnabled(estado)
        self.ui.horizontalSlider_r04.setEnabled(estado)
        self.ui.horizontalSlider_r03.setEnabled(estado)
        self.ui.horizontalSlider_r06.setEnabled(estado)
        self.ui.horizontalSlider_r05.setEnabled(estado)
        self.ui.pushButton_updateInfo.setEnabled(estado)
        self.ui.pushButton_serialAtualiza.setEnabled(estado)
        self.ui.pushButton_esteiraParar.setEnabled(estado)
        self.ui.pushButton_serialEnviaLinha.setEnabled(estado)
        self.ui.pushButton_emergencia.setEnabled(estado)
        self.ui.checkBox_serialAuto.setEnabled(estado)
        self.ui.checkBox_graficoAuto.setEnabled(estado)
        self.ui.radioButton_hold.setEnabled(estado)
        self.ui.radioButton_esteiraTras.setEnabled(estado)
        self.ui.radioButton_esteiraFrente.setEnabled(estado)
        self.ui.pushButton_periodoPWM.setEnabled(estado)
        self.ui.pushButton_leituraAnalogica.setEnabled(estado)

    def add_portas_disponiveis(self):
        ''' M�todo que altera os valores da combobox que mostra as portas dispon�veis
		Os valores s�o retirados da fun��o serial_ports '''
        escolha = self.ui.comboBox_portaSerial.currentIndex()  # Salva a porta atual escolhida
        self.ui.comboBox_portaSerial.blockSignals(True)  # Bloqueia sinais do PyQt na combobox para evitar que a fun��o seja chamada novamente
        self.ui.comboBox_portaSerial.clear()  # Limpa os itens da combobox
        self.ui.comboBox_portaSerial.addItem('Atualiza')  # Adiciona uma op��o de atualiza��o das portas
        self.ui.comboBox_portaSerial.addItem('/')  # Adiciona um item para a raiz do sistema
        ports = serial_ports()  # chama a fun��o que lista as portas
        for port in ports:
            self.ui.comboBox_portaSerial.addItem(port)  # Adiciona as portas a lista da combobox
        self.ui.comboBox_portaSerial.blockSignals(False)  # Desabitita o bloqueio de sinal do PyQt para que esta fun��o possa ser chamada novamente no futuro
        self.ui.comboBox_portaSerial.setCurrentIndex(escolha)  # Volta para a porta escolhida

    def limpa_texto(self):
        ''' Limpa as 3 textbox que informam os dados recebidos '''
        self.ui.textEdit_dadosSerial.clear()
        self.ui.textEdit_temperatura.clear()


if __name__ == "__main__":  # Executa quando o programa � executado diretamente
    app = QtGui.QApplication(sys.argv)
    if (platform.system() == 'Darwin'):
        app.setStyle(QtGui.QStyleFactory.create("macintosh"))
    else:
        app.setStyle(QtGui.QStyleFactory.create("plastique"))
    window = Main()
    window.show()
    #window.showFullScreen()
    sys.exit(app.exec_())
