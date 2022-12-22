from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
from PyQt5.QtWidgets import QFileDialog, QMessageBox,QMainWindow
import numpy as np
from pyqtgraph import PlotWidget
import matplotlib.pyplot as plt
import os
import pydicom as dicom
from functools import partial

class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        self.images = [None,None,None,None]
        self.volumes=[]
        self.imageProps = [None,None,None,None]
        self.lines = [[],[],[],[]]
        self.errors = []
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 900)
        MainWindow.setStyleSheet("\n"
"background-color: rgb(40, 53, 51);\n"
"")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.mainContainer = QtWidgets.QVBoxLayout(self.centralwidget)
        self.openFolder = QtWidgets.QPushButton(self.centralwidget)
        self.openFolder.setGeometry(QtCore.QRect(0, 0, 100, 60))
        self.openFolder.setStyleSheet("background-color: rgb(20, 30, 134);\n"
"color: rgb(255, 255, 255);\n"
"\n"
"")
        self.openFolder.setObjectName("Open Folder")
        self.openFolder.clicked.connect(self.openFolderAction)
        self.mainContainer.addWidget(self.openFolder)
        self.firstRow = QtWidgets.QHBoxLayout(self.centralwidget)
        self.secondRow = QtWidgets.QHBoxLayout(self.centralwidget)
        self.axial = PlotWidget(self.centralwidget,background=[255,255,255,0])
        self.axial.setGeometry(QtCore.QRect(10, 130, 281, 321))
        self.axial.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.axial.setObjectName("axial")
        self.axial.showAxis('bottom', False)
        self.axial.showAxis('left', False)
        self.axial.invertY(True)
        self.sagittal = PlotWidget(self.centralwidget,background=[255,255,255,0])
        self.sagittal.setGeometry(QtCore.QRect(320, 130, 281, 321))
        self.sagittal.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.sagittal.setObjectName("sagittal")
        self.sagittal.showAxis('bottom', False)
        self.sagittal.showAxis('left', False)
        self.sagittal.invertY(True)
        self.coronal = PlotWidget(self.centralwidget,background=[255,255,255,0])
        self.coronal.setGeometry(QtCore.QRect(10, 590, 281, 321))
        self.coronal.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.coronal.setObjectName("coronal")
        self.coronal.showAxis('bottom', False)
        self.coronal.showAxis('left', False)
        self.coronal.invertY(True)
        self.axial.setMouseEnabled(x=False,y=False)
        self.sagittal.setMouseEnabled(x=False,y=False)
        self.coronal.setMouseEnabled(x=False,y=False)
        self.oblique = PlotWidget(self.centralwidget,background=[255,255,255,0])
        self.oblique.setGeometry(QtCore.QRect(320, 590, 281, 321))
        self.oblique.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.oblique.setObjectName("oblique")
        self.oblique.showAxis('bottom', False)
        self.oblique.showAxis('left', False)
        self.oblique.invertY(True)
        self.selectors = [self.axial,self.sagittal,self.coronal,self.oblique]
        self.firstRow.addWidget(self.axial)
        self.firstRow.addWidget(self.sagittal)
        self.secondRow.addWidget(self.coronal)
        self.secondRow.addWidget(self.oblique)
        self.mainContainer.addLayout(self.firstRow)
        self.mainContainer.addLayout(self.secondRow)
        self.rotation = QtWidgets.QDial(self)        
        self.rotation.setMinimum(1)
        self.rotation.setMaximum(180)
        self.rotation.setValue(45)
        self.rotation.valueChanged.connect(self.rot)
        self.ims = [pg.ImageItem(axisOrder='row-major'),pg.ImageItem(axisOrder='row-major'),pg.ImageItem(axisOrder='row-major'),pg.ImageItem(axisOrder='row-major')]
        self.mainContainer.addWidget(self.rotation)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1218, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.openFolder.setText(_translate("MainWindow", "Open Folder"))
    def openFolderAction(self):
    
        filenames = QFileDialog().getExistingDirectory(options=QFileDialog.DontUseNativeDialog)
        ctImages=os.listdir(filenames)
        # Load the Dicom files
        slices = [dicom.read_file(filenames+'/'+s,force=True) for s in ctImages]
        slices = sorted(slices,key=lambda x:x.ImagePositionPatient[2])
        #create 3D  array
        imgShape = list(slices[0].pixel_array.shape)
        imgShape.append(len(slices))
        #print(imgShape)
        self.volume3d=np.zeros(imgShape)

        #fill 3D array with  the images from the files
        for i,s in enumerate(slices):
            array2D=s.pixel_array
            self.volume3d[:,:,i]= array2D
        
        self.images[0] = self.volume3d[:,:,i//2]
   
        self.images[1] = self.volume3d[:,i//2,:]
    
        self.images[2] = self.volume3d[i//2,:,:]
   

        self.update()
        self.drawLines()
        
   


    def newimg(self,i,q,slicevalue):

        if i==0: # iam moving line in axial plane
         if q==0:  # vertical
          self.images[1] = self.volume3d[:,slicevalue,:] # sagital
         if q==1:   # horizontal
          self.images[2] = self.volume3d[slicevalue,:,:] # coronal

        if i==1: #moving lines in sagital 
            if q==0: # vertival  moved
                self.images[2] = self.volume3d[slicevalue,:,:] # coronal changed
            if q==1: # horizontal moved 
                self.images[0]=self.volume3d[:,:,self.volume3d.shape[2]-1-slicevalue] # axial changed


        if i ==2: # iam moving lines in coronal plane
            if q==0: #vertical moved
                self.images[1]= self.volume3d[:,slicevalue,:] # sagital changed
            if q==1: # horizontal moved 
                self.images[0]=self.volume3d[:,:,self.volume3d.shape[2]-1-slicevalue] # axial changed 
 
        self.updateOne()

    def updateOne(self):
        for i in range(3):
            if i == 0:
                self.ims[i].setImage(self.images[i])
            else:
                self.ims[i].setImage(np.rot90(self.images[i]))
                self.selectors[i].autoRange(padding=0)

    def drawLines(self):
        
        for i in range(3):
            self.lines[i].append(pg.InfiniteLine(pos=self.images[i].shape[0]//2 ,bounds=(0,self.images[i].shape[0]-1),movable=True, angle=90,pen=pg.mkPen('b', width=2)))
            self.lines[i].append(pg.InfiniteLine(pos= self.images[i].shape[1]//2,bounds=(0,self.images[i].shape[1]-1),movable=True, angle=0,pen=pg.mkPen('g', width=2)))
            self.lines[i].append(pg.InfiniteLine(pos = QtCore.QPointF(0,0),movable=True, angle=45,pen=pg.mkPen('r', width=2)))
            for j,x in enumerate(self.lines[i]):
                
                x.sigPositionChanged.connect(partial(self.updateimg,i,j))
                self.selectors[i].addItem(x)
        self.lines[1][2].setVisible(False)
        self.lines[2][2].setVisible(False)
    def getPos(self,i,j):
        # print(self.lines[i][j].getPos())
        return (self.lines[i][j].getPos())


    def updateimg(self,i,j):
        newpos=self.getPos(i,j)
        self.lines[i][j].setPos(newpos)
        x=self.lines[i][j].getPos()
        if j==1:  # horizontal
          ne=round(x[1]) # y value
        if j==0:  #vertical
            ne=round(x[0])  # x value
      
      
        self.newimg(i,j,ne)
            
        
    

        
    def rot(self):
        getValue = self.rotation.value()
        self.lines[0][2].setAngle(getValue)
    def update(self):
        for x in range(3):
            #self.selectors[x].clear()
            img = self.ims[x]
            self.selectors[x].addItem(img)
            self.selectors[x].setXRange(min=0, max=self.images[x].shape[0], padding=0)
            self.selectors[x].setYRange(min=0, max=self.images[x].shape[1], padding=0)
           
            if x == 0:
                img.setImage((self.images[x]))
            else:
                img.setImage(np.rot90(self.images[x]))
            self.selectors[x].autoRange(padding=0)
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
