'''
Created on 13 giu 2016

@author: corrado
'''
import sys
import io
import os
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from scipy import fftpack
import urllib2
import IPython

import numpy
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from scipy import misc

from numpy.random import ranf
from PyQt4 import QtCore, QtGui
import gui_jpeg

class Convert_to_jpeg:
    
    #variabili di istanza
    n = 0
    quality = 0
    qf = 0
    q = np.array([[16.0000, 11.0000, 10.0000, 16.0000, 24.0000, 40.0000, 51.0000, 61.0000],
                  [12.0000, 12.0000, 14.0000, 19.0000, 26.0000, 58.0000, 60.0000, 55.0000],
                  [14.0000, 13.0000, 16.0000, 24.0000, 40.0000, 57.0000, 69.0000, 56.00000],
                  [14.0000, 17.0000, 22.0000, 29.0000, 51.0000, 87.0000, 80.0000, 62.0000],
                  [18.0000, 22.0000, 37.0000, 56.0000, 68.0000, 109.0000, 103.0000, 77.0000],
                  [24.0000, 35.0000, 55.0000, 64.0000, 81.0000, 104.0000, 113.0000,92.0000],
                  [49.0000, 64.0000, 78.0000, 87.0000, 103.0000, 121.0000, 120.0000, 101.0000],
                  [72.0000, 92.0000, 95.0000, 98.0000, 112.0000, 100.0000, 103.0000, 99.0000]
                  ]) 
    q1 = 0
    img = 0
    
    #setters
    def set_n(self, n):
        if n != 0:
            self.n = n
        else:
            self.n = 1
        
    def set_quality(self, q):
        if (q > 100):
            print "Warning: quality > 100 is not possible, quality initialize to 100"
            self.quality = 100
        elif(q < 1):
            print "Warning: quality < 1 is not possible, quality initialize to 1"
            self.quality = 1
        else: 
            self.quality = q
                
    def set_qf(self):
        if (self.quality >= 50):
            self.qf = float(100 - self.quality)/ 50
        else:
            self.qf = float(50)/self.quality

    def set_q1(self):
        self.q1 = np.ones((8*self.n, 8*self.n))
        
        if not (self.quality == 100):
            for line in range(len(self.q1)):
                for col in range(len(self.q1[line])):
                    self.q1[line][col] = self.q[line/self.n][col/self.n]
                
            self.q1 = np.multiply(self.q1, self.qf) 
        
            for line in range(len(self.q1)):
                for col in range(len(self.q1[line])):
                    self.q1[line][col] = int(round(self.q1[line][col]))
        
    def set_img(self, path):
        if path != 0:
            self.img = self.get_image_from_url(path)
     

    def get_image_from_url(self,image_url):
        image = Image.open(image_url) 
        img_grey = image.convert('L') # converte l'immagine monocromatico
       
        img = np.array(img_grey, dtype=np.float)
        return img  
        
    
    
        
    #costruttore
    def __init__(self, n, q, path):
        self.set_n(n)
        self.set_quality(q)
        self.set_qf()
        self.set_q1()
        self.set_img(path)
        
    def resize_img(self, m):
        line = len(m) 
        col = len(m[line-1])
        dim_q1 = len(self.q1)
     
        newMatrix = np.zeros(shape =(line + dim_q1 - (line % dim_q1), col + dim_q1 - (col % dim_q1)))
        for i in range(len(newMatrix)):    
            for j in range(len(newMatrix[i])):                
                if (i < line) and (j < col):
                    #print  newMatrix[i][j] 
                    #print m[i][j]
                    newMatrix[i][j] = m[i][j]
                elif (i >= line) and (j < col):
                    newMatrix[i][j] = m[line - 1][j]
                elif (i < line) and (j >= col):
                    newMatrix[i][j] = m[i][col - 1]
                else:
                    newMatrix[i][j] = m[line - 1][col - 1]
        return newMatrix
    
    def get_2D_dct(self,img):
        """ Get 2D Cosine Transform of Image"""
        return fftpack.dct(fftpack.dct(img.T, norm='ortho').T, norm='ortho')
    
    def get_2d_idct(self,coefficients):
        """ Get 2D Inverse Cosine Transform of Image"""
        return fftpack.idct(fftpack.idct(coefficients.T, norm='ortho').T, norm='ortho')
    
    def get_reconstructed_image(self, raw):
        img = raw.clip(0, 255)
        img = img.astype('uint8')
        img = Image.fromarray(img)
        return img

        
    def convert_img(self):
        ################## PASSO 0 ##################
        #aggiusta le dimensioni della img aumentandola fino al necessario
        if (len(self.img)% len(self.q1) != 0 or len(self.img[0]) % len(self.q1) != 0):
            self.img = self.resize_img(self.img)
        
        matrix_of_128s = np.full((self.n*8, self.n*8), 128) 
        
        #dividi img in blocchi e lavora su ognuno di essi
        for i in range(len(self.img)/(self.n*8)):
            for j in range(len(self.img[i])/(self.n*8)):
                #lavoro su blocchi di img alla volta
                b = self.img[i*(self.n*8):(i+1)*(self.n*8), j*(self.n*8):(j+1)*(self.n*8)]
                
                ################## PASSO 1 ##################
                b = np.subtract(b, matrix_of_128s)
                
                ################## PASSO 2 ##################
                b = self.get_2D_dct(b)
            
                ################## PASSO 3 ##################
                for h in range(len(b)):
                    for k in range(len(b[h])):
                        b[h, k] = int(round(b[h, k]/self.q1[h][k]))
                
                ################## PASSO 4 ##################
                for h in range(len(b)):
                    for k in range(len(b[h])):
                        b[h, k] = b[h, k]*self.q1[h][k]
                                
                ################## PASSO 5 ##################
                b = self.get_2d_idct(b) #non so cosa siano i coefficienti che chiede in paramentri
                    
                ################## PASSO 6 ##################
                b = np.add(b, matrix_of_128s)
                
                for h in range(len(b)):
                    for k in range(len(b[h])):
                        b[h, k] = int(round(b[h, k]))
                
                ################## PASSO 7 ##################
                for h in range(len(b)):
                    for k in range(len(b[h])):
                        b[h, k] = max(0, min(255, b[h, k]))
                
                ################## RISCRITTURA IMG ##################
                for h in range(len(b)):
                    for k in range(len(b[h])):
                        self.img[i*(self.n*8) + h][j*(self.n*8) + k] = b[h, k]
                        
        return self.get_reconstructed_image(self.img)
  
    
    
if __name__ == '__main__':
    
   
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    ui = gui_jpeg.Ui_Form()
    ui.setupUi(Form)
    
 
    
    
    #convertitor = Convert_to_jpeg(6, 10, filename)
    #pic = convertitor.convert_img()
    #pic.save("C:\Users\corrado\Desktop\AAAA.jpeg")
    
    Form.show()
    sys.exit(app.exec_())
    
    