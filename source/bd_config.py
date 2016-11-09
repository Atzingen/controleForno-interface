# -*- coding: latin-1 -*-
import sqlite3, datetime, modulo_global

def cria_tabela_config():
    try:
        db = sqlite3.connect(modulo_global.caminho_banco())
        cursor = db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS config
        (id INTEGER PRIMARY KEY, calibracao_selecionada TEXT UNIQUE, perfil_resistencia TEXT UNIQUE, perfil_potencia TEXT UNIQUE)''')
        db.commit()
        db.close()
        if cursor.rowcount > 0:
        	return True
        else:
        	return False
    except:
    	return False

def retorna_dados_config_calibracao():
    try:
    	db = sqlite3.connect(modulo_global.caminho_banco())
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
    	db = sqlite3.connect(modulo_global.caminho_banco())
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

def retorna_dados_config_resistencia():
    try:
    	db = sqlite3.connect(modulo_global.caminho_banco())
    	cursor = db.cursor()
    	cursor.execute('''SELECT perfil_resistencia FROM config''')
    	row = cursor.fetchall()
    	db.commit()
    	db.close()
    	if row:
    		return row[0][0]
    	else:
    		return None
    except:
    	return None

def salva_config_perfil_resistencia(nome):
    try:
    	db = sqlite3.connect(modulo_global.caminho_banco())
    	cursor = db.cursor()
    	cursor.execute('''UPDATE config SET perfil_resistencia=? WHERE id=?''',(nome,1))
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
    	db = sqlite3.connect(modulo_global.caminho_banco())
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


def salva_config_calibracao(nome):
    try:
    	db = sqlite3.connect(modulo_global.caminho_banco())
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
