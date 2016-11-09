# -*- coding: latin-1 -*-
from __future__ import division
from PyQt4 import QtGui
from functools import partial
import sys, time
try:
	import picamera
except:
	pass

def tira_foto(self):
	'''
	Método que tira fotos com a picamera
	A foto tirada é mostrada no label_camera, que foi alterado para mostrar imagens.
	As configurações de tempo de exposição e resolução são configuradas baseada
	nas informações da GUI
	'''
	# picamera apenas para raspberry (sistema unix)
	if sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
		# Objeto para capturar e manipular as imagens
		with picamera.PiCamera() as camera:
			# Pega os valores da resolução na combobox
			valores = self.ui.comboBox_cameraResolucao.currentText().split('x')
			img_x, img_y = int(valores[0]), int(valores[1])
			camera.resolution = (img_x, img_y)
			camera.start_preview()
			# valor do tempo para estabilizar a imagem
			tempo_delay = int(self.ui.spinBox_cameraDelay.value())/1000
			# tempo para estabilizar a imagem
			time.sleep(tempo_delay)
			camera.capture('teste.jpg')
			self.alerta_toolbar('tirando foto')
	else:
		# Quando estiver testando no windows
		self.alerta_toolbar('Raspicam nao disponivel')
	# Escala a imagem para mostrar na GUI
	self.ui.label_camera.setScaledContents(True)
	# Insere a imagem na tela
	self.ui.label_camera.setPixmap(QtGui.QPixmap("teste.jpg"))
	self.alerta_toolbar('foto salva')

def foto_update(self):
	'''
	Método recursivo.
	É chamado quando a checkbox de autoupdate da imagem é ativada.
	A função ativa uma thread do QT no modo singleShot após a quantidad de tempo
	escolhida no spinBox da GUI. caso a checkbox continue ativada, a função se
	chamará novamente de forma recursiva até que a checkbox seja desabilitada
	ou a conecção seja desfeita.
	'''
	# Chama a Thread apenas se a checkbox estiver ativada
	if self.ui.checkBox_cameraAutoUpdate.isChecked():
		tira_foto(self)
		tempo_delay = 1000*int(self.ui.spinBox_cameraRefresh.value())
		self.timer_foto.singleShot(tempo_delay,partial(foto_update,self))
