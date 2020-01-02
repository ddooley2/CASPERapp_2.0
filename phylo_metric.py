## This script is meant to be used for determining phylogenetic distances between a reference organism and a subset of
## species. This file takes a concatenated .fasta file and creates a multiple sequence alignment between all sequences
## in file. The first organism in the .fasta file is designated as the "reference" organism, and the distances between
## this organism and the remaining species in the fasta file is exported to a .csv file of the same name as the input
## .fasta file.
##
##      INPUT = .fasta file with reference sequence first and all other sequences following
##      OUTPUT = (1) Phylogenetic tree (pop up figure)
##               (2) Distance matrix printed in terminal
##               (3) Output files: .phy, .dnd, and .csv with same name as INPUT file.

import GlobalSettings
import os, csv, sys
from Bio.Align.Applications import ClustalOmegaCommandline
from Bio import Phylo, AlignIO
from Bio.Phylo.TreeConstruction import DistanceCalculator, DistanceTreeConstructor
from Bio.Phylo.Consensus import *
from CSPRparser import CSPRparser

"""
    class: phylo_metric
        This class takes a fasta file and aligns it. 
        It uses the Clustal Omega Executable to do this, so it assumes that it's in the CASPERapp2.0 folder
            It also assumes all pathing is done.
        It returns a dictionary
            Key: organism name
            value: the distance score
"""
class phylo_metric():
    """
        init - sets everything up
        Parameters:
            aligned_file: the fasta file with the un-aligned fasta file
    """
    def __init__(self, unaligned_file):
        self.clustal_exe = GlobalSettings.appdir + os.path.sep + 'clustalo.exe'
        self.in_file = unaligned_file
        self.out_file = GlobalSettings.CSPR_DB + os.path.sep + 'temp.phy'

    """
        run_exe: this function runs the Clustal Exe and parses the results
        Parameters:
            cspr_file_path: the path to the meta-genomic cspr file used for OT
    """
    def run_exe(self, cspr_file_path):
        # set up the command line, and run it
        cline = ClustalOmegaCommandline(self.clustal_exe, infile=self.in_file, outfile=self.out_file, outfmt="phy", auto=True, force=True)
        stdout, stderr = cline()
        
        # calculate the distance matrix
        phy = AlignIO.read(self.out_file, 'phylip')
        calculator = DistanceCalculator('identity')
        dm = calculator.get_distance(phy)
        print(dm)

        # get the list of full organism names
        org_list = self.get_orgs(cspr_file_path)

        # get the specie names
        names = list()
        for name in dm.names:
            names.append(name.split('.')[1])

        # assign the full names the scores
        org_dict = dict()
        for i in range(1,len(dm)):
            for name in org_list:
                if names[i] in name:
                    org_dict[name] = dm[i][0]

        os.remove(self.out_file)
        return org_dict

    """
        get_orgs: this function gets the organism names inside the meta-
            genomic cspr file
        Parameters:
            cspr_file: the path to the meta-genomic cspr file
    """
    def get_orgs(self, cspr_file):
        # load in the data
        ret_list = list()
        parser = CSPRparser(cspr_file)
        org_lsit = parser.get_orgs()

        # because the CSPRparser pulls out every chromosome, remove any duplicates
        for item in org_lsit:
            if item[0] not in ret_list:
                ret_list.append(item[0])

        return ret_list

"""
# Pathing stuff
muscle_exe = "/home/ddooley/phylo_vip/programs/muscle"
path = "/home/ddooley/phylo_vip"
in_file = path + "/" + input("Input filename: ")
out_file = in_file.split(".")[0] + ".phy"
mline = MuscleCommandline(muscle_exe, input=in_file, phyiout=out_file)

stdout, stderr = mline()

phy_file = out_file   #Specify path for .phy file
list = []

## Calculate distance matrix to be used for phylogenetic tree and export features
phy = AlignIO.read(phy_file, 'phylip') #Prepare input for distance matrix function "get_distance"
calculator = DistanceCalculator('identity')
dm = calculator.get_distance(phy)
print(dm)

## Construct UPGMA tree from distance matrix (with and without bootstrapping for comparison)
constructor1 = DistanceTreeConstructor() #no bootstrapping
constructor2 = DistanceTreeConstructor(calculator) #bootstrapping
upgma_tree = constructor1.upgma(dm)
consensus_tree = bootstrap_consensus(phy, 100, constructor2, majority_consensus)

## Construct Maximum Parsimony tree
starting_tree = upgma_tree
scorer = Phylo.TreeConstruction.ParsimonyScorer()
searcher = Phylo.TreeConstruction.NNITreeSearcher(scorer)
constructor = Phylo.TreeConstruction.ParsimonyTreeConstructor(searcher, starting_tree)
pars_tree = constructor.build_tree(phy)

## Assign indexes for species in dm
my_names = dm.names
ref_name = dm.names[0]
my_output = in_file.split(".")[0] + ".csv"

## Write contents of distance matrix to .csv output file
with open(my_output, mode='w') as output:
    my_writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    f = open(my_output, 'w+')
    for i in range(len(dm[0])):
        if dm[0][i] == 0:
            my_writer.writerow(["Reference organism:" + str(ref_name)])
            pass
        else:
            my_writer.writerow([my_names[i], dm[0][i]])

## Draw all trees
Phylo.draw(upgma_tree)
Phylo.draw(pars_tree)
Phylo.draw(consensus_tree)

##Export trees into phyloxml format for further manipulation/use
Phylo.write(upgma_tree, in_file.split(".")[0] + "_upgma" + ".xml", "phyloxml")
Phylo.write(pars_tree, in_file.split(".")[0] + "_pars" + ".xml", "phyloxml")
Phylo.write(consensus_tree, in_file.split(".")[0] + "_consensus" + ".xml", "phyloxml")
"""