# -*- coding: latin-1 -*-
import ast
import numpy as np
from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from functools import partial
import banco.bd_sensores as bd_sensores
import banco.bd_perfil as bd_perfil

'''
Classes para tela e gráfico.
Como por padrão o Qt4 não possui um objeto de gráfico adequado, é utilizado o matplotlib,
sendo que um objeto de tela comum do qt herdará suas propriedades.
'''

class MplCanvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure()
        self.fig.set_facecolor('white')
        self.fig.subplots_adjust(bottom=0.15)
        self.ax = self.fig.add_subplot(111)
        self.ax.grid(True)
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


class matplotlibWidget(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.canvas = MplCanvas()
        self.vbl = QtGui.QVBoxLayout()
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)

def plotar_sensores(self):
    '''
        Função que plota o gráfico na GUI, utilizando a classe Matplotlib
        que sobrecarrega a o lable do qt (ver arquivo matplotlibwidgetFile.py)
    '''
    # Limpa os eixos para plotar novamente
    self.ui.widget.canvas.ax.clear()
     # Pega o nome do experimento e verifica se é 'Sem nome' ou não.
    if (str(self.ui.label_nomeExperimento.text()) != 'Sem Nome'):
        d = bd_sensores.retorna_dados(1,
            experimento=str(self.ui.label_nomeExperimento.text()))
    else:
        delta_t = self.ui.horizontalSlider_graficoPeriodo.value()
        d = bd_sensores.retorna_dados(delta_t)
    try:
        if np.size(d[:,0]) > 1:                                                     # Adiciona os valores ao eixo do gráfico caso a checkbox do respectivo sensor
            if self.ui.checkBox_sensor1.isChecked():                                        # esteja marcada
                self.ui.widget.canvas.ax.plot(d[:,2],d[:,3],label="R1")
            if self.ui.checkBox_sensor2.isChecked():                                      # Repete o procedimento para todos os sensores
                self.ui.widget.canvas.ax.plot(d[:,2],d[:,4],label="R2")
            if self.ui.checkBox_sensor3.isChecked():
                self.ui.widget.canvas.ax.plot(d[:,2],d[:,5],label="R3")
            if self.ui.checkBox_sensor4.isChecked():
                self.ui.widget.canvas.ax.plot(d[:,2],d[:,6],label="R4")
            if self.ui.checkBox_sensor5.isChecked():
                self.ui.widget.canvas.ax.plot(d[:,2],d[:,7],label="R5")
            if self.ui.checkBox_sensor6.isChecked():
                self.ui.widget.canvas.ax.plot(d[:,2],d[:,8],label="R6")
            self.ui.widget.canvas.ax.legend(loc='lower left',
                frameon=True,shadow=True, fancybox=True)
            self.ui.widget.canvas.ax.set_title('Sensores Forno')
            self.ui.widget.canvas.ax.set_xlabel('tempo (minutos)')
            self.ui.widget.canvas.ax.set_ylabel('temperatura (Celcius)')
            self.ui.widget.canvas.ax.grid(True)
            self.ui.widget.canvas.draw()
    except:
        self.alerta_toolbar("Erro: Grafico Sensores")
        pass

def grafico_update(self):
    '''
    Método recursivo.
    É chamado quando a checkbox de autoupdate do gráfico é ativada.
    A função ativa uma thread do QT no modo singleShot após a quantidad de tempo escolhida no
    spinBox da GUI. caso a checkbox continue ativada, a função se chamará novamente de forma recursiva
    até que a checkbox seja desabilitada ou a conecção seja desfeita.
    '''
    self.alerta_toolbar("update-grafico")
    if self.ui.checkBox_graficoAuto.isChecked():
        plotar_sensores(self)
        tempo_delay = 1000*int(self.ui.spinBox_graficoLatencia.value())
        self.timer_grafico.singleShot(tempo_delay,partial(grafico_update,self))

def tempo_grafico(self):
    '''
    Evento ocorre quando o slider abaixo do gráfico é pressinado.
    - Altera o tempo que será mostrado no gráfico (entre 1 e 99 min)
    em relação ao tempo actual.
    - Chama a função atualiza grafico.
    '''
    valor = self.ui.horizontalSlider_graficoPeriodo.value()                                  # Pega o valor do intervalo de tempo do gráfico pelo slider
    texto = 'Delta T = ' + str(valor) + ' min'                      # Texto para ser mostrado ao lado do slider com o valor escolhido
    self.ui.label_graficoTempo.setText(texto)                                              # Altera o texto do lable na GUI

def plota_perfil(self,tipo,posicao_atual):
    '''
    Plota o gráfico mostrando o perfil escolhido
    '''
    if tipo == 'resistencia':
        escolha = unicode(self.ui.comboBox_perfilResistencia.currentText())
        dados = bd_perfil.leitura_perfil(escolha,'resistencia')
        indice = int(self.ui.comboBox_displayPerfilResistencia.currentIndex())
        self.ui.widget_perfilResistencia.canvas.ax.clear()
    elif tipo == 'potencia':
        escolha = unicode(self.ui.comboBox_perfilPotencia.currentText())
        dados = bd_perfil.leitura_perfil(escolha,'potencia')
        indice = int(self.ui.comboBox_displayPerfilPotencia.currentIndex())
        self.ui.widget_perfilPotencia.canvas.ax.clear()
    x , y = [], []
    if indice > 0:
        v = ast.literal_eval(dados[indice + 1])
        for i in v:
            x.append(i[0])
            y.append(i[1])
        if tipo == 'resistencia':
            self.ui.widget_perfilResistencia.canvas.ax.plot(x,y,label="R" + str(indice))
            self.ui.widget_perfilResistencia.canvas.ax.legend(loc='lower right',
                frameon=True,shadow=True, fancybox=True)
            if posicao_atual:
                self.ui.widget_perfilResistencia.canvas.ax.plot((posicao_atual[0], posicao_atual[1]),
                                    (posicao_atual[2], posicao_atual[3]), 'k--',)
            self.ui.widget_perfilResistencia.canvas.ax.set_title('Perfil Resistencias')
            self.ui.widget_perfilResistencia.canvas.ax.set_xlabel('Tempo (minutos)')
            self.ui.widget_perfilResistencia.canvas.ax.set_ylabel('Resistencia ()%)')
            self.ui.widget_perfilResistencia.canvas.ax.set_ylim([0,400])
            self.ui.widget_perfilResistencia.canvas.ax.grid(True)
            self.ui.widget_perfilResistencia.canvas.draw()
        elif tipo == 'potencia':
            self.ui.widget_perfilPotencia.canvas.ax.plot(x,y,label="R" + str(indice))
            self.ui.widget_perfilPotencia.canvas.ax.legend(loc='lower right',
                frameon=True,shadow=True, fancybox=True)
            if posicao_atual:
                self.ui.widget_perfilPotencia.canvas.ax.plot((posicao_atual[0], posicao_atual[1]),
                                (posicao_atual[2], posicao_atual[3]), 'k--')
            self.ui.widget_perfilPotencia.canvas.ax.set_title('Perfil Potencia')
            self.ui.widget_perfilPotencia.canvas.ax.set_xlabel('Tempo (minutos)')
            self.ui.widget_perfilPotencia.canvas.ax.set_ylabel('Potencia ()%)')
            self.ui.widget_perfilPotencia.canvas.ax.set_ylim([0,110])
            self.ui.widget_perfilPotencia.canvas.ax.grid(True)
            self.ui.widget_perfilPotencia.canvas.draw()
    elif indice == 0:
        for elemento in range(2,8):
            x , y = [], []
            v = ast.literal_eval(dados[elemento])
            for i in v:
                x.append(i[0])
                y.append(i[1])
            if tipo == 'resistencia':
                self.ui.widget_perfilResistencia.canvas.ax.set_title('Perfil Resistencias')
                self.ui.widget_perfilResistencia.canvas.ax.set_xlabel('Tempo (minutos)')
                self.ui.widget_perfilResistencia.canvas.ax.set_ylabel('Resistencia ()%)')
                self.ui.widget_perfilResistencia.canvas.ax.set_ylim([0,400])
                self.ui.widget_perfilResistencia.canvas.ax.grid(True)
                self.ui.widget_perfilResistencia.canvas.ax.plot(x,y,label="R" + str(elemento-1))
                self.ui.widget_perfilResistencia.canvas.ax.legend(loc='lower right',
                    frameon=True,shadow=True, fancybox=True, ncol=2)
                if posicao_atual:
                    self.ui.widget_perfilResistencia.canvas.ax.plot((posicao_atual[0], posicao_atual[1]),
                                        (posicao_atual[2], posicao_atual[3]), 'k--')
            elif tipo == 'potencia':
                self.ui.widget_perfilPotencia.canvas.ax.plot(x,y,label=str('R' + str(elemento-1)))
                self.ui.widget_perfilPotencia.canvas.ax.legend(loc='lower right',
                    frameon=True,shadow=True, fancybox=True, ncol=2)
                if posicao_atual:
                    self.ui.widget_perfilPotencia.canvas.ax.plot((posicao_atual[0], posicao_atual[1]),
                                        (posicao_atual[2], posicao_atual[3]), 'k--')
                self.ui.widget_perfilPotencia.canvas.ax.grid(True)
                self.ui.widget_perfilPotencia.canvas.ax.set_title('Perfil Potencia')
                self.ui.widget_perfilPotencia.canvas.ax.set_xlabel('Tempo (minutos)')
                self.ui.widget_perfilPotencia.canvas.ax.set_ylabel('Potencia ()%)')
                self.ui.widget_perfilPotencia.canvas.ax.set_ylim([0,110])
        if tipo == 'resistencia':
            self.ui.widget_perfilResistencia.canvas.draw()
        elif tipo == 'potencia':
            self.ui.widget_perfilPotencia.canvas.draw()
    else:
        return None
