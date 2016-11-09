# -*- coding: latin-1 -*-
import os, sys, serial

def local_parent():
	#caminho_source = os.getcwd()
	caminho_source = os.path.dirname(os.path.realpath(__file__))
	source_parent = os.path.abspath(os.path.join(caminho_source, os.pardir))
	if sys.platform.startswith('win'):
		barra = '\\'
	else:
		barra = '/'
	source_parent += barra
	return str(source_parent), barra

def caminho_banco():
    nome_arquivo_db = 'forno_data.db'
    caminho, barra = local_parent()
    return caminho + "bancoDados" + barra +  nome_arquivo_db

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

global s  				# objeto da comunição serial
s = serial.Serial()

global tempo_pwm
tempo_pwm = 30

global texto
texto = ""

global valor_resistencia01
global valor_resistencia02
global valor_resistencia03
global valor_resistencia04
global valor_resistencia05
global valor_resistencia06
global valor_esteira

valor_resistencia01 = 0
valor_resistencia02 = 0
valor_resistencia03 = 0
valor_resistencia04 = 0
valor_resistencia05 = 0
valor_resistencia06 = 0
valor_esteira = 0
