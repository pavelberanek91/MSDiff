#argparse library - used for using command line arguments
# CMD list:
# "-m","--muted" = app will not produce warning messages to user, use when you get to know app
import argparse

#system library - used in QApp initi
import sys

#PyQt5 library - used for creating GUI widgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton, QFileDialog, QRadioButton, QMessageBox, QLineEdit, QLabel, QDialogButtonBox, QProgressDialog, QCheckBox
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot

#matplotlib library - used for creating charts of MSD
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

#scipy library - used for fitting MSD with polynomial for calculation of diffusion coefficient
from scipy.optimize import curve_fit

#numpy library
import numpy as np

#for math.inf and -math.inf values when trying to find PBC boundary values without user input
import math


#import random



class App(QMainWindow):

	def __init__(self):

		#parse command line arguments
		parser = argparse.ArgumentParser(description="App for calculation of MSD and diffusion coefficient.")
		parser.add_argument("-m","--muted",help="app doest not show warnings (decrease verbosity)",
					action="store_true")
		self.args=parser.parse_args()

		#create QT App windows
		super().__init__()
		self.left = 10
		self.top = 10
		self.title = 'Diffusion Calculation'
		self.width = 880
		self.height = 620
		self.x = []
		self.y = []
		self.fnin = ""
		self.initUI()
		self.xmin = 0.0
		self.xmax = 0.0
		self.ymin = 0.0
		self.ymax = 0.0

	def initUI(self):

		self.setWindowTitle(self.title)
		self.setGeometry(self.left, self.top, self.width, self.height)

		self.m = PlotCanvas(self, width=7, height=6)
		self.m.move(0,0)

		#load XYZ file button
		self.button_load = QPushButton('Load XYZ file', self)
		self.button_load.setToolTip('Loads XYZ file for computing MSD and Diffusion')
		self.button_load.move(720,25)
		self.button_load.resize(140,30)
		self.button_load.clicked.connect(self.load_click)
		self.l3 = QLabel(self)
		self.l3.setText("XYZ NOT! Loaded")
		self.l3.move(725,55)

		#calculate msd button
		self.button_msd = QPushButton('Calculate MSD', self)
		self.button_msd.setToolTip('Calculate Mean Squared Displacement')
		self.button_msd.move(720,115)
		self.button_msd.resize(140,30)
		self.button_msd.clicked.connect(self.msd_click)
		self.button_msd.setEnabled(False)

		#logarithmic scale radio
		self.r1 = QRadioButton("Log", self)
		self.r1.setChecked(True)
		self.r1.setToolTip('Switches to log scale')
		self.r1.move(720,145)
		self.r1.toggled.connect(self.logtoggle)
		self.r1.setEnabled(False)
		self.r2 = QRadioButton("Normal", self)
		self.r2.setChecked(False)
		self.r2.setToolTip('Switches to normal scale')
		self.r2.move(720,165)
		self.r2.toggled.connect(self.logtoggle)
		self.r2.setEnabled(False)

		#PBC checkbox and boxlenght textboxex
		self.chbPBC = QCheckBox("Periodic Boundaries?",self)
		self.chbPBC.setToolTip("Check if your xyz file uses periodic boundary conditions.")
		self.chbPBC.move(720,185)
		self.chbPBC.resize(150,40)
		self.chbPBC.stateChanged.connect(self.pbctoggle)
		self.chbPBC.setEnabled(False)

		self.lb_mincol = QLabel(self)
		self.lb_mincol.setText("Min")
		self.lb_mincol.move(730,210)
		self.lb_mincol.setVisible(False)
		self.lb_maxcol = QLabel(self)
		self.lb_maxcol.setText("Max")
		self.lb_maxcol.move(810,210)
		self.lb_maxcol.setVisible(False)

		self.lb_xboxlen = QLabel(self)
		self.lb_xboxlen.setText("X:")
		self.lb_xboxlen.move(720,230)
		self.lb_xboxlen.setVisible(False)
		self.tb_xboxlenmin = QLineEdit(self)
		self.tb_xboxlenmin.setVisible(False)
		self.tb_xboxlenmin.move(735,235)
		self.tb_xboxlenmin.resize(60,20)
		self.tb_xboxlenmin.setToolTip("Minimum value on X-axis of your simulation box")
		self.tb_xboxlenmax = QLineEdit(self)
		self.tb_xboxlenmax.move(800,235)
		self.tb_xboxlenmax.resize(60,20)
		self.tb_xboxlenmax.setVisible(False)
		self.tb_xboxlenmax.setToolTip("Maximum value on X-axis of your simulation box")

		self.lb_yboxlen = QLabel(self)
		self.lb_yboxlen.setText("Y:")
		self.lb_yboxlen.move(720,250)
		self.lb_yboxlen.setVisible(False)
		self.tb_yboxlenmin = QLineEdit(self)
		self.tb_yboxlenmin.move(735,255)
		self.tb_yboxlenmin.resize(60,20)
		self.tb_yboxlenmin.setVisible(False)
		self.tb_yboxlenmin.setToolTip("Minimum value on Y-axis of your simulation box")
		self.tb_yboxlenmax = QLineEdit(self)
		self.tb_yboxlenmax.move(800,255)
		self.tb_yboxlenmax.resize(60,20)
		self.tb_yboxlenmax.setVisible(False)
		self.tb_yboxlenmax.setToolTip("Maximum value on Y-axis of your simulation box")

		self.lb_zboxlen = QLabel(self)
		self.lb_zboxlen.setText("Z:")
		self.lb_zboxlen.move(720,270)
		self.lb_zboxlen.setVisible(False)
		self.tb_zboxlenmin = QLineEdit(self)
		self.tb_zboxlenmin.move(735,275)
		self.tb_zboxlenmin.resize(60,20)
		self.tb_zboxlenmin.setVisible(False)
		self.tb_zboxlenmin.setToolTip("Minimum value on Z-axis of your simulation box")
		self.tb_zboxlenmax = QLineEdit(self)
		self.tb_zboxlenmax.move(800,275)
		self.tb_zboxlenmax.resize(60,20)
		self.tb_zboxlenmax.setVisible(False)
		self.tb_zboxlenmax.setToolTip("Maximum value on Z-axis of your simulation box")

		#zoom functionality button
		self.btn_zoom = QPushButton("Rescale Plot",self)
		self.btn_zoom.setToolTip('Rescales plot to specified range')
		self.btn_zoom.move(720,325)
		self.btn_zoom.resize(140,30)
		self.btn_zoom.clicked.connect(self.zoomclick)
		self.btn_zoom.setEnabled(False)

		#zoom xranges
		self.lb_xstart = QLabel(self)
		self.lb_xstart.setText("X start")
		self.lb_xstart.move(725,355)
		self.tb_xstart = QLineEdit(self)
		self.tb_xstart.move(720,380)
		self.tb_xstart.resize(140,20)
		self.tb_xstart.setEnabled(False)
		self.tb_xstart.setToolTip("Start of X-axis on rescaled plot")
		self.lb_xend = QLabel(self)
		self.lb_xend.setText("X end")
		self.lb_xend.move(725,400)
		self.tb_xend = QLineEdit(self)
		self.tb_xend.move(720,425)
		self.tb_xend.resize(140,20)
		self.tb_xend.setEnabled(False)
		self.tb_xend.setToolTip("End of X-axis on rescaled plot")

		#calculate diffusion button
		self.button_dif = QPushButton('Calculate Diffusion', self)
		self.button_dif.setToolTip('Calculate Diffusion coefficient')
		self.button_dif.move(720,480)
		self.button_dif.resize(140,30)
		self.button_dif.clicked.connect(self.diff_click)
		self.button_dif.setEnabled(False)

		#tstart and tmin tend textboxes
		self.lb_tstart = QLabel(self)
		self.lb_tstart.setText("T start")
		self.lb_tstart.move(725,510)
		self.tb_tstart = QLineEdit(self)
		self.tb_tstart.move(720,535)
		self.tb_tstart.resize(140,20)
		self.tb_tstart.setEnabled(False)
		self.tb_tstart.setToolTip("Beginning of time interval for diffusion calculation")
		self.lb_tend = QLabel(self)
		self.lb_tend.setText("T end")
		self.lb_tend.move(725,555)
		self.tb_tend = QLineEdit(self)
		self.tb_tend.move(720,580)
		self.tb_tend.resize(140,20)
		self.tb_tend.setEnabled(False)
		self.tb_tstart.setToolTip("End of time interval for diffusion calculation")

		#file menu
		self.file_menu = QMenu('&File', self)
		self.file_menu.addAction('&Load XYZ', self.load_click, QtCore.Qt.CTRL + QtCore.Qt.Key_O)
		self.file_menu.addAction('&Calculate MSD', self.msd_click, QtCore.Qt.CTRL + QtCore.Qt.Key_M)
		self.file_menu.addAction('&Calculate Diffusion', self.diff_click, QtCore.Qt.CTRL + QtCore.Qt.Key_D)
		self.file_menu.addAction('&Export Figure', self.exfig_click, QtCore.Qt.CTRL + QtCore.Qt.Key_S)
		self.file_menu.addAction('&Export MSD values', self.msdexport_click, QtCore.Qt.CTRL + QtCore.Qt.Key_E)
		self.file_menu.addAction('&Quit', self.fileQuit, QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
		self.menuBar().addMenu(self.file_menu)

		#help menu
		self.help_menu = QMenu('&Help', self)
		self.menuBar().addSeparator()
		self.menuBar().addMenu(self.help_menu)
		self.help_menu.addAction('&Help', self.help, QtCore.Qt.CTRL + QtCore.Qt.Key_H)

		#intro Messagebox
		if not self.args.muted:
			QMessageBox.about(self, "Diffusion Calculator", "This apps computes Mean Squared Displacement and Diffusion Coefficient from *.xyz file. Select help if you need guidance.")

		self.show()

	def msdexport_click(self):
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fnout, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()", "","TXT files (*.txt);;All Files (*)", options=options)
		fout = open(fnout,"w")
		for i in range(len(self.x)):
			fout.write("{} {}\n".format(self.x[i],self.y[i]))
		fout.close()


	def logtoggle(self):
		self.m.plot(self.x,self.y,self.r1,self.xmin,self.xmax,self.ymin,self.ymax)

	#this signals enabled/disables PBC min and max lenghts input
	def pbctoggle(self,state):
		if state == QtCore.Qt.Checked:
			self.lb_mincol.setVisible(True)
			self.lb_maxcol.setVisible(True)
			self.lb_xboxlen.setVisible(True)
			self.lb_yboxlen.setVisible(True)
			self.lb_zboxlen.setVisible(True)
			self.tb_xboxlenmin.setVisible(True)
			self.tb_xboxlenmax.setVisible(True)
			self.tb_yboxlenmin.setVisible(True)
			self.tb_yboxlenmax.setVisible(True)
			self.tb_zboxlenmin.setVisible(True)
			self.tb_zboxlenmax.setVisible(True)
		else:
			self.lb_mincol.setVisible(False)
			self.lb_maxcol.setVisible(False)
			self.lb_xboxlen.setVisible(False)
			self.lb_yboxlen.setVisible(False)
			self.lb_zboxlen.setVisible(False)
			self.tb_xboxlenmin.setVisible(False)
			self.tb_xboxlenmax.setVisible(False)
			self.tb_yboxlenmin.setVisible(False)
			self.tb_yboxlenmax.setVisible(False)
			self.tb_zboxlenmin.setVisible(False)
			self.tb_zboxlenmax.setVisible(False)


	#this signal rescales the range of chart with MSD values
	def zoomclick(self):

		#get axis ranges for rescaling with user input check
		if not self.tb_xstart.text().replace(".","",1).isdigit():
			if not self.args.muted:
				QMessageBox.about(self,"MSD Rescale Error","There is a problem with value in Xstart. Using default value Xstart = "+str(self.x[0]))
			xstart = self.x[0]
		else:
			xstart = float(self.tb_xstart.text())
		if not self.tb_xend.text().replace(".","",1).isdigit():
			if not self.args.muted:
				QMessageBox.about(self,"MSD Rescale Error","There is a problem with value in Xend. Using default value Xend = "+str(self.x[-1]))
			xend = self.x[-1]
		else:
			xend = float(self.tb_xend.text())

		#found y values for selected xrange
		ystart = self.y[0]
		for i in range(0,len(self.x)):
			if xstart < self.x[i]:
				ystart = self.y[i]
				break
		yend = self.y[:]
		for i in range(0,len(self.x)):
			print("xi:{} xend:{}".format(self.x[i],xend))
			if xend <= self.x[i]:
				yend = self.y[i]
				break

		#replot chart with new axis range
		self.m.plot(self.x,self.y,self.r1,xstart,xend,ystart,yend)


	def fileQuit(self):
		self.close()

	def closeEvent(self, ce):
		self.fileQuit()

	def help(self):
		QMessageBox.about(self, "Help","""This application calculates diffusion from input *.xyz file.\n
			\nsteps:
			\n1. Click on Load XYZ file button and choose input file in *.xyz file format.
			\n2. Choose logarithmic or normal scale with radio button under Calculate MSD button
			\n3. If your *.xyz data uses Periodic Boundary Conditions then check checkbox with Periodic Boundaries? label
			\n4. Write simulation box lenghts to newly visible textareas. If you left boxes empty then application will try to find simulation box lenghts by itself.
			\n5. Click Calculate MSD box and wait for calculation to finish. If you don't want to wait then cancel the calculation with Cancel button on progress bar.
			\n6. If you want to see data in specific time interval only then write the beginning and end of time interval in textboxes under Rescale plot button
			\n7. Click Rescale plot button and try to find the most linear time range
			\n8. Choose the beginning and end of timer interval and specify this range to Tstart and Tend textboxes.
			\n9. Click Calculate diffusion button and write down the result of calculation. If you want more precise result then try to find time interval that brings a parameter closer to 1.0""")

	@pyqtSlot()



	#------------------------------------------------------------
	# procedure that exports chart with MSD to PNG picture file |
	#------------------------------------------------------------
	def exfig_click(self):

		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fnout, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()", "","PNG files (*.png);;All Files (*)", options=options)
		self.m.export(fnout)



	#--------------------------------------------------------------------------------------------------------
	# procedure that loads file adress of .xyz file with configurations and checks validity of data in file |
	#--------------------------------------------------------------------------------------------------------
	def load_click(self):

		#create Open File Dialog
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		self.fnin, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Data Files (*.data)", options=options)

		#if user didn't cancle selection
		if self.fnin != "":

			#===========================================================
			# space for validity checking of data in file
			#===========================================================

			#QT elements enabling
			self.r1.setEnabled(True)
			self.r2.setEnabled(True)
			self.button_msd.setEnabled(True)

			#information for user - file is correctly loaded
			self.l3.setText("XYZ Loaded")
			if not self.args.muted:
				QMessageBox.about(self, "File Loaded", "You're .XYZ file was successfully loaded... Click OK to continue.")

		#QT elements enabling
		self.chbPBC.setEnabled(True)
		self.btn_zoom.setEnabled(False)
		self.tb_xstart.setEnabled(False)
		self.tb_xend.setEnabled(False)
		#self.tb_ystart.setEnabled(False)
		#self.tb_yend.setEnabled(False)
		self.button_dif.setEnabled(False)
		self.tb_tstart.setEnabled(False)
		self.tb_tend.setEnabled(False)


	#----------------------------------
	# Diffusion calculation procedure |
	#----------------------------------
	def diff_click(self):

		#polynomial function for fitting
		def fit_func(x,k,q,a):
			return k*x**a + q

		#lists with time/MSD values for calculating diffusion
		diff_x = []
		diff_y = []

		#get start time for MSD and end time for MSD
		if not self.tb_tstart.text().isdigit() and not self.args.muted:
			QMessageBox.about(self,"Time Range Error", "There is a problem with value in Tstart. Using default value Tstart = "+str(self.x[0]))
		if not self.tb_tend.text().isdigit() and not self.args.muted:
			QMessageBox.about(self,"Time Range Error", "There is a problem with value in Tend. Using default value Tend = "+str(self.x[-1]))
		if self.tb_tstart.text() != "" and self.tb_tstart.text().isdigit():
			tstart = int(self.tb_tstart.text())
			if tstart < int(self.x[0] and not self.args.muted):
				QMessageBox.about(self,"Time Range Error", "You have chosen lower value of Tstart then exists in your input file. Using default value Tstart = "+str(self.x[0]))
		else:
			tstart = int(self.x[0])
		if self.tb_tend.text() != "" and self.tb_tend.text().isdigit():
			tend = int(self.tb_tend.text())
			if tend > int(self.x[-1]) and not self.args.muted:
				QMessageBox.about(self,"Time Range Error","You have chosen higher value of Tend then exists in your input file. Using default value Tend = "+str(self.x[-1]))
		else:
			tend = int(self.x[-1])

		#if tstart is >= tend error check
		if tstart - tend >= 0 and not self.args.muted:
			QMessageBox.about(self,"Time Range Error","You have chosen higher tstart = {} then tend = {} or equal values. Using default value Tstar = {} and Tend = {}".format(tstart,tend,self.x[0],self.x[-1]))
			tstart = int(self.x[0])
			tend = int(self.x[-1])

		#get user-specified/default range for diffusion calculation
		for i in range(len(self.x)):
			if int(self.x[i]) >= tstart and int(self.x[i]) <= tend:
				diff_x.append(float(self.x[i]))
				diff_y.append(float(self.y[i]))

		#fit MSD with polynomial
		try:
			params = curve_fit(fit_func,diff_x,diff_y)
		except:
			if not self.args.muted:
				QMessageBox.about(self,"Diffusion Calculation Error","Cant calculate diffusion on specified time range. Try another time range.")
		k = params[0][0]
		q = params[0][1]
		a = params[0][2]
		k = np.polyfit(diff_x,diff_y,1)

		#diffusion calculation
		d = k/(6.0)

		#print diffusion result to user
		QMessageBox.about(self, "Diffusion Result", "Fitting polynomial kx^a + q \n\na = {}  \nDiffusion = {}".format(round(a,4),round(d[0],4)))



	#------------------------------------------------------
	# procedure that calculates Mean-Squared Displacement |
	#------------------------------------------------------
	def msd_click(self):

		fin = open(self.fnin,"r")

		#create progress bar for calculation progress
		MainWindow = QWidget()
		progress = QProgressDialog("Please Wait!", "Cancel", 0, 100, MainWindow)
		progress.setWindowModality(QtCore.Qt.WindowModal)
		progress.setAutoReset(True)
		progress.setAutoClose(True)
		progress.setMinimum(0)
		progress.setMaximum(100)
		progress.resize(500,100)

		#get the number of configurations in .xyz file
		nt = 0
		natoms = 0
		for line in fin:
			data = line.split()
			if len(data) == 1:
				natoms = int(data[0])
			elif len(data) == 3:
				nt += 1
		fin.seek(0)

		#load all configurations in .xyz to memory
		r = [[[0.0 for idim in range(3)] for itime in range(nt)] for ia in range(natoms)]
		time = [0 for itime in range(nt-1)]
		it = -1
		ia = 0
		xboxlenmin = math.inf
		yboxlenmin = math.inf
		zboxlenmin = math.inf
		xboxlenmax = -math.inf
		yboxlenmax = -math.inf
		zboxlenmax = -math.inf
		for line in fin:
			data = line.split()
			if len(data) == 4:

				#parse line in xyz file
				r[ia][it][0] = float(data[1])
				r[ia][it][1] = float(data[2])
				r[ia][it][2] = float(data[3])

				#find max and min particle coordinates - automatic PBC detection
				if xboxlenmin > r[ia][it][0]:
					xboxlenmin = r[ia][it][0]
				if yboxlenmin > r[ia][it][1]:
					yboxlenmin = r[ia][it][1]
				if zboxlenmin > r[ia][it][2]:
					zboxlenmin = r[ia][it][2]
				if xboxlenmax < r[ia][it][0]:
					xboxlenmax = r[ia][it][0]
				if yboxlenmax < r[ia][it][1]:
					yboxlenmax = r[ia][it][1]
				if zboxlenmax < r[ia][it][2]:
					zboxlenmax = r[ia][it][2]

				#particle id increment
				ia += 1

			#next configuration in new time
			if len(data) == 3:
				it += 1
				ia = 0
				if it < nt-1:
					time[it] = int(data[2])

		#if xyz is used with periodic boundary conditions
		if self.chbPBC.isChecked():
			if self.tb_xboxlenmin.text().replace(".","",1).isdigit():
				xboxlenmin = float(self.tb_xboxlenmin.text())
			else:
				self.tb_xboxlenmin.setText(str(xboxlenmin))
			if self.tb_xboxlenmax.text().replace(".","",1).isdigit():
				xboxlenmax = float(self.tb_xboxlenmax.text())
			else:
				self.tb_xboxlenmax.setText(str(xboxlenmax))
			if self.tb_yboxlenmin.text().replace(".","",1).isdigit():
				yboxlenmin = float(self.tb_yboxlenmin.text())
			else:
				self.tb_yboxlenmin.setText(str(yboxlenmin))
			if self.tb_yboxlenmax.text().replace(".","",1).isdigit():
				yboxlenmax = float(self.tb_yboxlenmax.text())
			else:
				self.tb_yboxlenmax.setText(str(yboxlenmax))
			if self.tb_zboxlenmin.text().replace(".","",1).isdigit():
				zboxlenmin = float(self.tb_zboxlenmin.text())
			else:
				self.tb_zboxlenmin.setText(str(zboxlenmin))
			if self.tb_zboxlenmax.text().replace(".","",1).isdigit():
				zboxlenmax = float(self.tb_zboxlenmax.text())
			else:
				self.tb_zboxlenmax.setText(str(zboxlenmax))

		#calculate box lenghts
		boxlen = [xboxlenmax - xboxlenmin,yboxlenmax-yboxlenmin,zboxlenmax-zboxlenmin]

		#get rid of periodic boundary conditions
		pcanceled = False
		if self.chbPBC.isChecked():
			progress.setWindowTitle("Configurations loading")
			progress.show()
			for it in range(nt-1):

				#status bar actualization
				QApplication.processEvents()
				progress.setValue(int(float(it)/(nt-1)*100))

				#if user clicked cancel button on progress dialog then cancel PBC expanding
				if progress.wasCanceled():
					pcanceled = True
					break

				for ia in range(natoms):
					for idim in range(3):
						r0 = r[ia][it][idim]
						r1 = r[ia][it+1][idim]
						if abs(r0-r1) >= boxlen[idim]/2.0:
							if r0 > r1:
								for it_tmp in range(it+1,nt):
									r[ia][it_tmp][idim] = r[ia][it_tmp][idim] + boxlen[idim]
							elif r0 < r1:
								for it_tmp in range(it+1,nt):
									r[ia][it_tmp][idim] = r[ia][it_tmp][idim] - boxlen[idim]

			progress.hide()

		#calculate Mean-Squared Displacement
		progress.setWindowTitle("MSD calculation")
		progress.show()
		msd = [0.0]*(nt-1)
		for ia in range(natoms):

			#status bar actualization
			QApplication.processEvents()
			if ia % 10 == 0:
				progress.setValue(int(ia/natoms*100))

			#if user clicked cancel button on progress dialog then cancel MSD calculations
			if pcanceled or progress.wasCanceled():
				break


			ri = r[ia][:][:]
			for it in range(nt-1):
				nnt = nt-it
				for idim in range(3):
					x2sum = 0.0
					for dt in range(nnt):
						x2sum += (ri[dt][idim] - ri[it+dt][idim])**2
					msd[it] += x2sum/float(nnt)
		for it in range(nt-1):
			msd[it] = msd[it]/float(natoms)

		#setting axis ranges
		self.xmin = time[0]
		self.xmax = time[-1]
		self.ymin = msd[0]
		self.ymax = msd[-1]

		#plot calculated MSD
		self.m.plot(time,msd,self.r1,self.xmin,self.xmax,self.ymin,self.ymax)

		#enable button for diffusion calculation
		self.button_dif.setEnabled(True)

		#save MSD chart data to global variables
		self.x = time
		self.y = msd

		#hide progress bar
		progress.setValue(100)
		progress.hide()

		#QT elements enabling
		self.tb_tstart.setEnabled(True)
		self.tb_tend.setEnabled(True)
		self.tb_xstart.setEnabled(True)
		self.tb_xend.setEnabled(True)
		self.btn_zoom.setEnabled(True)
		self.button_dif.setEnabled(True)



class PlotCanvas(FigureCanvas):

	def __init__(self, parent=None, width=5, height=4, dpi=100):
		fig = Figure(figsize=(width, height), dpi=dpi)

		self.axes = fig.add_subplot(111)
		self.axes.hold(False)

		FigureCanvas.__init__(self, fig)
		self.setParent(parent)

		FigureCanvas.setSizePolicy(self,QSizePolicy.Expanding,QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)
		#self.plot()


	def plot(self,x,y,r1,xmin,xmax,ymin,ymax):

		#
		ax = self.figure.add_subplot(111)
		ax.set_autoscalex_on(False)
		ax.set_autoscaley_on(False)

		#scale type
		if r1.isChecked():
			ax.plot(x,y,'b-')
			ax.set_xscale('log')
			ax.set_yscale('log')
			ax.set_xlim([xmin,xmax])
			ax.set_ylim([ymin,ymax])
		else:
			ax.plot(x,y,'b-')
			ax.set_xlim([xmin,xmax])
			ax.set_ylim([ymin,ymax])
			ax.set_xscale('linear')
			ax.set_yscale('linear')
			ax.ticklabel_format(style='sci',axis='both', scilimits=(-2,2))

		#labels
		ax.grid()
		ax.set_title('Mean Squared Displacement')
		ax.set_xlabel('t')
		ax.set_ylabel('MSD')
		self.draw()

	def export(self,path):
		self.figure.	savefig(path)

if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = App()
	sys.exit(app.exec_())
