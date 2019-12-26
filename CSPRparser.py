from Algorithms import SeqTranslate
import GlobalSettings

##################################################################################################################################
# CLASS NAME: CSPRparser
# Use: Use as a parser for the cspr files
# Precondition: Only to the used with .cspr files. Will not work with any other files
# This class also took some of the parsing functions from with classes (Multitargeting and Results) and stores them in here
##################################################################################################################################

class CSPRparser:
    #default ctor: currently just sets the file name and initializes all of the variables I will be using
    def __init__(self, inputFileName):

        # variables used in this class
        self.multiSum = 0 #multitargetting sum taken from the previous version of make_graphs
        self.multiCount = 0 #multitargetting count taken from the previous version of make_graphs
        self.seqTrans = SeqTranslate() #SeqTranslate variable. for decrompressing the data
        self.chromesomeList = list()  # list of a list for the chromesomes. As it currently stands, this variable is used in both read_chromesomes and in read_targets
        self.karystatsList = list()  # list of (ints) of the karyStats (whatever those are) to be used for the get_chrom_length function
        self.genome = ""  # genome name
        self.misc = ""  # anything from the misc line
        self.repeats = {}  #dictionary of the number of repeats. See the read_repeats function for more info
        self.seeds = {} #dictionary of which chromesomes are repeats. See the read_repeats function for more info
        self.dec_tup_data = {}
        self.chromesomesSelectedList = list()
        # data for population analysis
        # dict:
        # key = the seed
        #       value = tuple (org name, chom #, location, sequence, pam, score, strand, endo)
        self.popData = {}

        #file path variable
        self.fileName = inputFileName

    # this is the parser that is used for the gen_lib window
    # it returns a list of lists, essentially all of the chromosomes in the file, and their data
    # to make it faster, this now uses read_targets
    def gen_lib_parser(self, genDict, endo):
        retDict = dict()


        #for item in genDict:
         #   retList.append((list()))


        for gene in genDict:
            retDict[gene] = list()
            retDict[gene] = self.read_targets('', (genDict[gene][0], genDict[gene][1], genDict[gene][2]), endo)
        return retDict
    #this function reads the first 3 lines of the file: also stores the karyStats in a list of ints
    def read_first_lines(self):
        fileStream = open(self.fileName, 'r')

        #read and parse the genome line
        self.genome = fileStream.readline()
        colonIndex = self.genome.find(':') + 2
        buffer1 = self.genome[colonIndex:]
        self.genome = buffer1

        #read and store the karystats line on its own, it is parsed down below
        buffer = fileStream.readline()

        #read and parse the misc line
        self.misc = fileStream.readline()
        colonIndex = self.misc.find(':') + 2
        buffer1 = self.misc[colonIndex:]
        self.misc = buffer1


        #now parse the karystats line
        #ignore the first bit of the string. only care about what's after the colon
        colonIndex = buffer.find(':') + 2

        #parse the line, store the numbers in the list
        for i in range(colonIndex, len(buffer)):
            bufferString1 = ""
            if buffer[i] == ',':
                bufferString1 = buffer[colonIndex:i]
                #print(bufferString1)
                colonIndex = i + 1
                self.karystatsList.append(int(bufferString1))

        fileStream.close()
        #print(self.karystatsList)

    # this function gets the chromesome names out of the CSPR file provided
    # returns the gene line, and the misc line as well
    # also stores the Karystats
    def get_chromesome_names(self):
        self.read_first_lines()
        self.chromesomesSelectedList.clear()

        fileStream = open(self.fileName, 'r')

        retGen = fileStream.readline()
        junk = fileStream.readline()
        retMisc = fileStream.readline()

        buffer = fileStream.readline()

        while True:  # breaks out when the buffer line = REPEATS
            if buffer == 'REPEATS\n':
                break
            elif '>' in buffer:
                self.chromesomesSelectedList.append(buffer)
            buffer = fileStream.readline()

        return retGen, retMisc

#this function reads all of the chromosomes in the file
#stores the data into a list of lists. So the line starting with '>' is the first index of each sub list
    def read_chromesome(self):
        self.chromesomeList.clear()
        tempList = list()
        fileStream = open(self.fileName, 'r')

        #ignore the first 3 lines
        fileStream.readline()
        fileStream.readline()
        fileStream.readline()

        bufferString = fileStream.readline()
        while(True): #this loop breaks out when bufferString is REPEATS
            tempList.append(bufferString)

            if(bufferString == "REPEATS\n"):
                break
            bufferString = fileStream.readline()
            while(True): #this loop breaks out when bufferString[0] is >
                if(bufferString == "REPEATS\n"):
                    self.chromesomeList.append(tempList)
                    tempList = []
                    break

                elif(bufferString[0] == '>'): #if we get to the next chromesome, append the tempList, clear it, and break
                    self.chromesomeList.append(tempList)
                    tempList = []
                    break
                else: #else decompress the data, and append it to the list
                    bufferString = self.seqTrans.decompress_csf_tuple(bufferString)
                    tempList.append(bufferString)
                    #print(bufferString)
                    bufferString = fileStream.readline()
        fileStream.close()

########################################################################################################
#    this function reads just the repeats
#    it stores this data in 2 dictionaries:
#        repeats dictionary is the number of dictionaries
#               key = the seed, and the value is the number of repeats
#        seeds dictionary is each seed that is repeated
#           key =  the seeds, and the value is the actual chromesome that is repeated
#    this function also stores the sum and count in the class itself as well
#    this function is very similar to what make_graphs in Multitargeting.py was doing before
########################################################################################################
    def read_repeats(self, endoChoice):
        index = 0

        seedLength = int(self.seqTrans.endo_info[endoChoice][1])

        #clear what is already in there
        self.repeats.clear()
        self.seeds.clear()

        # only read the repeats section of the file
        fileStream = open(self.fileName, 'r')
        buf = fileStream.readline()
        while buf != "REPEATS\n":
            buf = fileStream.readline()
        split_info = fileStream.read().split('\n')
        fileStream.close()

        #parse the info now and store it in the correct dictionaries
        while(index + 1 < len(split_info)):
            seed = self.seqTrans.decompress64(split_info[index], slength=seedLength)
            repeat =split_info[index + 1].split("\t")

            self.repeats[seed] = 0
            self.seeds[seed] = []
            self.dec_tup_data[seed] = []
            for item in repeat:
                #print(self.seqTrans.decompress_csf_tuple(item, endo=endoChoice, bool=True))
                if item != "":
                    self.repeats[seed] += 1
                    sequence =item.split(',')
                    self.seeds[seed].append(sequence)
                    temp = sequence[1:4]

                    #print(seed)
                    #print(str(self.seqTrans.compress(seed,64)))
                    #print(temp[1])

                    #temp[1] = str(self.seqTrans.compress(seed,64)) + str(temp[1])
                    #print(temp)

                    temp.append(str(self.seqTrans.decompress64(seed, toseq=True ,slength=int(seedLength))))
                    #print(temp)
                    string = ",".join(temp)
                    #print(string)
                    #print('\t', self.seqTrans.decompress_csf_tuple(string, bool=True, endo=endoChoice))
                    self.dec_tup_data[seed].append(self.seqTrans.decompress_csf_tuple(string, bool=True, endo=endoChoice))
                    self.multiSum += self.seqTrans.decompress64(sequence[3], slength=seedLength)
                    self.multiCount += 1

            index = index + 2

    """
        get_orgs: this function gets every chromosome (thus orgs) in the misc line
        NOTE: This function should only be used on what is known to be a META genomic CSPR file
        Returns: a list of tuples storing the data
            [0] is the organism name
            [1] is the chromosome name itself
    """
    def get_orgs(self):
        # read and throw away the junk, but store the misc line
        fp = open(self.fileName, 'r')
        fp.readline()
        fp.readline()
        misc_data = fp.readline()
        fp.close()

        # only pull out the data we care about
        colonIndex = misc_data.find(':') + 2
        usefulData = misc_data[colonIndex:]
        usefulData = usefulData.split('|')
        usefulData.pop()

        # update the list we're returning
        i = 0
        misc_data = list()
        while i < len(usefulData):
            temp = usefulData[i].split(',')
            misc_data.append((temp[0], temp[1]))
            i += 1

        return misc_data

    # this function takes a list of all the file names
    # it finds the repeats for each file, and also checks to see if those repeats are in each file, not just the first
    # stores the data in a class object
    def popParser(self, cspr_file, endoChoice):
        self.popData.clear()
        seedLength = self.seqTrans.endo_info[endoChoice][1]

        referenceList = list()

        # skip the junk
        file_stream = open(cspr_file, 'r')
        genomeLine = file_stream.readline()
        file_stream.readline()

        # parse the genome line
        genomeLine = genomeLine.split(',')
        retNumber = int(genomeLine[len(genomeLine ) - 1])

        # parse the miscalleneous line and get the data we want out of it
        misc_line = file_stream.readline()
        colonIndex = misc_line.find(':') + 2
        usefulData = misc_line[colonIndex:]
        
        usefulData = usefulData.split('|')
        usefulData.pop()
        
        i = 0
        while i < len(usefulData):
            temp = usefulData[i].split(',')
            referenceList.append((temp[0], temp[1]))
            i += 1

        buf = file_stream.readline()
        while buf != 'REPEATS\n':
            buf = file_stream.readline()
        
        split_info = file_stream.read().split('\n')
        file_stream.close()

        index = 0
        while (index + 1 < len(split_info)):
            # get the seed and repeat line
            seed_d = self.seqTrans.decompress64(split_info[index], slength=int(seedLength), toseq=True)
            repeat = split_info[index + 1].split('\t')

            # if the seed is not in the dict, put it in there
            if seed_d not in self.popData:
                self.popData[seed_d] = list()

            for item in repeat:
                if item != '':
                    commaIndex = item.find(',')
                    chrom = item[:commaIndex] 
                    sequence = item.split(',')
                    temp = sequence[1:4]
                    temp.append(str(seed_d))
                    string = ",".join(temp)
                    tempTuple = self.seqTrans.decompress_csf_tuple(string, bool=True, endo=endoChoice)
                    orgName = referenceList[int(chrom) - 1][0]

                    storeTuple = (orgName, chrom,  tempTuple[0], tempTuple[1], tempTuple[2], tempTuple[3], tempTuple[4], tempTuple[5],)
                    
                    self.popData[seed_d].append(storeTuple)
            
            index += 2

        return retNumber, referenceList

        """
        # for each file given
        for count in range(len(file_list)):

            # open the file and get the orgName
            fileStream = open(file_list[count], 'r')
            buf = fileStream.readline()
            colonIndex = buf.find(':')
            orgName = buf[colonIndex + 2:]
            orgName = orgName.replace('\n', '')
            print(orgName)

            # now skip until the repeats section
            while buf != 'REPEATS\n':
                buf = fileStream.readline()

            # read the whole repeats section
            split_info = fileStream.read().split('\n')
            fileStream.close()

            index = 0
            seedLength = self.seqTrans.endo_info[endoChoice][1]
            while (index + 1 < len(split_info)):
                # get the seed and repeat line
                seed_d = self.seqTrans.decompress64(split_info[index], slength=int(seedLength), toseq=True)
                repeat = split_info[index + 1].split("\t")

                # if the seed is not in the dict, put it in there
                if seed_d not in self.popData:
                    self.popData[seed_d] = list()


                # go through and append each line
                for item in repeat:
                    if item != "":
                        # get the chromosome number
                        commaIndex = item.find(',')
                        chrom = item[:commaIndex]
                        # from read_repeats
                        sequence = item.split(',')
                        temp = sequence[1:4]
                        temp.append(str(seed_d))
                        string = ",".join(temp)
                        tempTuple = self.seqTrans.decompress_csf_tuple(string, bool=True, endo=endoChoice)

                        # store what we need
                        storeTuple = (orgName, chrom,  tempTuple[0], tempTuple[1], tempTuple[2], tempTuple[3], tempTuple[4], tempTuple[5],)
                        #storeTuple = (orgName, chrom, temp)

                        # append it
                        self.popData[seed_d].append(storeTuple)
                index += 2
            split_info.clear()
        """
    #this function just reads the whole file
    def read_all(self):
        print("Reading First Lines.")
        self.read_first_lines()
        print("Reading Chromesomes.")
        self.read_chromesome()
        print("Reading Repeats.")
        self.read_repeats()

    #this functions reads the entirety of the file into one string
    def get_whole_file(self):
        fileStream = open(self.fileName)
        fileData = fileStream.read()
        fileStream.close()
        return(fileData)

    #this function reads all of the targets in the file. It is essentially a copy of get_targets from the results.py file, written by Brian Mendoza
    def read_targets(self, genename, pos_tuple, endo):
        #open the file, and store the genome and the misc tags.
        #Note: The KARYSTATS is not stored at all. This should not be hard to implement if it is needed
        fileStream = open(self.fileName)
        self.genome = fileStream.readline()
        fileStream.readline()
        retList = list()
        self.misc = fileStream.readline()

        header = fileStream.readline()

        # get the sequence length for the decompressor
        seqLength = self.seqTrans.endo_info[endo][2]
        # Find the right chromosome:
        while True:
            # quick error check so the loop eventually breaks out if nothing is found
            if header == "":
                print("Error: the target could not be found in this file!")
                break
            # in the right chromosome/scaffold?
            if header.find("(" + str(pos_tuple[0]) + ")") != -1:
                while True:
                    # Find the appropriate location by quickly decompressing the location at the front of the line
                    myline = fileStream.readline()
                    if self.seqTrans.decompress64(myline.split(",")[0],slength=seqLength) >= pos_tuple[1]:
                        while self.seqTrans.decompress64(myline.split(",")[0],slength=seqLength) < pos_tuple[2]:
                            retList.append(self.seqTrans.decompress_csf_tuple(myline, endo=endo))
                            myline = fileStream.readline()
                    else:
                        continue
                    break
                break
            else:
                header = fileStream.readline()
        fileStream.close()

        return retList




# this is testing code. show's how popParser function works

"""
if __name__ == '__main__':
    files = ['C:/Users/Josh/Desktop/Work/Testing/crisper_files/New_CSPR_files/sce_spCas9.cspr', 'C:/Users/Josh/Desktop/Work/Testing/crisper_files/New_CSPR_files/pde_spCas9.cspr']
    GlobalSettings.appdir = 'C:/Users/Josh/Desktop/Work/CASPERapp'
    parser = CSPRparser("")

    parser.popParser(files, 'spCas9')

    outFile = open('testStore2.txt', 'w')

    seedLength = int(parser.seqTrans.endo_info['spCas9'][1])

    for item in parser.popData:
        seed = parser.seqTrans.decompress64(item, slength=seedLength)
        outFile.write(str(seed) + '\n')
        for i in range(len(parser.popData[item])):
            outFile.write('\t')

            #outFile.write(' ' + str(parser.popData[item][i][0]))
            #outFile.write(' ' + str(parser.popData[item][i][1]))

            #temp = parser.popData[item][i][2]
            #temp.append(str(parser.seqTrans.decompress64(seed, toseq=True, slength=seedLength)))
            #string = ",".join(temp)
            #tempTuple = parser.seqTrans.decompress_csf_tuple(string, bool=True, endo='spCas9')

            #for j in range(len(tempTuple)):
             #   outFile.write(' ' + str(tempTuple[j]))

            # DO NOT USE
            for j in range(len(parser.popData[item][i])):
                outFile.write(' ' + str(parser.popData[item][i][j]))

            outFile.write('\n')
"""