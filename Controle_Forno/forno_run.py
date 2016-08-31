# -*- coding: latin-1 -*-
from __future__ import division
from forno_gui import Ui_MainWindow
import sensor_db
import numpy as np
import sys, os, serial, glob, thread, time, datetime, sqlite3, PIL, scipy, csv, smtplib, shutil
from threading import Thread
from PyQt4 import QtGui, QtCore
from PIL import Image, ImageQt
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import Encoders
try:
	import picamera
except:
	pass

############ Comandos do forno ################################
ubee       = '0010'		# primeiros 4 dados que chegam (código do ubee)
liga_02    = 'S21\n'	# Resistência 2
desliga_02 = 'S22\n'
liga_04    = 'S31\n'	# Resistência 4
desliga_04 = 'S32\n'
liga_06    = 'S41\n'	# Resistência 6
desliga_06 = 'S42\n'
liga_05    = 'S51\n'	# Resistência 5
desliga_05 = 'S52\n'
liga_03    = 'S61\n'	# Resistência 3
desliga_03 = 'S62\n'
liga_01    = 'S71\n'	# Resistência 1
desliga_01 = 'S72\n'

def verifica_dado(dado):
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
				d = converte_dado(dado)												# Chama a função para retirar os dados e converter
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

def converte_dado(dado):	
	'''Função que recebe o dado como stringo e particiona em um vetor com 7 posições.
	A primeira posição é o tempo atual e as outras 6 são os 6 dados do sensor (int de 0 a 1023)'''
	try:
		dado = dado.strip('S')
		d = np.zeros([7,1])
		d[0] = time.time() 															# tempo_coleta 	
		d[1] = float(window.S_01_A) + (float(window.S_01_B) * int(dado[4:8]))		# Sensor 1
		d[2] = float(window.S_02_A) + (float(window.S_02_B) * int(dado[8:12]))		# Sensor 2
		d[3] = float(window.S_03_A) + (float(window.S_03_B) * int(dado[24:28]))  	# Sensor 3 
		d[4] = float(window.S_04_A) + (float(window.S_04_B) * int(dado[12:16]))		# Sensor 4
		d[5] = float(window.S_05_A) + (float(window.S_05_B) * int(dado[20:24]))		# Sensor 5
		d[6] = float(window.S_06_A) + (float(window.S_06_B) * int(dado[16:20]))		# Sensor 6
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
		QtGui.QMainWindow.__init__(self)						# Interface Gráfica			
		self.ui = Ui_MainWindow()   							# Qtdesigner
		self.ui.setupUi(self)			
		####### Variáveis de configuração #####################################
		self.tempo_update_serial = 431 	  						# tempo em milisegundos 
		self.serial_timeout = False 							# Timeout da leirura serial
		self.experimento_nome = 'Sem Nome'						# Veriável para o nome do experimento
		###     Variáveis da calibração        ################################
		self.S_01_A = float(self.ui.lineEdit_4.text())
		self.S_01_B = float(self.ui.lineEdit_5.text())
		self.S_02_A = float(self.ui.lineEdit_7.text())
		self.S_02_B = float(self.ui.lineEdit_6.text())
		self.S_03_A = float(self.ui.lineEdit_9.text())
		self.S_03_B = float(self.ui.lineEdit_8.text())
		self.S_04_A = float(self.ui.lineEdit_11.text())
		self.S_04_B = float(self.ui.lineEdit_10.text()) 
		self.S_05_A = float(self.ui.lineEdit_13.text()) 
		self.S_05_B = float(self.ui.lineEdit_12.text()) 
		self.S_06_A = float(self.ui.lineEdit_15.text())
		self.S_06_B = float(self.ui.lineEdit_14.text())
		###   Variáveis de estado do forno (flags) #############################
		self.resitencia01 = 0
		self.resitencia02 = 0 
		self.resitencia03 = 0 
		self.resitencia04 = 0 
		self.resitencia05 = 0
		self.resitencia06 = 0 
		self.esteira = 0
		self.flag = []										

		################### Remover ###########################################
		if sys.platform.startswith('win'):						# Parte de teste - apagar no final
			if os.path.isdir("F:\Google Drive\Doutorado\Codigos-dr\Controle\interfacegrafica"):
				self.ui.label_18.setText('F:\Google Drive\Doutorado\Codigos-dr\Controle\interfacegrafica\\')
			else:
				self.ui.label_18.setText("C:/")
		else:
			if os.path.isdir("/home/pi/Desktop"):
				self.ui.label_18.setText('/home/pi/Desktop/')
			else:
				self.ui.label_18.setText("/")

		####### Banco de dados ################################################
		tempo_coleta = time.time()
		sensor_db.cria_tabela()
		#####  QTimers ########################################################
		self.timer_foto    = QtCore.QTimer()
		self.timer_grafico = QtCore.QTimer()
		self.timer_serial  = QtCore.QTimer()
		self.timer_ST	   = QtCore.QTimer()
		#####  Acertando a hora do experimento (datetimeedit) #################
		agora = QtCore.QDateTime.currentDateTime()
		antes = agora.addDays(-5)
		self.ui.dateTimeEdit.setDateTime(agora)
		self.ui.dateTimeEdit_2.setDateTime(antes)
		#####  testes #########################################################

		#######  Atualizando os valores das portas no inicio do programa #####
		self.f_add_portas_disponiveis()

		## Remover depois				- Porta serial com5 pc de casa
		if sys.platform.startswith('win'):
			self.ui.comboBox.setCurrentIndex(6)

		####### Connexões #####################################################
		# Slider do tempo de intervalo grafico
		self.ui.horizontalSlider_8.sliderReleased.connect(self.f_tempo_grafico)
		self.ui.horizontalSlider_r01.sliderReleased.connect(self.f_resistencia01)
		self.ui.horizontalSlider_r02.sliderReleased.connect(self.f_resistencia02)
		self.ui.horizontalSlider_r04.sliderReleased.connect(self.f_resistencia04)
		self.ui.horizontalSlider_r03.sliderReleased.connect(self.f_resistencia03)
		self.ui.horizontalSlider_r05.sliderReleased.connect(self.f_resistencia05)
		self.ui.horizontalSlider_r06.sliderReleased.connect(self.f_resistencia06)
		self.ui.horizontalSlider.sliderReleased.connect(self.f_esteira)
		self.ui.pushButton.pressed.connect(self.f_conecta)
		self.ui.pushButton_3.pressed.connect(self.f_emergencia)
		self.ui.pushButton_4.pressed.connect(self.f_para_esteira)
		self.ui.pushButton_2.pressed.connect(self.f_atualiza_temp)
		self.ui.pushButton_7.pressed.connect(self.f_limpa_texto)
		self.ui.pushButton_6.pressed.connect(self.f_envia_manual)
		self.ui.comboBox.activated.connect(self.f_add_portas_disponiveis)
		self.ui.radioButton.clicked.connect(self.f_hold)
		self.ui.pushButton_5.pressed.connect(self.f_tira_foto)
		self.ui.checkBox_10.stateChanged.connect(self.f_foto_update)
		self.ui.checkBox_14.stateChanged.connect(self.f_grafico_update)
		self.ui.checkBox_9.stateChanged.connect(self.f_auto_ST)
		self.ui.pushButton_8.pressed.connect(self.f_gera_arquivo)
		self.ui.pushButton_11.pressed.connect(self.f_envia_email)
		self.ui.pushButton_12.pressed.connect(self.f_pendrive)
		self.ui.pushButton_13.pressed.connect(self.f_zerabd)
		self.ui.pushButton_14.pressed.connect(self.f_limpa_senha)
		self.ui.pushButton_15.pressed.connect(self.f_novo_exp)
		self.ui.pushButton_16.pressed.connect(self.f_local_arquivo)
		self.ui.pushButton_17.pressed.connect(self.f_atualiza_calibra_linear)
	#########################  Calibracao linear ###########################
	def f_atualiza_calibra_linear(self):
		'''Pega os valores dos campos da calibração linear para fazer a conversão entre tensão e temperatura'''
		self.S_01_A = float(self.ui.lineEdit_4.text())
		self.S_01_B = float(self.ui.lineEdit_5.text())
		self.S_02_A = float(self.ui.lineEdit_7.text())
		self.S_02_B = float(self.ui.lineEdit_6.text())
		self.S_03_A = float(self.ui.lineEdit_9.text())
		self.S_03_B = float(self.ui.lineEdit_8.text())
		self.S_04_A = float(self.ui.lineEdit_11.text())
		self.S_04_B = float(self.ui.lineEdit_10.text()) 
		self.S_05_A = float(self.ui.lineEdit_13.text()) 
		self.S_05_B = float(self.ui.lineEdit_12.text()) 
		self.S_06_A = float(self.ui.lineEdit_15.text())
		self.S_06_B = float(self.ui.lineEdit_14.text())

	########################## Aba dados ###################################
	def f_local_arquivo(self):
		''' Altera o texto do lable que mostra o caminho onde são salvos os arquivos''' 
		local = str(QtGui.QFileDialog.getExistingDirectory())
		if sys.platform.startswith('win'):
			local = local + '\\'
		else:
			local = local + '/'
		self.ui.label_18.setText(local)

	def f_gera_arquivo(self):
		''' Método que é ativado quando o botão 'Gera Arquivo' é pressionada.
		Os dados são retirados do bd de acordo com as configurações do experimento (nome ou período)
		e salvas no formato adequado de acordo com as opções no checkbox formato do Arquivo'''
		t = datetime.datetime.now()															# Pega o tempo para o nome do arquivo
		tempo = str(t.month) + '-' + str(t.day) + '-' + str(t.hour) + '-' + str(t.minute) 	# Coloca os valores do tempo em uma string
		caminho = str(self.ui.label_18.text())
		if self.experimento_nome == 'Sem Nome' and self.ui.checkBox_18.isChecked():			# Checa se é um experimento sem nome (por data) e foi selecionado dados por período
			Ti = self.ui.dateTimeEdit_2.dateTime().toPyDateTime()							# Pega a data inicial desejada
			Tf = self.ui.dateTimeEdit.dateTime().toPyDateTime()								# Pega a data final desejada
			d = sensor_db.retorna_dados(1,Ti=Ti,Tf=Tf)										# Pedido ao banco de dados para o período escolhido
		elif self.ui.checkBox_19.isChecked():
			d = sensor_db.retorna_dados(1,experimento=str(self.experimento_nome))			# Busca no bd os dados com o nome do experimento específico
			tempo = str(self.experimento_nome) + '_' + tempo 								# Adiciona o nome do experimento ao tempo
		for a in glob.glob('*'):															# loop pelo diretório para buscar se o arquivo ja existe
			if tempo in a:																	# Caso já exista:
				tempo = tempo + '(1)'														# 	adiciona o texto (1) no final do nome do arquivo para 
				break 																		#   evitar sobrescrever e apagar dados	
		# if para as 3 opçoes (txt, csv, db)
		if self.ui.checkBox_15.isChecked():													# Salvar em arquivo .txt
			with open(caminho + tempo + '.txt', "w") as arquivo_texto:						# Abre o arquivo que irá ser escrito
				arquivo_texto.write('Arquivo gerado automaticamente - Dados do forno - LAFAC USP \n \n \n')						# Cabeçalho
				arquivo_texto.write('chave \t Data e horario completo  \tt_0 \t\ts1 \ts2 \ts3 \ts4 \ts5 \ts6\texperimento\n\n') # informações sobre as colunas
				for i in d:																	# loop para andar por todas as linhas de dados
					arquivo_texto.write('\n')												# pula uma linha 
					for j in i:																# loop pelas colunas
						arquivo_texto.write(str(j) + '\t')									# adiciona os dados e um tab
				arquivo_texto.close()														# fecha o manipulador do arquivo

		elif self.ui.checkBox_16.isChecked():												# Salvar em arquivo .csv (segunda opção)
			with open(caminho + tempo + '.csv', 'wt') as arquivo_csv:						# abre o arquivo para salvar os dados
				writer = csv.writer(arquivo_csv,lineterminator = '\n',dialect='excel')		
				writer.writerow(('chave','Data e horario completo','t_0','s1','s2','s3','s4','s5','s6','experimento'))
				if np.size(d) > 0:															# Caso d não esteja vazio
					try:
						for i in range(np.size(d[:,1])):									# loop por todas as linhas
							writer.writerow(( d[i,0], d[i,1], d[i,2], d[i,3], d[i,4], 
											  d[i,5], d[i,6], d[i,7], d[i,8], d[i,9] ))
						arquivo_csv.close()													# fecha o arquivo
					except:
						pass
		else:																				# Salva em banco de dados sqlite3
			pass

	def f_envia_email(self):
		''' Método que envia os dados do experimento por email'''
		f = str(QtGui.QFileDialog.getOpenFileName())										# popup que pede para selecionar o arquivo (retorna o caminho do arquivo)
		endereco = str(self.ui.lineEdit_2.text())											
		senha    = str(self.ui.lineEdit_3.text())
		if ('@gmail.com' in endereco) and (senha is not ''):								# implementado apenas envio para o gmail
			try:																			# Envio do email: 
				t = datetime.datetime.now()															
				tempo = str(t.month) + '-' + str(t.day) + '-' + str(t.hour) + '-' + str(t.minute)
				#f = 'F:\Google Drive\Doutorado\Codigos-dr\Controle\interfacegrafica\este.jpg'
				arquivo = os.path.basename(f)
				msg = MIMEMultipart()
				msg['From'] = endereco
				msg['To'] = endereco
				msg['Subject'] = "Dados: " + os.path.basename(f) + ' ' + tempo
				corpo_email = "E-mail gerado automaticamente \n\n Programa de controle - Forno Lafac \n\n formato da data (Assunto do e-mail: Mes - dia - hora - minuto) "
				msg.attach(MIMEText(corpo_email))

				part = MIMEBase('application', "octet-stream")
				part.set_payload(open(f,'rb').read())
				Encoders.encode_base64(part)
				part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
				msg.attach(part)

				server = smtplib.SMTP('smtp.gmail.com', 587)
				server.starttls()
				server.login(endereco, senha)
				text = msg.as_string()
				server.sendmail(endereco, endereco, text)
				server.quit()
			except:
				print 'Erro ao enviar e-mail - smtp (senha ou login)'
		else:
			print 'erro de parametros - email, senha, arquivo'

	def f_pendrive(self):
		''' Método é acionado ao clicar no botão 'pendrive'.
		É aberto um popup para pegar o caminho do arquivo a ser salvo e depois o local aonde será salvo (no pendrive) '''
		self.statusBar().showMessage('teste')
		fonte   = str(QtGui.QFileDialog.getOpenFileName())
		destino = str(QtGui.QFileDialog.getExistingDirectory())
		if len(str(fonte)) > 1 and len(str(destino)) > 1:
			shutil.copy2(fonte,destino)


	def f_zerabd(self):
		''' Método para zerar o banco de dados (acionado pelo botão 'Zerar Bando de dados') 
		Um popup é aberto para confirmar que os dados serão mesmo apagados'''
		reply = QtGui.QMessageBox.question(self, 'Mensagem',"Ter certeza que quer zerar o banco de dados?", 
											QtGui.QMessageBox.Yes | 
											QtGui.QMessageBox.No, QtGui.QMessageBox.No)
		if reply == QtGui.QMessageBox.Yes:
			reply = QtGui.QMessageBox.question(self, 'Mensagem',"Ter certeza ? Isto apagara TODOS os dados", 
											QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, 
											QtGui.QMessageBox.No)
			if reply == QtGui.QMessageBox.Yes:
				print 'zerando banco de dados'
				sensor_db.deleta_tabeta()

	def f_limpa_senha(self):
		''' Limpa o campo senha e email '''
		reply = QtGui.QMessageBox.question(self,'Mensagem',"Tem certeza que quer limpar senha e e-mail?", 
											QtGui.QMessageBox.Yes | 
											QtGui.QMessageBox.No, QtGui.QMessageBox.No)
		if reply == QtGui.QMessageBox.Yes:
			self.ui.lineEdit_2.setText("")
			self.ui.lineEdit_3.setText("")

	def f_novo_exp(self):
		if self.ui.pushButton_15.text() == 'Encerrar Experimento':		# Caso o botão esteja no modo Encerrar Experimento
			self.ui.pushButton_15.setText('Novo Experimento')			# Altera o lable do botão para Novo Experimento
			self.ui.label_20.setText("Sem Nome")
			self.ui.checkBox_19.setEnabled(False)						# Desabilita o checkbox de seleção do experimento atual
			self.ui.checkBox_18.setChecked(True)						# Marca a checkbox de salvar dados por período
			self.ui.checkBox_20.setChecked(False)						# Desmarca o checbox de seleção do experimento atual (plot)
			self.ui.checkBox_20.setEnabled(False)						# Desabilita o checkbox de seleção do experimento atual (plot)
			self.experimento_nome = 'Sem Nome'
		else:
			text, ok = QtGui.QInputDialog.getText(self, '', 			# Caixa de dialogo para nome do experimento
												'Digite o nome do seu experimento')
			if ok and len(text) > 1:
				self.experimento_nome = text 							# Salva o nome do experimento
				self.ui.label_20.setText(self.experimento_nome)			# Altera o label do nome do experimento
				self.ui.pushButton_15.setText('Encerrar Experimento')	# Altera o texto do botão 
				self.ui.checkBox_19.setEnabled(True)					# Habilita o checkbox de seleção do experimento atual
				self.ui.checkBox_20.setEnabled(True)					# Habilita o checkbox de seleção dos dados por período
				self.ui.checkBox_19.setChecked(True)					# Marca a checkbox de salvar dados do ultimo experimento

	########################## Conexão Porta Serial I/O ###################################
	def f_conecta(self):
		''' Evento ocorre quando o botao de conectar/desconectar é pressionado
		'''
		texto_botao = self.ui.pushButton.text()
		if ( texto_botao == 'Conectar' ):
			baudrate = int(self.ui.comboBox_2.currentText())			# Configurações da comunicação serial
			porta    = str(self.ui.comboBox.currentText())
			if ( porta > 1 and baudrate is not '' ):					# Caso os dados de conf. tenham sido selecionados
				try:
					global s
					s = serial.Serial(porta,baudrate,timeout=self.serial_timeout)  	# s -> objeto da com serial
					if s.isOpen():
						s.close()
						time.sleep(0.1)
					s.open()											# abre a comunicação
					self.enabled_disabled(True)							# altera as informações da ui para conectado
					self.ui.pushButton.setText('Desconectar')
					self.f_serial_read()
				except:
					print 'erro ao conectar'
		elif ( texto_botao == 'Desconectar'):							# idem ao desconectar
			self.enabled_disabled(False)
			try:
				s.close()												# fecha a conecção
			except:
				pass
			self.ui.pushButton.setText('Conectar')

	def f_envia_serial(self,dado):
		''' Método que envia uma string pela serial '''
		try:
			if s.isOpen():
				s.write(dado)
		except:
			print 'Erro ao enviar dado pela serial'
			pass

	def f_serial_read(self):
		try:
			texto = s.readline()										# Quando os dados do forno chegam com quebra de linha '\n'
			if texto is not '':											# Caso tenham dados na pilha
				texto = texto.rstrip('\r\n')							# remove os caracteres de fim de linha e carro.
				print 'got data: ', texto 								# Debug - Remover
				self.ui.textEdit.insertPlainText(texto + '\n')    		# Tempo para o delay
				tipo, d = verifica_dado(texto)							# Envia a string recebida para a função que trata os dados
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
						sensor_db.adiciona_dado(float(d[0]),float(d[1]),float(d[2]),
															float(d[3]),float(d[4]),float(d[5]),float(d[6]))
					else:
						sensor_db.adiciona_dado(float(d[0]),float(d[1]),
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
		except:
			print 'except - função f_serial_read'
		if s.isOpen() and self.ui.pushButton.text() == 'Desconectar':
			self.timer_serial.singleShot(self.tempo_update_serial,self.f_serial_read)
		# Retirar - debug
		# print self.esteira, self.resitencia01, self.resitencia02, self.resitencia03, 
		# print self.resitencia04, self.resitencia05, self.resitencia06

	def enabled_disabled(self,estado):
		''' Habilita ou desabilita as funções de controle da esteira (caso esteja ou não conectado ao forno) '''
		if ( not estado ):									# Caso esteja conectado:
			self.ui.horizontalSlider_r01.setValue(0)		# Volta os sliders para a opsição inicial
			self.ui.horizontalSlider_r02.setValue(0)
			self.ui.horizontalSlider_r04.setValue(0)
			self.ui.horizontalSlider_r03.setValue(0)
			self.ui.horizontalSlider_r06.setValue(0)
			self.ui.horizontalSlider_r05.setValue(0)
		self.ui.horizontalSlider.setEnabled(estado)			# Habilita/desabilita os controles
		self.ui.horizontalSlider_r01.setEnabled(estado)
		self.ui.horizontalSlider_r02.setEnabled(estado)
		self.ui.horizontalSlider_r04.setEnabled(estado)
		self.ui.horizontalSlider_r03.setEnabled(estado)
		self.ui.horizontalSlider_r06.setEnabled(estado)
		self.ui.horizontalSlider_r05.setEnabled(estado)
		self.ui.pushButton_2.setEnabled(estado)
		self.ui.pushButton_4.setEnabled(estado)
		self.ui.pushButton_6.setEnabled(estado)
		self.ui.pushButton_3.setEnabled(estado)
		self.ui.checkBox_9.setEnabled(estado)

	def f_add_portas_disponiveis(self):
		''' Método que altera os valores da combobox que mostra as portas disponíveis
		Os valores são retirados da função serial_ports '''
		escolha = self.ui.comboBox.currentIndex()			# Salva a porta atual escolhida
		self.ui.comboBox.blockSignals(True)					# Bloqueia sinais do PyQt na combobox para evitar que a função seja chamada novamente
		self.ui.comboBox.clear()							# Limpa os itens da combobox
		self.ui.comboBox.addItem('Atualiza')				# Adiciona uma opção de atualização das portas
		self.ui.comboBox.addItem('/')						# Adiciona um item para a raiz do sistema
		ports = serial_ports()								# chama a função que lista as portas
		for port in ports:
			self.ui.comboBox.addItem(port)					# Adiciona as portas a lista da combobox
		self.ui.comboBox.blockSignals(False)				# Desabitita o bloqueio de sinal do PyQt para que esta função possa ser chamada novamente no futuro
		self.ui.comboBox.setCurrentIndex(escolha)			# Volta para a porta escolhida

	def f_limpa_texto(self):
		''' Limpa as 3 textbox que informam os dados recebidos '''
		self.ui.textEdit.clear()
		self.ui.textEdit_2.clear()

	def f_envia_manual(self):
		''' Envia manualmente dados pela serial. A string contida na lineEdit é capturada e eniada '''
		texto = self.ui.lineEdit.text()						# captura o texto da lineEdit
		s.write(str(texto))									# envia a string pela serial
		s.write('\n')										# envia um caracter de fim de linha
		self.ui.lineEdit.setText('')						# Apaga a string enviada da lineEdit

	def f_auto_ST(self):
		''' Método recursivo.
		É chamado quando a checkbox de receber a temperatura dos sensores automaticamente é ativada.
		A função ativa uma thread do QT no modo singleShot após a quantidad de tempo escolhida no 
		spinBox da GUI. caso a checkbox continue ativada, a função se chamará novamente de forma recursiva
		até que a checkbox seja desabilitada ou a conecção seja desfeita.
		'''
		if self.ui.checkBox_9.isChecked():					# Executa apenas quando a checkbox está ativada
			self.f_atualiza_temp()							# Função que envia o pedido de temperatura para o microcontrolador
			tempo = 1000*self.ui.spinBox.value()			# *1000 pois o tempo da do método singleshot é em milissegundos
			self.timer_ST.singleShot(tempo,self.f_auto_ST)  # Thread recursiva única que se chamará.

	############################# Camera Raspberry pi ##################################################
	def f_tira_foto(self):
		''' Método que tira fotos com a picamera
		A foto tirada é mostrada no label_15, que foi alterado para mostrar imagens.
		As configurações de tempo de exposição e resolução são configuradas baseada nas 
		informações da GUI '''
		if sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):	# picamera apenas para raspberry (sistema unix)
			with picamera.PiCamera() as camera:										# Objeto para capturar e manipular as imagens
				valores = self.ui.comboBox_3.currentText().split('x')				# Pega os valores da resolução na combobox
				img_x, img_y = int(valores[0]), int(valores[1])						
				camera.resolution = (img_x, img_y)									# Resolução horizontal e vertical em função da combobox
				camera.start_preview()												# Inicia a câmera
				tempo_delay = int(self.ui.spinBox_2.value())/1000  					# valor do tempo para estabilizar a imagem
				time.sleep(tempo_delay)												# tempo para estabilizar a imagem
				camera.capture('teste.jpg')											# Captura a imagem
				print 'tirando foto'												# debug - retirar
		else:
			print 'Raspicam não disponível'   										# Quando estiver testando no windows # debug - retirar	
		self.ui.label_15.setScaledContents(True)									# Escala a imagem para mostrar na GUI
		self.ui.label_15.setPixmap(QtGui.QPixmap("teste.jpg"))						# Insere a imagem na tela
		print 'foto salva'

	def f_foto_update(self):
		''' Método recursivo. 
		É chamado quando a checkbox de autoupdate da imagem é ativada.
		A função ativa uma thread do QT no modo singleShot após a quantidad de tempo escolhida no 
		spinBox da GUI. caso a checkbox continue ativada, a função se chamará novamente de forma recursiva
		até que a checkbox seja desabilitada ou a conecção seja desfeita. '''
		if self.ui.checkBox_10.isChecked():											# Chama a Thread apenas se a checkbox estiver ativada
			self.tira_foto()														# Função que tira a foto
			tempo_delay = 1000*int(self.ui.spinBox_3.value())						# Tempo até ativar a thread para chamar a função novamente
			self.timer_foto.singleShot(tempo_delay,self.f_foto_update)				# Chama a Thread - modo singleshot

	############################## Gráfico da temperatura ##################################################
	def plotar(self):
		''' Função que plota o gráfico na GUI, utilizando a classe Matplotlib que sobrecarrega a o lable do qt (ver arquivo matplotlibwidgetFile.py) '''
		self.ui.widget.canvas.ax.clear()											# Limpa os eixos para plotar novamente
		if self.ui.checkBox_20.isChecked() and 										# Verifica se a checkbox do experimento atual esta marcada
			(self.experimento_nome is not 'Sem Nome'):								# Pega o nome do experimento e verifica se é 'Sem nome' ou não.
			d = sensor_db.retorna_dados(1,											# Pega os dados no bd
				experimento=str(self.experimento_nome))
		else:
			delta_t = self.ui.horizontalSlider_8.value()							# Pega os dados no bd
			d = sensor_db.retorna_dados(delta_t)
		if np.size(d[:,0]) > 1:														# Adiciona os valores ao eixo do gráfico caso a checkbox do respectivo sensor
			if self.ui.checkBox.isChecked():										# esteja marcada
				self.ui.widget.canvas.ax.plot(d[:,2],d[:,3])
			if self.ui.checkBox_2.isChecked():									    # Repete o procedimento para todos os sensores
				self.ui.widget.canvas.ax.plot(d[:,2],d[:,4])
			if self.ui.checkBox_4.isChecked():
				self.ui.widget.canvas.ax.plot(d[:,2],d[:,5])
			if self.ui.checkBox_3.isChecked():
				self.ui.widget.canvas.ax.plot(d[:,2],d[:,6])
			if self.ui.checkBox_6.isChecked():
				self.ui.widget.canvas.ax.plot(d[:,2],d[:,7])
			if self.ui.checkBox_5.isChecked():
				self.ui.widget.canvas.ax.plot(d[:,2],d[:,8])
			self.ui.widget.canvas.draw()

	def f_grafico_update(self):
		''' Método recursivo. 
		É chamado quando a checkbox de autoupdate do gráfico é ativada.
		A função ativa uma thread do QT no modo singleShot após a quantidad de tempo escolhida no 
		spinBox da GUI. caso a checkbox continue ativada, a função se chamará novamente de forma recursiva
		até que a checkbox seja desabilitada ou a conecção seja desfeita. '''
		if self.ui.checkBox_14.isChecked():											# Verifica se a checkbox de plotar o gráfico automaticamente está ativada
			self.plotar()															# Chama a função plotar 
			tempo_delay = 1000*int(self.ui.spinBox_4.value())						# Tempo até chamar a Thread
			self.timer_grafico.singleShot(tempo_delay,self.f_grafico_update)		# Chama a própria função de forma recursiva

	def f_tempo_grafico(self):
		'''
		Evento ocorre quando o slider abaixo do gráfico é pressinado.
		- Altera o tempo que será mostrado no gráfico (entre 1 e 99 min)
		em relação ao tempo actual.
		- Chama a função atualiza grafico.
		'''
		valor = self.ui.horizontalSlider_8.value()									# Pega o valor do intervalo de tempo do gráfico pelo slider
		texto = 'Intervalor de tempo = ' + str(valor) + ' min'						# Texto para ser mostrado ao lado do slider com o valor escolhido
		self.ui.label_9.setText(texto)												# Altera o texto do lable na GUI

	############################# Envio comandos para o forno ##################################################
	def f_teste_retorno(self):
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

		if not(int(self.ui.horizontalSlider_r02.value()) == self.resitencia02):		# Idem para resistências 2 a 6
			self.ui.horizontalSlider_r02.setValue(self.resitencia02)

		if not(int(self.ui.horizontalSlider_r04.value()) == self.resitencia04):
			self.ui.horizontalSlider_r04.setValue(self.resitencia04)

		if not(int(self.ui.horizontalSlider_r03.value()) == self.resitencia03):
			self.ui.horizontalSlider_r03.setValue(self.resitencia03)

		if not(int(self.ui.horizontalSlider_r06.value()) == self.resitencia06):
			self.ui.horizontalSlider_r06.setValue(self.resitencia06)

		if not(int(self.ui.horizontalSlider_r05.value()) == self.resitencia05):
			self.ui.horizontalSlider_r05.setValue(self.resitencia05)


	def f_atualiza_temp(self):
		''' Envia o pedid de atualização da temperatura (o mc retornará os dados da temperatura dos 6 sensores) '''
		s.write('ST\n')

	def f_resistencia01(self):
		''' Função que é chamada quando alguma mudança no controle da GUI relativa a resistência 1 ocorre
		A função verifica o estado da resistência 1 e envia para o mc caso seja necessário '''
		if (not self.ui.radioButton.isChecked()):									# Os dados são enviados apenas se o 'hold' não estiver pressionado
			valor = int(self.ui.horizontalSlider_r01.value())						# Pega o valor do slider relativo a resistência 1
			if valor == 100:														# envia o dado adequado em função do valor 0, 1..99, 100
				self.f_envia_serial(liga_02)
			elif valor == 0:
				self.f_envia_serial(desliga_02)
			elif valor > 0 and valor < 100:
				self.f_envia_serial('SP2' + str(valor) + '\n')
			QtCore.QTimer.singleShot(3000, self.f_teste_retorno)					# Chama a função teste_retorno em t segundos para verificar se o mc recebeu
																					# o comando e retornou a string esperada.

	def f_resistencia02(self):														# Idem para as resistências 2 a 6
		if (not self.ui.radioButton.isChecked()):
			valor = int(self.ui.horizontalSlider_r02.value())
			if valor == 100:
				self.f_envia_serial(liga_04)
			elif valor == 0:
				self.f_envia_serial(desliga_04)
			elif valor > 0 and valor < 100:
				self.f_envia_serial('SP3' + str(valor) + '\n')
			QtCore.QTimer.singleShot(3000, self.f_teste_retorno)	

	def f_resistencia03(self):
		if (not self.ui.radioButton.isChecked()):
			valor = int(self.ui.horizontalSlider_r03.value())
			if valor == 100:
				self.f_envia_serial(liga_06)
			elif valor == 0:
				self.f_envia_serial(desliga_06)
			elif valor > 0 and valor < 100:
				self.f_envia_serial('SP4' + str(valor) + '\n')
			QtCore.QTimer.singleShot(3000, self.f_teste_retorno)	

	def f_resistencia04(self):
		if (not self.ui.radioButton.isChecked()):
			valor = int(self.ui.horizontalSlider_r04.value())
			if valor == 100:
				self.f_envia_serial(liga_05)
			elif valor == 0:
				self.f_envia_serial(desliga_05)
			elif valor > 0 and valor < 100:
				self.f_envia_serial('SP5' + str(valor) + '\n')
			QtCore.QTimer.singleShot(3000, self.f_teste_retorno)	

	def f_resistencia05(self):
		if (not self.ui.radioButton.isChecked()):
			valor = int(self.ui.horizontalSlider_r05.value())
			if valor == 100:
				self.f_envia_serial(liga_03)
			elif valor == 0:
				self.f_envia_serial(desliga_03)
			elif valor > 0 and valor < 100:
				self.f_envia_serial('SP6' + str(valor) + '\n')
			QtCore.QTimer.singleShot(3000, self.f_teste_retorno)	

	def f_resistencia06(self):
		if (not self.ui.radioButton.isChecked()):
			valor = int(self.ui.horizontalSlider_r06.value())
			if valor == 100:
				self.f_envia_serial(liga_01)
			elif valor == 0:
				self.f_envia_serial(desliga_01)
			elif valor > 0 and valor < 100:
				self.f_envia_serial('SP7' + str(valor) + '\n')
			QtCore.QTimer.singleShot(3000, self.f_teste_retorno)

	def f_hold(self):
		''' Função que é chamada quando o estado do checkbox 'hold' é alterado.
		Caso o hold seja deslicado. São chamadas as funções de todas as esteiras
		para enviar os dados caso haja diferença entre o estado da variável e do
		slider.'''
		if ( self.ui.radioButton.isChecked() == False ):							# Caso o 'hold' tenha sido desligado:
			self.f_resistencia01()													# Chama a função da resistência 1
			time.sleep(0.1)															# Espera um pequeno tempo por precaução de sobrecarregar a serial
			self.f_resistencia02()													# Idem para as resistências 2 .. 6
			time.sleep(0.1)
			self.f_resistencia03()
			time.sleep(0.1)
			self.f_resistencia04()
			time.sleep(0.1)
			self.f_resistencia05()
			time.sleep(0.1)
			self.f_resistencia06()

	def f_esteira(self):
		''' Função que é acionada ao alterar o valor do slider da esteira. Envia para o mc o comando adequado '''
		valor = self.ui.horizontalSlider.value()
		if valor > 0:																# SH'xy' para frente (valores maiores que zero)
			s.write('SH' + str(valor) + '\n')
		elif valor < 0:																# SA'xy' para tras (valores menores que zero)
			s.write('SA' + str(abs(valor)) + '\n')
		else:
			s.write('SD\n')															# Parar a esteira (0)

	def f_para_esteira(self):
		''' Função de parada total da esteira. Envia o comando para o mc e altera o valor do slider. '''
		self.ui.horizontalSlider.setValue(0)
		s.write('SD\n')

	def f_emergencia(self):
		''' Função de Emergência. Para a esteira e desliga todas as resistências ''' 
		s.write('SD\n')
		for i in range(2,8):
			s.write('S' + str(i) + '2\n')
			time.sleep(0.1)
		QtCore.QTimer.singleShot(4000, self.f_teste_retorno)

if __name__ == "__main__":														# Executa quando o programa é executado diretamente
	app = QtGui.QApplication(sys.argv)											
	window = Main()
	window.show()
	sys.exit(app.exec_())










