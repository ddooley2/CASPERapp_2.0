import os
from os.path import isfile, join
import csv
import GlobalSettings


class ot_parser():
    def __init__(self):
        self.dir = GlobalSettings.CSPR_DB + os.path.sep
        self.nt = ['A', 'C', 'G', 'T']
        self.appended_file = self.dir + 'temp_app_file.csv'

        self.offdict = dict()
        self.chromdict = dict()
        self.off_temp = list()
        self.chrom_temp = list()

    def get_data(self, ot_data_path):
        self.offdict.clear()
        self.chromdict.clear()
        self.chrom_temp.clear()
        self.off_temp.clear()
        fp = open(ot_data_path)

        myList = fp.read().splitlines()
        fp.close()
        good_lines = [line for line in myList if line]

        for x in good_lines:
            if x[0] in self.nt:
                if x[21:29] == '0.000000':
                    self.offdict[x[0:19]] = x[21:28]
                else:
                    temp_seq = x[0:19]
                    self.off_temp = []
                    self.chrom_temp = []
            elif x[0] == '0':
                line_temp = [e.strip() for e in x.split(',')]
                self.off_temp.append((line_temp[0]))
                self.chrom_temp.append(line_temp[1])
                self.offdict[temp_seq] = self.off_temp
                self.chromdict[temp_seq] = self.chrom_temp
        
        self.write_data()

    def write_data(self):
        with open(self.appended_file, 'w+') as data_output:
            data_writer = csv.writer(data_output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for key, values in self.offdict.items():
                if float(values[0]) == 0.00000:
                    data_writer.writerow([key, values])
                else:
                    chrom_values = self.chromdict.get(key)
                    for i in range(len(values)):
                        data_writer.writerow([key, values[i], chrom_values[i]])

        


"""
## Append all off-target .txt files into one .txt file:
## Path to off-target .txt files is hard-coded.
path = "/home/ddooley/phylo_vip/data/ATCC_off/sao ATCC Results/"
file_list = [f for f in os.listdir(path) if isfile(join(path, f))]
nt = ['A', 'C', 'G', 'T']
appended_file = input("Please give an appended/output file name (without extension): ")
with open(os.getcwd() + "/" + appended_file + '.txt', 'w+') as outfile:
    for fname in file_list:
        infile = open(path + fname, "r")
        outfile.write(infile.read() + '\n')
        ind = file_list.index(fname)
        if ind == len(file_list)-1:
            outfile.write(infile.read() + '\n' + 'END OF FILE')

## Look through off-target data and make two dictionaries, each with target sequences as key,
## one with all off-target scores and one with all off-target hit locations
f = open(os.getcwd() + "/" + appended_file + '.txt', 'r')
offdict = {}
chromdict = {}
off_temp = []
chrom_temp = []
mylist = f.read().splitlines()
good_lines = [line for line in mylist if line]
for x in good_lines:
    if x[0] in nt:
        if x[21:29] == '0.000000':
            offdict[x[0:19]] = x[21:28]
        else:
            temp_seq = x[0:19]
            off_temp = []
            chrom_temp = []
    elif x[0] == '0':
        line_temp = [e.strip() for e in x.split(',')]
        off_temp.append((line_temp[0]))
        chrom_temp.append(line_temp[1])
        offdict[temp_seq] = off_temp
        chromdict[temp_seq] = chrom_temp
f.close()


## Write off-target data to CSV file
with open(os.getcwd() +"/" + appended_file + '.csv', 'w+') as data_output:
    data_writer = csv.writer(data_output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for key, values in offdict.items():
        if float(values[0]) == 0.00000:
            data_writer.writerow([key, values])
        else:
            chrom_values = chromdict.get(key)
            for i in range(len(values)):
                data_writer.writerow([key, values[i], chrom_values[i]])
"""