# -*- coding: latin-1 -*-
import os, sys, serial, cv2
import simulacao.alimento, simulacao.forno1d
import numpy as np

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
		self.T_ambiente = 28
		self.T_alimento = self.T0_alimento()
		self.dt_alimento = 10

	def T0_alimento(self, T=None):
		if T:
			Ta = T
		else:
			Ta = self.T_ambiente
		return np.ones((30,60))*Ta

	def incrementaContador(self):
		self.contador += 1

	def forno(self, tela, T):
		if self.contador % tela.ui.spinBox_nLeiturasForno.value() == 0 \
		and tela.ui.checkBox_calcPerfil.isChecked():
			T1 , T2, T3 = T[0], T[1], T[2]
			R1, R2, R3 = tela.valor_resistencia01, tela.valor_resistencia02, tela.valor_resistencia03
			T = simulacao.forno1d.calcula_perfil(self.T_ambiente, T1 , T2, T3, R1, R2, R3)
			simulacao.forno1d.display_perfilForno(tela,T)
