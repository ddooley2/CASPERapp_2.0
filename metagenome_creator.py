from PyQt5 import QtWidgets, Qt, QtGui, QtCore, uic
import GlobalSettings
import os

class metagenome_creator(QtWidgets.QDialog):
    def __init__(self):
        # Qt init stuff
        super(metagenome_creator, self).__init__()
        uic.loadUi('metagenome_creator.ui', self)
        self.seq_progress.setValue(0)

        # button connections
        self.cancel_button.clicked.connect(self.cancel_function)

        # variables
        self.Endos = dict()

        # fna table stuff

        # update the endo drop down menu
        self.fillEndo()


    def cancel_function(self):
        self.org_name.setText('')
        self.org_code.setText('')
        self.num_of_orgs.setText('')
        self.hide()

    def launch(self):
        self.show()

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