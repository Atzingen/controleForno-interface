# -*- coding: latin-1 -*-
import os, sys, serial, cv2

global forno
forno = cv2.imread('imagens/forno-pre.jpg')


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

def monta_caminho_banco():
    nome_arquivo_db = 'forno_data.db'
    caminho, barra = local_parent()
    return caminho + "bancoDados" + barra +  nome_arquivo_db

global caminho_banco
caminho_banco = monta_caminho_banco()
