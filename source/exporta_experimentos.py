# -*- coding: latin-1 -*-
from __future__ import division
import sys, os, datetime, glob, smtplib, shutil, csv
import numpy as np
from functools import partial
from PyQt4 import QtGui, QtCore
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import Encoders
from tr import tr

# Imports Locais
#from forno_run import Ui_MainWindow
from banco_dados import *

def local_parent():
	caminho_source = os.getcwd()
	source_parent = os.path.abspath(os.path.join(caminho_source, os.pardir))
	if sys.platform.startswith('win'):
		barra = '\\'
	else:
		barra = '/'
	source_parent += barra
	return str(source_parent), barra

def local_arquivo(self):
	''' Altera o texto do lable que mostra o caminho onde s�o salvos os arquivos'''
	source_parent, _ = local_parent()
	local = str(QtGui.QFileDialog.getExistingDirectory(caption="Escolha a pasta em que os arquivos serao salvos",directory=source_parent + "dadosExperimento"))
	print local

	self.label_18.setText(local)

def gera_arquivo(self):
	''' M�todo que � ativado quando o bot�o 'Gera Arquivo' � pressionado.
	Os dados s�o retirados do bd de acordo com as configura��es do experimento (nome ou per�odo)
	e salvas no formato adequado de acordo com as op��es no checkbox formato do Arquivo'''
	t = datetime.datetime.now()															# Pega o tempo para o nome do arquivo
	tempo = str(t.month) + '-' + str(t.day) + '-' + str(t.hour) + '-' + str(t.minute) 	# Coloca os valores do tempo em uma string
	caminho = str(self.ui.label_18.text())
	if self.experimento_nome == 'Sem Nome' and self.ui.checkBox_18.isChecked():			# Checa se � um experimento sem nome (por data) e foi selecionado dados por per�odo
		Ti = self.ui.dateTimeEdit_2.dateTime().toPyDateTime()							# Pega a data inicial desejada
		Tf = self.ui.dateTimeEdit.dateTime().toPyDateTime()								# Pega a data final desejada
		d = retorna_dados(1,Ti=Ti,Tf=Tf)												# Pedido ao banco de dados para o per�odo escolhido
	elif self.ui.checkBox_19.isChecked():
		d = retorna_dados(1,experimento=str(self.experimento_nome))						# Busca no bd os dados com o nome do experimento espec�fico
		tempo = str(self.experimento_nome) + '_' + tempo 								# Adiciona o nome do experimento ao tempo
	for a in glob.glob('*'):															# loop pelo diret�rio para buscar se o arquivo ja existe
		if tempo in a:																	# Caso j� exista:
			tempo = tempo + '(1)'														# 	adiciona o texto (1) no final do nome do arquivo para
			break 																		#   evitar sobrescrever e apagar dados
	# if para as 2 op�oes (txt, csv)
	if self.ui.checkBox_15.isChecked():													# Salvar em arquivo .txt
		with open(caminho + tempo + '.txt', "w") as arquivo_texto:						# Abre o arquivo que ir� ser escrito
			arquivo_texto.write('Arquivo gerado automaticamente - Dados do forno - LAFAC USP \n \n \n')						# Cabe�alho
			arquivo_texto.write('chave \t Data e horario completo  \tt_0 \t\ts1 \ts2 \ts3 \ts4 \ts5 \ts6\texperimento\n\n') # informa��es sobre as colunas
			for i in d:																	# loop para andar por todas as linhas de dados
				arquivo_texto.write('\n')												# pula uma linha
				for j in i:																# loop pelas colunas
					arquivo_texto.write(str(j) + '\t')									# adiciona os dados e um tab
			arquivo_texto.close()														# fecha o manipulador do arquivo

	elif self.ui.checkBox_16.isChecked():												# Salvar em arquivo .csv (segunda op��o)
		with open(caminho + tempo + '.csv', 'wt') as arquivo_csv:						# abre o arquivo para salvar os dados
			writer = csv.writer(arquivo_csv,lineterminator = '\n',dialect='excel')
			writer.writerow(('chave','Data e horario completo','t_0','s1','s2','s3','s4','s5','s6','experimento'))
			if np.size(d) > 0:															# Caso d n�o esteja vazio
				try:
					for i in range(np.size(d[:,1])):									# loop por todas as linhas
						writer.writerow(( d[i,0], d[i,1], d[i,2], d[i,3], d[i,4],
										  d[i,5], d[i,6], d[i,7], d[i,8], d[i,9] ))
					arquivo_csv.close()													# fecha o arquivo
				except:
					pass
	else:																				# Salva em banco de dados sqlite3
		pass

def envia_email(self):
	''' M�todo que envia os dados do experimento por email'''
	f = str(QtGui.QFileDialog.getOpenFileName())										# popup que pede para selecionar o arquivo (retorna o caminho do arquivo)
	endereco = str(self.ui.lineEdit_2.text())
	senha    = str(self.ui.lineEdit_3.text())
	if ('@gmail.com' in endereco) and (senha is not ''):								# implementado apenas envio para o gmail
		#try:																			# Envio do email:
		t = datetime.datetime.now()
		tempo = str(t.month) + '-' + str(t.day) + '-' + str(t.hour) + '-' + str(t.minute)
		arquivo = os.path.basename(f)
		msg = MIMEMultipart()
		msg['From'] = endereco
		msg['To'] = endereco
		msg['Subject'] = "Dados: " + os.path.basename(f) + ' ' + tempo
		corpo_email = "E-mail gerado automaticamente \n\n Programa de controle - Forno Lafac \n\n formato da data (Assunto do e-mail: Mes - dia - hora - minuto) "
		msg.attach(MIMEText(corpo_email))

		part = MIMEBase('application', "octet-stream")
		part.set_payload(open(f,'rb').read())
		Encoders.encode_base64(part)
		part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
		msg.attach(part)

		server = smtplib.SMTP('smtp.gmail.com', 587)
		server.starttls()
		server.login(endereco, senha)
		text = msg.as_string()
		server.sendmail(endereco, endereco, text)
		server.quit()
	else:
		self.alerta_toolbar('erro de parametros-smtp')

def pendrive(self):
	''' M�todo � acionado ao clicar no bot�o 'pendrive'.
	� aberto um popup para pegar o caminho do arquivo a ser salvo e depois o local aonde ser� salvo (no pendrive) '''
	self.alerta_toolbar("teste-pendrive")
	fonte   = str(QtGui.QFileDialog.getOpenFileName())
	destino = str(QtGui.QFileDialog.getExistingDirectory())
	if len(str(fonte)) > 1 and len(str(destino)) > 1:
		shutil.copy2(fonte,destino)

def limpa_senha(self):
	''' Limpa o campo senha e email '''
	self.mensagem = "teste"
	self.alerta_toolbar("teste-limpasenha")
	reply = QtGui.QMessageBox.question(self,'Mensagem',"Tem certeza que quer limpar senha e e-mail?",
										QtGui.QMessageBox.Yes |
										QtGui.QMessageBox.No, QtGui.QMessageBox.No)
	if reply == QtGui.QMessageBox.Yes:
		self.ui.lineEdit_2.setText("")
		self.ui.lineEdit_3.setText("")

def novo_exp(self):
	''' Inicia ou termina um novo experimento.
	Caso haja um experimento em andamento, o experimento � terminado.
	Caso n�o haja, uma janela de di�logo abre perguntando o nome do experimento
	e este � salvo. Todos os dados ap�s isto s�o salvos com o nome deste experimento.'''
	if self.ui.pushButton_15.text() == 'Encerrar Experimento':		# Caso o bot�o esteja no modo Encerrar Experimento
		self.ui.pushButton_15.setText('Novo Experimento')			# Altera o lable do bot�o para Novo Experimento
		self.ui.label_20.setText("Sem Nome")
		self.ui.checkBox_19.setEnabled(False)						# Desabilita o checkbox de sele��o do experimento atual
		self.ui.checkBox_18.setChecked(True)						# Marca a checkbox de salvar dados por per�odo
		self.ui.checkBox_20.setChecked(False)						# Desmarca o checbox de sele��o do experimento atual (plot)
		self.ui.checkBox_20.setEnabled(False)						# Desabilita o checkbox de sele��o do experimento atual (plot)
		self.experimento_nome = 'Sem Nome'
	else:
		text, ok = QtGui.QInputDialog.getText(self, '', 			# Caixa de dialogo para nome do experimento
											'Digite o nome do seu experimento')
		if ok and len(text) > 1:
			self.experimento_nome = text 							# Salva o nome do experimento
			self.ui.label_20.setText(self.experimento_nome)			# Altera o label do nome do experimento
			self.ui.pushButton_15.setText('Encerrar Experimento')	# Altera o texto do bot�o
			self.ui.checkBox_19.setEnabled(True)					# Habilita o checkbox de sele��o do experimento atual
			self.ui.checkBox_20.setEnabled(True)					# Habilita o checkbox de sele��o dos dados por per�odo
			self.ui.checkBox_19.setChecked(True)					# Marca a checkbox de salvar dados do ultimo experimento
