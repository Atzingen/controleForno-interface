# -*- coding: latin-1 -*-
import serial
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
