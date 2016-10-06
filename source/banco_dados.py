# -*- coding: latin-1 -*-
import sys, os
import sqlite3
import datetime
import scipy
from PyQt4 import QtGui

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

nome_arquivo_db = 'forno_data.db'
caminho, barra = local_parent()
caminho_banco = caminho + "bancoDados" + barra +  nome_arquivo_db

def cria_tabela_config():
	try:
		db = sqlite3.connect(caminho_banco)
		cursor = db.cursor()
		cursor.execute('''CREATE TABLE IF NOT EXISTS config
		(id INTEGER PRIMARY KEY, calibracao_selecionada TEXT UNIQUE)''')
		db.commit()
		db.close()
		if cursor.rowcount > 0:
			return True
		else:
			return False
	except:
		return False

def retorna_dados_config():
	try:
		db = sqlite3.connect(caminho_banco)
		cursor = db.cursor()
		cursor.execute('''SELECT calibracao_selecionada FROM config''')
		row = cursor.fetchall()
		db.commit()
		db.close()
		if row:
			return row[0][0]
		else:
			return None
	except:
		return None

def salva_config_calibracao(nome):
	try:
		db = sqlite3.connect(caminho_banco)
		cursor = db.cursor()
		cursor.execute('''UPDATE config SET calibracao_selecionada=? WHERE id=?''',(nome,1))
		db.commit()
		db.close()
		if cursor.rowcount > 0:
			return True
		else:
			return False
	except:
		return None

def cria_tabela_calibracao():
	try:
		db = sqlite3.connect(caminho_banco)
		cursor = db.cursor()
		cursor.execute('''CREATE TABLE IF NOT EXISTS calibracao
		(id INTEGER PRIMARY KEY,nome TEXT,s1_A REAL,s2_A REAL,s3_A REAL,s4_A REAL,s5_A REAL,s6_A REAL,
								s1_B REAL,s2_B REAL,s3_B REAL,s4_B REAL,s5_B REAL,s6_B REAL)''')
		db.commit()
		db.close()
		if cursor.rowcount > 0:
			return True
		else:
			return False
	except:
		return None

def deleta_calibracao_bd(nome):
	try:
		print "bd", nome
		db = sqlite3.connect(caminho_banco)
		cursor = db.cursor()
		cursor.execute('''SELECT id FROM calibracao WHERE nome = ?''',(nome,))
		numero_ids = cursor.fetchall()
		for numero_id in numero_ids:
			cursor.execute("DELETE FROM calibracao WHERE id = ?",(numero_id[0],))
		db.commit()
		db.close()
		if cursor.rowcount > 0:
			return True
		else:
			return False
	except:
		return False

def insere_calibracao(nome,s1_A,s2_A,s3_A,s4_A,s5_A,s6_A,
					s1_B,s2_B,s3_B,s4_B,s5_B,s6_B):
	try:
		db = sqlite3.connect(caminho_banco)
		cursor = db.cursor()
		cursor.execute('''INSERT INTO calibracao (nome,s1_A,s2_A,s3_A,s4_A,s5_A,s6_A,
						s1_B,s2_B,s3_B,s4_B,s5_B,s6_B) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)''',
						(nome,s1_A,s2_A,s3_A,s4_A,s5_A,s6_A,s1_B,s2_B,s3_B,s4_B,s5_B,s6_B))
		db.commit()
		db.close()
		if cursor.rowcount > 0:
			return True
		else:
			return False
	except:
		return False

def nomes_calibracao():
	try:
		db = sqlite3.connect(caminho_banco)
		cursor = db.cursor()
		cursor.execute('''SELECT nome FROM calibracao''')
		row = cursor.fetchall()
		db.close()
		if row:
			return row
		else:
			return None
	except:
		return None

def leitura_calibracao(nome):
	try:
		db = sqlite3.connect(caminho_banco)
		cursor = db.cursor()
		cursor.execute('''SELECT * FROM calibracao WHERE nome = ?''',(nome,))
		row = cursor.fetchone()
		db.close()
		if row:
			return row
		else:
			return [1,"sem calibracao",0,0,0,0,0,0,1,1,1,1,1,1]
	except:
		return None

def cria_tabela():
	'''
	Cira a tabela 'dados_forno' caso ela não exista, criando o esquema e as
	colunas no formato correto. O nome do arquivo do banco de dados é
	caminho_banco e esta na mesma pasta /bandoDados.
	'''
	try:
		createDB = sqlite3.connect(caminho_banco)
		queryCurs = createDB.cursor()
		queryCurs.execute('''CREATE TABLE IF NOT EXISTS dados_forno
		(id INTEGER PRIMARY KEY,t_abs TIMESTAMP DEFAULT (DATETIME('now')),t_0 REAL,
		s1 REAL, s2 REAL, s3 REAL, s4 REAL, s5 REAL, s6 REAL,experimento TEXT,
		calibracao TEXT, atuadores TEXT)''')
		createDB.commit()
	except:
		pass

def adiciona_dado(t_0,s1,s2,s3,s4,s5,s6,experimento=None,calibracao=None,atuadores=None):
	'''
	Recebe os dados de tempo e o estado dos 6 sensores. todos os dados são salvos no bd na tabela 'dados_forno', nas coluna apropriadas
	O instante atual é capturado para salvar na culuna timestap. Caso a variável experimento (que significa o nome do experimento) seja passada,
	ela tambénm é salva no bd.
	'''
	print "add dados ",caminho_banco, t_0,s1,s2,s3,s4,s5,s6,experimento,calibracao,atuadores
	try:
		createDB = sqlite3.connect(caminho_banco)
		cursor = createDB.cursor()
		# Pegando o tempo atual do SO
		t_abs = datetime.datetime.now()
		if experimento and calibracao and atuadores:
			cursor.execute('''INSERT INTO dados_forno (t_abs,t_0,s1,s2,s3,s4,s5,s6,
				experimento,calibracao,atuadores) VALUES(?,?,?,?,?,?,?,?,?,?,?)''',
				(t_abs,t_0,s1,s2,s3,s4,s5,s6,experimento,calibracao,atuadores))
			createDB.commit()
		elif experimento:
			cursor.execute('''INSERT INTO dados_forno (t_abs,t_0,s1,s2,s3,s4,s5,s6,
				experimento) VALUES(?,?,?,?,?,?,?,?,?)''',
				(t_abs,t_0,s1,s2,s3,s4,s5,s6,experimento))
			createDB.commit()
		elif calibracao and atuadores:
			cursor.execute('''INSERT INTO dados_forno (t_abs,t_0,s1,s2,s3,s4,s5,s6,
				calibracao,atuadores) VALUES(?,?,?,?,?,?,?,?,?,?)''',
				(t_abs,t_0,s1,s2,s3,s4,s5,s6,calibracao,atuadores))
			createDB.commit()
		else:
			cursor.execute('''INSERT INTO dados_forno (t_abs,t_0,s1,s2,s3,s4,s5,s6) VALUES(?,?,?,?,?,?,?,?)''',
				(t_abs,t_0,s1,s2,s3,s4,s5,s6))
			createDB.commit()
	except:
		print "except"
		pass

def deleta_tabeta():
	'''
	Função que deleta dodos os dados do bd.
	'''
	try:
		createDB = sqlite3.connect(caminho_banco)
		cursor = createDB.cursor()
		cursor.execute("DELETE FROM dados_forno WHERE id > -1")
		createDB.commit()
	except:
		pass

def retorna_dados(delta_t,experimento=None,Ti=None,Tf=None):
	'''
	Função que retorna os dados do bd.
		-Caso o nome do experimento seja fornecido, serão retornaos todos os dados relativos a este experimento
		-Caso os tempos inicial e final sejam fornecidos, serão retornados todos os dados dentro deste período
		-Tempo delta (padrão) - Retorna dados entre o tempo atual e o tempo atual - delta_t.
	'''
	try:
		createDB = sqlite3.connect(caminho_banco)
		cursor = createDB.cursor()
		if experimento:
			cursor.execute("SELECT * FROM dados_forno WHERE experimento = ?",(experimento,))
		else:
			# Caso não tenha sido passado Ti e Tf, usa-se o tempo padrão - delta_t
			if Ti == None and Tf == None:
				tempo_inicial = datetime.datetime.now() - datetime.timedelta(minutes=delta_t)
				cursor.execute("SELECT * FROM dados_forno WHERE t_abs > ?",(tempo_inicial,))
			else:														# Op��o Ti - Tf
				cursor.execute("SELECT * FROM dados_forno WHERE t_abs > ? AND t_abs < ?",(Ti,Tf))
		createDB.commit()
		# Retorna os dados no formato matricial
		return scipy.array(cursor.fetchall())
	except:
		return None

def zerabd_gui(self):
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
			self.alerta_toolbar("Apagando bd")
			deleta_tabeta()
