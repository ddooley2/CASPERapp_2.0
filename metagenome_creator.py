from PyQt5 import QtWidgets, Qt, QtGui, QtCore, uic
import GlobalSettings
import os
import Algorithms
from functools import partial


###############################################################################
# class name: metagenome_creator
# This window allows the user to create metagenomic CSPR files
# Combines FNA files selected, and then runs the sequencer. Creates 1 CSPR file with all FNA/Fasta files in it
###############################################################################
class metagenome_creator(QtWidgets.QDialog):
    def __init__(self):
        # Qt init stuff
        super(metagenome_creator, self).__init__()
        uic.loadUi('metagenome_creator.ui', self)
        self.setWindowTitle("Metagenome Creator")
        self.setWindowIcon(Qt.QIcon("cas9image.png"))
        self.seq_progress.setValue(0)

        # button connections
        self.cancel_button.clicked.connect(self.cancel_function)
        self.ncbi_searcher.clicked.connect(self.launch_ncbi_searcher)
        self.create_button.clicked.connect(self.create_meta)

        # variables
        self.Endos = dict()
        self.fna_files = dict()
        self.proc = 1 # initialized here, but will be changed to a QProcess on launch
        self.proc_running = False
        self.chrom_list = list()
        self.sq = Algorithms.SeqTranslate()

        # fna table stuff
        self.fasta_table.setColumnCount(1)
        self.fasta_table.setShowGrid(False)
        self.fasta_table.setHorizontalHeaderLabels(["Organism"])
        self.fasta_table.horizontalHeader().setSectionsClickable(True)
        self.fasta_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.fasta_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.fasta_table.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.fasta_table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)

        # update the endo drop down menu
        self.fillEndo()

    """
        create_meta: this function makes sure all the inputs are correct
                and begins the process of creating a meta genomic cspr file
    """
    def create_meta(self):
        # if the process is already running, just return
        if self.proc_running:
            return

        # make sure the name/code/number of orgs is give
        if self.org_name.text() == '' or self.org_code.text() == '' or self.num_of_orgs.text() == '':
            QtWidgets.QMessageBox.question(self, "Missing Information",
                                           "Please input an Organism Name, an Organism Code, and the number of Organisms you are analyzing.",
                                           QtWidgets.QMessageBox.Ok)
            return
        
        # make sure the number of orgs is actually a digit
        if not self.num_of_orgs.text().isdigit():
            QtWidgets.QMessageBox.question(self, "Error",
                                           "Organism Number must be integers only!",
                                           QtWidgets.QMessageBox.Ok)
            return

        # make sure they actually select an endonuclease
        if self.endoBox.currentText() == 'None Selected':
            QtWidgets.QMessageBox.question(self, "Error",
                                            "Please select an endonuclease.",
                                            QtWidgets.QMessageBox.Ok)
            return

        # error check the organism selection
        selected_list = self.fasta_table.selectedItems()
        if len(selected_list) == 0:
            QtWidgets.QMessageBox.question(self, "Error",
                                            "Please choose at least 1 Fasta/FNA file!",
                                            QtWidgets.QMessageBox.Ok)
            return
        
        self.seq_progress.setValue(0)
        self.combine_fna_files()
        self.build_new_cspr_file()

    def build_new_cspr_file(self):
        self.num_chromo_next = False
        self.num_chromo = 0
        # this function reads output. Just used to populate the progress bar
        def output_stdout(p):
            line = str(p.readAll())
            line = line[2:]
            line = line[:len(line) - 1]
            for lines in filter(None, line.split(r'\r\n')):
                if (lines == 'Finished reading in the genome file.'):
                    self.num_chromo_next = True
                elif (self.num_chromo_next == True):
                    self.num_chromo_next = False
                    self.num_chromo = int(lines)
                elif (lines.find('Chromosome') != -1 and lines.find('complete.') != -1):
                    temp = lines
                    temp = temp.replace('Chromosome ', '')
                    temp = temp.replace(' complete.', '')
                    if (int(temp) == self.num_chromo):
                        self.seq_progress.setValue(99)
                    else:
                        self.seq_progress.setValue(int(temp) / self.num_chromo * 100)
                elif (lines == 'Finished Creating File.'):
                    self.seq_progress.setValue(100)
        # what to do when the process is finished
        def finished():
            self.proc_running = False
            os.remove(GlobalSettings.CSPR_DB + os.path.sep + 'temp.fna')
            self.proc.kill()
            self.cancel_function()


        #------------getting the arguments----------------------
        # path to the fna file used
        fna_file_path = GlobalSettings.CSPR_DB + os.path.sep + 'temp.fna'

        # endo and pam
        endo_choice = self.endoBox.currentText().split(' ')[0]
        pam = self.sq.endo_info[endo_choice][0].split(',')[0]

        # code and pamdir
        code = self.org_code.text()
        if int(self.sq.endo_info[endo_choice][3]) == 3:
            pamdir = False
        else:
            pamdir = True

        # output location
        output_location = GlobalSettings.CSPR_DB

        path_to_info = GlobalSettings.appdir + os.path.sep + 'CASPERinfo'
        orgName = self.org_name.text() + ' , (meta), ' +  self.num_of_orgs.text()
        gRNA_length = self.sq.endo_info[endo_choice][2]
        seed_length = self.sq.endo_info[endo_choice][1]

        # get the second code - basically every chromosome
        second_code = ''
        for i in range(len(self.chrom_list)):
            second_code = second_code + self.chrom_list[i][0] + ',' + self.chrom_list[i][1] + '|'
            second_code = second_code.replace('\n', '')
        #------------done getting the arugments-----------------
        
        program = '"' + GlobalSettings.appdir + os.path.sep + 'Casper_Seq_Finder_Windows' + '" '
        
        # combine the args into the program
        args =  '"' + endo_choice + '" '
        args = args + '"' + pam + '" '
        args = args + '"' + code + '" '
        args = args + str(pamdir) + ' '
        args = args + '"' + output_location + '" '
        args = args + '"' + path_to_info + '" '
        args = args + '"' + fna_file_path + '" '
        args = args + '"' + orgName + '" '
        args = args + gRNA_length + ' '
        args = args + seed_length + ' '
        args = args + '"' + second_code + '"'
        program = program + args

        self.proc.readyReadStandardOutput.connect(partial(output_stdout, self.proc))
        self.proc_running = True
        self.proc.start(program)
        self.proc.finished.connect(finished)

    """
        combine_fna_files: this function combines all the fasta/fna files
                selected into 1 temp file
    """
    def combine_fna_files(self):
        self.chrom_list.clear()
        combined_fna_file = GlobalSettings.CSPR_DB + os.path.sep + 'temp.fna'

        # get the files selected
        selected_list = self.fasta_table.selectedItems()
        fna_keys = list()
        for item in selected_list:
            fna_keys.append(item.text())

        # now loop for each file
        fp = open(combined_fna_file, 'w')
        for key in fna_keys:
            fp2 = open(self.fna_files[key], 'r')

            # get the organism name
            buf = fp2.readline()
            spaceIndex = buf.find(' ') + 1
            commaIndex = buf.find(',')
            orgName = buf[spaceIndex:commaIndex]

            # copy the data over
            while buf != "":
                if buf == '' or buf == '\n':
                    break
                
                # update the chromosome list as we go
                if buf.startswith('>'):
                    self.chrom_list.append((orgName, buf))

                fp.write(buf)
                buf = fp2.readline()
            fp2.close()

        fp.close()

    # for when the user clicks the 'x' button
    def closeEvent(self, event):
        closeWindow = self.cancel_function()

        # if the user is doing OT and does not decide to cancel it ignore the event
        if closeWindow == -2:
            event.ignore()
        else:
            event.accept()

    # launches the NCBI_Searcher window
    def launch_ncbi_searcher(self):
        GlobalSettings.mainWindow.ncbi_search_dialog.searchProgressBar.setValue(0)
        GlobalSettings.mainWindow.ncbi_search_dialog.show()

    """
        cancel_function: stops the process, and gets everything cleared up
            Also hides the window
    """
    def cancel_function(self):
        # if the procress is running, make sure to alert the user
        if self.proc_running:
            error = QtWidgets.QMessageBox.question(self, "Sequencer is Running",
                                                   "Sequencer is running. Closing this window will cancel that process, and return to the Population Analysis window. .\n\n"
                                                   "Do you wish to continue?",
                                                   QtWidgets.QMessageBox.Yes |
                                                   QtWidgets.QMessageBox.No,
                                                   QtWidgets.QMessageBox.No)
            if (error == QtWidgets.QMessageBox.No):
                return -2
            else:
                self.proc_running = False
                self.proc.kill()

        self.org_name.setText('')
        self.org_code.setText('')
        self.num_of_orgs.setText('')
        self.seq_progress.setValue(0)
        self.hide()

    """
        launch: this function will be called whenever the window is opened
            It will get the window ready for use
    """
    def launch(self):
        self.proc = QtCore.QProcess()
        self.proc_running = False
        self.fill_fasta_table()
        self.show()

    """
        fill_fasta_table: 
            this function fills the fna/fasta table with all of the 
            fasta/fna files in the CSPR_DB folder
            Should be called upon loading the window, and when the 
            NCBI_Searcher window downloads files.
    """
    def fill_fasta_table(self):
        onlyfiles = [f for f in os.listdir(GlobalSettings.CSPR_DB) if os.path.isfile(os.path.join(GlobalSettings.CSPR_DB, f))]
        self.fna_files.clear()

        index = 0
        for file in onlyfiles:
            if file.find('.fna') != -1 or file.find('.fasta') != -1:
                f = open(file, 'r')
                hold = f.readline()
                f.close()

                spaceIndex = hold.find(' ') + 1
                commaIndex = hold.find(',')
                buf = hold[spaceIndex:commaIndex]

                self.fna_files[buf] = file
                tabWidget = QtWidgets.QTableWidgetItem(buf)
                self.fasta_table.setRowCount(index + 1)
                self.fasta_table.setItem(index, 0, tabWidget)
                index += 1

        if index == 0:
            self.fasta_table.clearContents()
            self.fasta_table.setRowCount(0)

        self.fasta_table.resizeColumnsToContents()

    """
        fillEndo: opens the CASPERinfo file and gets the 
            Endonuclease options out of it.
        Should only be called on init
    """
    def fillEndo(self):
        if GlobalSettings.OPERATING_SYSTEM_ID == "Windows":
            f = open(GlobalSettings.appdir + "\\CASPERinfo")
        else:
            f = open(GlobalSettings.appdir + "/CASPERinfo")
        while True:
            line = f.readline()
            if line.startswith('ENDONUCLEASES'):
                while True:
                    line = f.readline()
                    if(line[0]=="-"):
                        break
                    line_tokened = line.split(";")
                    endo = line_tokened[0]
                    # Checking to see if there is more than one pam sequence in the list
                    if line_tokened[1].find(",") != -1:
                        p_pam = line_tokened[1].split(",")[0]
                    else:
                        p_pam = line_tokened[1]
                    default_seed_length = line_tokened[2]
                    default_tot_length = line_tokened[3]
                    self.Endos[endo + " PAM: " + p_pam] = (endo, p_pam, default_seed_length, default_tot_length)

                break
        f.close()
        self.endoBox.addItem("None Selected")
        self.endoBox.addItems(self.Endos.keys())