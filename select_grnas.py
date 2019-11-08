import GlobalSettings
from PyQt5 import QtWidgets, Qt, QtGui, QtCore, uic


"""
    sel_grnas class: allows the user to select which singular GRNAs they
        want to show in the graph
"""
class sel_grnas(QtWidgets.QMainWindow):
    def __init__(self):
        #-------------PyQt init stuff------------------------
        super(sel_grnas, self).__init__()
        uic.loadUi('select_grnas.ui', self)
        self.setWindowIcon(QtGui.QIcon("cas9image.png"))
        #-------------end init stuff-------------------------

        #--------------button connections--------------------
        self.return_button.clicked.connect(self.return_func)
        self.submit_button.clicked.connect(self.submit_func)
        #--------------End button connections----------------

        #--------------variables-----------------------------
        self.vip_window = 1
        self.seq_data = dict()
        #--------------end variables-------------------------


    def launch(self, calling_window, grna_data):
        self.vip_window = calling_window
        self.seq_data = grna_data
        self.show()

    """
        return_func: this function is the back button. Just goes back to CASPER_VIP
    """
    def return_func(self):
        self.hide()
        self.vip_window.show()

    def submit_func(self):
        print("I need to submit now!")