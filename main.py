# Copyright 2022 by Justin Jaro, VLT Media.
# All rights reserved.
# Released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package or find the MIT License Agreement online.


import os, json, sys
import numpy as np
from PIL import Image as im
from PySide2.QtWidgets import *
class TextImageEncoder:
    def __init__(self, imageSize = [64,64]):
        file = open(os.path.join(os.path.dirname(__file__), 'wordsFreq.json'))
        self.wordsJson = json.load(file)
        file.close()
        self.range = (self.min() , self.max())
        self.imageSize = imageSize
        self.repeat = False
        
    def max(self):
        maxx = 0
        for word in self.wordsJson: 
            if self.wordsJson[word] > maxx:
                maxx = self.wordsJson[word]
        return maxx
    
    def min(self):
        minn = self.max()
        for word in self.wordsJson: 
            if self.wordsJson[word] < minn:
                minn = self.wordsJson[word]
        return minn
    
    def remapValueToNewRange(self, value, oldRange, newRange):
        return (((value - oldRange[0]) * (newRange[1] - newRange[0])) / (oldRange[1] - oldRange[0])) + newRange[0]
    
    def getWordValue(self, word):
        if word in self.wordsJson:
            return self.remapValueToNewRange(self.wordsJson[word], self.range, [0,1])
        return 0
    
    def remapArrayBasedOnImageSize(self, array):
        newArray = []
        count = 0
        for i in range(self.imageSize[0]):
            newArray.append([])
            for j in range(self.imageSize[1]):
                indx = int((i/self.imageSize[0])*len(array))
                if len(array) > count:
                    newArray[i].append(array[count])
                else:
                    newArray[i].append(0)
                count += 1
        return newArray
    
    
    # def remapArrayBasedOnImageSize(self, array):
    #     newArray = []
    #     for i in range(self.imageSize[0]):
    #         newArray.append([])
    #         for j in range(self.imageSize[1]):
    #             indx = int((i/self.imageSize[0])*len(array))
    #             if len(array) > indx:
    #                 newArray[i].append(array[indx])
    #             else:
    #                 newArray[i].append(0)
    #     return newArray
    def remapArrayBasedOnImageSize(self, array):
        newArray = []
        for i in range(self.imageSize[0] * self.imageSize[1]):
            if len(array) > i:
                newArray.append(array[i])
            else:
                newArray.append(0)
        v = 0
        return newArray
    
    def encodeText(self, text, repeat = True):
        self.repeat = repeat
        words = text.split(' ')
        encoded = []
        for word in words:
            if word in self.wordsJson:
                encoded.append(self.getWordValue(word))
        baseEncode = np.array(encoded)
        # baseEncode = np.array(self.remapArrayBasedOnImageSize(encoded))
        # array1 = np.array(self.remapArrayBasedOnImageSize(encoded))
        if repeat:
            array = np.resize(baseEncode, [self.imageSize[0], self.imageSize[1]])
        else:
            array1 = np.array(self.remapArrayBasedOnImageSize(encoded))
            array = np.resize(array1, [self.imageSize[0], self.imageSize[1]])
        # array = array1.reshape(self.imageSize[0], self.imageSize[1])
        v = 0
        return array
        # return np.array(self.remapArrayBasedOnImageSize(encoded))
        
    def encodeNumpy(self, text, repeat = True):
        self.repeat = repeat
        encoded = self.encodeText(text,repeat)
        return encoded
    
    def encode(self, text, repeat = True):
        self.repeat = repeat
        encoded = self.encodeText(text,repeat)
        data = im.fromarray(encoded)
        return data
    
    def saveToFile(self, text, path):
        if '.bin' in path or '.npy' in path or '.txt' in path or '.json' in path or '.csv' in path:
            np.save(path, self.encodeNumpy(text))
        else:
            self.encode(text).save(path)
            
            
            
from PySide2 import QtWidgets, QtGui,QtCore
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
import os
import sys
import pyqtgraph as pg


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # widget = v03dFileIO()
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        self.contentWidget = QWidget(self)
        self.layout = QVBoxLayout()
        self.formContent = QWidget(self)
        self.formlayout = QFormLayout()
        self.formContent.setLayout(self.formlayout)
        self.textEdit = QTextEdit()
        self.doClone = QCheckBox()
        self.doClone.setChecked(True)
        
        self.imageViewContent = QWidget(self)
        self.imageViewlayout = QVBoxLayout()
        self.imageViewContent.setLayout(self.imageViewlayout)
        self.imageView = pg.image(np.zeros([64,64]))
        self.imageViewlayout.addWidget(self.imageView)
        
        
        
        self.v2ViewContent = QWidget(self)
        self.v2Viewlayout = QHBoxLayout()
        self.v2ViewContent.setLayout(self.v2Viewlayout)
        self.x = QSpinBox()
        self.y = QSpinBox()
        self.x.setValue(64)
        self.x.setRange(0,100000)
        self.y.setValue(64)
        self.y.setRange(0,100000)
        
        
        self.v2Viewlayout.addWidget(self.x)
        self.v2Viewlayout.addWidget(self.y)
        self.v2Viewlayout.addStretch()
        
        
        
        
        self.formlayout.addRow("Text", self.textEdit)
        self.formlayout.addRow("Clone On End of Text", self.doClone)
        self.formlayout.addRow("Image Size", self.v2ViewContent)
        v = 0
        # create qimage from image
        # qimage = QImage(image)
        self.EncodeButton = QPushButton("Encode Text")
        self.EncodeButton.clicked.connect(self.onEncodeButtonClick)
        self.SaveButton = QPushButton("Save Image")
        self.SaveButton.clicked.connect(self.onSaveButtonClick)
        self.SaveButton.setEnabled(False)
        self.layout.addWidget(self.imageViewContent)
        self.layout.addWidget(self.formContent)
        self.layout.addWidget(self.EncodeButton)
        self.layout.addWidget(self.SaveButton)
        self.contentWidget.setLayout(self.layout)
        self.setCentralWidget(self.contentWidget)
        self.setWindowTitle("Text to Image Encoder")
        
        self.setStyle()
        # self.setLayout(layout)
        
        # self.setStyle()
    def setStyle(self):
        filee = open('style.qss')
        self.styleData = f'{filee.read()}'
        filee.close()
        self.setStyleSheet(self.styleData)
        
    def onEncodeButtonClick(self):
        encoder = TextImageEncoder(imageSize=[self.x.value(), self.y.value()])
        data = encoder.encodeNumpy(self.textEdit.toPlainText(), self.doClone.isChecked())
        # self.imageViewlayout.removeWidget(self.imageView)
        self.imageView.setImage(data)
        # self.imageViewlayout.addWidget(self.imageView)
        self.SaveButton.setEnabled(True)
    def onSaveButtonClick(self):
        filename = QFileDialog.getSaveFileName(self, 'Save File', os.path.expanduser('~'), "Image Files (*.png *.jpg *.bmp)")
        if filename[0] != '':
            self.imageView.export(filename[0])
            print("saved!")
        
    def setStyle(self):
        
        filee = open('style.qss')
        self.styleData = f'{filee.read()}'
        filee.close()
        self.setStyleSheet(self.styleData)



def main():
    
    app = QtWidgets.QApplication(sys.argv)
    form = MainWindow()
    form.setGeometry(100, 100, 600, 500)
    form.show()
    sys.exit(app.exec_())
    

if __name__ == '__main__':

    main()
        