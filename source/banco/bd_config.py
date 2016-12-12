# -*- coding: latin-1 -*-
import sqlite3, datetime
import cPickle as pickle

def cria_tabela_config(caminho_banco):
    try:
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
            print 'Erro: cria_tabela_config'
            return False
    except:
        print 'Erro: except - cria_tabela_config'
    	return False

def retorna_dados_config(caminho_banco):
    try:
    	db = sqlite3.connect(caminho_banco)
    	cursor = db.cursor()
    	cursor.execute('''SELECT * FROM config WHERE id = 1''')
    	row = cursor.fetchall()
    	db.commit()
    	db.close()
    	if row:
    		return row[0]
    	else:
            print 'Erro: retorna_dados_config'
            return None
    except:
        print 'Erro: except - retorna_dados_config'
    	return None

def retorna_dados_config_calibracao(caminho_banco):
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
            print 'Erro: retorna_dados_config_calibracao'
            return None
    except:
        print 'Erro: except - retorna_dados_config_calibracao'
    	return None

def retorna_dados_config_potencia(caminho_banco):
    try:
    	db = sqlite3.connect(caminho_banco)
    	cursor = db.cursor()
    	cursor.execute('''SELECT perfil_potencia FROM config''')
    	row = cursor.fetchall()
    	db.commit()
    	db.close()
    	if row:
    		return row[0][0]
    	else:
            print 'Erro: retorna_dados_config_potencia'
            return None
    except:
        print 'Erro: except - retorna_dados_config_potencia'
    	return None

def retorna_dados_config_temperatura(caminho_banco):
    try:
    	db = sqlite3.connect(caminho_banco)
    	cursor = db.cursor()
    	cursor.execute('''SELECT perfil_temperatura FROM config''')
    	row = cursor.fetchall()
    	db.commit()
    	db.close()
    	if row:
    		return row[0][0]
    	else:
            print 'Erro: retorna_dados_config_temperatura'
            return None
    except:
        print 'Erro: except - retorna_dados_config_temperatura'
    	return None

def salva_config_perfil_temperatura(caminho_banco, nome):
    try:
    	db = sqlite3.connect(caminho_banco)
    	cursor = db.cursor()
    	cursor.execute('''UPDATE config SET perfil_temperatura=? WHERE id=?''',(nome,1))
    	db.commit()
    	db.close()
    	if cursor.rowcount > 0:
    		return True
    	else:
            print 'Erro: salva_config_perfil_temperatura'
            return False
    except:
        print 'Erro: except - salva_config_perfil_temperatura'
    	return None

def salva_config_perfil_potencia(caminho_banco, nome):
    try:
    	db = sqlite3.connect(caminho_banco)
    	cursor = db.cursor()
    	cursor.execute('''UPDATE config SET perfil_potencia=? WHERE id=?''',(nome,1))
    	db.commit()
    	db.close()
    	if cursor.rowcount > 0:
            return True
    	else:
            print 'Erro: salva_config_perfil_potencia'
            return False
    except:
        print 'Erro: except - salva_config_perfil_potencia'
    	return None

def salva_config_pid(caminho_banco, v):
    try:
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
            print 'Erro: salva_config_pid'
            return False
    except:
        print 'Erro: except - salva_config_pid'
    	return None

def salva_config_calibracao(caminho_banco, nome):
    try:
    	db = sqlite3.connect(caminho_banco)
    	cursor = db.cursor()
    	cursor.execute('''UPDATE config SET calibracao_selecionada=? WHERE id=?''',(nome,1))
    	db.commit()
    	db.close()
    	if cursor.rowcount > 0:
    		return True
    	else:
            print 'Erro: salva_config_calibracao'
            return False
    except:
        print 'Erro: except - salva_config_calibracao'
    	return None

def salva_config_pwm(caminho_banco, nome):
    try:
    	db = sqlite3.connect(caminho_banco)
    	cursor = db.cursor()
    	cursor.execute('''UPDATE config SET periodo_pwm=? WHERE id=?''',(nome,1))
    	db.commit()
    	db.close()
    	if cursor.rowcount > 0:
    		return True
    	else:
            print 'Erro: salva_config_pwm'
            return False
    except:
        print 'Erro: except - salva_config_pwm'
    	return None

def salva_config_ad(caminho_banco, n_leituras,delay):
    try:
    	db = sqlite3.connect(caminho_banco)
    	cursor = db.cursor()
    	cursor.execute('''UPDATE config SET n_leituras_ad=? WHERE id=?''',(n_leituras,1))
        cursor.execute('''UPDATE config SET delay_ad=? WHERE id=?''',(delay,1))
    	db.commit()
    	db.close()
    	if cursor.rowcount > 0:
    		return True
    	else:
            print 'Erro: salva_config_ad'
            return False
    except:
        print 'Erro: except - salva_config_ad'
    	return None



##############################################################################
def retorna_lista_config_alimento(caminho):
    try:
        lista_cfg = pickle.load( open(caminho + '/alimento_cfg.p', "rb" ) )
        return lista_cfg
    except Exception as e:
        print 'Except: retorna_lista_config_alimento', e
        return None

def retorna_escolha_alimento(caminho):
    try:
        lista = retorna_lista_config_alimento(caminho)
        for i, item in enumerate(lista):
            if item['nome'] == 'escolha':
                escolhido = item['qual']
                for v in lista:
                    if v['nome'] == escolhido:
                        return v
                print 'DEBUG: nome nao encontrado'
                return False
        print 'DEBUG: item[nome] nao encontrado'
        return False
    except Exception as e:
        print 'Except: retorna_escolha_alimento', e
        return None

def salva_config_alimento(caminho,alimento):
    try:
        antigo = retorna_lista_config_alimento(caminho)
        antigo.append(alimento)
        pickle.dump(antigo, open(caminho + '/alimento_cfg.p', "wb"))
        return True
    except Exception as e:
        print 'Except: salva_config_alimento', e
        return False

def deleta_config_alimento(caminho, nome):
    try:
        lista = retorna_lista_config_alimento(caminho)
        apagar = []
        for i, item in enumerate(lista):
            print i
            if item['nome'] == nome:
                apagar.append(i)
        for i in reversed(apagar):
            lista.pop(i)
        pickle.dump(lista, open(caminho + '/alimento_cfg.p', "wb"))
        return None
    except Exception as e:
        print 'Except: deleta_config_alimento', e
        return False
