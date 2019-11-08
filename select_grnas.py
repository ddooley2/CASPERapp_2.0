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

        #--------------table stuff---------------------------
        self.grna_table.setColumnCount(4)
        self.grna_table.setShowGrid(False)
        self.grna_table.setHorizontalHeaderLabels(['GRNA ID', 'Sequence', 'Organism', 'Relatedness Score'])
        self.grna_table.horizontalHeader().setSectionsClickable(True)
        self.grna_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.grna_table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.grna_table.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.grna_table.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.grna_table.resizeColumnsToContents()
        #--------------end table stuff-----------------------



    """
        launch: this function launches the window.
        takes the data and loads the table
    """
    def launch(self, calling_window, grna_data):
        self.vip_window = calling_window
        self.seq_data = grna_data
        self.load_table_data()
        self.show()

    """
        return_func: this function is the back button. Just goes back to CASPER_VIP
    """
    def return_func(self):
        self.hide()
        self.vip_window.show()

    """
        submit_func: to submits the selected GRNAs to the casper-vip window
    """
    def submit_func(self):
        print("I need to submit now!")

    """
        load_table_data: this function loads all the data into the table
    """    
    def load_table_data(self):
        counter = 1
        # for now, counter is a temp-id
        row_index = 0

        for item in self.seq_data:
            if item != 'Sequence' and self.seq_data[item][0][1] != '0':
                self.grna_table.setRowCount(row_index + 1)

                # get the widgets
                tab_id = QtWidgets.QTableWidgetItem()
                tab_sequence = QtWidgets.QTableWidgetItem() 
                tab_org = QtWidgets.QTableWidgetItem()   
                tab_relate = QtWidgets.QTableWidgetItem()

                # set the data we need
                tab_id.setData(QtCore.Qt.EditRole, counter)
                tab_sequence.setData(QtCore.Qt.EditRole, item)
                tab_org.setData(QtCore.Qt.EditRole, self.seq_data[item][0][2])
                tab_relate.setData(QtCore.Qt.EditRole, self.seq_data[item][0][3])

                # now set the items in the table
                self.grna_table.setItem(row_index, 0, tab_id)
                self.grna_table.setItem(row_index, 1, tab_sequence)
                self.grna_table.setItem(row_index, 2, tab_org)
                self.grna_table.setItem(row_index, 3, tab_relate)

                for tup in self.seq_data[item]:
                    print('\t', tup)

                counter += 1
                row_index += 1

        self.grna_table.resizeColumnsToContents()