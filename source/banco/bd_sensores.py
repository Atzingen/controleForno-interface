# -*- coding: latin-1 -*-
import sqlite3, scipy, datetime

def cria_tabela(caminho_banco):
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
		print 'Erro: except cria_tabela'

def adiciona_dado(caminho_banco,t_0,s1,s2,s3,s4,s5,s6,experimento=None,calibracao=None,atuadores=None):
	'''
	Recebe os dados de tempo e o estado dos 6 sensores. todos os dados são salvos no bd na tabela 'dados_forno', nas coluna apropriadas
	O instante atual é capturado para salvar na culuna timestap. Caso a variável experimento (que significa o nome do experimento) seja passada,
	ela tambénm é salva no bd.
	'''
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
		print 'Erro: except adiciona_dado'

def deleta_tabeta(caminho_banco):
	'''
	Função que deleta dodos os dados do bd.
	'''
	try:
		createDB = sqlite3.connect(caminho_banco)
		cursor = createDB.cursor()
		cursor.execute("DELETE FROM dados_forno WHERE id > -1")
		createDB.commit()
	except:
		print 'Erro: except adiciona_dado'

def retorna_dados(caminho_banco,delta_t,experimento=None,Ti=None,Tf=None):
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
			else:											
				cursor.execute("SELECT * FROM dados_forno WHERE t_abs > ? AND t_abs < ?",(Ti,Tf))
		createDB.commit()
		# Retorna os dados no formato matricial
		return scipy.array(cursor.fetchall())
	except:
		print 'Erro: except adiciona_dado'
		return None
