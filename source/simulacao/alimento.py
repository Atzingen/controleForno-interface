# -*- coding: latin-1 -*-
import numpy as np
from PyQt4 import QtGui
from PyQt4 import QtCore
from matplotlib import rcParams, cm
import cv2
from modulo_global import *

def display_alimento(self, T):
    # T0 = np.ones((30,60))*300 #   dimensão 2, size nr + 1, nh + 1
    # T = evolui_tempo(10, T0, T_paredes=500, T_esteira=400) - 273.5
    T = np.flipud(T)
    T = np.concatenate((np.fliplr(T),T),axis=1)
    self.ui.widget_3.canvas.ax.clear()
    cax = self.ui.widget_3.canvas.ax.imshow(T,label="teste",interpolation='nearest',
                                      aspect='auto', cmap=cm.jet)#, vmin=25, vmax=350)
    self.ui.widget_3.canvas.ax.axis('off')
    self.ui.widget_3.canvas.fig.savefig('imagens/temp-alimento.jpg', bbox_inches='tight', pad_inches=0)
    self.ui.widget_3.canvas.ax.axis('on')
    #self.ui.widget_2.canvas.fig.colorbar(cax)
    self.ui.widget_3.canvas.draw()

    perfil = cv2.imread('imagens/temp-alimento.jpg')
    perfil = perfil[7:-25,27:]

    global biscoito

    col, lin, _ = biscoito.shape
    perfil = cv2.resize(perfil,(lin, col))

    pts1 = np.float32([[0,0],[0,col],[lin,col],[lin,0]])
    p1, p2, p3, p4 = [85,120], [85,320], [1050,320], [1050,120]
    pts2 = np.float32([p1, p2, p3, p4])

    M = cv2.getPerspectiveTransform(pts1,pts2)

    perfil = cv2.warpPerspective(perfil,M,(lin,col))
    perfil = cv2.addWeighted(biscoito,0.8,perfil,0.6,0)
    cv2.imwrite('imagens/teste-img2.jpg',perfil)
    self.ui.label_39.setPixmap(QtGui.QPixmap("imagens/teste-img2.jpg").scaled(self.ui.label_39.size(), QtCore.Qt.KeepAspectRatio))

def evolui_tempo(tf, T,
                 dt=0.05, nr = 60, nh = 30,
                 R = 5.0e-2, H = 1.0e-2,
                 k = 0.1, rho = 400, Cp = 3000, h_convec = 5.0, epsion = 0.7,
                 T_esteira = 420.0, T_paredes = 470.0, T_ar = 450.0, T_ambiente = 293.0):
    '''
    Função principal da simulação.
    Recebe a temperatura inicial e os parâmetros necessários para realizar via método direto (fowad in time, center in space),
    as iterações necessárias (nt) até o tempo final

    Parameters:
    -----------------------
    tf: float
        tempo em segundos em que o sistema irá evoluir T0 = 0.
        O número de iterações (time steps) dependerá de tf e dt (tf/dt)
    dt: float
        time step (em segundos)
    nr: int
        número de elementos discretos na direção radial
    nh: int
        número de elementos discretos no eixo z (altura)
    R: float
        Raio do alimento
    H: float
        Altura do alimento
    k, rho, sigma, h_convec, epsilon: float
        Constantes Físicas do alimento
    T_esteira, T_paredes, T_ar, T_ambiente: float
        Valores das temperaturas para a simulação
    '''
    pi = np.pi              # 22/7
    sigma = 5.67032e-8      # Constante de Stefan Boltzman
    alpha = k/(rho*Cp)      # constante alpha a partir de k, rho e Cp
    dr = R/(nr + 1)         # tamanho físico do elemento em r
    dh = H/(nh + 1)         # tamanho físico do elemento em h

    r = np.linspace(0,R,nr)

    # cria a matriz da temperatura inicial - array of float
    #T = np.ones((nh,nr))*T_ambiente #   dimensão 2, size nr + 1, nh + 1

    # matriz para valores de r en função, montadas em uma matriz concatenada de
    # colunas para operação vetorizada no loop
    r_cilindrico = 1/np.tile(r+dr,(nh,1))[1:-1,1:-1]

    nt = int(tf/dt)        # Número de vezes que o método será aplicado (fowad in time)

    ######### Condições de contorno de Dirichilet #######################################
    #  (fora do loop pois estes valores não são afetados).
    # Temperatura da esteira - Inferior
    T[0,:] = T_esteira
    #T[-1,:] = 400 # Teste - temperatura superior fixa
    #T[:,-1] = 430 # Teste - temperatura lateral fixa
    for n in range(nt):
        Tn = T.copy()   # Cria uma nova matriz para não alterar a incial no processo
        T[1:-1,1:-1] = Tn[1:-1,1:-1] + alpha *( \
            (dt/dh**2) * (Tn[2:,1:-1] - 2*Tn[1:-1,1:-1] + Tn[:-2,1:-1]) +\
            (dt/dr**2) * (Tn[1:-1,2:] - 2*Tn[1:-1,1:-1] + Tn[1:-1,:-2]) +\
            (dt/(dr*r_cilindrico)) *  (Tn[2:,1:-1] - Tn[1:-1,1:-1]) )
        ###### Condições de contorno: ###################################################
        # Direichilet
        #    Retirada do loop pois o valor não é alterado
        # Mista em todas as outras:
        # Radiação + convercção
        T[:,-1] = T[:,-2] + dr*epsion*sigma*( (T_paredes**4) - (T[:,-1]**4) ) + dr*h_convec*(T_ar - T[:,-1])
        T[-1,:] = T[-2,:] + dh*epsion*sigma*( (T_paredes**4) - (T[-1,:]**4) ) + dh*h_convec*(T_ar - T[-1,:])
        # Condição de Neuman (?)
        # simetria em r=0:
        T[:,0] = T[:,1]
    else:
        return T
