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
        self.check_boxes = list()
        #--------------end variables-------------------------

        #--------------table stuff---------------------------
        self.grna_table.setColumnCount(5)
        self.grna_table.setShowGrid(False)
        self.grna_table.setHorizontalHeaderLabels(['GRNA ID', 'Sequence', 'Organism', 'Relatedness Score', 'Select'])
        self.grna_table.horizontalHeader().setSectionsClickable(True)
        self.grna_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.grna_table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.grna_table.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.grna_table.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.grna_table.resizeColumnsToContents()

        self.switcher = [1,1,1,1,1]
        self.grna_table.horizontalHeader().sectionClicked.connect(self.sort_table)
        #--------------end table stuff-----------------------


    def sort_table(self, logical_index):
        self.switcher[logical_index] *= -1
        if self.switcher[logical_index] == -1:
            self.grna_table.sortItems(logical_index, QtCore.Qt.DescendingOrder)
        else:
            self.grna_table.sortItems(logical_index, QtCore.Qt.AscendingOrder)

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
        is_one_checked = False
        temp_data = dict()

        # go through for every checkbox
        for ckbox in self.check_boxes:
            if ckbox[4].isChecked():
                # set the error checker
                is_one_checked = True

                # store the right data
                if ckbox[1].text() not in temp_data:
                    temp_data[ckbox[1].text()] = list()

                # now get every single grna as well
                for item in self.seq_data[ckbox[1].text()]:
                    temp_data[ckbox[1].text()].append((ckbox[0].text(), item[0], item[1], item[2], item[3]))

        # make sure the user has selected a grna 
        if not is_one_checked:
            QtWidgets.QMessageBox.question(self, "Nothing to analyze!",
                                           "Please choose at least 1 GRNA to graph!",
                                           QtWidgets.QMessageBox.Ok)
            return -1

        self.vip_window.grna_data = temp_data
        self.grna_table.setRowCount(0)
        self.hide()
        self.vip_window.show()
        self.vip_window.graph_selected_grans()

    """
        load_table_data: this function loads all the data into the table
    """    
    def load_table_data(self):
        counter = 1
        # for now, counter is a temp-id
        row_index = 0
        self.check_boxes.clear()

        for item in self.seq_data:
            if item != 'Sequence':
                self.grna_table.setRowCount(row_index + 1)

                # get the widgets
                tab_id = QtWidgets.QTableWidgetItem()
                tab_sequence = QtWidgets.QTableWidgetItem() 
                tab_org = QtWidgets.QTableWidgetItem()   
                tab_relate = QtWidgets.QTableWidgetItem()
                ckbox = QtWidgets.QCheckBox()

                # set the data we need
                tab_id.setData(QtCore.Qt.EditRole, counter)
                tab_sequence.setData(QtCore.Qt.EditRole, item)

                # set the data based on whether or not the grna has a hit or not
                if self.seq_data[item][0][1] == '0':
                    tab_org.setData(QtCore.Qt.EditRole, 'No Hits')
                    tab_relate.setData(QtCore.Qt.EditRole, 0)
                else: 
                    print(self.seq_data[item])
                    tab_org.setData(QtCore.Qt.EditRole, self.seq_data[item][0][2])
                    tab_relate.setData(QtCore.Qt.EditRole, float(self.seq_data[item][0][3]))

                # now set the items in the table
                self.grna_table.setItem(row_index, 0, tab_id)
                self.grna_table.setItem(row_index, 1, tab_sequence)
                self.grna_table.setItem(row_index, 2, tab_org)
                self.grna_table.setItem(row_index, 3, tab_relate)

                # store the checkbox and make sure it is in the list as well
                self.grna_table.setCellWidget(row_index, 4, ckbox)
                self.check_boxes.append((tab_id, tab_sequence, tab_org, tab_relate, ckbox))

                counter += 1
                row_index += 1

        self.grna_table.resizeColumnsToContents()