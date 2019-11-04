import os
from PyQt5 import QtWidgets, Qt, QtGui, QtCore, uic
import GlobalSettings
from PyQt5.QtChart import (QBarCategoryAxis,QBarSet, QChartView, QBarSeries,QChart,QLineSeries, QValueAxis)
from PyQt5.QtGui import QPainter, QBrush, QPen
from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)
from matplotlib.backends.backend_qt5agg import FigureCanvasAgg as FigureCanvas
from matplotlib.ticker import MaxNLocator


"""
    This is the CASPER_VIP class. 
"""
class CASPER_VIP(QtWidgets.QMainWindow):
    def __init__(self, parent=None):

        #------------PyQt init stuff----------------------
        super(CASPER_VIP, self).__init__()
        uic.loadUi('casper_vip.ui', self)
        self.setWindowIcon(QtGui.QIcon('cas9image.png'))
        #-----------end PyQt init stuff--------------------

        #-----------Graph stuff----------------------------
        #self.whole_graph = QChartView()
        #-----------End Graph stuff------------------------

        #--------------button connections--------------------
        self.back_button.clicked.connect(self.go_back)
        self.browse_for_excel_button.clicked.connect(self.browse_csv)
        self.analyze_button.clicked.connect(self.parse_csv)
        #--------------End button connections----------------

        #------------variables-------------------------------
        self.seq_data = dict()
        #------------end variables---------------------------

    """
        launch: this launches the window. For now it just shows the window
    """
    def launch(self):
        self.show()

    """
        go_back: hide the current window and show the main window again
    """
    def go_back(self):
        GlobalSettings.mainWindow.show()
        self.hide()

    """
        browse_csv: allows the user to browse for a csv file
        Only accepts csv files though
    """
    def browse_csv(self):
        filed = QtWidgets.QFileDialog()
        myFile = QtWidgets.QFileDialog.getOpenFileName(filed, "Choose a CSV File!")

        # make sure the user actually chose a CSV file
        if '.csv' not in myFile[0]:
            QtWidgets.QMessageBox.question(self, "Wrong type of file selected",
                                           "Please only select a CSV file!",
                                           QtWidgets.QMessageBox.Ok)
            self.excel_label.setText("Please browse for a CSV file")
            return
        
        # set the file name if it isn't empty
        if (myFile[0] != ""):
            self.excel_label.setText(myFile[0])

    """
        parse_csv: this function will parse the csv file chosen for analysis
    """
    def parse_csv(self):
        # check to make sure they actually have a csv file search
        if self.excel_label.text() == 'Please browse for a CSV file' or self.excel_label.text() == "":
            QtWidgets.QMessageBox.question(self, "Nothing to analyze!",
                                           "Please choose a CSV file to analyze",
                                           QtWidgets.QMessageBox.Ok)
            return

        self.seq_data.clear()

        # try opening and reading the file, if not throw and error
        try:
            fp = open(self.excel_label.text())
            file_data = fp.read()
            
            file_data = file_data.split('\n')
            for item in file_data:
                buf = item.split(',')

                if len(buf) > 1:
                    tempTuple = (buf[0], buf[1], buf[2], buf[3])
                    if buf[0] not in self.seq_data:
                        self.seq_data[buf[0]] = list()
                    
                    self.seq_data[buf[0]].append(tempTuple)
        # throw whatever exception occurs
        except Exception as e:
            print(e)
            return
        # now close the file when its finally done
        finally:
            fp.close()
            self.plot_whole_graph()

    """
        plot_whole_graph: this function plots everything from the CSV file. Similar to the first graph in the excel sheet
    """
    def plot_whole_graph(self):
        x1 = []
        y1 = []

        # go through and get the data that we are plotting
        for seed in self.seq_data:
            #print(seed)
            for i in range(len(self.seq_data[seed])):
                #print('\t', self.seq_data[seed][i])

                if(self.seq_data[seed][i][1] != '0') and seed != 'Sequence':
                    x1.append(float(self.seq_data[seed][i][1]))
                    y1.append(float(self.seq_data[seed][i][3]))

        # set the settings for the graph
        self.whole_graph.canvas.axes.clear()
        self.whole_graph.canvas.axes.scatter(x1,y1)
        self.whole_graph.canvas.axes.axis((0,1.2,0,1.2))
        self.whole_graph.canvas.axes.set_title("Some Title here")
        self.whole_graph.canvas.axes.set_xticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
        self.whole_graph.canvas.axes.set_yticks([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
        self.whole_graph.canvas.axes.set_xlabel('Off-Target Score')
        self.whole_graph.canvas.axes.set_ylabel('Relatedness')
        self.whole_graph.canvas.draw()