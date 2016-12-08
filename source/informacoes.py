# -*- coding: latin-1 -*-
import os, sys, serial, cv2
import simulacao.alimento, simulacao.forno1d

def local_parent():
	caminho_source = os.path.dirname(os.path.realpath(__file__))
	source_parent = str(os.path.abspath(os.path.join(caminho_source, os.pardir)))
	source_parent = source_parent.replace('\\','/')
	return str(source_parent)

class status:
	def __init__(self):
		self.contador = 0
		self.simForno = False
		self.simAlimento = False

	def incrementaContador(self):
		self.contador += 1

	def forno(self, tela, T):
		if self.contador % tela.ui.spinBox_nLeiturasForno.value() == 0 \
		and tela.ui.checkBox_calcPerfil.isChecked():
			Ta = 30
			T1 , T2, T3 = T[0], T[1], T[2]
			print T1 , T2, T3
			R1, R2, R3 = tela.valor_resistencia01, tela.valor_resistencia02, tela.valor_resistencia03
			T = simulacao.forno1d.calcula_perfil(Ta, T1 , T2, T3, R1, R2, R3)
			simulacao.forno1d.display_perfilForno(tela,T)

	def alimento(self, tela, T):
		if self.contador % tela.ui.spinBox_nLeiturasSim.value() == 0 \
		and tela.ui.checkBox_calcSim.isChecked():
			simulacao.alimento.evolui_tempo(10,T)
			simulacao.alimento.display_alimento(tela,T)
