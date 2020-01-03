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
        self.grna_table.setColumnCount(10)
        self.grna_table.setShowGrid(False)
        self.grna_table.setHorizontalHeaderLabels(['gRNA ID', 'Sequence', 'Number of Hits', 'Select', 'Off-Target Score', 'Gene', 'Location', 'PAM', 'Strand', 'On-Target Score'])
        self.grna_table.horizontalHeader().setSectionsClickable(True)
        self.grna_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.grna_table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.grna_table.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.grna_table.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.grna_table.resizeColumnsToContents()

        self.switcher = [1,1,1,1,1,1,1,1,1,1]
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
            if ckbox[3].isChecked():
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
                tab_hits = QtWidgets.QTableWidgetItem() 
                ckbox = QtWidgets.QCheckBox()
                tab_ot = QtWidgets.QTableWidgetItem()
                tab_gene = QtWidgets.QTableWidgetItem()
                tab_location = QtWidgets.QTableWidgetItem()
                tab_pam = QtWidgets.QTableWidgetItem()
                tab_strand = QtWidgets.QTableWidgetItem()
                tab_onscore = QtWidgets.QTableWidgetItem()

                # set the data we need
                tab_id.setData(QtCore.Qt.EditRole, counter)
                tab_sequence.setData(QtCore.Qt.EditRole, item)
                tab_ot.setData(QtCore.Qt.EditRole, float(self.seq_data[item][0][1]))
                tab_gene.setData(QtCore.Qt.EditRole, self.seq_data[item][0][4])
                tab_location.setData(QtCore.Qt.EditRole, int(self.seq_data[item][0][5]))
                tab_pam.setData(QtCore.Qt.EditRole, self.seq_data[item][0][6])
                tab_strand.setData(QtCore.Qt.EditRole, self.seq_data[item][0][7])
                tab_onscore.setData(QtCore.Qt.EditRole, int(self.seq_data[item][0][8]))
                
                # set the data based on whether or not the grna has a hit or not
                if self.seq_data[item][0][1] == '0':
                    tab_hits.setData(QtCore.Qt.EditRole, 0)
                else: 
                    tab_hits.setData(QtCore.Qt.EditRole, int(len(self.seq_data[item])))
                

                # now set the items in the table
                self.grna_table.setItem(row_index, 0, tab_id)
                self.grna_table.setItem(row_index, 1, tab_sequence)
                self.grna_table.setItem(row_index, 2, tab_hits)
                self.grna_table.setItem(row_index, 4, tab_ot)
                self.grna_table.setItem(row_index, 5, tab_gene)
                self.grna_table.setItem(row_index, 6, tab_location)
                self.grna_table.setItem(row_index, 7, tab_pam)
                self.grna_table.setItem(row_index, 8, tab_strand)
                self.grna_table.setItem(row_index, 9, tab_onscore)

                # store the checkbox and make sure it is in the list as well
                self.grna_table.setCellWidget(row_index, 3, ckbox)
                self.check_boxes.append((tab_id, tab_sequence, tab_hits, ckbox))

                counter += 1
                row_index += 1

        self.grna_table.resizeColumnsToContents()