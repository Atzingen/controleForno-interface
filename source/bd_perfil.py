# -*- coding: latin-1 -*-
from modulo_global import *
import sqlite3, datetime

def cria_tabela_perfil_resistencia():
	try:
		global caminho_banco
		db = sqlite3.connect(caminho_banco)
		cursor = db.cursor()
		cursor.execute('''CREATE TABLE IF NOT EXISTS perfil_resistencia
		(id INTEGER PRIMARY KEY,nome TEXT,R1 TEXT,R2 TEXT,R3 TEXT,R4 TEXT,
		R5 TEXT,R6 TEXT,esteira TEXT)''')
		db.commit()
		db.close()
		if cursor.rowcount > 0:
			return True
		else:
			return False
	except:
		return None

def cria_tabela_perfil_potencia():
	try:
		global caminho_banco
		db = sqlite3.connect(caminho_banco)
		cursor = db.cursor()
		cursor.execute('''CREATE TABLE IF NOT EXISTS perfil_potencia
		(id INTEGER PRIMARY KEY,nome TEXT,R1 TEXT,R2 TEXT,R3 TEXT,R4 TEXT,
		R5 TEXT,R6 TEXT,esteira TEXT)''')
		db.commit()
		db.close()
		if cursor.rowcount > 0:
			return True
		else:
			return False
	except:
		return None

def insere_perfil(tipo,nome,R1,R2,R3,R4,R5,R6,esteira):
	try:
		global caminho_banco
		db = sqlite3.connect(caminho_banco)
		cursor = db.cursor()
		if tipo == 'resistencia':
			cursor.execute('''INSERT INTO perfil_resistencia (nome,R1,R2,R3,
							R4,R5,R6,esteira) VALUES(?,?,?,?,?,?,?,?)''',
							(nome,R1,R2,R3,R4,R5,R6,esteira))
		elif tipo == 'potencia':
			cursor.execute('''INSERT INTO perfil_potencia (nome,R1,R2,R3,
							R4,R5,R6,esteira) VALUES(?,?,?,?,?,?,?,?)''',
							(nome,R1,R2,R3,R4,R5,R6,esteira))
		else:
			return False
		db.commit()
		db.close()
		if cursor.rowcount > 0:
			return True
		else:
			return False
	except:
		return False


def nomes_perfil_resistencia():
	try:
		global caminho_banco
		db = sqlite3.connect(caminho_banco)
		cursor = db.cursor()
		cursor.execute('''SELECT nome FROM perfil_resistencia''')
		row = cursor.fetchall()
		db.close()
		if row:
			return row
		else:
			return None
	except:
		return None

def nomes_perfil_potencia():
	try:
		global caminho_banco
		db = sqlite3.connect(caminho_banco)
		cursor = db.cursor()
		cursor.execute('''SELECT nome FROM perfil_potencia''')
		row = cursor.fetchall()
		db.close()
		if row:
			return row
		else:
			return None
	except:
		return None

def leitura_perfil(nome,tipo):
	try:
		global caminho_banco
		db = sqlite3.connect(caminho_banco)
		cursor = db.cursor()
		if tipo == 'resistencia':
			cursor.execute('''SELECT * FROM perfil_resistencia WHERE nome = ?''',(nome,))
		elif tipo == 'potencia':
			cursor.execute('''SELECT * FROM perfil_potencia WHERE nome = ?''',(nome,))
		row = cursor.fetchone()
		db.close()
		if row:
			return row
		else:
			return None
	except:
		return None
