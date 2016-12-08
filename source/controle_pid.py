# -*- coding: latin-1 -*-
import banco.bd_config as bd_config
'''
Classe de controle PID Discreto
Baseado no programa desenvolvido por http://code.activestate.com/recipes/577231-discrete-pid-controller/
sobre a licença MIT: http://opensource.org/licenses/MIT
'''

class PID:
	'''
	Controle PID Discreto
	Este objeto deve ser instanciado com os valores de Kp, Ki e Kd (padrão = 2, 0.5 e 1) e com o set_point
	set_point -> Valor desejado para o controle
	Limite máximo e mínimo para o integrador = 100 e -100 respectivamente
	Integrador e Derivador iniciam com valor 0
	'''
	def __init__(self, P_up=0.5, I_up=3, D_up=0.001,
				P_down=0.5, I_down=0.25, D_down=0.001,
				_point=1.0,Derivador=0, dt=1, set_point=100,
				Integrador=0, max_Integrador=100, min_Integrator=-100):
		# Construtor - Inicia automaticamente quando um objeto da classe PID é instanciado
		self.Kp_up=P_up
		self.Ki_up=I_up
		self.Kd_up=D_up
		self.Kp_down=P_down
		self.Ki_down=I_down
		self.Kd_down=D_down
		self.Derivador=Derivador
		self.Integrador=Integrador
		self.max_Integrador=max_Integrador
		self.min_Integrator=min_Integrator
		self.set_point=set_point
		self.error=0.0
		self.dt = dt

	def update(self,current_value):
		'''
		Recebe um novo dado lido pelo sensor e retorna a resposta
		do controle PID para o sistema
		'''
		# Cálculo do erro: Objetivo - Valor atual
		novo_erro = self.set_point - current_value

		# verifica se passou a linha do Objetivo
		if novo_erro*self.error < 0:
			print "cruzou"
			self.Integrador=0
			self.Derivador=0
		self.error = novo_erro
		print self.error
		# Cálculo de K,P e D
		if self.error > 0:
			self.P_value = self.Kp_up * self.error
			self.D_value = self.Kd_up * (self.error - self.Derivador)/self.dt
			self.Derivador = self.error
			self.Integrador = self.Integrador + (self.error*self.dt)
			ki_f = self.Ki_up
		else:
			self.P_value = self.Kp_down * self.error
			self.D_value = self.Kd_down * (self.error - self.Derivador)/self.dt
			self.Derivador = self.error
			self.Integrador = self.Integrador + (self.error*self.dt)
			ki_f = self.Ki_down
		# Checa se o valor do Integrador não saturou
		if self.Integrador > self.max_Integrador:
			self.Integrador = self.max_Integrador
		elif self.Integrador < self.min_Integrator:
			self.Integrador = self.min_Integrator

		self.I_value = self.Integrador * ki_f
		# Atualiza o valor da resposta
		PID = self.P_value + self.I_value + self.D_value
		print 'P:{}, I:{}, D:{}'.format(self.P_value,self.I_value,self.D_value)
		# Retorna o valor para a rotina que chamou o objeto
		return PID

	def setPoint(self,set_point):
		'''
		Atualiza o valor do set_point, caso um novo objetivo seja desejado
		Zera os valores do Integrador e do Derivador pois é como se o controle
		estivesse começando novamente.
		'''
		self.set_point = set_point
		self.Integrador=0
		self.Derivador=0

def update_label_pid(self):
	try:
	    cfg = bd_config.retorna_dados_config(self.caminho_banco)
	    kp, ki, kd, kp_d, ki_d, kd_d, max_Integrador, min_Integrator = cfg[4], cfg[5], cfg[6], cfg[7], cfg[8], cfg[9], cfg[10], cfg[11]
	    texto_label = 'kp=' + str(kp) + ' ki=' + str(ki) + ' kd=' + str(kd) + \
		'\nkp_d=' + str(kp_d) + ' ki_d=' + str(ki_d) + ' kd_d=' + str(kd_d) + \
	    '\nmax=' + str(max_Integrador) + ' min=' + str(min_Integrator)
	    self.ui.label_infoPID.setText(texto_label)
	except:
		self.alerta_toolbar("erro update_label_pid")

def update_config_pid(self):
	try:
		kp = float(self.ui.lineEdit_kp.text())
		ki = float(self.ui.lineEdit_ki.text())
		kd = float(self.ui.lineEdit_kd.text())
		kp_d = float(self.ui.lineEdit_kp_d.text())
		ki_d = float(self.ui.lineEdit_ki_d.text())
		kd_d = float(self.ui.lineEdit_kd_d.text())
		max_Integrador = float(self.ui.lineEdit_maxIntegrador.text())
		min_Integrator = float(self.ui.lineEdit_minIntegrador.text())
		r = bd_config.salva_config_pid(self.caminho_banco, [kp, ki, kd, kp_d, ki_d, kd_d, max_Integrador, min_Integrator])
		update_valores_pid(self)
	except:
		self.alerta_toolbar("erro update_config_pid")

def update_valores_pid(self):
	try:
		cfg = bd_config.retorna_dados_config(self.caminho_banco)
		kp, ki, kd, kp_d, ki_d, kd_d, max_Integrador, min_Integrator = cfg[4], cfg[5], cfg[6], cfg[7], cfg[8], cfg[9], cfg[10], cfg[11]
		self.pid.Kp_up = kp
		self.pid.Ki_up = ki
		self.pid.Kd_up = kd
		self.pid.Kp_down = kp_d
		self.pid.Ki_down = ki_d
		self.pid.Kd_down = kd_d
		self.pid.max_Integrador = max_Integrador
		self.pid.min_Integrator = min_Integrator
	except:
		self.alerta_toolbar("erro update_valores_pid")

def limpa_lineEdit(self):
	self.ui.lineEdit_kp.setText("")
	self.ui.lineEdit_ki.setText("")
	self.ui.lineEdit_kd.setText("")
	self.ui.lineEdit_kp_d.setText("")
	self.ui.lineEdit_ki_d.setText("")
	self.ui.lineEdit_kd_d.setText("")
	self.ui.lineEdit_maxIntegrador.setText("")
	self.ui.lineEdit_minIntegrador.setText("")
