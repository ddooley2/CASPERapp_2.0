from PyQt5 import QtWidgets, Qt, QtGui, QtCore, uic
import GlobalSettings
import os


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

        # variables
        self.Endos = dict()
        self.fna_files = dict()

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

    # launches the NCBI_Searcher window
    def launch_ncbi_searcher(self):
        GlobalSettings.mainWindow.ncbi_search_dialog.searchProgressBar.setValue(0)
        GlobalSettings.mainWindow.ncbi_search_dialog.show()

    """
        cancel_function: stops the process, and gets everything cleared up
            Also hides the window
    """
    def cancel_function(self):
        self.org_name.setText('')
        self.org_code.setText('')
        self.num_of_orgs.setText('')
        self.hide()

    """
        launch: this function will be called whenever the window is opened
            It will get the window ready for use
    """
    def launch(self):
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
                commaIndex = hold.find(',') + 1
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