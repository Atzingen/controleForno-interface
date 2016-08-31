# -*- coding: latin-1 -*-
import sqlite3
import datetime
import time
import scipy

def cria_tabela():
	'''
	Cira a tabela 'dados_forno' caso ela não exista, criando o esquema e as colunas no formato correto.
	O nome do arquivo do banco de dados é 'forno_data.db' e esta na mesma pasta que o proprama principal.
	'''
	createDB = sqlite3.connect('forno_data.db')
	queryCurs = createDB.cursor()
	queryCurs.execute('''CREATE TABLE IF NOT EXISTS dados_forno
	(id INTEGER PRIMARY KEY,t_abs TIMESTAMP DEFAULT (DATETIME('now')),t_0 REAL,s1 REAL, s2 REAL, s3 REAL, s4 REAL, s5 REAL, s6 REAL,experimento TEXT)''')
	createDB.commit()

def adiciona_dado(t_0,s1,s2,s3,s4,s5,s6,experimento=None):
	'''
	Recebe os dados de tempo e o estado dos 6 sensores. todos os dados são salvos no bd na tabela 'dados_forno', nas coluna apropriadas
	O instante atual é capturado para salvar na culuna timestap. Caso a variável experimento (que significa o nome do experimento) seja passada,
	ela tambénm é salva no bd.
	'''
	createDB = sqlite3.connect('forno_data.db')							# Conecta com o bd
	queryCurs = createDB.cursor()										# Cria um cursor para interagir com o bd
	t_abs = datetime.datetime.now()										# Pegando o tempo atual
	if experimento:														# Caso o experimento tenha nome, sava o nome do experimento
		queryCurs.execute('''INSERT INTO dados_forno (t_abs,t_0,s1,s2,s3,s4,s5,s6,experimento)		# Inserindo no bando de dados (com experimento)
						VALUES(?,?,?,?,?,?,?,?,?)''',(t_abs,t_0,s1,s2,s3,s4,s5,s6,experimento))
	else:
		queryCurs.execute('''INSERT INTO dados_forno (t_abs,t_0,s1,s2,s3,s4,s5,s6)					# Inserindo no bando de dados (sem experimento)
						VALUES(?,?,?,?,?,?,?,?)''',(t_abs,t_0,s1,s2,s3,s4,s5,s6))		
	createDB.commit()													# Salva as alterações.

def deleta_tabeta():
	'''
	Função que deleta dodos os dados do bd.
	'''
	createDB = sqlite3.connect('forno_data.db')						# Conecta com o bd
	queryCurs = createDB.cursor()									# Cria um cursor para interagir com o bd
	queryCurs.execute("DELETE FROM dados_forno WHERE id > -1")		# Envia o comando que apaga todos os valores
	createDB.commit()												# Salva as alterações.

def retorna_dados(delta_t,experimento=None,Ti=None,Tf=None):
	'''
	Função que retorna os dados do bd. 
		-Caso o nome do experimento seja fornecido, serão retornaos todos os dados relativos a este experimento
		-Caso os tempos inicial e final sejam fornecidos, serão retornados todos os dados dentro deste período
		-Tempo delta (padrão) - Retorna dados entre o tempo atual e o tempo atual - delta_t.
	'''
	createDB = sqlite3.connect('forno_data.db')						# Conecta com o bd
	queryCurs = createDB.cursor()									# Cria um cursor para interagir com o bd
	if experimento:													# Caso a variável experimento tenha sido passada:
		queryCurs.execute("SELECT * FROM dados_forno WHERE experimento = ?",(experimento,))
	else:
		if Ti == None and Tf == None:								# Caso não tenha sido passado Ti e Tf, usa-se o tempo padrão - delta_t
			tempo_inicial = datetime.datetime.now() - datetime.timedelta(minutes=delta_t)
			queryCurs.execute("SELECT * FROM dados_forno WHERE t_abs > ?",(tempo_inicial,))
		else:														# Opção Ti - Tf
			queryCurs.execute("SELECT * FROM dados_forno WHERE t_abs > ? AND t_abs < ?",(Ti,Tf))
	createDB.commit()
	return scipy.array(queryCurs.fetchall())						# Retorna os dados no formato matricial
