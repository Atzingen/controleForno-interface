# -*- coding: latin-1 -*-
'''
Classe de controle PID Discreto
Baseado no programa desenvolvido por http://code.activestate.com/recipes/577231-discrete-pid-controller/
sobre a licença MIT: http://opensource.org/licenses/MIT
'''

class PID:
	"""
	Controle PID Discreto
	Este objeto deve ser instanciado com os valores de Kp, Ki e Kd (padrão = 2, 0.5 e 1) e com o set_point
	set_point -> Valor desejado para o controle
	Limite máximo e mínimo para o integrador = 100 e -100 respectivamente
	Integrador e Derivador iniciam com valor 0
	"""
	def __init__(self, P=2.0, I=0.5, D=1.0, set_point=1.0,Derivador=0,
				Integrador=0, max_Integrador=100, min_Integrator=-100):
		# Construtor - Inicia automaticamente quando um objeto da classe PID é instanciado
		self.Kp=P
		self.Ki=I
		self.Kd=D
		self.Derivador=Derivador
		self.Integrador=Integrador
		self.max_Integrador=max_Integrador
		self.min_Integrator=min_Integrator
		self.set_point=set_point
		self.error=0.0

	def update(self,current_value):
		"""
		Recebe um novo dado lido pelo sensor e retorna a resposta
		do controle PID para o sistema
		"""
		# Cálculo do erro: Objetivo - Valor atual
		self.error = self.set_point - current_value
		# Cálculo de K,P e D
		self.P_value = self.Kp * self.error
		self.D_value = self.Kd * (self.error - self.Derivador)
		self.Derivador = self.error
		self.Integrador = self.Integrador + self.error
		# Checa se o valor do Integrador não saturou
		if self.Integrador > self.max_Integrador:
			self.Integrador = self.max_Integrador
		elif self.Integrador < self.min_Integrator:
			self.Integrador = self.min_Integrator

		self.I_value = self.Integrador * self.Ki
		# Atualiza o valor da resposta
		PID = self.P_value + self.I_value + self.D_value
		# Retorna o valor para a rotina que chamou o objeto
		return PID

	def setPoint(self,set_point):
		"""
		Atualiza o valor do set_point, caso um novo objetivo seja desejado
		Zera os valores do Integrador e do Derivador pois é como se o controle
		estivesse começando novamente.
		"""
		self.set_point = set_point  # Atualiza o set_point (obejtivo)
		self.Integrador=0  # Zera o valor do Integrador
		self.Derivador=0   # Zera o valor do Derivador
