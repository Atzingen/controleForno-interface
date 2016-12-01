# -*- coding: latin-1 -*-
from modulo_global import *
import sqlite3, datetime

def cria_tabela_config():
    try:
        global caminho_banco
        db = sqlite3.connect(caminho_banco)
        cursor = db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS config
        (id INTEGER PRIMARY KEY, calibracao_selecionada TEXT UNIQUE,
        perfil_temperatura TEXT UNIQUE, perfil_potencia TEXT UNIQUE,
        kp REAL UNIQUE, ki REAL UNIQUE, kd REAL UNIQUE,
        kp_d REAL UNIQUE, ki_d REAL UNIQUE, kd_d REAL UNIQUE,
        max_Integrador REAL UNIQUE, min_Integrator REAL UNIQUE,
        periodo_pwm INTEGER UNIQUE, n_leituras_ad INTEGER UNIQUE,
        delay_ad INTEGER UNIQUE )''')
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
        global caminho_banco
    	db = sqlite3.connect(caminho_banco)
    	cursor = db.cursor()
    	cursor.execute('''SELECT * FROM config WHERE id = 1''')
    	row = cursor.fetchall()
    	db.commit()
    	db.close()
    	if row:
    		return row[0]
    	else:
    		return None
    except:
    	return None

def retorna_dados_config_calibracao():
    try:
        global caminho_banco
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

def retorna_dados_config_potencia():
    try:
        global caminho_banco
    	db = sqlite3.connect(caminho_banco)
    	cursor = db.cursor()
    	cursor.execute('''SELECT perfil_potencia FROM config''')
    	row = cursor.fetchall()
    	db.commit()
    	db.close()
    	if row:
    		return row[0][0]
    	else:
    		return None
    except:
    	return None

def retorna_dados_config_temperatura():
    try:
        global caminho_banco
    	db = sqlite3.connect(caminho_banco)
    	cursor = db.cursor()
    	cursor.execute('''SELECT perfil_temperatura FROM config''')
    	row = cursor.fetchall()
    	db.commit()
    	db.close()
    	if row:
    		return row[0][0]
    	else:
    		return None
    except:
    	return None

def salva_config_perfil_temperatura(nome):
    try:
        global caminho_banco
    	db = sqlite3.connect(caminho_banco)
    	cursor = db.cursor()
    	cursor.execute('''UPDATE config SET perfil_temperatura=? WHERE id=?''',(nome,1))
    	db.commit()
    	db.close()
    	if cursor.rowcount > 0:
    		return True
    	else:
    		return False
    except:
    	return None

def salva_config_perfil_potencia(nome):
    try:
        global caminho_banco
    	db = sqlite3.connect(caminho_banco)
    	cursor = db.cursor()
    	cursor.execute('''UPDATE config SET perfil_potencia=? WHERE id=?''',(nome,1))
    	db.commit()
    	db.close()
    	if cursor.rowcount > 0:
    		return True
    	else:
    		return False
    except:
    	return None

def salva_config_pid(v):
    try:
        global caminho_banco
    	db = sqlite3.connect(caminho_banco)
    	cursor = db.cursor()
        cursor.execute('''UPDATE config SET kp=? WHERE id=?''',(v[0],1))
        cursor.execute('''UPDATE config SET ki=? WHERE id=?''',(v[1],1))
        cursor.execute('''UPDATE config SET kd=? WHERE id=?''',(v[2],1))
        cursor.execute('''UPDATE config SET kp_d=? WHERE id=?''',(v[3],1))
        cursor.execute('''UPDATE config SET ki_d=? WHERE id=?''',(v[4],1))
        cursor.execute('''UPDATE config SET kd_d=? WHERE id=?''',(v[5],1))
        cursor.execute('''UPDATE config SET max_Integrador=? WHERE id=?''',(v[6],1))
        cursor.execute('''UPDATE config SET min_Integrator=? WHERE id=?''',(v[7],1))
    	db.commit()
    	db.close()
    	if cursor.rowcount > 0:
    		return True
    	else:
    		return False
    except:
    	return None

def salva_config_calibracao(nome):
    try:
        global caminho_banco
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

def salva_config_pwm(nome):
    try:
        global caminho_banco
    	db = sqlite3.connect(caminho_banco)
    	cursor = db.cursor()
    	cursor.execute('''UPDATE config SET periodo_pwm=? WHERE id=?''',(nome,1))
    	db.commit()
    	db.close()
    	if cursor.rowcount > 0:
    		return True
    	else:
    		return False
    except:
    	return None

def salva_config_ad(n_leituras,delay):
    try:
        global caminho_banco
    	db = sqlite3.connect(caminho_banco)
    	cursor = db.cursor()
    	cursor.execute('''UPDATE config SET n_leituras_ad=? WHERE id=?''',(n_leituras,1))
        cursor.execute('''UPDATE config SET delay_ad=? WHERE id=?''',(delay,1))
    	db.commit()
    	db.close()
    	if cursor.rowcount > 0:
    		return True
    	else:
    		return False
    except:
    	return None
