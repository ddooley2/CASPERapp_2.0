from PyQt5 import QtWidgets, Qt, QtGui, QtCore, uic
import GlobalSettings
import os
import Algorithms
from functools import partial

class ot_vip(QtWidgets.QDialog):
    def __init__(self):
        #Qt init stuff
        super(ot_vip, self).__init__()
        uic.loadUi('ot_vip.ui', self)
        self.setWindowTitle('VIP Off-Targeting')
        self.setWindowIcon(Qt.QIcon("cas9image.png"))
        self.progressBar.setValue(0)

        # button connections
        self.cancel_button.clicked.connect(self.cancel_function)
        self.start_button.clicked.connect(self.start_function)
        self.browse_button.clicked.connect(self.browse_function)

        # variables
        self.temp_compressed_file = GlobalSettings.CSPR_DB + os.path.sep + 'temp_comp.txt'


        # meta table stuff
        self.meta_table.setColumnCount(1)
        self.meta_table.setShowGrid(False)
        self.meta_table.setHorizontalHeaderLabels(["Organism"])
        self.meta_table.horizontalHeader().setSectionsClickable(True)
        self.meta_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.meta_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.meta_table.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.meta_table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)

    def launch(self):
        self.show()

    def browse_function(self):
        print("I should browse now!")

    def cancel_function(self):
        print("I should cancel now!")
        self.hide()

    def start_function(self):
        print("I should start now!")