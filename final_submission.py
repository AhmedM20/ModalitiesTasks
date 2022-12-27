from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QFont, QFontDatabase
import pyqtgraph as pg
from PyQt5.QtWidgets import QFileDialog, QMessageBox,QMainWindow
import numpy as np
from pyqtgraph import PlotWidget
import matplotlib.pyplot as plt
import os
import pydicom as dicom
from functools import partial
from scipy import ndimage, misc
import math
import sys
from PyQt5.QtWidgets import *
import difflib
from pathlib import Path
CURRENT_DIRECTORY = Path(__file__).resolve().parent
def load_fonts_from_dir(directory):
    families = set()
    for fi in QtCore.QDir(directory).entryInfoList(["*.ttf"]):
        _id = QFontDatabase.addApplicationFont(fi.absoluteFilePath())
        families |= set(QFontDatabase.applicationFontFamilies(_id))
    return families

class anglePolygon(pg.PolyLineROI):
    def segmentClicked(self, segment, ev=None, pos=None):
        pass
class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        self.images = [None,None,None,None]
        self.volumes=[]
        self.imageProps = [None,None,None,None]
        self.lines = [[],[],[],[]]
        self.errors = []
        font_dir = CURRENT_DIRECTORY / "font"
        families = load_fonts_from_dir(os.fspath(font_dir))
        db = QFontDatabase()
        styles = db.styles("Roboto")
        self.font = db.font("Roboto", "Medium Italic", 15)
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
        self.openFolder.setFont(self.font)
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
        self.oblique.setMouseEnabled(x=False,y=False)
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
        self.b1 = QCheckBox("Line")
        self.b1.stateChanged.connect(lambda:self.btnstate(self.b1))
        self.b1.hide()
        self.b1Label = QLabel()
        self.b1Label.setHidden(True)
        self.b2 = QCheckBox("Polygon")
        self.b2.toggled.connect(lambda:self.btnstate(self.b2))
        self.b2.hide()
        self.b2Label = QLabel()
        self.b2Label.setHidden(True)
        self.b3 = QCheckBox("Angle")
        self.b3.toggled.connect(lambda:self.btnstate(self.b3))
        self.b3.hide()
        self.b3Label = QLabel()
        self.b3Label.setHidden(True)
        self.b4 = QCheckBox("Ellipse")
        self.b4.toggled.connect(lambda:self.btnstate(self.b4))
        self.b4.hide()
        self.b4Label = QLabel()
        self.b4Label.setHidden(True)
        self.b1.setFont(self.font)
        self.b2.setFont(self.font)
        self.b3.setFont(self.font)
        self.b4.setFont(self.font)
        self.b1Label.setFont(self.font)
        self.b2Label.setFont(self.font)
        self.b3Label.setFont(self.font)
        self.b4Label.setFont(self.font)
        self.b1.setStyleSheet("color: rgb(255, 255, 255);")
        self.b2.setStyleSheet("color: rgb(255, 255, 255);")
        self.b3.setStyleSheet("color: rgb(255, 255, 255);")
        self.b4.setStyleSheet("color: rgb(255, 255, 255);")
        self.b1Label.setStyleSheet("color: rgb(255, 255, 255);")
        self.b2Label.setStyleSheet("color: rgb(255, 255, 255);")
        self.b3Label.setStyleSheet("color: rgb(255, 255, 255);")
        self.b4Label.setStyleSheet("color: rgb(255, 255, 255);")
        self.lineRow = QtWidgets.QHBoxLayout(self.centralwidget)
        self.lineRow.addWidget(self.b1)
        self.lineRow.addWidget(self.b1Label)
        self.polygonRow = QtWidgets.QHBoxLayout(self.centralwidget)
        self.polygonRow.addWidget(self.b2)
        self.polygonRow.addWidget(self.b2Label)
        self.angleRow = QtWidgets.QHBoxLayout(self.centralwidget)
        self.angleRow.addWidget(self.b3)
        self.angleRow.addWidget(self.b3Label)
        self.ellipseRow = QtWidgets.QHBoxLayout(self.centralwidget)
        self.ellipseRow.addWidget(self.b4)
        self.ellipseRow.addWidget(self.b4Label)
        self.mainContainer.addLayout(self.lineRow)
        self.mainContainer.addLayout(self.polygonRow)
        self.mainContainer.addLayout(self.angleRow)
        self.mainContainer.addLayout(self.ellipseRow)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.openFolder.setText(_translate("MainWindow", "Folder picker"))
    def openFolderAction(self):
    
        filenames = QFileDialog().getExistingDirectory(options=QFileDialog.DontUseNativeDialog)
        ctImages=os.listdir(filenames)
        # Load the Dicom files
        slices = [dicom.read_file(filenames+'/'+s,force=True) for s in ctImages]
        slices = sorted(slices,key=lambda x:x.ImagePositionPatient[2])
        #create 3D  array
        imgShape = list(slices[0].pixel_array.shape)
        imgShape.append(len(slices))
        self.volume3d=np.zeros(imgShape)
        #fill 3D array with  the images from the files
        sx, sy, sz = self.volume3d.shape
        self.voxelspacingx = 1
        self.voxelspacingy = 1
        if slices[0].PixelSpacing:
            self.voxelspacingx = slices[0].PixelSpacing[0]
            self.voxelspacingy = slices[0].PixelSpacing[1]
        print(self.volume3d.shape)
        for i,s in enumerate(slices):
            array2D=s.pixel_array
            self.volume3d[:,:,i]= array2D

        self.images[0] = self.volume3d[:,:,sz//2]
   
        self.images[1] = self.volume3d[:,sy//2,:]
    
        self.images[2] = self.volume3d[sx//2,:,:]

        self.images[3] = np.zeros((sx,sy))

        self.update()
        self.drawLines()
        points=self.get_line(list(self.lines[0][2].value()))
        if not points:
            if self.rotation.value() == 90:
                self.images[3] = self.volume3d[sx//2,:,:]
            elif self.rotation.value() == 0:
                self.images[3] = self.volume3d[:,sy//2,:]
        self.images[3]=self.volume3d[tuple(np.transpose(points))]
        self.update()
        self.b1.show()
        self.b2.show()
        self.b3.show()
        self.b4.show()
    def get_line(self,coords):
        if len(coords) != 2:
            return
        x1,y1 = coords[0],coords[1]
        sx, sy, sz = self.volume3d.shape
        x2 = 0
        y2=round(math.tan(math.radians(self.rotation.value()))*(x2-x1)+y1)
        if y2 > 0:
            x3=sx-1
            y3=round(math.tan(math.radians(self.rotation.value()))*(x3-x1)+y1)
            print("Y2"+str(y2))
            
        else:
            y2=0
            x2=round((y2-y1)/math.tan(math.radians(self.rotation.value()))+x1)
            y3=sy-1
            x3=round((y3-y1)/math.tan(math.radians(self.rotation.value()))+x1)
        lineLength = np.sqrt(pow(x3 -x2, 2) + pow(y3 -y2, 2))
        points = []
        for pt in range(int(lineLength)-1):
            inc = pt / lineLength
            v1 = max(round((1-inc) * y2 + inc* y3),0)
            v1 = min(v1,sx-1)
            v2 = max(round((1-inc)*x2 + inc* x3),0)
            v2 = min(v2,sy-1)
            points.append([v1,v2])
        return points
    def newimg(self,i,q,slicevalue,slicevalue2=0):
        sx, sy, sz = self.volume3d.shape

        if i==0: # iam moving line in axial plane
         if q==0:  # vertical
          self.images[1] = self.volume3d[:,slicevalue,:] # sagital
         if q==1:   # horizontal
          self.images[2] = self.volume3d[slicevalue,:,:] # coronal
         if q==2:   # oblique
          points=self.get_line([slicevalue,slicevalue2])
          if not points:
            if self.rotation.value() == 90:
                self.images[3] = self.volume3d[sx//2,:,:]
            elif self.rotation.value() == 0:
                self.images[3] = self.volume3d[:,sy//2,:]
          self.images[3] = self.volume3d[tuple(np.transpose(points))]# oblique
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
        for i in range(4):
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
                if j != 2:
                    x.sigPositionChanged.connect(partial(self.updateimg,i,j))
                else:
                    x.sigPositionChangeFinished.connect(partial(self.updateimg,i,j))
                self.selectors[i].addItem(x)
        self.lines[1][2].setVisible(False)
        self.lines[2][2].setVisible(False)
    def getPos(self,i,j):
        return (self.lines[i][j].getPos())


    def updateimg(self,i,j):
        newpos=self.getPos(i,j)
        self.lines[i][j].setPos(newpos)
        x=self.lines[i][j].getPos()
        if j==1:  # horizontal
          ne=round(x[1]) # y value
          self.newimg(i,j,ne)
        if j==0:  #vertical
            ne=round(x[0])  # x value
            self.newimg(i,j,ne)
        if j==2:    
            self.newimg(i,j,round(x[0]),round(x[1]))
    def rot(self):
        getValue = self.rotation.value()
        self.lines[0][2].setAngle(getValue)
    def update(self):
        for x in range(4):
            img = self.ims[x]
            self.selectors[x].addItem(img)
            self.selectors[x].setXRange(min=0, max=self.images[x].shape[0], padding=0)
            self.selectors[x].setYRange(min=0, max=self.images[x].shape[1], padding=0)
           
            if x == 0:
                img.setImage((self.images[x]))
            else:
                img.setImage(np.rot90(self.images[x]))
            self.selectors[x].autoRange(padding=0)

    def updateElipse(self):
        self.p_ellipse = pg.EllipseROI(pos=QtCore.QPointF(200,200),movable=True,size=(100,50))
        self.selectors[0].addItem(self.p_ellipse)
        br= (self.p_ellipse.boundingRect())
        center = br.center()
        b = br.width() / 2.
        a = br.height() / 2.
        br= (self.p_ellipse.boundingRect())
        self.p_ellipse.sigRegionChanged.connect(self.update_elipse_roi)
        self.update_elipse_roi()
    def update_elipse_roi(self):
        br= (self.p_ellipse.boundingRect())
        center = br.center()
        b = br.width() / 2.
        a = br.height() / 2.
        theta = np.linspace(0, 2*np.pi, 24)
        area= np.pi*a*self.voxelspacingx*b*self.voxelspacingy
        print(area)
        self.b3Label.setText("Ellipse area = "+str(round(area,2))+" mm2")
        self.b3Label.repaint()
        return area 
    def updateLine(self):
        self.pline=pg.LineSegmentROI(positions=(200,250))
        self.selectors[0].addItem(self.pline)
        self.pline.sigRegionChanged.connect(self.update_line_length)
        self.update_line_length()
    def updatePolyLine(self):
        self.pgn=pg.PolyLineROI(positions=[[0, 0], [27, 0], [0, 28]],closed=True,pen=pg.mkPen(color=(0, 201, 255, 255), width=3))
        self.pgn.setPos(1, 1)
        self.selectors[0].addItem(self.pgn)
        self.pgn.sigRegionChanged.connect(self.updatePolyLineROI)
        self.updatePolyLineROI()
    def PolyArea(self,x,y):
        return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))
    def updatePolyLineROI(self):
        points = self.pgn.getLocalHandlePositions()
        x = []
        y = []
        for i in points:
            x.append(i[1].x()*self.voxelspacingx)
            y.append(i[1].y()*self.voxelspacingy)
        self.b2Label.setText("Area = "+str(round(self.PolyArea(x,y),2))+ " mm2")
        self.b2Label.repaint()
    def updateAngle(self):
        self.pa=anglePolygon(positions=[[0, 0], [27, 0], [0, 28]],closed=False,pen=pg.mkPen(color=(0, 201, 255, 255), width=3))
        self.selectors[0].addItem(self.pa)
        self.pa.sigRegionChanged.connect(self.updateAngleROI)
        self.updateAngleROI()
    def updateAngleROI(self):
        points = self.pa.getLocalHandlePositions()
        x = []
        y = []
        for i in points:
            x.append(i[1].x())
            y.append(i[1].y())
        ang = math.degrees(math.atan2(y[2]-y[1], x[2]-x[1]) - math.atan2(y[0]-y[1], x[0]-x[1]))
        if ang < 0:
            ang=ang+360
        self.b3Label.setText("Angle = "+str(ang))
        self.b3Label.repaint()
    def update_line_length(self):
        points = self.pline.getLocalHandlePositions()
        x = []
        y = []
        for i in points:
            x.append(i[1].x())
            y.append(i[1].y())
        print(x)
        print(y)

        dist = math.sqrt( ((x[1] - x[0])*self.voxelspacingx)**2 + ((y[1] - y[0])*self.voxelspacingy)**2 )
        print("distance: "+str(round(dist,2)))
        self.b1Label.setText("Distance: "+str(round(dist,2))+" mm")
        self.b1Label.repaint()
        return 0
    def btnstate(self,b):
      if b.text() == "Line":
         if b.isChecked() == True:
            self.b1Label.setHidden(False)
            print (b.text()+" is selected")
            self.updateLine()
         else:
            self.b1Label.setHidden(True)
            self.selectors[0].removeItem(self.pline)
            print( b.text()+" is deselected")
				
      if b.text() == "Polygon":
         if b.isChecked() == True:
            self.b2Label.setHidden(False)
            print (b.text()+" is selected")
            self.updatePolyLine()
         else:
            self.b2Label.setHidden(True)
            self.selectors[0].removeItem(self.pgn)
            print (b.text()+" is deselected")
      if b.text() == "Angle":
         if b.isChecked() == True:
            self.b3Label.setHidden(False)
            print (b.text()+" is selected")
            self.updateAngle()
         else:
            self.b3Label.setHidden(True)
            self.selectors[0].removeItem(self.pa)
            print (b.text()+" is deselected")
      if b.text() == "Ellipse":
         if b.isChecked() == True:
            self.b3Label.setHidden(False)
            print (b.text()+" is selected")
            self.updateElipse()
         else:
            self.b3Label.setHidden(True)
            self.selectors[0].removeItem(self.p_ellipse)
            print (b.text()+" is deselected")
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())