# -*- coding: latin-1 -*-
import sqlite3, datetime

def cria_tabela_perfil_temperatura(caminho_banco):
	try:
		db = sqlite3.connect(caminho_banco)
		cursor = db.cursor()
		cursor.execute('''CREATE TABLE IF NOT EXISTS perfil_temperatura
		(id INTEGER PRIMARY KEY,nome TEXT,ar TEXT,esteira TEXT)''')
		db.commit()
		db.close()
		if cursor.rowcount > 0:
			return True
		else:
			print 'Erro: cria_tabela_perfil_temperatura'
			return False
	except:
		print 'Erro: except - cria_tabela_perfil_temperatura'
		return None

def cria_tabela_perfil_potencia(caminho_banco):
	try:
		db = sqlite3.connect(caminho_banco)
		cursor = db.cursor()
		cursor.execute('''CREATE TABLE IF NOT EXISTS perfil_potencia
		(id INTEGER PRIMARY KEY,nome TEXT,R1 TEXT,R2 TEXT,R3 TEXT,R4 TEXT,
		R5 TEXT,R6 TEXT)''')
		db.commit()
		db.close()
		if cursor.rowcount > 0:
			return True
		else:
			print 'Erro: cria_tabela_perfil_potencia'
			return False
	except:
		print 'Erro: except - cria_tabela_perfil_potencia'
		return None

def insere_perfil(caminho_banco,tipo,nome,v1,v2,v3=None,v4=None,v5=None,v6=None):
	try:
		db = sqlite3.connect(caminho_banco)
		cursor = db.cursor()
		if tipo == 'potencia':
			cursor.execute('''INSERT INTO perfil_potencia (nome,R1,R2,R3,
							R4,R5,R6) VALUES(?,?,?,?,?,?,?)''',
							(nome,v1,v2,v3,v4,v5,v6))
		else:
			cursor.execute('''INSERT INTO perfil_temperatura (nome,ar,esteira) VALUES(?,?,?)''',
							(nome,v1,v2))
		db.commit()
		db.close()
		if cursor.rowcount > 0:
			return True
		else:
			print 'Erro: insere_perfil'
			return False
	except:
		print 'Erro: except - insere_perfil'
		return False


def nomes_perfil_temperatura(caminho_banco):
	try:
		db = sqlite3.connect(caminho_banco)
		cursor = db.cursor()
		cursor.execute('''SELECT nome FROM perfil_temperatura''')
		row = cursor.fetchall()
		db.close()
		if row:
			return row
		else:
			print 'Erro: nomes_perfil_temperatura'
			return None
	except:
		print 'Erro: except - nomes_perfil_temperatura'
		return None

def nomes_perfil_potencia(caminho_banco):
	try:
		db = sqlite3.connect(caminho_banco)
		cursor = db.cursor()
		cursor.execute('''SELECT nome FROM perfil_potencia''')
		row = cursor.fetchall()
		db.close()
		if row:
			return row
		else:
			print 'Erro: nomes_perfil_potencia'
			return None
	except:
		print 'Erro: except - nomes_perfil_potencia'
		return None

def leitura_perfil(caminho_banco, nome, tipo):
	try:
		db = sqlite3.connect(caminho_banco)
		cursor = db.cursor()
		if tipo == 'temperatura':
			cursor.execute('''SELECT * FROM perfil_temperatura WHERE nome = ?''',(nome,))
		elif tipo == 'potencia':
			cursor.execute('''SELECT * FROM perfil_potencia WHERE nome = ?''',(nome,))
		row = cursor.fetchone()
		db.close()
		if row:
			return row
		else:
			print 'Erro: leitura_perfil'
			return None
	except:
		print 'Erro: except - leitura_perfil'
		return None
