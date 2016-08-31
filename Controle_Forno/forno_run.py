# -*- coding: latin-1 -*-
from __future__ import division
# Minhas Funções e Objetos
from forno_gui import Ui_MainWindow
import sensor_db
# Bibliotecas
from PyQt4 import QtGui, QtCore
import sqlite3
import sys, os, serial, glob, thread, time, datetime
from threading import Thread
import numpy as np
import PIL, scipy
from PIL import Image, ImageQt
try:
	import picamera
except:
	pass

############ Comandos do forno ################################
ubee       = '0010'		# primeiros 4 dados que chegam (código do ubee)
liga_02    = 'S21\n'
desliga_02 = 'S22\n'
liga_04    = 'S31\n'
desliga_04 = 'S32\n'
liga_06    = 'S41\n'
desliga_06 = 'S42\n'
liga_05    = 'S51\n'
desliga_05 = 'S52\n'
liga_03    = 'S61\n'
desliga_03 = 'S62\n'
liga_01    = 'S71\n'
desliga_01 = 'S72\n'

def verifica_dado(dado):
	try:
		print len(dado), dado[0], dado[1:-1].isdigit()
		if dado[0] == 'S' and len(dado) > 28 and dado[1:29].isdigit() and dado[1:5].isdigit():
			return True
		else:
			return False
	except:
		return False

def converte_dado(dado):	
	try:
		dado = dado.strip('S')
		d = np.zeros([7,1])
		d[0] = time.time() 			# tempo_coleta
		d[3] = int(dado[24:28])  	# Sensor 3  	
		d[1] = int(dado[4:8])		# Sensor 1
		d[2] = int(dado[8:12])		# Sensor 2
		d[4] = int(dado[12:16])		# Sensor 4
		d[6] = int(dado[16:20])		# Sensor 6
		d[5] = int(dado[20:24])		# Sensor 5
		print d
		return d
	except:
		d = 'erro'
		print d
		return d

def serial_ports():
    """Lists serial ports

    :raises EnvironmentError:
        On unsupported or unknown platforms
    :returns:
        A list of available serial ports
    """
    if sys.platform.startswith('win'):
        ports = ['COM' + str(i + 1) for i in range(256)]

    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this is to exclude your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')

    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')

    else:
        raise EnvironmentError('Unsupported platform')
    return ports

class Main(QtGui.QMainWindow):
	"""
	Classe principal da tela.
	a ui usa as propriedades da classe Ui_MainWindow, 
	feita com o Qt Designer, e mantida separadamente no 
	arquivo gui_forno_gui, compilada com o pyuic4
	"""
	def __init__(self):
		# Iniciando a ui
		QtGui.QMainWindow.__init__(self)
		self.ui = Ui_MainWindow()   # Qtdesigner
		self.ui.setupUi(self)
		####### Variáveis de configuração #####################################
		self.tempo_update_serial = 431 	  # tempo em milisegundos
		self.serial_timeout = False
		####### Banco de dados ################################################
		tempo_coleta = time.time()
		sensor_db.cria_tabela()
		#####  QTimers ########################################################
		self.timer_foto    = QtCore.QTimer()
		self.timer_grafico = QtCore.QTimer()
		self.timer_serial  = QtCore.QTimer()
		self.timer_ST	   = QtCore.QTimer()
		#####  testes #########################################################
		
		#######  Atualizando os valores das portas no inicio do programa #####
		self.f_add_portas_disponiveis()
		####### Connexões #####################################################
		# Slider do tempo de intervalo grafico
		self.ui.horizontalSlider_8.sliderReleased.connect(self.f_tempo_grafico)
		self.ui.pushButton.pressed.connect(self.f_conecta)
		self.ui.horizontalSlider_2.valueChanged.connect(self.f_resistencia01)
		self.ui.horizontalSlider_3.valueChanged.connect(self.f_resistencia02)
		self.ui.horizontalSlider_4.valueChanged.connect(self.f_resistencia04)
		self.ui.horizontalSlider_5.valueChanged.connect(self.f_resistencia03)
		self.ui.horizontalSlider_7.valueChanged.connect(self.f_resistencia05)
		self.ui.horizontalSlider_6.valueChanged.connect(self.f_resistencia06)
		self.ui.pushButton_3.pressed.connect(self.f_emergencia)
		self.ui.horizontalSlider.sliderReleased.connect(self.f_esteira)
		self.ui.pushButton_4.pressed.connect(self.f_para_esteira)
		self.ui.pushButton_2.pressed.connect(self.f_atualiza_temp)
		self.ui.pushButton_7.pressed.connect(self.f_limpa_texto)
		self.ui.pushButton_6.pressed.connect(self.f_envia_manual)
		self.ui.comboBox.activated.connect(self.f_add_portas_disponiveis)
		self.ui.radioButton.clicked.connect(self.f_hold)
		self.ui.pushButton_5.pressed.connect(self.f_botoa_foto)
		self.ui.checkBox_10.stateChanged.connect(self.f_foto_update)
		self.ui.checkBox_14.stateChanged.connect(self.f_grafico_update)
		self.ui.checkBox_9.stateChanged.connect(self.f_auto_ST)

	def f_teste(self):
		print 'teste'

	########################## Conexão Porta Serial I/O ###################################
	def f_conecta(self):
		'''
		Evento ocorre quando o botao de conectar/desconectar é pressionado
		'''
		texto_botao = self.ui.pushButton.text()
		if ( texto_botao == 'Conectar' ):
			baudrate = int(self.ui.comboBox_2.currentText())
			porta    = str(self.ui.comboBox.currentText())
			if ( porta > 1 and baudrate is not '' ):
				try:
					global s
					s = serial.Serial(porta,baudrate,timeout=self.serial_timeout)
					if s.isOpen():
						s.close()
						time.sleep(0.1)
					s.open()
					self.enabled_disabled(True)
					self.ui.pushButton.setText('Desconectar')
					self.f_serial_read()
				except:
					print 'erro ao conectar'
		elif ( texto_botao == 'Desconectar'):
			self.enabled_disabled(False)
			try:
				s.close()
			except:
				pass
			self.ui.pushButton.setText('Conectar')

	def f_serial_read(self):
		try:
			texto = s.read(30)				# Quandidade fixa de bytes enviados pelo forno
			#texto = s.readline()			# Quando os dados do forno chegam com quebra de linha '\n'
			if texto is not '':
				print 'got data'	
				self.ui.textEdit.insertPlainText(texto)    		# Tempo para o delay
				if verifica_dado(texto):
					d = converte_dado(texto)
					if not 'erro' in d:
						self.ui.lcdNumber.display(d[1])
						self.ui.lcdNumber_2.display(d[2])
						self.ui.lcdNumber_3.display(d[3])
						self.ui.lcdNumber_4.display(d[4])
						self.ui.lcdNumber_5.display(d[5])
						self.ui.lcdNumber_6.display(d[6])
						data = str(["%i" % x for x in d])
						data = data + '\n'
						self.ui.textEdit_2.insertPlainText(data)
						sensor_db.adiciona_dado(float(d[0]),int(d[1]),int(d[2]),int(d[3]),int(d[4]),int(d[5]),int(d[6]))
		except:
			print 'erro ao ler dados porta serial'
		if s.isOpen() and self.ui.pushButton.text() == 'Desconectar':
			self.timer_serial.singleShot(self.tempo_update_serial,self.f_serial_read)

	def enabled_disabled(self,estado):
		if ( not estado ):
			self.ui.horizontalSlider_2.setValue(0)
			self.ui.horizontalSlider_3.setValue(0)
			self.ui.horizontalSlider_4.setValue(0)
			self.ui.horizontalSlider_5.setValue(0)
			self.ui.horizontalSlider_6.setValue(0)
			self.ui.horizontalSlider_7.setValue(0)
		self.ui.horizontalSlider.setEnabled(estado)
		self.ui.horizontalSlider_2.setEnabled(estado)
		self.ui.horizontalSlider_3.setEnabled(estado)
		self.ui.horizontalSlider_4.setEnabled(estado)
		self.ui.horizontalSlider_5.setEnabled(estado)
		self.ui.horizontalSlider_6.setEnabled(estado)
		self.ui.horizontalSlider_7.setEnabled(estado)
		self.ui.pushButton_2.setEnabled(estado)
		self.ui.pushButton_4.setEnabled(estado)
		self.ui.pushButton_6.setEnabled(estado)
		self.ui.pushButton_3.setEnabled(estado)
		self.ui.checkBox_9.setEnabled(estado)

	def f_add_portas_disponiveis(self):
		print 'teste'
		escolha = self.ui.comboBox.currentIndex()
		self.ui.comboBox.blockSignals(True)
		self.ui.comboBox.clear()
		self.ui.comboBox.addItem('Atualiza')
		self.ui.comboBox.addItem('/')
		ports = serial_ports()
		for port in ports:
			self.ui.comboBox.addItem(port)
		self.ui.comboBox.blockSignals(False)
		self.ui.comboBox.setCurrentIndex(escolha)

	def f_limpa_texto(self):
		self.ui.textEdit.clear()
		self.ui.textEdit_2.clear()

	def f_envia_manual(self):
		texto = self.ui.lineEdit.text()
		print texto
		s.write(str(texto))
		s.write('\n')
		self.ui.lineEdit.setText('')

	def f_auto_ST(self):
		# pede temperatura
		if self.ui.checkBox_9.isChecked():
			self.f_atualiza_temp()
			tempo = 1000*self.ui.spinBox.value()
			self.timer_ST.singleShot(tempo,self.f_auto_ST)

	############################# Camera Raspberry pi ##################################################
	def tira_foto(self):
		if sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
			with picamera.PiCamera() as camera:
				valores = self.ui.comboBox_3.currentText().split('x')
				img_x, img_y = int(valores[0]), int(valores[1])
				camera.resolution = (img_x, img_y)
				camera.start_preview()
				# Camera warm-up time
				tempo_delay = int(self.ui.spinBox_2.value())/1000
				print tempo_delay, img_x, img_y
				time.sleep(tempo_delay)
				camera.capture('teste.jpg')
				print 'tirando foto'
		else:
			print 'Raspicam não disponível'   # Quando estiver testando no windows
		#PilImage = Image.open('teste.jpg')
		#QtImage1 = ImageQt.ImageQt(PilImage)
		#QtImage2 = QtImage1.copy()
		#pixmap = QtGui.QPixmap.fromImage(QtImage2)		
		self.ui.label_15.setScaledContents(True)
		self.ui.label_15.setPixmap(QtGui.QPixmap("teste.jpg"))
		print 'foto salva'

	def f_foto_update(self):
		if self.ui.checkBox_10.isChecked():
			self.tira_foto()
			tempo_delay = 1000*int(self.ui.spinBox_3.value())
			self.timer_foto.singleShot(tempo_delay,self.f_foto_update)

	def f_botoa_foto(self):
		print 'botao tirar foto'
		self.tira_foto()

	############################## Gráfico da temperatura ##################################################
	def plotar(self):
		self.ui.widget.canvas.ax.clear()
		delta_t = self.ui.horizontalSlider_8.value()
		print 'delta_t', delta_t
		d = sensor_db.retorna_dados(delta_t)
		if np.size(d[:,0]) > 1:
			if self.ui.checkBox.isChecked():
				self.ui.widget.canvas.ax.plot(d[:,2],d[:,3])
			if self.ui.checkBox_2.isChecked():
				self.ui.widget.canvas.ax.plot(d[:,2],d[:,4])
			print self.ui.checkBox_4.isChecked()
			if self.ui.checkBox_4.isChecked():
				self.ui.widget.canvas.ax.plot(d[:,2],d[:,5])
			if self.ui.checkBox_3.isChecked():
				self.ui.widget.canvas.ax.plot(d[:,2],d[:,6])
			if self.ui.checkBox_6.isChecked():
				self.ui.widget.canvas.ax.plot(d[:,2],d[:,7])
			if self.ui.checkBox_5.isChecked():
				self.ui.widget.canvas.ax.plot(d[:,2],d[:,8])
			#if window.ui.checkBox_7.isChecked():
			#	window.ui.widget.canvas.ax.plot(d[:,2],d[9])
			self.ui.widget.canvas.draw()

	def f_grafico_update(self):
		if self.ui.checkBox_14.isChecked():
			self.plotar()
			tempo_delay = 1000*int(self.ui.spinBox_4.value())
			self.timer_grafico.singleShot(tempo_delay,self.f_grafico_update)

	def f_tempo_grafico(self):
		'''
		Evento ocorre quando o slider abaixo do gráfico é pressinado.
		- Altera o tempo que será mostrado no gráfico (entre 1 e 99 min)
		em relação ao tempo actual.
		- Chama a função atualiza grafico.
		'''
		valor = self.ui.horizontalSlider_8.value()
		texto = 'Intervalor de tempo = ' + str(valor) + ' min'
		self.ui.label_9.setText(texto)
		# Chamar a função atualiza grafico

	############################# Envio comandos para o forno ##################################################
	def f_atualiza_temp(self):
		s.write('ST\n')

	def f_resistencia06(self):			# Resistência 06
		if ( self.ui.horizontalSlider_6.value() == 1 ):
			if ( self.ui.radioButton.isChecked() == False ):
				try:
					s.write(liga_01)
					self.ui.progressBar_2.setValue(100) 
				except:
					pass
		else:
			if ( self.ui.radioButton.isChecked() == False ):
				try:
					s.write(desliga_01)
					self.ui.progressBar_2.setValue(0) 
				except:
					pass

	def f_resistencia05(self):
		if ( self.ui.horizontalSlider_7.value() == 1 ):
			if ( self.ui.radioButton.isChecked() == False ):
				try:
					s.write(liga_03)
					self.ui.progressBar_3.setValue(100) 
				except:
					pass
		else:
			if ( self.ui.radioButton.isChecked() == False ):
				try:
					s.write(desliga_03)
					self.ui.progressBar_3.setValue(0) 
				except:
					pass		

	def f_resistencia04(self):
		if ( self.ui.horizontalSlider_4.value() == 1 ):
			if ( self.ui.radioButton.isChecked() == False ):
				try:
					s.write(liga_05)
					self.ui.progressBar_5.setValue(100) 
				except:
					pass
		else:
			if ( self.ui.radioButton.isChecked() == False ):
				try:
					s.write(desliga_05)
					self.ui.progressBar_5.setValue(0) 
				except:
					pass

	def f_resistencia03(self):
		if ( self.ui.horizontalSlider_5.value() == 1 ):
			if ( self.ui.radioButton.isChecked() == False ):
				try:
					s.write(liga_06)
					self.ui.progressBar_4.setValue(100) 
				except:
					pass
		else:
			if ( self.ui.radioButton.isChecked() == False ):
				try:
					s.write(desliga_06)
					self.ui.progressBar_4.setValue(0) 
				except:
					pass

	def f_resistencia02(self):
		if ( self.ui.horizontalSlider_3.value() == 1 ):
			if ( self.ui.radioButton.isChecked() == False ):
				try:
					s.write(liga_04)
					self.ui.progressBar_7.setValue(100) 
				except:
					pass
		else:
			if ( self.ui.radioButton.isChecked() == False ):
				try:
					s.write(desliga_04)
					self.ui.progressBar_7.setValue(0) 
				except:
					pass

	def f_resistencia01(self):
		if ( self.ui.horizontalSlider_2.value() == 1 ):
			if ( self.ui.radioButton.isChecked() == False ):
				try:
					s.write(liga_02)
					self.ui.progressBar_6.setValue(100) 
				except:
					pass
		else:
			if ( self.ui.radioButton.isChecked() == False ):
				try:
					s.write(desliga_02)
					self.ui.progressBar_6.setValue(0) 
				except:
					pass

	def f_hold(self):
		if ( self.ui.radioButton.isChecked() == False ):
			# slider 2 - progress 6 S21-S22
			if ( self.ui.horizontalSlider_2.value() == 1 ):
				try:
					s.write(liga_02)
					self.ui.progressBar_6.setValue(100) 
				except:
					pass
			else:
				try:
					s.write(desliga_02)
					self.ui.progressBar_6.setValue(0) 
				except:
					pass	
			# slider 3 - progress 7 S31-S32
			if ( self.ui.horizontalSlider_3.value() == 1 ):
				try:
					s.write(liga_04)
					self.ui.progressBar_7.setValue(100) 
				except:
					pass
			else:
				try:
					s.write(desliga_04)
					self.ui.progressBar_7.setValue(0) 
				except:
					pass				
			# slider 5 - progress 4 S41-S42
			if ( self.ui.horizontalSlider_5.value() == 1 ):
				try:
					s.write(liga_06)
					self.ui.progressBar_4.setValue(100) 
				except:
					pass
			else:
				try:
					s.write(desliga_06)
					self.ui.progressBar_4.setValue(0) 
				except:
					pass	
			# slider 4 - progress 5 S51-S52
			if ( self.ui.horizontalSlider_4.value() == 1 ):
				try:
					s.write(liga_05)
					self.ui.progressBar_5.setValue(100) 
				except:
					pass
			else:
				try:
					s.write(desliga_05)
					self.ui.progressBar_5.setValue(0) 
				except:
					pass	
			# slider 7 - progress 3 - S61-S62
			if ( self.ui.horizontalSlider_7.value() == 1 ):
				try:
					s.write(liga_03)
					self.ui.progressBar_3.setValue(100) 
				except:
					pass
			else:
				try:
					s.write(desliga_03)
					self.ui.progressBar_3.setValue(0) 
				except:
					pass	
			# slider 6 - progress 2 S71-S72
			if ( self.ui.horizontalSlider_6.value() == 1 ):
				try:
					s.write(liga_01)
					self.ui.progressBar_2.setValue(100) 
				except:
					pass
			else:
				try:
					s.write(desliga_01)
					self.ui.progressBar_2.setValue(0) 
				except:
					pass	

	def f_esteira(self):
		valor = self.ui.horizontalSlider.value()
		if valor > 0:
			s.write('SH' + str(valor) + '\n')
		elif valor < 0:
			s.write('SA' + str(abs(valor)) + '\n')
		else:
			s.write('SD\n')

	def f_para_esteira(self):
		self.ui.horizontalSlider.setValue(0)
		s.write('SD\n')

	def f_emergencia(self):
		s.write('SD\n')
		for i in range(2,8):
			s.write('S' + str(i) + '2\n')
			time.sleep(0.1)
		self.ui.horizontalSlider.setValue(0)
		self.ui.horizontalSlider_2.setValue(0)
		self.ui.horizontalSlider_3.setValue(0)
		self.ui.horizontalSlider_4.setValue(0)
		self.ui.horizontalSlider_5.setValue(0)
		self.ui.horizontalSlider_6.setValue(0)
		self.ui.horizontalSlider_7.setValue(0)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())










