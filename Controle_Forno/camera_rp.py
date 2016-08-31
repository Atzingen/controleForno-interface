# -*- coding: latin-1 -*-
from __future__ import division
from forno_run import Ui_MainWindow
from PyQt4 import QtGui, QtCore 
from functools import partial
import sys, time
try:
	import picamera
except:
	pass

def tira_foto(self):
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
			self.alerta_toolbar('tirando foto')									# debug - retirar
	else:
		self.alerta_toolbar('Raspicam não disponível')   						# Quando estiver testando no windows # debug - retirar	
	self.ui.label_15.setScaledContents(True)									# Escala a imagem para mostrar na GUI
	self.ui.label_15.setPixmap(QtGui.QPixmap("teste.jpg"))						# Insere a imagem na tela
	self.alerta_toolbar('foto salva')

def foto_update(self):
	''' Método recursivo. 
	É chamado quando a checkbox de autoupdate da imagem é ativada.
	A função ativa uma thread do QT no modo singleShot após a quantidad de tempo escolhida no 
	spinBox da GUI. caso a checkbox continue ativada, a função se chamará novamente de forma recursiva
	até que a checkbox seja desabilitada ou a conecção seja desfeita. '''
	if self.ui.checkBox_10.isChecked():											# Chama a Thread apenas se a checkbox estiver ativada
		tira_foto(self)															# Função que tira a foto
		tempo_delay = 1000*int(self.ui.spinBox_3.value())						# Tempo até ativar a thread para chamar a função novamente
		self.timer_foto.singleShot(tempo_delay,partial(foto_update,self))		# Chama a Thread - modo singleshot