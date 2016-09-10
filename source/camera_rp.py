# -*- coding: latin-1 -*-
from __future__ import division
from app_run import Ui_MainWindow
from PyQt4 import QtGui, QtCore
from functools import partial
import sys, time
try:
	import picamera
except:
	pass

def tira_foto(self):
	''' M�todo que tira fotos com a picamera
	A foto tirada � mostrada no label_15, que foi alterado para mostrar imagens.
	As configura��es de tempo de exposi��o e resolu��o s�o configuradas baseada nas
	informa��es da GUI '''
	if sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):	# picamera apenas para raspberry (sistema unix)
		with picamera.PiCamera() as camera:										# Objeto para capturar e manipular as imagens
			valores = self.ui.comboBox_3.currentText().split('x')				# Pega os valores da resolu��o na combobox
			img_x, img_y = int(valores[0]), int(valores[1])
			camera.resolution = (img_x, img_y)									# Resolu��o horizontal e vertical em fun��o da combobox
			camera.start_preview()												# Inicia a c�mera
			tempo_delay = int(self.ui.spinBox_2.value())/1000  					# valor do tempo para estabilizar a imagem
			time.sleep(tempo_delay)												# tempo para estabilizar a imagem
			camera.capture('teste.jpg')											# Captura a imagem
			self.alerta_toolbar('tirando foto')									# debug - retirar
	else:
		self.alerta_toolbar('Raspicam n�o dispon�vel')   						# Quando estiver testando no windows # debug - retirar
	self.ui.label_15.setScaledContents(True)									# Escala a imagem para mostrar na GUI
	self.ui.label_15.setPixmap(QtGui.QPixmap("teste.jpg"))						# Insere a imagem na tela
	self.alerta_toolbar('foto salva')

def foto_update(self):
	''' M�todo recursivo.
	� chamado quando a checkbox de autoupdate da imagem � ativada.
	A fun��o ativa uma thread do QT no modo singleShot ap�s a quantidad de tempo escolhida no
	spinBox da GUI. caso a checkbox continue ativada, a fun��o se chamar� novamente de forma recursiva
	at� que a checkbox seja desabilitada ou a conec��o seja desfeita. '''
	if self.ui.checkBox_10.isChecked():											# Chama a Thread apenas se a checkbox estiver ativada
		tira_foto(self)															# Fun��o que tira a foto
		tempo_delay = 1000*int(self.ui.spinBox_3.value())						# Tempo at� ativar a thread para chamar a fun��o novamente
		self.timer_foto.singleShot(tempo_delay,partial(foto_update,self))		# Chama a Thread - modo singleshot
