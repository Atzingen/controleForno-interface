# -*- coding: latin-1 -*-
import ast
from functools import partial
import numpy as np
from PyQt4 import QtGui
import banco.bd_perfil as bd_perfil
import banco.bd_config as bd_config
import banco.bd_sensores as bd_sensores
import graficos, trata_dados
import comunicacao_serial
import controle_pid

def atuacao_automatico(self,tipo,targuets):
    '''
    Atua no controle automatico do forno, enviando informaçao para o
    microcontrolador para o controle das resistências.

    tipo -> { resistencia, forno}
    targuet -> lista de lista com dois elementos cada.update_config_pid
    [[r1,targuet1],[r2,targuet2],...].
    Quando o tipo é Potencia, são até 6 targuets e o valor do targuet é
    enviado diretamente para o MC.
    Quando o tipo é Temperatura, os 2 targuets (t_esteira e t_ar) são enviados
    para o controle pid para processamento e após este o comando é enviado para
    o MC.
    '''
    try:
        if tipo == 'potencia':
            sliders = [self.ui.horizontalSlider_r01,self.ui.horizontalSlider_r02,
                       self.ui.horizontalSlider_r03,self.ui.horizontalSlider_r04,
                       self.ui.horizontalSlider_r05,self.ui.horizontalSlider_r06]
            for i, targuet in enumerate(targuets):
                sliders[i].setValue(targuet[1])
                comunicacao_serial.envia_resistencia(self,targuet[0]+1)
        elif tipo == 'temperatura':
            T_bd = bd_sensores.retorna_dados(self.caminho_banco,1)
            if int(T_bd.shape[0]) > 0:
                T_esteira = T_bd[-1][3]
                T_ar = ( T_bd[-1][6] + T_bd[-1][7] + T_bd[-1][8] )/3
                #print 'DEBUG: Val. ar:{} est:{} - Targ. ar:{} est:{}'.format(T_ar, T_esteira,targuets[0][1], targuets[1][1])
                for i, targuet in enumerate(targuets):
                    if i == 0:
                        if self.pidAr.set_point != targuet[1]:
                            self.pidAr.setPoint(targuet[1])
                        resposta = self.pidAr.update(T_ar)
                        self.ui.horizontalSlider_r01.setValue(resposta)
                        self.ui.horizontalSlider_r03.setValue(resposta)
                        self.ui.horizontalSlider_r05.setValue(resposta)
                    elif i == 1:
                        if self.pidEsteira.set_point != targuet[1]:
                            self.pidEsteira.setPoint(targuet[1])
                        resposta = self.pidEsteira.update(T_esteira)
                        self.ui.horizontalSlider_r02.setValue(resposta)
                        self.ui.horizontalSlider_r04.setValue(resposta)
                        self.ui.horizontalSlider_r06.setValue(resposta)
                    for i in range(1,7):
                        comunicacao_serial.envia_resistencia(self,i)
            else:
                self.alerta_toolbar("Sem Valores Temp")
    except Exception as e:
        print 'ERRO atuacao_automatico', e
        self.alerta_toolbar("Erro: Perfil atuacao_automatico")

def automatico_perfil_update(self,tipo,estados):
    '''
    Função que é chamada ao início de um novo controle de perfil
    automático. Esta função se chamará de forma recursiva até que
    o controle termine.

    tipo -> { resistencia , forno}
    estados -> || ponto, passo |    (R1)
                | ...  , ...   |    (R2)
                ...
                | ponto, passo ||   (R6)

            ponto: mostra qual o ultimo ponto* que o perfil passou,
            sendo o instante atual um tempo entre ponto e ponto + 1

            passo: quantos elementos discretos o tempo atual está entre o
            ponto e ponto + 1. A separação em elementos discretos é feita
            separando o tempo entre ponto e ponto + 1 entre pwm segundos,
            que é o período completo.

    '''
    try:
        if tipo == 'temperatura':
            nome = unicode(self.ui.comboBox_perfilTemperatura.currentText())
            nf, max_y_grafico = 2, 300
        elif tipo == 'potencia':
            nome = unicode(self.ui.comboBox_perfilPotencia.currentText())
            nf, max_y_grafico = 6, 100
        else:
            print "DEBUG: erro tipo "
            self.alerta_toolbar("Erro - tipo perfil automatico")
            return None
        perfil = bd_perfil.leitura_perfil(self.caminho_banco, nome, tipo)
        n_terminos = 0
        targuets = []
        # r 0..5 para passar pela info de todas as resistencias tipo=potencia
        # r 0..1 para as 2 temperaturas tipo=temperatura
        for r in range(nf):
            # perfir[i+2] -> +2 pois as duas primeiras linhas recebidas
            # do bd são a chave primária e o nome.
            perfil_r = ast.literal_eval(perfil[r+2])
            # pega o número de pontos para a resistencia r:
            numero_pontos = len(perfil_r)
            # pega em que ponto específico o controle do perfil está:
            # ponto e passo antes de agir
            ponto_atual = int(estados[r,0])
            passo = estados[r,1]
            if ( numero_pontos  > ponto_atual + 1):
                #informacao dos pontos Pn e Pn+1
                t_inicial = perfil_r[ponto_atual][0]
                t_final = perfil_r[ponto_atual+1][0]
                r_inicial = perfil_r[ponto_atual][1]
                r_final = perfil_r[ponto_atual+1][1]
                delta_r = r_final - r_inicial
                delta_t = (t_final - t_inicial)*60.0 # convertendo para segundos
                numero_passos = delta_t//self.tempo_pwm
                if numero_passos > 0:
                    pwm = r_inicial + float(passo*delta_r)/float(numero_passos)
                    t_atual = t_inicial + float(passo*delta_t)/float(numero_passos)
                else:
                    pwm = r_inicial
                    t_atual = t_inicial
                # Salva o valor no targuet para ser enviado a função atuacao_automatico
                targuets.append([r,pwm])
                # if - condição de mudança abrusca (slope 90 graus)
                if t_final <= t_inicial:
                    # zera o passo
                    estados[r,1] = 0
                    # incrementa 1 no ponto atual
                    estados[r,0] += 1
                else: # condição normal de incremento (passo)
                    # caso ainda esteja entre um ponto e outro (não chegou o
                    # final do passo):
                    if (numero_passos > passo + 1):
                        # incrementa o passo e não altera o ponto
                        estados[r,1] += 1
                    else: # fim de passo entre um ponto e outro
                        # zera o passo
                        estados[r,1] = 0
                        # incrementa o ponto
                        estados[r,0] += 1
            else:
                n_terminos += 1
                pwm = 0
        if n_terminos < nf and\
           (self.ui.pushButton_perfilTemperatura.text() == "Cancelar" or \
           self.ui.pushButton_perfilPotencia.text() == "Cancelar"):
            dt = t_final - t_inicial
            if numero_passos > 0:
                graficos.plota_perfil(self,tipo,(t_inicial + passo*dt/numero_passos,
                                        t_inicial + passo*dt/numero_passos,
                                        0  ,max_y_grafico ))
            atuacao_automatico(self,tipo,targuets)
            self.timer_serial.singleShot(self.tempo_pwm*1000,
                                         partial(automatico_perfil_update,
                                                self,tipo,estados))
        else:
            graficos.plota_perfil(self,tipo,(0, 0, 0, 100))
            if tipo == 'temperatura':
                self.ui.pushButton_perfilTemperatura.setText("Iniciar")
            elif tipo == 'potencia':
                self.ui.pushButton_perfilPotencia.setText("Iniciar")
            print "DEBUG: fim do controle automatico"
            self.alerta_toolbar("fim do controle automatico")
    except Exception as e:
        print 'ERRO automatico_perfil_update', e
        self.alerta_toolbar("Perfil automatico_perfil_update")

def inicia_perfil(self, tipo):
    '''
    Função acionada pelo sinal do botão Inicia/Fim do perfil_resistencia
    ou perfil_potencia.
    Altera o texto do botão inicia/fim e chama a função
    automatico_perfil_update
    '''
    try:
        # Desabilita o Hold para que o controle automatico possa ocorrer
        self.ui.radioButton_hold.setChecked(False)
        if tipo == 'temperatura':
            if self.ui.pushButton_perfilTemperatura.text() == "Iniciar":
                self.ui.pushButton_perfilTemperatura.setText("Cancelar")
                self.ui.comboBox_perfilTemperatura.setEnabled(False)
                self.ui.pushButton_apagarPerfilTemperatura.setEnabled(False)
                self.ui.pushButton_NovoPerfilTemperatura.setEnabled(False)
                # variavel estado: vetor 6,2 com as informações de indice e
                # passo de cada resistencia
                estados = np.zeros([2,2])
                controle_pid.update_valores_pid(self)
                self.pidEsteira.setPoint(100)
                self.pidAr.setPoint(100)

            elif self.ui.pushButton_perfilTemperatura.text() == "Cancelar":
                reply = QtGui.QMessageBox.question(self,'Mensagem',
                                    "Tem certeza que terminar ?",
        							QtGui.QMessageBox.Yes |QtGui.QMessageBox.No,
                                    QtGui.QMessageBox.No)
                if reply == QtGui.QMessageBox.Yes:
                    self.ui.pushButton_perfilTemperatura.setText("Iniciar")
                    self.ui.comboBox_perfilTemperatura.setEnabled(True)
                    self.ui.pushButton_apagarPerfilTemperatura.setEnabled(True)
                    self.ui.pushButton_NovoPerfilTemperatura.setEnabled(True)
                    self.alerta_toolbar("Fim perfil Automatico")
                else:
                    self.alerta_toolbar("Perfil Automatico continua")

                return None
            else:
                self.alerta_toolbar("Erro IniciaPerfil")
                return None
        elif tipo == 'potencia':
            if self.ui.pushButton_perfilPotencia.text() == "Iniciar":
                self.ui.pushButton_perfilPotencia.setText("Cancelar")
                self.ui.pushButton_NovoPerfilPotencia.setEnabled(False)
                self.ui.pushButton_apagarPerfilPotencia.setEnabled(False)
                self.ui.comboBox_perfilPotencia.setEnabled(False)
                estados = np.zeros([6,2])
                automatico_perfil_update(self,'potencia',estados)
            elif self.ui.pushButton_perfilPotencia.text() == "Cancelar":
                reply = QtGui.QMessageBox.question(self,'Mensagem',
                                    "Tem certeza que terminar ?",
        							QtGui.QMessageBox.Yes |QtGui.QMessageBox.No,
                                    QtGui.QMessageBox.No)
                if reply == QtGui.QMessageBox.Yes:
                    self.ui.pushButton_perfilPotencia.setText("Iniciar")
                    self.ui.pushButton_NovoPerfilPotencia.setEnabled(True)
                    self.ui.pushButton_apagarPerfilPotencia.setEnabled(True)
                    self.ui.comboBox_perfilPotencia.setEnabled(True)
                    self.alerta_toolbar("Fim perfil Automatico")
                else:
                    self.alerta_toolbar("Perfil Automatico continua")
                return None
            else:
                self.alerta_toolbar("Erro IniciaPerfil")
                return None
        else:
            self.alerta_toolbar("Erro IniciaPerfil")
            return None
        automatico_perfil_update(self,'temperatura',estados)
    except Exception as e:
        print 'ERRO inicia_perfil', e
        self.alerta_toolbar("Perfil inicia_perfil")

def novo_perfil(self,tipo):
    '''
    Abre um Dialog box para o usuário preencher as informações sobre
    um novo perfil, com os dados tempo e velor para todas as resistencias
    ou tempo e valor comum (caso de todas as resistencias iguais).
    '''
    flags = QtGui.QMessageBox.Yes
    flags |= QtGui.QMessageBox.No
    sim, n, i, sair = False, 1, 1, False
    if tipo == "temperatura":
        R =  [ [], []]
        mensagem = "Digite o tempo, T_ar e T_esteira separados por ',': t,ar,esteira"
        nf = 2
    else:
        mensagem = "Digite o tempo e potencia separados por ',': t,p"
        question = "As potencias das resistencias r1...r6 serao iguais ?"
        R =  [ [], [], [], [], [], [] ]
        response = QtGui.QMessageBox.question(self, "Question",question,flags)
        sim = (response == QtGui.QMessageBox.Yes)
    if sim:
        while  not sair:
            dado, result = QtGui.QInputDialog.getText(self,
                    "Toras Resistencias: Inserir ponto " + str(n),mensagem)
            if result:
                try:
                    v1_str, v2_str = dado.split(',')
                    v1 = trata_dados.converte_numero(v1_str)
                    v2 = trata_dados.converte_numero(v2_str)
                    for i in range(6):
                        R[i].append([v1,v2])
                except:
                    QtGui.QMessageBox.warning(self, "Erro",
                                "O valor digitado nao esta no formato (numero,numero)",
                                QtGui.QMessageBox.Cancel, QtGui.QMessageBox.NoButton,
                                QtGui.QMessageBox.NoButton)
                    sair = True
                    break
            else:
                sair = True
                break
            n += 1
    else:
        if tipo == "potencia":
            for i in range(6):
                n = 1
                sair = False
                while  not sair:
                    dado, result = QtGui.QInputDialog.getText(self,
                            "Inserir ponto " + str(n),
                            "R" + str(i+1) + " " + mensagem)
                    if result:
                        try:
                            v1_str, v2_str = dado.split(',')
                            v1 = trata_dados.converte_numero(v1_str)
                            v2 = trata_dados.converte_numero(v2_str)
                            R[i].append([v1,v2])
                        except:
                            QtGui.QMessageBox.warning(self, "Erro",
                                        "O valor digitado nao esta no formato (numero,numero)",
                                        QtGui.QMessageBox.Cancel, QtGui.QMessageBox.NoButton,
                                        QtGui.QMessageBox.NoButton)
                            sair = True
                            break
                    else:
                        sair = True
                    n += 1
        else:
            sair = False
            while  not sair:
                dado, result = QtGui.QInputDialog.getText(self,
                        "Inserir ponto " + str(n),mensagem)
                if result:
                    try:
                        tempo,T_ar,T_esteira  = dado.split(',')
                        tempo = trata_dados.converte_numero(tempo)
                        T_ar = trata_dados.converte_numero(T_ar)
                        T_esteira = trata_dados.converte_numero(T_esteira)
                        R[0].append([tempo,T_ar])
                        R[1].append([tempo,T_esteira])
                    except:
                        QtGui.QMessageBox.warning(self, "Erro",
                                    "O valor digitado nao esta no formato (numero,numero)",
                                    QtGui.QMessageBox.Cancel, QtGui.QMessageBox.NoButton,
                                    QtGui.QMessageBox.NoButton)
                        sair = True
                        break
                else:
                    sair = True
                n += 1
    text = "Verifique o perfil digitado: \n"
    for i in range(nf):
        text += "R" + str(i) + ": " + str(R[i]) +  "\n"
    nome, result = QtGui.QInputDialog.getText(self,"Digitar nome do perfil",text)
    if result:
        if tipo == "potencia":
            bd_perfil.insere_perfil(self.caminho_banco, tipo,str(nome),
                        str(R[0]), str(R[1]), str(R[2]), str(R[3]),
                        str(R[4]),str(R[5]))
        else:
            bd_perfil.insere_perfil(self.caminho_banco, tipo,str(nome),
                                    str(R[0]),str(R[1]))

def lista_perfil_temperatura(self):
    try:
        self.ui.comboBox_perfilTemperatura.blockSignals(True)
        nomes = bd_perfil.nomes_perfil_temperatura(self.caminho_banco)
        numero_escolha = self.ui.comboBox_perfilTemperatura.currentIndex()
        escolha = bd_config.retorna_dados_config_temperatura(self.caminho_banco)
        self.ui.comboBox_perfilTemperatura.clear()
        i = 0
        for nome in nomes:
            self.ui.comboBox_perfilTemperatura.addItem(str(nome[0]))
            if escolha == nome[0] and numero_escolha == -1:
                numero_escolha = i
            i = i + 1
        self.ui.comboBox_perfilTemperatura.setCurrentIndex(numero_escolha)
        self.ui.comboBox_perfilTemperatura.blockSignals(False)
        escolha = unicode(self.ui.comboBox_perfilTemperatura.currentText())
        bd_config.salva_config_perfil_temperatura(self.caminho_banco,escolha)
        graficos.plota_perfil(self,'temperatura',None)
    except:
        self.alerta_toolbar("except:lista_perfil_temperatura")
        pass


def lista_perfil_potencia(self):
    try:
        self.ui.comboBox_perfilPotencia.blockSignals(True)
        nomes = bd_perfil.nomes_perfil_potencia(self.caminho_banco)
        numero_escolha = self.ui.comboBox_perfilPotencia.currentIndex()
        escolha = bd_config.retorna_dados_config_potencia(self.caminho_banco)
        self.ui.comboBox_perfilPotencia.clear()
        i = 0
        for nome in nomes:
            self.ui.comboBox_perfilPotencia.addItem(str(nome[0]))
            if escolha == nome[0] and numero_escolha == -1:
                numero_escolha = i
            i = i + 1
        self.ui.comboBox_perfilPotencia.setCurrentIndex(numero_escolha)
        self.ui.comboBox_perfilPotencia.blockSignals(False)
        escolha = unicode(self.ui.comboBox_perfilPotencia.currentText())
        bd_config.salva_config_perfil_potencia(self.caminho_banco, escolha)
        graficos.plota_perfil(self,'potencia',None)
    except:
        self.alerta_toolbar("except:lista_perfil_potencia")


def atualiza_label_microcontrolador(self):
    try:
        resposta = bd_config.retorna_dados_config(self.caminho_banco)
        t_pwm, n_leituras, delay_leituras = resposta[12], resposta[13], resposta[14]
        texto =  't_pwm=' + str(t_pwm) + ' n_leituras=' + str(n_leituras) + \
        '\ndelay_leituras=' + str(delay_leituras)
        self.ui.label_infoPWM_ADC.setText(texto)
    except:
        self.alerta_toolbar("except:atualiza_label_microcontrolador")
