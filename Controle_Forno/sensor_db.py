# -*- coding: latin-1 -*-
import sqlite3
import datetime
import time
import scipy

def cria_tabela():
	createDB = sqlite3.connect('forno_data.db')
	queryCurs = createDB.cursor()
	queryCurs.execute('''CREATE TABLE IF NOT EXISTS dados_forno
	(id INTEGER PRIMARY KEY,t_abs TIMESTAMP DEFAULT (DATETIME('now')),t_0 REAL,s1 INTEGER, s2 INTEGER, s3 INTEGER, s4 INTEGER, s5 INTEGER, s6 INTEGER)''')
	createDB.commit()

def adiciona_dado(t_0,s1,s2,s3,s4,s5,s6):
	createDB = sqlite3.connect('forno_data.db')
	queryCurs = createDB.cursor()
	t_abs = datetime.datetime.now()
	queryCurs.execute('''INSERT INTO dados_forno (t_abs,t_0,s1,s2,s3,s4,s5,s6)
	VALUES(?,?,?,?,?,?,?,?)''',(t_abs,t_0,s1,s2,s3,s4,s5,s6))
	createDB.commit()

def retorna_dados(delta_t):
    createDB = sqlite3.connect('forno_data.db')
    queryCurs = createDB.cursor()
    tempo_inicial = datetime.datetime.now() - datetime.timedelta(minutes=delta_t)
    queryCurs.execute("SELECT * FROM dados_forno WHERE t_abs > ?",(tempo_inicial,))
    createDB.commit()
    return scipy.array(queryCurs.fetchall())

