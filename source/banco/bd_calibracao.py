# -*- coding: latin-1 -*-
import sqlite3, datetime

def cria_tabela_calibracao(caminho_banco):
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
			print 'Erro: cria_tabela_calibracao'
			return False
	except:
		print 'Erro: except - cria_tabela_calibracao'
		return None

def deleta_calibracao_bd(caminho_banco, nome,tipo):
	try:
		db = sqlite3.connect(caminho_banco)
		cursor = db.cursor()
		if tipo == 'Fit':
			cursor.execute('''SELECT id FROM calibracao WHERE nome = ?''',(nome,))
			numero_ids = cursor.fetchall()
			for numero_id in numero_ids:
				cursor.execute("DELETE FROM calibracao WHERE id = ?",(numero_id[0],))
		elif tipo == 'temperatura':
			cursor.execute('''SELECT id FROM perfil_temperatura WHERE nome = ?''',(nome,))
			numero_ids = cursor.fetchall()
			for numero_id in numero_ids:
				cursor.execute("DELETE FROM perfil_temperatura WHERE id = ?",(numero_id[0],))
		elif tipo == 'potencia':
			cursor.execute('''SELECT id FROM perfil_potencia WHERE nome = ?''',(nome,))
			numero_ids = cursor.fetchall()
			for numero_id in numero_ids:
				cursor.execute("DELETE FROM perfil_potencia WHERE id = ?",(numero_id[0],))
		else:
			print 'error - deleta_calibracao_bd'
			db.close()
			return False
		db.commit()
		db.close()
		if cursor.rowcount > 0:
			return True
		else:
			print 'Erro: deleta_calibracao_bd'
			return False
	except:
		print 'Erro: except - deleta_calibracao_bd'
		return False

def insere_calibracao(caminho_banco, nome,s1_A,s2_A,s3_A,s4_A,s5_A,s6_A,
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
			print 'Erro: insere_calibracao'
			return False
	except:
		print 'Erro: except - insere_calibracao'
		return False

def nomes_calibracao(caminho_banco):
	try:
		db = sqlite3.connect(caminho_banco)
		cursor = db.cursor()
		cursor.execute('''SELECT nome FROM calibracao''')
		row = cursor.fetchall()
		db.close()
		if row:
			return row
		else:
			print 'Erro: nomes_calibracao'
			return None
	except:
		print 'Erro: except - nomes_calibracao'
		return None

def leitura_calibracao(caminho_banco, nome):
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
		print 'Erro: except - leitura_calibracao'
		return None
