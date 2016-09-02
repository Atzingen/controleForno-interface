# -*- coding: latin-1 -*-
import sqlite3
import datetime
import scipy
from PyQt4 import QtGui

def cria_tabela_config():
	db = sqlite3.connect('forno_data.db')
	cursor = db.cursor()
	cursor.execute('''CREATE TABLE IF NOT EXISTS config
	(id INTEGER PRIMARY KEY, calibracao_selecionada TEXT UNIQUE)''')
	db.commit()
	db.close()

def retorna_dados_config():
	db = sqlite3.connect('forno_data.db')
	cursor = db.cursor()
	cursor.execute('''SELECT calibracao_selecionada FROM config''')
	row = cursor.fetchall()
	db.commit()
	db.close()
	return row[0][0]

def salva_config_calibracao(nome):
	db = sqlite3.connect('forno_data.db')
	cursor = db.cursor()
	cursor.execute('''UPDATE config SET calibracao_selecionada=? WHERE id=?''',(nome,1))
	db.commit()
	db.close()

def cria_tabela_calibracao():
	db = sqlite3.connect('forno_data.db')
	cursor = db.cursor()
	cursor.execute('''CREATE TABLE IF NOT EXISTS calibracao
	(id INTEGER PRIMARY KEY,nome TEXT,s1_A REAL,s2_A REAL,s3_A REAL,s4_A REAL,s5_A REAL,s6_A REAL,
							s1_B REAL,s2_B REAL,s3_B REAL,s4_B REAL,s5_B REAL,s6_B REAL)''')
	db.commit()
	db.close()

def insere_calibracao(nome,s1_A,s2_A,s3_A,s4_A,s5_A,s6_A,
					s1_B,s2_B,s3_B,s4_B,s5_B,s6_B):
	db = sqlite3.connect('forno_data.db')
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


def nomes_calibracao():
	try:
		db = sqlite3.connect('forno_data.db')
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
		db = sqlite3.connect('forno_data.db')
		cursor = db.cursor()
		cursor.execute('''SELECT * FROM calibracao WHERE nome = ?''',(nome,))
		row = cursor.fetchone()
		db.close()
		if row:
			return row
		else:
			return None
	except:
		return None

def cria_tabela():
	'''
	Cira a tabela 'dados_forno' caso ela não exista, criando o esquema e as colunas no formato correto.
	O nome do arquivo do banco de dados � 'forno_data.db' e esta na mesma pasta que o proprama principal.
	'''
	createDB = sqlite3.connect('forno_data.db')
	queryCurs = createDB.cursor()
	queryCurs.execute('''CREATE TABLE IF NOT EXISTS dados_forno
	(id INTEGER PRIMARY KEY,t_abs TIMESTAMP DEFAULT (DATETIME('now')),t_0 REAL,s1 REAL, s2 REAL, s3 REAL, s4 REAL, s5 REAL, s6 REAL,experimento TEXT)''')
	createDB.commit()

def adiciona_dado(t_0,s1,s2,s3,s4,s5,s6,experimento=None):
	'''
	Recebe os dados de tempo e o estado dos 6 sensores. todos os dados s�o salvos no bd na tabela 'dados_forno', nas coluna apropriadas
	O instante atual � capturado para salvar na culuna timestap. Caso a vari�vel experimento (que significa o nome do experimento) seja passada,
	ela tamb�nm � salva no bd.
	'''
	createDB = sqlite3.connect('forno_data.db')							# Conecta com o bd
	queryCurs = createDB.cursor()										# Cria um cursor para interagir com o bd
	t_abs = datetime.datetime.now()										# Pegando o tempo atual
	if experimento:														# Caso o experimento tenha nome, sava o nome do experimento
																		# Inserindo no bando de dados
		queryCurs.execute('''INSERT INTO dados_forno (t_abs,t_0,s1,s2,s3,s4,s5,s6,experimento)
						VALUES(?,?,?,?,?,?,?,?,?)''',(t_abs,t_0,s1,s2,s3,s4,s5,s6,experimento))
	else:
		queryCurs.execute('''INSERT INTO dados_forno (t_abs,t_0,s1,s2,s3,s4,s5,s6)
						  VALUES(?,?,?,?,?,?,?,?)''',(t_abs,t_0,s1,s2,s3,s4,s5,s6))
	createDB.commit()													# Salva as altera��es.

def deleta_tabeta():
	'''
	Fun��o que deleta dodos os dados do bd.
	'''
	createDB = sqlite3.connect('forno_data.db')						# Conecta com o bd
	queryCurs = createDB.cursor()									# Cria um cursor para interagir com o bd
	queryCurs.execute("DELETE FROM dados_forno WHERE id > -1")		# Envia o comando que apaga todos os valores
	createDB.commit()												# Salva as altera��es.

def retorna_dados(delta_t,experimento=None,Ti=None,Tf=None):
	'''
	Fun��o que retorna os dados do bd.
		-Caso o nome do experimento seja fornecido, ser�o retornaos todos os dados relativos a este experimento
		-Caso os tempos inicial e final sejam fornecidos, ser�o retornados todos os dados dentro deste per�odo
		-Tempo delta (padr�o) - Retorna dados entre o tempo atual e o tempo atual - delta_t.
	'''
	createDB = sqlite3.connect('forno_data.db')						# Conecta com o bd
	queryCurs = createDB.cursor()									# Cria um cursor para interagir com o bd
	if experimento:													# Caso a vari�vel experimento tenha sido passada:
		queryCurs.execute("SELECT * FROM dados_forno WHERE experimento = ?",(experimento,))
	else:
		if Ti == None and Tf == None:								# Caso n�o tenha sido passado Ti e Tf, usa-se o tempo padr�o - delta_t
			tempo_inicial = datetime.datetime.now() - datetime.timedelta(minutes=delta_t)
			queryCurs.execute("SELECT * FROM dados_forno WHERE t_abs > ?",(tempo_inicial,))
		else:														# Op��o Ti - Tf
			queryCurs.execute("SELECT * FROM dados_forno WHERE t_abs > ? AND t_abs < ?",(Ti,Tf))
	createDB.commit()
	return scipy.array(queryCurs.fetchall())						# Retorna os dados no formato matricial

def zerabd_gui(self):
	''' M�todo para zerar o banco de dados (acionado pelo bot�o 'Zerar Bando de dados')
	Um popup � aberto para confirmar que os dados ser�o mesmo apagados'''
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
