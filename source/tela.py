# -*- coding: latin-1 -*-
from __future__ import division
import sys, os, time, platform, serial
from functools import partial
from PyQt4 import QtGui, QtCore
import cv2
import informacoes
import banco.bd_config as bd_config
import banco.bd_calibracao as bd_calibracao
import banco.bd_sensores as bd_sensores
import simulacao.forno1d
import simulacao.alimento
import simulacao.controle
import forno_gui, calibracao, comunicacao_serial, automatico
import camera_rp, graficos, exporta_experimentos, controle_pid

class Main(QtGui.QMainWindow):
    '''
	Classe principal da tela.
	a ui usa as propriedades da classe Ui_MainWindow,
	feita com o Qt Designer, e mantida separadamente no
	arquivo gui_forno_gui, compilada com o pyuic4
	'''
    def __init__(self):
        '''
        Construtor do objeto da tela principal. Executa quando o programa
        inicia e cria o objeto tela principal.
        '''
        # Iniciando a ui
        QtGui.QMainWindow.__init__(self)
        self.ui = forno_gui.Ui_MainWindow()
        self.ui.setupUi(self)

        #####  QTimers ########################################################
        self.timer_foto = QtCore.QTimer()
        self.timer_grafico = QtCore.QTimer()
        self.timer_serial = QtCore.QTimer()
        self.timer_ST = QtCore.QTimer()
        self.timer_status = QtCore.QTimer()
        self.timer_alimento = QtCore.QTimer()

        ###  Variaveis de controle geral  #####################################
        self.caminho_inicial = informacoes.local_parent()
        self.caminho_banco = self.caminho_inicial + '/bancoDados/forno_data.db'
        self.caminho_forno_pre = self.caminho_inicial + '/imagens/forno-pre.jpg'
        self.caminho_biscoito = self.caminho_inicial + '/imagens/biscoito.PNG'
        self.caminho_forno_layout = self.caminho_inicial + '/imagens/forno_layout.png'
        self.caminho_colorbar = self.caminho_inicial + '/imagens/colorbar.png'

        self.img_forno = cv2.imread(self.caminho_forno_pre)
        self.img_biscoito = cv2.imread(self.caminho_biscoito)

        ###     Variáveis da calibração        ################################
        nomes = bd_config.retorna_dados_config_calibracao(self.caminho_banco)
        cal = bd_calibracao.leitura_calibracao(self.caminho_banco, str(nomes))
        calibracao.atualiza_valores_calibracoes(self,cal)
        calibracao.atualiza_lineEdit_calibracao(self)

        ##### Variáveis para controle dos estados do forno ####################
        self.valor_resistencia01 = 0
        self.valor_resistencia02 = 0
        self.valor_resistencia03 = 0
        self.valor_resistencia04 = 0
        self.valor_resistencia05 = 0
        self.valor_resistencia06 = 0
        self.valor_esteira = 0

        self.s = serial.Serial()

        self.texto = ""
        self.tempo_pwm = 3

        self.CHR_pedidoTemperaturas = 'T'
        self.STR_emergencia = 'E'
        self.STR_inicioTemperatura = '0001'
        self.CHR_inicioDado = 'S'
        self.CHR_fimDado = '\n'
        self.CHR_ligaForno = '1'
        self.CHR_desligaForno = '2'
        self.CHR_setPotenciaPWM = 'P'
        self.CHR_esteiraFrente = 'H'
        self.CHR_esteiraTras = 'A'
        self.CHR_esteiraParada = 'D'
        self.CHR_tempoPWM = 'U'
        self.CHR_check = 'K'
        self.CHR_setADC = 'L'

        self.pos_sensor_esteira = 12
        self.pos_sensor_teto1 = 8
        self.pos_sensor_teto2 = 24
        self.pos_sensor_lateral1 = 20
        self.pos_sensor_lateral2 = 4
        self.pos_sensor_lateral3 = 16

        self.pinR1 = '3'
        self.pinR2 = '5'
        self.pinR3 = '2'
        self.pinR4 = '6'
        self.pinR5 = '4'
        self.pinR6 = '7'
        self.pinResistencias = [self.pinR1, self.pinR2, self.pinR3, self.pinR4,
                                self.pinR5, self.pinR6]

        #####  Controle PID ####################################################
        self.pidEsteira = controle_pid.PID('pidEsteira')
        self.pidAr = controle_pid.PID('pidAr')
        controle_pid.update_valores_pid(self)

        #####  testes ##########################################################

        self.status = informacoes.status()

        ##### Efeitos visuais para outros OS (teste)
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
        self.ui.label_caminho.setText(self.caminho_inicial + '/dadosExperimento')

        ####### Banco de dados ################################################
        tempo_coleta = time.time()
        bd_sensores.cria_tabela(self.caminho_banco)#Caso não exista, cria a tabela com os esquemas necessários

        #####  Acertando a hora do experimento (datetimeedit) #################
        agora = QtCore.QDateTime.currentDateTime()
        antes = agora.addDays(-5)
        self.ui.dateTimeEdit_inicio.setDateTime(antes)
        self.ui.dateTimeEdit_fim.setDateTime(agora)

        #######  Atualizando os valores do controle PID
        controle_pid.update_label_pid(self)

        #######  Atualizando os valores das portas no inicio do programa #####
        self.add_portas_disponiveis()

        ####### Atualiza o dropbox da calibracao ##############################
        calibracao.lista_calibracoes(self)
        automatico.lista_perfil_potencia(self)
        automatico.lista_perfil_temperatura(self)

        ####### Atualizando o label do tempo PWM e leituras AD ###############
        automatico.atualiza_label_microcontrolador(self)

        #######################################################################
        # Adicionando a foto do layout do forno
    	self.ui.label_layoutForno.setScaledContents(True)
    	self.ui.label_layoutForno.setPixmap(QtGui.QPixmap(self.caminho_forno_layout))
        self.ui.label_colorbar.setPixmap(QtGui.QPixmap(self.caminho_colorbar).scaled(self.ui.label_colorbar.size(), QtCore.Qt.KeepAspectRatio))
        self.ui.label_colorbar_2.setPixmap(QtGui.QPixmap(self.caminho_colorbar).scaled(self.ui.label_colorbar_2.size(), QtCore.Qt.KeepAspectRatio))
        ## Remover depois				- Porta serial com4 pc de casa
        try:
            self.ui.comboBox_portaSerial.setCurrentIndex(4)
        except:
            pass

        ####### Atualza combobox simulacao alimento ###########################
        simulacao.controle.atualiza_comboBox(self)
        simulacao.controle.set_colobarAlimentoLabel(self)
        simulacao.controle.set_colobarFornoLabel(self)

        ####### Connexões #####################################################
        self.ui.spinBox_alimento_max.valueChanged.connect(partial(simulacao.controle.set_colobarAlimentoLabel,self))
        self.ui.spinBox_alimento_min.valueChanged.connect(partial(simulacao.controle.set_colobarAlimentoLabel,self))
        self.ui.spinBox_forno_max.valueChanged.connect(partial(simulacao.controle.set_colobarFornoLabel,self))
        self.ui.spinBox_forno_min.valueChanged.connect(partial(simulacao.controle.set_colobarFornoLabel,self))
        self.ui.pushButton_simAlimento.pressed.connect(partial(simulacao.controle.iniciar_perfil_alimento,self))
        self.ui.pushButton_NovoPerfilAlimento.pressed.connect(partial(simulacao.controle.novo_perfil_alimento,self))
        self.ui.pushButton_apagarPerfilAlimento.pressed.connect(partial(simulacao.controle.apagar_perfil,self))
        self.ui.comboBox_perfilAlimento.activated.connect(partial(simulacao.controle.lista_perfil_alimento_update,self))
        self.ui.pushButton_pidUpdate.pressed.connect(partial(controle_pid.update_config_pid,self))
        self.ui.pushButton_pid_limpar.pressed.connect(partial(controle_pid.limpa_lineEdit,self))
        self.ui.horizontalSlider_graficoPeriodo.sliderReleased.connect(partial(graficos.tempo_grafico, self))
        self.ui.horizontalSlider_r01.sliderReleased.connect(partial(comunicacao_serial.envia_resistencia, self, 1))
        self.ui.horizontalSlider_r02.sliderReleased.connect(partial(comunicacao_serial.envia_resistencia, self, 2))
        self.ui.horizontalSlider_r03.sliderReleased.connect(partial(comunicacao_serial.envia_resistencia, self, 3))
        self.ui.horizontalSlider_r04.sliderReleased.connect(partial(comunicacao_serial.envia_resistencia, self, 4))
        self.ui.horizontalSlider_r05.sliderReleased.connect(partial(comunicacao_serial.envia_resistencia, self, 5))
        self.ui.horizontalSlider_r06.sliderReleased.connect(partial(comunicacao_serial.envia_resistencia, self, 6))
        self.ui.horizontalSlider_esteira.sliderReleased.connect(partial(comunicacao_serial.esteira, self, 'slider'))
        self.ui.radioButton_esteiraTras.pressed.connect(partial(comunicacao_serial.esteira,self,'tras'))
        self.ui.radioButton_esteiraFrente.pressed.connect(partial(comunicacao_serial.esteira, self,'frente'))
        self.ui.pushButton_esteiraParar.pressed.connect(partial(comunicacao_serial.esteira,self,'parar'))
        self.ui.pushButton_conectar.pressed.connect(partial(comunicacao_serial.conecta, self))
        self.ui.pushButton_emergencia.pressed.connect(partial(comunicacao_serial.emergencia, self))
        self.ui.pushButton_serialAtualiza.pressed.connect(partial(comunicacao_serial.envia_serial,self,self.CHR_pedidoTemperaturas ))
        self.ui.pushButton_updateInfo.pressed.connect(partial(comunicacao_serial.envia_serial,self,self.CHR_check))
        self.ui.pushButton_limpaTexto.pressed.connect(self.limpa_texto)
        self.ui.pushButton_serialEnviaLinha.pressed.connect(partial(comunicacao_serial.envia_manual, self))
        self.ui.pushButton_periodoPWM.pressed.connect(partial(comunicacao_serial.envia_setpwm, self, atualiza=True))
        self.ui.pushButton_leituraAnalogica.pressed.connect(partial(comunicacao_serial.envia_setanalog, self,atualiza=True))
        self.ui.comboBox_portaSerial.activated.connect(self.add_portas_disponiveis)
        self.ui.comboBox_fitLinear.activated.connect(partial(calibracao.lista_calibracoes,self))
        self.ui.comboBox_perfilPotencia.activated.connect(partial(automatico.lista_perfil_potencia,self))
        self.ui.comboBox_perfilTemperatura.activated.connect(partial(automatico.lista_perfil_temperatura,self))
        self.ui.radioButton_hold.clicked.connect(partial(comunicacao_serial.hold, self))
        self.ui.pushButton_tiraFoto.pressed.connect(partial(camera_rp.tira_foto, self))
        self.ui.checkBox_cameraAutoUpdate.stateChanged.connect(partial(camera_rp.foto_update, self))
        self.ui.checkBox_graficoAuto.stateChanged.connect(partial(graficos.grafico_update, self))
        self.ui.checkBox_serialAuto.stateChanged.connect(partial(comunicacao_serial.auto_ST, self))
        self.ui.pushButton_gerarArquivo.pressed.connect(partial(exporta_experimentos.gera_arquivo, self))
        self.ui.pushButton_enviarEmail.pressed.connect(partial(exporta_experimentos.envia_email, self))
        self.ui.pushButton_pendrive.pressed.connect(partial(exporta_experimentos.pendrive, self))
        self.ui.pushButton_zerarBanco.pressed.connect(partial(exporta_experimentos.zerabd_gui, self))
        self.ui.pushButton_limpaSenha.pressed.connect(partial(exporta_experimentos.limpa_senha, self))
        self.ui.pushButton_experimento.pressed.connect(partial(exporta_experimentos.novo_exp, self))
        self.ui.pushButton_localArquivo.pressed.connect(partial(exporta_experimentos.local_arquivo, self.ui))
        self.ui.pushButton_salvarFit.pressed.connect(partial(calibracao.salva_calibracao,self))
        self.ui.comboBox_displayPerfilPotencia.activated.connect(partial(graficos.plota_perfil,self,'potencia',None))
        self.ui.comboBox_displayPerfilTemperatura.activated.connect(partial(graficos.plota_perfil,self,'temperatura',None))
        self.ui.pushButton_NovoPerfilTemperatura.pressed.connect(partial(automatico.novo_perfil,self,'temperatura'))
        self.ui.pushButton_NovoPerfilPotencia.pressed.connect(partial(automatico.novo_perfil,self,'potencia'))
        self.ui.pushButton_deletarFit.pressed.connect(partial(calibracao.deleta_calibracao,self,'Fit'))
        self.ui.pushButton_apagarPerfilPotencia.pressed.connect(partial(calibracao.deleta_calibracao,self,'potencia'))
        self.ui.pushButton_apagarPerfilTemperatura.pressed.connect(partial(calibracao.deleta_calibracao,self,'temperatura'))
        self.ui.pushButton_perfilTemperatura.pressed.connect(partial(automatico.inicia_perfil,self,'temperatura'))
        self.ui.pushButton_perfilPotencia.pressed.connect(partial(automatico.inicia_perfil,self,'potencia'))

    #####################  Funções da GUI #################################
    def alerta_toolbar(self, texto):
    	'''
		Função que coloca o texto na statusbar. O texto passado como parâmetro
        na função é anexado ao texto já existente.
		Ao final da função, um Qtimer é acionado, chamando a função
        apaga_alterta, que retira o aviso da statusbar 5 segundos após ser
        adicionado devido a thread singleShot.
    	'''
        texto_inicial = str(self.statusBar().currentMessage())
        texto_append = texto + ' | '
        self.statusBar().showMessage(texto_inicial + texto_append)
        self.timer_status.singleShot(3000,partial(self.apaga_alterta,texto_append))

    def apaga_alterta(self, texto):
    	'''
		Função que apaga o texto passado como parâmetro da statusbar.
    	'''
        mensagem_total = str(self.statusBar().currentMessage())
        try:
            mensagem_total = mensagem_total.replace(texto,'')
            self.statusBar().clearMessage()
            self.statusBar().showMessage(mensagem_total)
        except:
            print "DEBUG: Erro ao apagar msg da statusbar - texto:", texto
            pass


    def enabled_disabled(self, estado):
        ''' Habilita ou desabilita as funções de controle da esteira
         (caso esteja ou não conectado ao forno)
        '''
        if (not estado):  # Caso esteja conectado:
            self.ui.horizontalSlider_r01.setValue(0)
            self.ui.horizontalSlider_r02.setValue(0)
            self.ui.horizontalSlider_r04.setValue(0)
            self.ui.horizontalSlider_r03.setValue(0)
            self.ui.horizontalSlider_r06.setValue(0)
            self.ui.horizontalSlider_r05.setValue(0)
        self.ui.horizontalSlider_esteira.setValue(0)
        self.ui.horizontalSlider_esteira.setEnabled(estado)
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
        self.ui.checkBox_serialAuto.setChecked(False)
        self.ui.checkBox_serialAuto.setEnabled(estado)
        self.ui.checkBox_graficoAuto.setChecked(False)
        self.ui.checkBox_graficoAuto.setEnabled(estado)
        self.ui.radioButton_hold.setEnabled(estado)
        self.ui.radioButton_esteiraTras.setChecked(False)
        self.ui.radioButton_esteiraTras.setEnabled(estado)
        self.ui.radioButton_esteiraFrente.setChecked(False)
        self.ui.radioButton_esteiraFrente.setEnabled(estado)
        self.ui.pushButton_periodoPWM.setEnabled(estado)
        self.ui.pushButton_leituraAnalogica.setEnabled(estado)
        self.ui.checkBox_calcPerfil.setChecked(False)
        self.ui.checkBox_calcPerfil.setEnabled(estado)
        self.ui.checkBox_mostraPerfil.setChecked(False)
        self.ui.checkBox_mostraPerfil.setEnabled(estado)
        self.ui.pushButton_perfilTemperatura.setText('Iniciar')
        self.ui.pushButton_perfilTemperatura.setEnabled(estado)
        self.ui.pushButton_perfilPotencia.setText('Iniciar')
        self.ui.pushButton_perfilPotencia.setEnabled(estado)

    def add_portas_disponiveis(self):
        '''
        Metodo que altera os valores da combobox que mostra as portas disponíveis
		Os valores são retirados da função serial_ports
        '''
        # Salva a porta atual escolhida
        escolha = self.ui.comboBox_portaSerial.currentIndex()
        # Bloqueia sinais do PyQt na combobox para evitar que a funcão seja chamada novamente
        self.ui.comboBox_portaSerial.blockSignals(True)
        self.ui.comboBox_portaSerial.clear()
        self.ui.comboBox_portaSerial.addItem('Atualiza')
        self.ui.comboBox_portaSerial.addItem('/')
        ports = comunicacao_serial.serial_ports()
        for port in ports:
            self.ui.comboBox_portaSerial.addItem(port)
        # Desabitita o bloqueio de sinal do PyQt para que esta função possa
        # ser chamada novamente no futuro.
        self.ui.comboBox_portaSerial.blockSignals(False)
        self.ui.comboBox_portaSerial.setCurrentIndex(escolha)

    def limpa_texto(self):
        '''
        Limpa as 3 textbox que informam os dados recebidos
        '''
        self.ui.textEdit_dadosSerial.clear()
        self.ui.textEdit_temperatura.clear()
