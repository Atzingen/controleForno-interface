# -*- coding: latin-1 -*-
from __future__ import division
import sys, os, time, platform, serial
from functools import partial
from PyQt4 import QtGui, QtCore
from modulo_global import *
import bd_config, bd_calibracao, bd_sensores
import forno_gui, calibracao, comunicacao_serial, automatico
import camera_rp, graficos, exporta_experimentos

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

        ###     Variáveis da calibração        ################################
        nomes = bd_config.retorna_dados_config_calibracao()
        cal = bd_calibracao.leitura_calibracao(str(nomes))
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
        self.tempo_pwm = 30

        self.ubee       = '0010'		# primeiros 4 dados que chegam (código do ubee)
        self.liga_02    = 'S21\n'	# Resistência 2
        self.desliga_02 = 'S22\n'
        self.liga_04    = 'S31\n'	# Resistência 4
        self.desliga_04 = 'S32\n'
        self.liga_06    = 'S41\n'	# Resistência 6
        self.desliga_06 = 'S42\n'
        self.liga_05    = 'S51\n'	# Resistência 5
        self.desliga_05 = 'S52\n'
        self.liga_03    = 'S61\n'	# Resistência 3
        self.desliga_03 = 'S62\n'
        self.liga_01    = 'S71\n'	# Resistência 1
        self.desliga_01 = 'S72\n'

        #####  testes #########################################################


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
        source_parent, _ = local_parent()
        self.ui.label_caminho.setText(source_parent + "dadosExperimento")

        ####### Banco de dados ################################################
        tempo_coleta = time.time()
        bd_sensores.cria_tabela()#Caso não exista, cria a tabela com os esquemas necessários

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

        #######  Atualizando os valores das portas no inicio do programa #####
        self.add_portas_disponiveis()

        ####### Atualiza o dropbox da calibracao ##############################
        calibracao.lista_calibracoes(self)
        automatico.lista_perfil_potencia(self)
        automatico.lista_perfil_resistencia(self)

        #######################################################################
        # Adicionando a foto do layout do forno
    	self.ui.label_layoutForno.setScaledContents(True)
    	self.ui.label_layoutForno.setPixmap(QtGui.QPixmap("../imagens/forno_layout.png"))
        ## Remover depois				- Porta serial com4 pc de casa
        if sys.platform.startswith('win'):
            self.ui.comboBox_portaSerial.setCurrentIndex(4)

        ####### Connexões #####################################################
        self.ui.horizontalSlider_graficoPeriodo.sliderReleased.connect(partial(graficos.tempo_grafico, self))
        self.ui.horizontalSlider_r01.sliderReleased.connect(partial(comunicacao_serial.resistencia01, self))
        self.ui.horizontalSlider_r02.sliderReleased.connect(partial(comunicacao_serial.resistencia02, self))
        self.ui.horizontalSlider_r03.sliderReleased.connect(partial(comunicacao_serial.resistencia03, self))
        self.ui.horizontalSlider_r04.sliderReleased.connect(partial(comunicacao_serial.resistencia04, self))
        self.ui.horizontalSlider_r05.sliderReleased.connect(partial(comunicacao_serial.resistencia05, self))
        self.ui.horizontalSlider_r06.sliderReleased.connect(partial(comunicacao_serial.resistencia06, self))
        self.ui.horizontalSlider_esteira.sliderReleased.connect(partial(comunicacao_serial.esteira, self, 'slider'))
        self.ui.radioButton_esteiraTras.pressed.connect(partial(comunicacao_serial.esteira,self,'tras'))
        self.ui.radioButton_esteiraFrente.pressed.connect(partial(comunicacao_serial.esteira, self,'frente'))
        self.ui.pushButton_esteiraParar.pressed.connect(partial(comunicacao_serial.esteira,self,'parar'))
        self.ui.pushButton_conectar.pressed.connect(partial(comunicacao_serial.conecta, self))
        self.ui.pushButton_emergencia.pressed.connect(partial(comunicacao_serial.emergencia, self))
        self.ui.pushButton_serialAtualiza.pressed.connect(partial(comunicacao_serial.envia_serial,self, 'ST\n'))
        self.ui.pushButton_updateInfo.pressed.connect(partial(comunicacao_serial.envia_serial,self, 'SK\n'))
        self.ui.pushButton_limpaTexto.pressed.connect(self.limpa_texto)
        self.ui.pushButton_serialEnviaLinha.pressed.connect(partial(comunicacao_serial.envia_manual, self))
        self.ui.pushButton_periodoPWM.pressed.connect(partial(comunicacao_serial.envia_setpwm, self))
        self.ui.pushButton_leituraAnalogica.pressed.connect(partial(comunicacao_serial.envia_setanalog, self))
        self.ui.comboBox_portaSerial.activated.connect(self.add_portas_disponiveis)
        self.ui.comboBox_fitLinear.activated.connect(partial(calibracao.lista_calibracoes,self))
        self.ui.comboBox_perfilPotencia.activated.connect(partial(automatico.lista_perfil_potencia,self))
        self.ui.comboBox_perfilResistencia.activated.connect(partial(automatico.lista_perfil_resistencia,self))
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
        self.ui.comboBox_displayPerfilResistencia.activated.connect(partial(graficos.plota_perfil,self,'resistencia',None))
        self.ui.pushButton_NovoPerfilResistencia.pressed.connect(partial(automatico.novo_perfil,'resistencia'))
        self.ui.pushButton_NovoPerfilPotencia.pressed.connect(partial(automatico.novo_perfil,'potencia'))
        self.ui.pushButton_deletarFit.pressed.connect(partial(calibracao.deleta_calibracao,'Fit'))
        self.ui.pushButton_apagarPerfilPotencia.pressed.connect(partial(calibracao.deleta_calibracao,'potencia'))
        self.ui.pushButton_apagarPerfilResistencia.pressed.connect(partial(calibracao.deleta_calibracao,'resistencia'))
        self.ui.pushButton_perfilResistencia.pressed.connect(partial(automatico.inicia_perfil,self,'resistencia'))
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
        self.ui.checkBox_graficoAuto.setChecked(False)
        self.ui.radioButton_hold.setEnabled(estado)
        self.ui.radioButton_esteiraTras.setEnabled(estado)
        self.ui.radioButton_esteiraFrente.setEnabled(estado)
        self.ui.pushButton_periodoPWM.setEnabled(estado)
        self.ui.pushButton_leituraAnalogica.setEnabled(estado)
        #self.ui.pushButton_perfilPotencia.setEnabled(estado)
        #self.ui.pushButton_perfilPotenciaFim.setEnabled(estado)
        #self.ui.pushButton_perfilResistencia.setEnabled(estado)
        #self.ui.pushButton_perfilResistenciaFim.setEnabled(estado)

    def add_portas_disponiveis(self):
        ''' M�todo que altera os valores da combobox que mostra as portas dispon�veis
		Os valores s�o retirados da fun��o serial_ports '''
        escolha = self.ui.comboBox_portaSerial.currentIndex()  # Salva a porta atual escolhida
        self.ui.comboBox_portaSerial.blockSignals(True)  # Bloqueia sinais do PyQt na combobox para evitar que a fun��o seja chamada novamente
        self.ui.comboBox_portaSerial.clear()  # Limpa os itens da combobox
        self.ui.comboBox_portaSerial.addItem('Atualiza')  # Adiciona uma op��o de atualiza��o das portas
        self.ui.comboBox_portaSerial.addItem('/')  # Adiciona um item para a raiz do sistema
        ports = comunicacao_serial.serial_ports()  # chama a fun��o que lista as portas
        for port in ports:
            self.ui.comboBox_portaSerial.addItem(port)  # Adiciona as portas a lista da combobox
        self.ui.comboBox_portaSerial.blockSignals(False)  # Desabitita o bloqueio de sinal do PyQt para que esta fun��o possa ser chamada novamente no futuro
        self.ui.comboBox_portaSerial.setCurrentIndex(escolha)  # Volta para a porta escolhida

    def limpa_texto(self):
        ''' Limpa as 3 textbox que informam os dados recebidos '''
        self.ui.textEdit_dadosSerial.clear()
        self.ui.textEdit_temperatura.clear()
