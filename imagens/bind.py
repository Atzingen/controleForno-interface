# -*- coding: latin-1 -*-
import numpy as np
import cv2
from matplotlib import pyplot as plt

perfil = cv2.imread('temperatura.jpg')
forno = cv2.imread('forno-pre.jpg')

col_perfil, lin_perfil, _ = perfil.shape
col_forno, lin_forno, _ = forno.shape
print 'perfil antes:', lin_perfil, col_perfil, 'forno:', lin_forno, col_forno

perfil = perfil[7:-25,27:]

b,g,r = cv2.split(perfil)       # get b,g,r
perfil = cv2.merge([r,g,b])     # switch it to rgb

perfil = cv2.resize(perfil,(lin_forno, col_forno))
col_perfil, lin_perfil, _ = perfil.shape
print 'perfil depois:', lin_perfil, col_perfil

lin = lin_perfil
col = col_perfil

pts1 = np.float32([[0,0],[0,col],[lin,col],[lin,0]])

p1, p2, p3, p4 = [70,120], [320,200], [780,55], [600,20]
pts2 = np.float32([p1, p2, p3, p4])

M = cv2.getPerspectiveTransform(pts1,pts2)

dst2 = cv2.warpPerspective(perfil,M,(lin,col))
dst = cv2.warpPerspective(perfil,M,(lin,col))

print dst.shape, forno.shape

f = cv2.addWeighted(dst,0.3,forno,0.7,0)

plt.subplot(221),plt.imshow(perfil),plt.title('Input'), plt.colorbar()
plt.subplot(222),plt.imshow(dst),plt.title('Output')
plt.subplot(223),plt.imshow(f),plt.title('Final')
plt.subplot(224),plt.imshow(dst2),plt.title('rwa-pers')
plt.show()
plt.show()
