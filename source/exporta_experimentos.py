# -*- coding: latin-1 -*-
from __future__ import division
import os, sys, datetime, glob, smtplib, shutil, csv
import numpy as np
from PyQt4 import QtGui
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import Encoders
import banco.bd_sensores as bd_sensores

def local_arquivo(self):
	''' Altera o texto do lable que mostra o caminho onde s�o salvos os arquivos'''
	source_parent, _ = modulo_global.local_parent()
	local = str(QtGui.QFileDialog.getExistingDirectory(caption="Escolha a pasta em que os arquivos serao salvos",
													   directory=source_parent + "dadosExperimento"))
	if sys.platform.startswith('win'):
		local += '\\'
	else:
		local += '/'
	self.label_caminho.setText(local)

def gera_arquivo(self):
	''' Método que é ativado quando o botão 'Gera Arquivo' é pressionado.
	Os dados são retirados do bd de acordo com as configurações do experimento (nome ou período)
	e salvas no formato adequado de acordo com as opções no checkbox formato do Arquivo'''
	t = datetime.datetime.now()
	tempo = str(t.month) + '-' + str(t.day) + '-' + str(t.hour) + '-' + str(t.minute)
	caminho = str(self.ui.label_caminho.text())

	if self.ui.checkBox_experimentoPeriodo.isChecked():
		Tf = self.ui.dateTimeEdit_fim.dateTime().toPyDateTime()
		Ti = self.ui.dateTimeEdit_inicio.dateTime().toPyDateTime()
		d = bd_sensores.retorna_dados(self.caminho_banco, 1, Ti=Ti, Tf=Tf)
	elif self.ui.checkBox_experimentoAtualData.isChecked():
		d = bd_sensores.retorna_dados(self.caminho_banco, 1,
						experimento=str(self.ui.label_nomeExperimento.text()))
		tempo = str(self.ui.label_nomeExperimento.text()) + '_' + tempo
	for a in glob.glob('*'):
		if tempo in a:
			tempo = tempo + '(1)'
			break

	# Opção para salvar o arquivo em txt (checkbox .txt selecionado)
	if self.ui.checkBox_formatoTxt.isChecked():
		with open(caminho + tempo + '.txt', "w") as arquivo_texto:
			# Cabeçalho do arquivo:
			arquivo_texto.write('Arquivo gerado automaticamente - Dados do forno - LAFAC USP \n \n \n')
			# Informação sobre as colunas
			arquivo_texto.write('chave \t Data e horario completo  \tt_0 \t\ts1 \ts2 \ts3 \ts4 \ts5 \ts6\texperimento\n\n')
			try:
				for i in d:
					arquivo_texto.write('\n')
					for j in i:
						arquivo_texto.write(str(j) + '\t')
			except:
				pass
			arquivo_texto.close()

	# Opção para salvar o arquivo em csv (checkbox .csv selecionado)
	elif self.ui.checkBox_formatoCsv.isChecked():
		with open(caminho + tempo + '.csv', 'wt') as arquivo_csv:
			writer = csv.writer(arquivo_csv,lineterminator = '\n',dialect='excel')
			writer.writerow(('chave','Data e horario completo','t_0','s1','s2','s3','s4','s5','s6','experimento'))																	# Caso d n�o esteja vazio
			try:
				for i in range(np.size(d[:,1])):
					writer.writerow(( d[i,0], d[i,1], d[i,2], d[i,3], d[i,4],
									  d[i,5], d[i,6], d[i,7], d[i,8], d[i,9] ))
			except:
				pass
			arquivo_csv.close()
	else:
		pass

def envia_email(self):
	'''
		Função que envia os dados do experimento por email
	'''
	f = str(QtGui.QFileDialog.getOpenFileName())										# popup que pede para selecionar o arquivo (retorna o caminho do arquivo)
	endereco = str(self.ui.lineEdit_email.text())
	senha    = str(self.ui.lineEdit_senha.text())
	if ('@gmail.com' in endereco) and (senha is not ''):								# implementado apenas envio para o gmail
		#try:																			# Envio do email:
		t = datetime.datetime.now()
		tempo = str(t.month) + '-' + str(t.day) + '-' + str(t.hour) + '-' + str(t.minute)
		arquivo = os.path.basename(f)
		msg = MIMEMultipart()
		msg['From'] = endereco
		msg['To'] = endereco
		msg['Subject'] = "Dados: " + os.path.basename(f) + ' ' + tempo
		corpo_email = "E-mail gerado automaticamente  Programa de controle - Forno Lafac  formato da data (Assunto do e-mail: Mes - dia - hora - minuto) "
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
	'''
		Função que é acionada ao clicar no botão 'pendrive'.
		É aberto um popup para pegar o caminho do arquivo a ser salvo e depois
		o local aonde será salvo (no pendrive)
	'''
	self.alerta_toolbar("teste-pendrive")
	fonte   = str(QtGui.QFileDialog.getOpenFileName())
	destino = str(QtGui.QFileDialog.getExistingDirectory())
	if len(str(fonte)) > 1 and len(str(destino)) > 1:
		shutil.copy2(fonte,destino)

def limpa_senha(self):
	'''
		Limpa o campo senha e email
	'''
	self.mensagem = "teste"
	self.alerta_toolbar("teste-limpasenha")
	reply = QtGui.QMessageBox.question(self,'Mensagem',"Tem certeza que quer limpar senha e e-mail?",
										QtGui.QMessageBox.Yes |
										QtGui.QMessageBox.No, QtGui.QMessageBox.No)
	if reply == QtGui.QMessageBox.Yes:
		self.ui.lineEdit_email.setText("")
		self.ui.lineEdit_senha.setText("")

def novo_exp(self):
	'''
	Inicia ou termina um novo experimento.
	Caso haja um experimento em andamento, o experimento é terminado.
	Caso não haja, uma janela de diálogo abre perguntando o nome do experimento
	e este é salvo. Todos os dados após isto são salvos com o nome deste
	experimento.
	'''
	if self.ui.pushButton_experimento.text() == 'Encerrar Experimento':
		self.ui.pushButton_experimento.setText('Novo Experimento')
		self.ui.label_nomeExperimento.setText("Sem Nome")
		self.ui.checkBox_experimentoAtualData.setEnabled(False)
		self.ui.checkBox_experimentoPeriodo.setChecked(True)
		self.ui.checkBox_experimentoAtualData.setChecked(False)
		self.ui.label_nomeExperimento.setText('Sem Nome')
	else:
		text, ok = QtGui.QInputDialog.getText(self, '',
						'Digite o nome do seu experimento')
		if ok and len(text) > 1:
			self.ui.label_nomeExperimento.setText(str(text))
			self.ui.pushButton_experimento.setText('Encerrar Experimento')
			self.ui.checkBox_experimentoAtualData.setEnabled(True)
			self.ui.checkBox_experimentoAtualData.setChecked(True)

def zerabd_gui(self):
	'''
		Método para zerar o banco de dados (acionado pelo botão 'Zerar
		Bando de dados').
		Um popup é aberto para confirmar que os dados serão mesmo apagados.
	'''
	reply = QtGui.QMessageBox.question(self, 'Mensagem',
						"Tem certeza que quer zerar o banco de dados?",
						QtGui.QMessageBox.Yes |
						QtGui.QMessageBox.No, QtGui.QMessageBox.No)
	if reply == QtGui.QMessageBox.Yes:
		reply = QtGui.QMessageBox.question(self,
		  				'Mensagem',"Ter certeza ? Isto apagara TODOS os dados",
						QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
						QtGui.QMessageBox.No)
		if reply == QtGui.QMessageBox.Yes:
			self.alerta_toolbar("Apagando bd")
			bd_sensores.deleta_tabeta(self.caminho_banco)
