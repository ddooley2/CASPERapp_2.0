from PyQt5 import QtWidgets, Qt, QtGui, QtCore, uic
import GlobalSettings
import os
import Algorithms
from functools import partial
from OT_parser import ot_parser

LIB_PATH_DEFAULT = "Please browse to choose a CSV Library File"
FASTA_LINE_DEFAULT = "Please browse to choose an aligned FASTA file"
OUTPUT_FILE_DEFAULT = "Please choose a file name for output. (leave out the .csv)"

"""
    ot_vip: this window is used in the CASPER VIP window
        It is used to run OT on the sequences from the Lib file against 
        the Metagenmoic CSPR file given to us.
"""
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
        self.browse_button_lib.clicked.connect(self.browse_function_lib)
        self.browse_button_fasta.clicked.connect(self.browse_function_fasta)

        # variables
        self.temp_compressed_file = GlobalSettings.CSPR_DB + os.path.sep + 'temp_comp.txt'
        self.files = dict()
        self.sequences = dict()
        self.sq = Algorithms.SeqTranslate()
        self.process = 1
        self.proc_running = False
        self.off_tol = 0.0
        self.off_max_misMatch = 5
        self.otParser = ot_parser()

        # meta table stuff
        self.meta_table.setColumnCount(1)
        self.meta_table.setShowGrid(False)
        self.meta_table.setHorizontalHeaderLabels(["Organism"])
        self.meta_table.horizontalHeader().setSectionsClickable(True)
        self.meta_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.meta_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.meta_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.meta_table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)

    """
        fill_meta_table: this function fills the meta_table with
            metagenmoic CSPR files
    """
    def fill_meta_table(self):
        # get the files in the CSPR_DB folder
        onlyfiles = [f for f in os.listdir(GlobalSettings.CSPR_DB) if os.path.isfile(os.path.join(GlobalSettings.CSPR_DB, f))]
        index = 0

        # go through each file
        for file in onlyfiles:
            # only work with cspr files
            if file.find('.cspr') != -1:
                # get the first line of the file
                fp = open(file, 'r')
                hold = fp.readline()
                fp.close()

                # only work with metagenomic cspr files
                if '(meta)' in hold:
                    # get the orgName and set the data in files
                    colonIndex = hold.find(':') + 1
                    commaIndex = hold.find(',')
                    orgName = hold[colonIndex:commaIndex]
                    self.files[orgName] = file

                    # set the data in the table
                    tabWidget = QtWidgets.QTableWidgetItem(orgName)
                    self.meta_table.setRowCount(index + 1)
                    self.meta_table.setItem(index, 0, tabWidget)
                    index += 1

        # if none are found
        if index == 0:
            self.meta_table.clearContents()
            self.meta_table.setRowCount(0)

        self.meta_table.resizeColumnsToContents()

    # sets the correct settings and opens the window
    def launch(self):
        self.fill_meta_table()
        self.process = QtCore.QProcess()
        self.proc_running = False
        self.progressBar.setValue(0)
        self.show()

    """
        browse_function_faste: this function allows the user to browse for an aligned fasta file
    """
    def browse_function_fasta(self):
        filed = QtWidgets.QFileDialog()
        myFile = QtWidgets.QFileDialog.getOpenFileName(filed, "Choose an aligned FASTA file")

        if not myFile[0].endswith('.fasta'):
            QtWidgets.QMessageBox.question(self, "Wrong type of file selected",
                                           "Please only select a FASTA file!",
                                           QtWidgets.QMessageBox.Ok)
            self.fasta_line.setText(FASTA_LINE_DEFAULT)
            return

        if myFile[0] != "":
            self.fasta_line.setText(myFile[0])

    """
        browse_function: this function allows the user to search for a CSV lib file.
        This function is for browsing for the CSV Lib file
    """
    def browse_function_lib(self):
        # get the file the user searched for
        filed = QtWidgets.QFileDialog()
        myFile = QtWidgets.QFileDialog.getOpenFileName(filed, "Choose a CSV Library File!")

        # make sure it's a CSV file
        if not myFile[0].endswith('.csv'):
            QtWidgets.QMessageBox.question(self, "Wrong type of file selected",
                                           "Please only select a CSV file!",
                                           QtWidgets.QMessageBox.Ok)
            self.lib_path.setText(LIB_PATH_DEFAULT)
            return

        # update the lib_path if it's not empty
        if myFile[0] != "":
            self.lib_path.setText(myFile[0])

        self.parse_lib_file()

    """
        parse_lib_file: this file parses the Library File
        NOTE: It expects a CSV file generated by Generate Library
            WITH all the data outputed
    """
    def parse_lib_file(self):
        self.sequences.clear()

        # try to read the file
        try:
            # read in everything
            fp = open(self.lib_path.text(), 'r')
            buf = fp.readline()
            while buf != '':
                # get rid of the \n
                buf = buf.replace('\n', '')
                
                # split it up, and ignore the first one
                temp_list = buf.split(',')
                if temp_list[0] != 'Gene Name':
                    # get the sequence and store the rest of the data
                    key_data = temp_list[1]
                    if key_data not in self.sequences:
                        self.sequences[key_data] = [temp_list[0], temp_list[1], temp_list[2], temp_list[3], temp_list[4], temp_list[5]]
                buf = fp.readline()
        # excetpion for permission error
        except PermissionError:
            QtWidgets.QMessageBox.question(self, "File Cannot Open",
                                           "This file cannot be opened. Please make sure that the file is not opened elsewhere and try again.",
                                           QtWidgets.QMessageBox.Ok)
            return 
        # any other exception
        except Exception as e:
            # throw the error, and alert the user.
            print(e)
            QtWidgets.QMessageBox.question(self, "Error",
                                           "This file could not be parsed by our program.\nPlease make sure that it is a CSV file from our Generate Library functionality with the 'Output All Data' option selected!",
                                           QtWidgets.QMessageBox.Ok)
            self.lib_path.setText(LIB_PATH_DEFAULT)
            fp.close()
            return
        fp.close()

    # if the user clicks the red X button
    def closeEvent(self, event):
        closeWindow = self.cancel_function()

        if closeWindow == -2:
            event.ignore()
        else:
            event.accept()

    # cancel function - resets everything and hides the window
    def cancel_function(self):

        # if the process is running, warn the user
        if self.proc_running:
            error = QtWidgets.QMessageBox.question(self, "Off-Targeting is running",
                                            "Off-Targetting is running. Closing this window will cancel that process, and return to the main window. .\n\n"
                                            "Do you wish to continue?",
                                            QtWidgets.QMessageBox.Yes |
                                            QtWidgets.QMessageBox.No,
                                            QtWidgets.QMessageBox.No)
            if (error == QtWidgets.QMessageBox.No):
                    return -2
            else:
                self.proc_running = False
                self.process.kill()

        self.lib_path.setText(LIB_PATH_DEFAULT)
        self.fasta_line.setText(FASTA_LINE_DEFAULT)
        self.output_file_edit.setText(OUTPUT_FILE_DEFAULT)
        self.meta_table.clearContents()
        self.progressBar.setValue(0)
        self.meta_table.setRowCount(0)
        self.hide()

    def start_function(self):
        # do nothing if the process is already running
        if self.proc_running == True:
            return
        
        selected_list = self.meta_table.selectedItems()

        # make sure at least 1 and no more than 1 metagenomic file is selected
        if len(selected_list) > 1 or len(selected_list) == 0:
            QtWidgets.QMessageBox.question(self, "Error",
                        "Only 1 meta genomic file is allowed to be used!",
                        QtWidgets.QMessageBox.Ok)
            return

        # make sure they've chosen a library file
        if self.lib_path.text() == LIB_PATH_DEFAULT:
            QtWidgets.QMessageBox.question(self, "Error",
                        "Please choose a CSV file created by Generate Library before continuing.",
                        QtWidgets.QMessageBox.Ok)
            return

        # make sure they've chosen a file name
        if self.output_file_edit.text() == OUTPUT_FILE_DEFAULT or self.output_file_edit.text().endswith('.csv'):
            QtWidgets.QMessageBox.question(self, "Error",
                        "Please choose an output file name! (Leave the .csv out)",
                        QtWidgets.QMessageBox.Ok)
            return

        if self.fasta_line.text() == FASTA_LINE_DEFAULT:
            QtWidgets.QMessageBox.question(self, "Error",
                        "Please choose an aligned fasta file!",
                        QtWidgets.QMessageBox.Ok)
            return

        self.compress_file_off()
        self.run_OT(self.files[selected_list[0].text()])

    """
        run_OT: this function builds the commands and actually runs OT
        Parameters:
            cspr_file_path: the path to the cspr file
    """
    def run_OT(self, cspr_file_path):
        self.perc = False
        self.bool_temp = False
        self.running = False
        
        # what should happen when the process is done
        def finished():
            self.progressBar.setValue(100)
            self.proc_running = False
            os.remove(self.temp_compressed_file)
            self.process.kill()

            # run the OT parser, and the close out the window
            self.otParser.appended_file = GlobalSettings.CSPR_DB + os.path.sep + self.output_file_edit.text() + '.csv'
            self.otParser.get_data(GlobalSettings.CSPR_DB + os.path.sep + 'temp_off.txt', cspr_file_path, self.fasta_line.text(), self.sequences)
            os.remove(GlobalSettings.CSPR_DB + os.path.sep + 'temp_off.txt')
            self.cancel_function()

        # update the progress bar
        def progUpdate(p):
            line = str(p.readAllStandardOutput())
            line = line[2:]
            line = line[:len(line) - 1]
            for lines in filter(None, line.split(r'\r\n')):
                if (lines.find("Running Off Target Algorithm for") != -1 and self.perc == False):
                    self.perc = True
                if (self.perc == True and self.bool_temp == False and lines.find(
                        "Running Off Target Algorithm for") == -1):
                    lines = lines[32:]
                    lines = lines.replace("%", "")
                    if (float(lines) <= 99.5):
                        num = float(lines)
                        self.progressBar.setValue(num)
                    else:
                        self.bool_temp = True

        #------------------getting the args------------------------------
        app_path = GlobalSettings.appdir
        exe_path = app_path + os.path.sep + 'OffTargetFolder' + os.path.sep + 'OT'
        exe_path = '"' + exe_path + '" '
        data_path = '"' + GlobalSettings.CSPR_DB.replace('/','\\') + "\\temp_comp.txt" + '" '
        compressed = r' True ' ##
        cspr_path = '"' + cspr_file_path.replace('/', '\\') + '" '
        output_path = '"' + GlobalSettings.CSPR_DB.replace('/','\\') + '\\temp_off.txt" '
        filename = output_path
        filename = filename[:len(filename) - 1]
        filename = filename[1:]
        filename = filename.replace('"', '')
        CASPER_info_path = r' "' + app_path + os.path.sep + 'CASPERinfo' + '" '
        num_of_mismatches = self.off_max_misMatch
        tolerance = self.off_tol
        detailed_output = " True "
        avg_output = " False "
        #------------------done getting args-----------------------------

        # build the command
        cmd = exe_path + data_path + compressed + cspr_path + output_path + CASPER_info_path + str(
            num_of_mismatches) + ' ' + str(tolerance) + detailed_output + avg_output

        # connect the functions and start it
        self.process.readyReadStandardOutput.connect(partial(progUpdate, self.process))
        self.progressBar.setValue(0)
        self.proc_running = True
        QtCore.QTimer.singleShot(100, partial(self.process.start, cmd))
        self.process.finished.connect(finished)
        

    """
        compress_file_file: this function compresses all the data for the
                sequences and outputs it to a file
    """
    def compress_file_off(self):
        fp = open(self.temp_compressed_file, 'w')

        # for each sequence
        for seq in self.sequences:
            # compress the data
            loc = self.sq.compress(int(self.sequences[seq][3]), 64)
            sq = self.sq.compress(seq, 64)
            pam = self.sq.compress(self.sequences[seq][4], 64)
            score = self.sq.compress(int(self.sequences[seq][2]), 64)
            strand = self.sequences[seq][5]

            # output the data
            output = str(loc) + ',' + str(sq) + str(strand) + str(pam) + ',' + score
            fp.write(output + '\n')

        fp.close()