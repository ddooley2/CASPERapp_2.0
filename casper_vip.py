import os
from PyQt5 import QtWidgets, Qt, QtGui, QtCore, uic
import GlobalSettings
from PyQt5.QtChart import (QBarCategoryAxis,QBarSet, QChartView, QBarSeries,QChart,QLineSeries, QValueAxis)
from PyQt5.QtGui import QPainter, QBrush, QPen
from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)
from matplotlib.backends.backend_qt5agg import FigureCanvasAgg as FigureCanvas
from matplotlib.ticker import MaxNLocator
from select_grnas import sel_grnas
from ot_vip import ot_vip

# these two are constants for the default quality cutoff points. Y is a list because the user cannot edit it, while the user can edit X
DEFAULT_X_COORD = ".05,.2"
DEFAULT_Y_COORD = [0, 1.05]

"""
    This is the CASPER_VIP class. 
"""
class CASPER_VIP(QtWidgets.QMainWindow):
    def __init__(self, parent=None):

        #------------PyQt init stuff----------------------
        super(CASPER_VIP, self).__init__()
        uic.loadUi('casper_vip.ui', self)
        self.setWindowIcon(QtGui.QIcon('cas9image.png'))
        self.setWindowTitle("CASPER VIP")
        #-----------end PyQt init stuff--------------------

        #-----------tool button connections----------------
        self.actionOff_Targeting.triggered.connect(self.launch_ot_window)
        #-----------end tool button connections------------

        #------------checkbox trigger connections-----------------------
        self.hide_selected_legend.stateChanged.connect(self.select_legend_hider)
        self.hide_total_legend.stateChanged.connect(self.total_legend_hider)
        #------------end checkox trigger connections--------------------

        #--------------button connections--------------------
        self.back_button.clicked.connect(self.go_back)
        self.browse_for_excel_button.clicked.connect(self.browse_csv)
        self.analyze_button.clicked.connect(self.prep_analyze)
        self.select_individ_grnas.clicked.connect(self.launch_sel_grnas)
        self.clear_selected_graph_button.clicked.connect(self.clear_selected_graph)
        self.clear_total_graph_button.clicked.connect(self.clear_total_graph)
        #--------------End button connections----------------

        #------------variables-------------------------------
        self.seq_data = dict()
        self.grna_data = dict()
        self.org_relate_data = dict()
        self.select_window = sel_grnas()
        self.ot_window = ot_vip()
        #------------end variables---------------------------

    def launch_ot_window(self):
        self.ot_window.launch()

    # this is needed to get the graph to work
    def prep_analyze(self):
        self.parse_csv()

    """
        select_legend_hider: the function that the 'hide selected
            gRNA legend' checkbox connects to.
            This function hides the legend if the checkbox is true, shows it if false
    """
    def select_legend_hider(self):
        # if the checkbox if checked, hide the legend and re-draw, otherwise show and re-draw
        if self.hide_selected_legend.isChecked():
            self.selected_grnas_graph.canvas.axes.legend().set_visible(False)
            self.selected_grnas_graph.canvas.draw()
        else:
            self.selected_grnas_graph.canvas.axes.legend().set_visible(True)
            self.selected_grnas_graph.canvas.draw()

    """
        graph_selected_grans: this function will graph the data from the
            select_grnas window
    """
    def graph_selected_grans(self):

        x1 = dict()
        y1 = dict()

        # this is used for the markers
        markers = ['o', 'v', 's', '*', 'x']

        # get each of the seeds and data
        for seed in self.grna_data:
            for i in range(len(self.grna_data[seed])):
                # get the ID
                temp_id = self.grna_data[seed][i][0]

                if temp_id not in x1 and temp_id not in y1:
                    x1[temp_id] = list()
                    y1[temp_id] = list()


                # check to see if they have a hit or not. No hit graph at 0,0, otherwise graph where it should be graphed
                if self.grna_data[seed][i][2] == '0':
                    x1[temp_id].append(0)
                    y1[temp_id].append(0)
                else:
                    x1[temp_id].append(float(self.grna_data[seed][i][2]))
                    y1[temp_id].append(float(self.grna_data[seed][i][4]))

        x_line = self.get_x_coords()
        if x_line == -1:
            return

        self.selected_grnas_graph.canvas.axes.clear()

        # sort the organisms, and graph the relatadness
        sorted_data = sorted(self.org_relate_data.items(), key=lambda x: x[1], reverse=True)
        for org in sorted_data:
            # do some math to set the color correctly
            self.selected_grnas_graph.canvas.axes.plot([0,1.05], [org[1], org[1]], label=org[0], color=[1,0 + (org[1]/1.3),0 + (org[1]/1.3)], linewidth=1)

        # graph the specifics
        counter = 0
        for id in x1:
            # if counter is greater than 
            if counter > len(markers) - 1:
                counter = 0
            self.selected_grnas_graph.canvas.axes.scatter(x1[id], y1[id], label=id, marker=markers[counter])
            counter += 1

        # graph the red line
        self.selected_grnas_graph.canvas.axes.plot(x_line, DEFAULT_Y_COORD, color='black')

        
        # set the rest of the settings for the graph
        self.selected_grnas_graph.canvas.axes.legend()
        self.selected_grnas_graph.canvas.axes.grid(True)
        self.selected_grnas_graph.canvas.axes.set_xlim(left=0, right=1.05)
        self.selected_grnas_graph.canvas.axes.set_ylim(bottom=0, top=1.05)
        self.selected_grnas_graph.canvas.axes.set_title("Selected gRNAs")
        self.selected_grnas_graph.canvas.axes.set_xticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
        self.selected_grnas_graph.canvas.axes.set_yticks([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
        self.selected_grnas_graph.canvas.axes.set_xlabel('Off-Target Score')
        self.selected_grnas_graph.canvas.axes.set_ylabel('Phylogenetic Distance')
        self.selected_grnas_graph.canvas.draw()
        self.hide_selected_legend.setEnabled(True)

    """
        prepare the data and launch the select grnas window
    """
    def launch_sel_grnas(self):
        checker = self.parse_csv(show_graph=False)

        if checker == -1:
            return

        self.select_window.launch(self, self.seq_data)
        self.hide()

    """
        launch: this launches the window. For now it just shows the window
    """
    def launch(self):
        self.show()

    # clears just the selected graph -  also sets the checkbox to false
    def clear_total_graph(self):
        self.hide_total_legend.setChecked(False)
        self.total_grnas_graph.canvas.axes.clear()
        self.total_grnas_graph.canvas.draw()
        self.hide_total_legend.setEnabled(False)

    # clears just the selected graph -  also sets the checkbox to false
    def clear_selected_graph(self):
        self.hide_selected_legend.setChecked(False)
        self.selected_grnas_graph.canvas.axes.clear()
        self.selected_grnas_graph.canvas.draw()
        self.hide_selected_legend.setEnabled(False)

    """
        go_back: hide the current window and show the main window again
    """
    def go_back(self):
        GlobalSettings.mainWindow.show()
        self.x_coord_line.setText(DEFAULT_X_COORD)
        self.clear_total_graph()
        self.clear_selected_graph()
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
        Paramters:
            show_graph: whether or not to show the whole graph
    """
    def parse_csv(self, show_graph=True):
        # check to make sure they actually have a csv file search
        if self.excel_label.text() == 'Please browse for a CSV file' or self.excel_label.text() == "":
            QtWidgets.QMessageBox.question(self, "Nothing to analyze!",
                                           "Please choose a CSV file to analyze",
                                           QtWidgets.QMessageBox.Ok)
            return -1

        self.seq_data.clear()

        # try opening and reading the file, if not throw and error
        try:
            fp = open(self.excel_label.text())
            file_data = fp.read()
            
            file_data = file_data.split('\n')
            for item in file_data:
                buf = item.split(',')

                if len(buf) > 1:
                    tempTuple = (buf[0], buf[1], buf[2], buf[3], buf[4], buf[5], buf[6], buf[7], buf[8])
                    if buf[0] not in self.seq_data:
                        self.seq_data[buf[0]] = list()
                    
                    # store the relatedness data for the organism
                    if tempTuple[2] not in self.org_relate_data and tempTuple[2] != 'Organism' and tempTuple[2] != '':
                        self.org_relate_data[tempTuple[2]] = float(tempTuple[3])
                    
                    self.seq_data[buf[0]].append(tempTuple)
        # throw whatever exception occurs
        except Exception as e:
            print(e)
            fp.close()
            QtWidgets.QMessageBox.question(self, "Error!",
                                           "The CSV file could not be parsed. Please make sure to submit a CSV file generated by the Off-Targeting tool.",
                                           QtWidgets.QMessageBox.Ok)
            return -1
        # now close the file when its finally done
        fp.close()
        # only show the graph is the user clicked on analyze
        if show_graph:
            self.plot_whole_graph()

    """
        get_x_coords: this function pulls out the x-coordinates about the editable box 
        Returns: a list: [first x coord, second x coord]
    """
    def get_x_coords(self):
        # split the data and make sure there's 2 items
        coords = self.x_coord_line.text().split(',')
        if len(coords) != 2:
            QtWidgets.QMessageBox.question(self, "Error!",
                                           "Please follow the correct format for the X coordinates. It must be: <x1,x2>.",
                                           QtWidgets.QMessageBox.Ok)
            self.x_coord_line.setText(DEFAULT_X_COORD)
            return -1

        # try and convert both numbers from strings to float
        ret_list = list()
        try:
            for item in coords:
                x = float(item)

                # make sure each item is 0 <= x <= 1
                if x > 1 or x < 0:
                    QtWidgets.QMessageBox.question(self, "Error!",
                                           "Please make sure that each value for X is no greater than 1, and no smaller than 0. So 0 <= x <= 1",
                                           QtWidgets.QMessageBox.Ok)
                    self.x_coord_line.setText(DEFAULT_X_COORD)
                    return -1
                ret_list.append(x)

        # if trying to convert to a float fails, throw an error
        except ValueError:
            QtWidgets.QMessageBox.question(self, "Error!",
                                           "Please make sure only decimal numbers are given!",
                                           QtWidgets.QMessageBox.Ok)
            self.x_coord_line.setText(DEFAULT_X_COORD)
            return -1
        return ret_list

    """
        total_legend_hider: hides the legend in the total_grna_graph in Tab 1
        Hides the legend if the checkbox is checked, shows it if not.
    """
    def total_legend_hider(self):
        # if the checkbox if checked, hide the legend and re-draw, otherwise show and re-draw
        if self.hide_total_legend.isChecked():
            self.total_grnas_graph.canvas.axes.legend().set_visible(False)
            self.total_grnas_graph.canvas.draw()
        else:
            self.total_grnas_graph.canvas.axes.legend().set_visible(True)
            self.total_grnas_graph.canvas.draw()

    """
        plot_whole_graph: this function plots everything from the CSV file. Similar to the first graph in the excel sheet
    """
    def plot_whole_graph(self):
        x1 = dict()
        y1 = dict()

        # this is the red line from the excel spread sheet
        # for now, it's hard coded, but eventually the user will select this as well
        x_line = self.get_x_coords()
        if x_line == -1:
            return

        # go through and get the data that we are plotting
        for seed in self.seq_data:
            for i in range(len(self.seq_data[seed])):
                # get the org name
                temp_org = self.seq_data[seed][i][2]

                # now score the OT score and relatedness score
                if(self.seq_data[seed][i][1] != '0') and seed != 'Sequence':
                    if temp_org not in x1 and temp_org not in y1:
                        x1[temp_org] = list()
                        y1[temp_org] = list()

                    x1[temp_org].append(float(self.seq_data[seed][i][1]))
                    y1[temp_org].append(float(self.seq_data[seed][i][3]))

        # set the settings for the graph
        self.total_grnas_graph.canvas.axes.clear()

        # graph the scatter plot
        for org in x1:
            self.total_grnas_graph.canvas.axes.scatter(x1[org],y1[org], label=org)
            

        # graph the red line
        self.total_grnas_graph.canvas.axes.plot(x_line, DEFAULT_Y_COORD, color='black')

        # set the rest of the settings for the graph
        self.total_grnas_graph.canvas.axes.legend()
        self.total_grnas_graph.canvas.axes.grid(True)
        self.total_grnas_graph.canvas.axes.set_xlim(left=0, right=1.05)
        self.total_grnas_graph.canvas.axes.set_ylim(bottom=0, top=1.05)
        self.total_grnas_graph.canvas.axes.set_title("Total gRNA Set")
        self.total_grnas_graph.canvas.axes.set_xticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
        self.total_grnas_graph.canvas.axes.set_yticks([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
        self.total_grnas_graph.canvas.axes.set_xlabel('Off-Target Score')
        self.total_grnas_graph.canvas.axes.set_ylabel('Phylogenetic Distance')
        self.total_grnas_graph.canvas.draw()
        self.hide_total_legend.setEnabled(True)