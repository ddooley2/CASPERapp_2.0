import os
from PyQt5 import QtWidgets, Qt, QtGui, QtCore, uic
import GlobalSettings
import operator
from PyQt5.QtChart import (QBarCategoryAxis,QBarSet, QChartView, QBarSeries,QChart,QLineSeries, QValueAxis)
from PyQt5.QtGui import QPainter, QBrush, QPen
#import PyQt5
from Algorithms import SeqTranslate
from CSPRparser import CSPRparser
from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)
from matplotlib.backends.backend_qt5agg import FigureCanvasAgg as FigureCanvas
from matplotlib.ticker import MaxNLocator
import datetime


class Multitargeting(QtWidgets.QMainWindow):

    BAD_instances = {}
    sorted_instances = []
    def __init__(self, parent = None):

        super(Multitargeting, self).__init__()
        uic.loadUi('multitargetingwindow.ui', self)
        self.setWindowIcon(QtGui.QIcon("cas9image.png"))
        # Storage containers for the repeats and seed sequences
        self.sq=SeqTranslate()  # SeqTranslate object used in class

        # Initializes the three graphs
        self.chart_view_chro_bar=QChartView()
        self.chart_view_repeat_bar = QChartView()
        self.chart_view_repeat_line = QChartView()


        self.data = ""
        self.shortHand =""
        self.chromo_length = list()

        # Listeners for changing the seed sequence or the .cspr file
        self.max_chromo.currentIndexChanged.connect(self.fill_seed_id_chrom)
        self.min_chromo.currentIndexChanged.connect(self.fill_seed_id_chrom)
        self.chromo_seed.currentIndexChanged.connect(self.chro_bar_data)
        self.Analyze_Button.clicked.connect(self.make_graphs)
        self.export_button.clicked.connect(self.export)

        #go back to main button
        self.back_button.clicked.connect(self.go_back)

        #Tool Bar options
        self.actionCASPER.triggered.connect(self.changeto_main)

        # Statistics storage variables
        self.max_repeats=1
        self.average = 0
        self.median = 0
        self.mode = 0
        self.average_unique = 0
        self.average_rep = 0
        self.bar_coords = []
        self.bars = {}
        self.rects = []
        self.seed_id_seq_pair = {}
        self.positions = []
        self.bar_data = []

        #parser object
        self.parser = CSPRparser("")

        self.ready_chromo_min_max = True
        self.ready_chromo_make_graph = True
        self.directory = 'Cspr files'
        self.info_path = os.getcwd()

        #seed ID substring filter button
        self.filterButton.clicked.connect(self.fill_seed_id_chrom)

        ##################################
        self.scene = QtWidgets.QGraphicsScene()
        self.graphicsView.setScene(self.scene)
        self.scene2 = QtWidgets.QGraphicsScene()
        self.graphicsView_2.setScene(self.scene2)
        self.installEventFilter(self)
        self.graphicsView.installEventFilter(self)
        self.graphicsView.viewport().installEventFilter(self)

        self.bar_counter = 0
        self.rect_counter = 0
        self.counter = 0

        #group button for chromo viewer
        self.group_button.clicked.connect(self.group)
        self.reset_chromo.clicked.connect(self.reset_chromo_viewer)
        self.mouse_option.clicked.connect(self.mouse_enable)
        self.arrow_option.clicked.connect(self.arrow_enable)
        #Qt_FocusPolicy = Qt.StrongFocus
        #self.setFocusPolicy(QtCore.Qt.StrongFocus)

    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.MouseMove and source is self.graphicsView.viewport() and self.mouse_option.isChecked()):
            pen_bl = QtGui.QPen(QtCore.Qt.blue)
            pen_bl.setWidth(3)
            pen_red = QtGui.QPen(QtCore.Qt.red)
            pen_red.setWidth(3)

            coord = self.graphicsView.mapToScene(event.pos())
            for i in self.bar_coords:
                x = i[0][1]
                y1 = i[0][2]
                y2 = i[0][3]
                if ((coord.x() == x or coord.x() == x + 1 or coord.x() == x - 1) and (
                        coord.y() >= y1 and coord.y() <= y2)):

                    tup = tuple([x, y1, y2])
                    line = self.bars[tup]
                    line.setPen(pen_bl)
                    listtemp = i

                    self.scene2 = QtWidgets.QGraphicsScene()
                    self.graphicsView_2.setScene(self.scene2)
                    output = str()
                    i = 1
                    for item in listtemp:
                        ind = item[0]
                        seq = str(self.seq_data[ind])
                        seed_id = self.seed_id_seq_pair[seq]
                        temp = self.parser.dec_tup_data[seed_id]
                        temp = temp[ind]
                        if len(listtemp) > 1 and i < len(listtemp):
                            output += 'Location: ' + str(temp[0]) + ' | Seq: ' + str(temp[1]) + ' | PAM: ' + str(
                                    temp[2]) + ' | SCR: ' + str(temp[3]) + ' | DIRA: ' + str(temp[4]) + '\n'
                        else:
                            output += 'Location: ' + str(temp[0]) + ' | Seq: ' + str(temp[1]) + ' | PAM: ' + str(
                                temp[2]) + ' | SCR: ' + str(temp[3]) + ' | DIRA: ' + str(temp[4])
                        i += 1
                    text = self.scene2.addText(output)
                    font = QtGui.QFont()
                    font.setBold(True)
                    font.setPointSize(9)
                    text.setFont(font)
                    text.setFont(font)
                else:
                    tup = tuple([x, y1, y2])
                    line = self.bars[tup]
                    line.setPen(pen_red)

        elif (event.type() == QtCore.QEvent.KeyPress and self.arrow_option.isChecked()):
            key = event.key()

            pen_bl = QtGui.QPen(QtCore.Qt.blue)
            pen_bl.setWidth(3)
            pen_red = QtGui.QPen(QtCore.Qt.red)
            pen_red.setWidth(3)

            old_bar = self.bar_counter
            old_rect = self.rect_counter

            if key == QtCore.Qt.Key_Left:
                if self.bar_counter > 0:
                    self.bar_counter -= 1
                    self.counter -= 1

            elif key == QtCore.Qt.Key_Right:
                if self.bar_counter < len(self.bar_data[self.rect_counter]) - 1:
                    self.bar_counter += 1
                    self.counter += 1

            elif key == QtCore.Qt.Key_Up:
                if self.rect_counter > 0:
                    self.rect_counter -= 1
                    self.bar_counter = 0
                    self.counter = 0
                    for r in range(0, self.rect_counter):
                        self.counter += len(self.bar_data[r])

            elif key == QtCore.Qt.Key_Down:
                if self.rect_counter < len(self.rects)-1:
                    self.rect_counter += 1
                    self.bar_counter = 0
                    self.counter = 0
                    for r in range(0, self.rect_counter):
                        self.counter += len(self.bar_data[r])

            line = self.bar_data[old_rect][old_bar]
            line.setPen(pen_red)
            line = self.bar_data[self.rect_counter][self.bar_counter]
            line.setPen(pen_bl)

            listtemp = self.bar_coords[self.counter]

            self.scene2 = QtWidgets.QGraphicsScene()
            self.graphicsView_2.setScene(self.scene2)
            output = str()
            i = 1
            for item in listtemp:
                ind = item[0]
                seq = str(self.seq_data[ind])

                seed_id = self.seed_id_seq_pair[seq]

                temp = self.parser.dec_tup_data[seed_id]
                temp = temp[ind]
                if len(listtemp) > 1 and i < len(listtemp):
                    output += 'Location: ' + str(temp[0]) + ' | Seq: ' + str(temp[1]) + ' | PAM: ' + str(
                        temp[2]) + ' | SCR: ' + str(temp[3]) + ' | DIRA: ' + str(temp[4]) + '\n'
                else:
                    output += 'Location: ' + str(temp[0]) + ' | Seq: ' + str(temp[1]) + ' | PAM: ' + str(
                        temp[2]) + ' | SCR: ' + str(temp[3]) + ' | DIRA: ' + str(temp[4])
                i += 1
            text = self.scene2.addText(output)
            font = QtGui.QFont()
            font.setBold(True)
            font.setPointSize(9)
            text.setFont(font)
            text.setFont(font)
        event.accept()

        return Qt.QWidget.eventFilter(self, source, event)

    def launch(self,path):
        os.chdir(path)
        self.directory = path
        self.get_data()
        self.make_graphs()

    def get_data(self):
        onlyfiles = [f for f in os.listdir(self.directory) if os.path.isfile(os.path.join(self.directory, f))]
        print(onlyfiles)
        orgsandendos = {}
        shortName = {}
        self.endo_drop.clear()
        for file in onlyfiles:
            if file.find('.cspr')!=-1:
                newname = file[0:-4]
                s = newname.split('_')
                hold = open(file)
                buf = (hold.readline())
                species = buf[8:buf.find('\n')]
                endo = str(s[1])
                if species not in shortName:
                    shortName[species] = s[0]
                if species in orgsandendos:
                    orgsandendos[species].append(endo)
                else:
                    orgsandendos[species] =[endo]
                    if self.organism_drop.findText(species) == -1:
                        self.organism_drop.addItem(species)
        self.data = orgsandendos
        self.shortHand = shortName
        temp = self.data[str(self.organism_drop.currentText())]
        temp1=[]
        for i in temp:
            i = i.strip('.')
            temp1.append(i)
        self.endo_drop.addItems(temp1)
        self.organism_drop.currentIndexChanged.connect(self.changeEndos)

    def changeEndos(self):
        self.endo_drop.clear()
        temp = self.data[str(self.organism_drop.currentText())]
        temp1 = []
        for i in temp:
            i = i.strip('.')
            temp1.append(i)
        self.endo_drop.addItems(temp1)

    def make_graphs(self):
        self.rect_counter = 0
        self.bar_counter = 0
        self.counter = 0
        #get the correct file name
        self.chromo_length.clear()
        file_name = self.shortHand[self.organism_drop.currentText()] + "_" + self.endo_drop.currentText()
        if self.directory.find("/") != -1:
            file = (self.directory + "/" + file_name + ".cspr")
        else:
            file = (self.directory + "\\" + file_name + ".cspr")

        #set up parser, and get the repeats and carry stats
        self.parser.fileName = file
        print(self.endo_drop.currentText())
        self.parser.read_repeats(self.endo_drop.currentText())
        self.parser.read_chromesome(self.endo_drop.currentText())
        self.parser.read_first_lines()
        self.chromo_length = self.parser.karystatsList

        #calculations and setting the windows
        self.average_rep = self.parser.multiSum/self.parser.multiCount
        self.plot_repeats_vs_seeds()
        self.bar_seeds_vs_repeats()
        self.fill_min_max()
        #self.chro_bar_data()
        self.group_val_box.clear()
        self.nbr_seq.setText(str(len(self.parser.seeds)))
        self.nbr_unq.setText(str(self.parser.uniq_seq_count()))
        self.avg_rep.setText(str(self.average))
        self.med_rep.setText(str(self.median))
        self.mode_rep.setText(str(self.mode))
        self.scr_lbl.setText(str(self.average_rep))

    #fill in chromo bar visualization
    def chro_bar_data(self):

        if self.ready_chromo_make_graph==False:
            return
        dic_info = {}
        seqLength = int(self.sq.endo_info[self.endo_drop.currentText()][1])
        for seed in self.parser.seeds:
            temp = seed
            temp1 = str(self.sq.decompress64(temp, slength=seqLength, toseq=True))
            self.seed_id_seq_pair[temp1] = seed
            dic_info[temp1] = {}
            for repeat in self.parser.seeds[seed]:
                if repeat[0] in dic_info[temp1]:
                    dic_info[temp1][repeat[0]].append(self.sq.decompress64(repeat[1]))
                else:
                    dic_info[temp1][repeat[0]] = [self.sq.decompress64(repeat[1])]
        self.info=dic_info
        self.chro_bar_create(dic_info)
        self.fill_Chromo_Text(dic_info)
        self.group_val_box.clear()

    #fill in chromo bar visualization
    def fill_Chromo_Text(self, info, dist=0):
        self.scene2 = QtWidgets.QGraphicsScene()
        self.graphicsView_2.setScene(self.scene2)
        self.chromo_pos = {}
        self.chromo_locs = {}
        self.seq_data = []
        self.export_data = []
        self.positions.clear()
        self.bar_counter = 0
        self.rect_counter = 0
        self.counter = 0
        chomonum = 0
        for chromo in info[self.chromo_seed.currentText()]:
            pos = []
            locs = []
            for position in info[(self.chromo_seed.currentText())][chromo]:
                self.seq_data.append(self.chromo_seed.currentText())
                test1 = position/self.chromo_length[int(chromo)-1]
                test1 = int(test1 * 485)
                self.positions.append(test1)
                pos.append(test1)
                locs.append(position)

            self.chromo_pos[chromo] = pos
            self.chromo_locs[chromo] = locs
            chomonum+=1

        i = 0
        self.scene = QtWidgets.QGraphicsScene()
        self.scene.activeWindow()
        self.graphicsView.setScene(self.scene)
        self.bar_coords.clear() #clear bar_coords list before creating visual
        self.bars = {}
        self.rects.clear()
        self.bar_data.clear()
        ind = 0
        r = 0
        index=0
        for chromo in self.chromo_pos:
            pen_blk = QtGui.QPen(QtCore.Qt.black)
            pen_red = QtGui.QPen(QtCore.Qt.red)
            pen_blk.setWidth(3)
            pen_red.setWidth(3)
            if i == 0:
                text = self.scene.addText(str(chromo))
                text.setPos(0,0)
                font = QtGui.QFont()
                font.setBold(True)
                font.setPointSize(10)
                text.setFont(font)
                rect = self.scene.addRect(40, (i * 25), 525, 25, pen_blk)
                self.rects.append(rect)
                self.bar_data.append([])
            else:
                text = self.scene.addText(str(chromo))
                font = QtGui.QFont()
                font.setBold(True)
                font.setPointSize(10)
                text.setFont(font)
                text.setPos(0,i*25+10*i)
                rect = self.scene.addRect(40, (i * 25)+10*i, 525, 25, pen_blk)
                self.rects.append(rect)
                self.bar_data.append([])
            found = False
            self.chromo_pos[chromo] = sorted(self.chromo_pos[chromo])

            num = 0
            while num < len(self.chromo_pos[chromo]):
                found = False
                k = self.chromo_pos[chromo][num]
                temp = [] #used for storing coordinates and saving them in self.bar_coords[]
                temp.append(ind) #index value
                temp.append(k+40) #x value
                temp.append((i*25)+3+10*i) #y1
                temp.append((i*25)+22+10*i) #y2
                ind_1 = ind
                seq_1 = str(self.seq_data[ind_1])
                seed_id_1 = self.seed_id_seq_pair[seq_1]
                temp_1 = self.parser.dec_tup_data[seed_id_1]
                temp_1 = temp_1[ind]
                loc_1 = int(temp_1[0])
                for coords in self.bar_coords:
                    for sub_coords in coords:
                        ind_2 = sub_coords[0]
                        seq_2 = str(self.seq_data[ind_2])
                        seed_id_2 = self.seed_id_seq_pair[seq_2]
                        temp_2 = self.parser.dec_tup_data[seed_id_2]
                        temp_2 = temp_2[ind_2]
                        loc_2 = int(temp_2[0])
                        if temp[1:4] == sub_coords[1:4] or (loc_2 < (loc_1 + dist) and loc_2 > (loc_1 - dist) and temp[2:4] == sub_coords[2:4]):
                            found = True
                            self.bar_coords[index-1].append(temp)

                            exp = temp
                            exp.append(loc_1)
                            exp.append(seq_1)
                            exp.append(seed_id_1)
                            self.export_data[index-1].append(exp)
                            break
                    if found == True:
                        break
                if found != True:
                    line = self.scene.addLine(k + 40, (i * 25) + 3 + 10 * i, k + 40, (i * 25) + 22 + 10 * i, pen_red)
                    self.bar_data[r].append(line)
                    self.bars[tuple(temp[1:4])]=line
                    self.bar_coords.append([temp]) #push x, y1, and y2 to this list

                    exp = temp
                    exp.append(loc_1)
                    exp.append(seq_1)
                    exp.append(seed_id_1)
                    self.export_data.append([exp])

                    index+=1
                ind += 1
                num += 1
            i = i + 1
            r += 1

        #initialize chromo window to first repeat in first chromo
        if(self.arrow_option.isChecked()):
            pen_bl = QtGui.QPen(QtCore.Qt.blue)
            pen_bl.setWidth(3)

            line = self.bar_data[0][0]
            line.setPen(pen_bl)

            listtemp = self.bar_coords[0]

            output = str()
            i = 1
            for item in listtemp:
                ind = item[0]
                seq = str(self.seq_data[ind])
                seed_id = self.seed_id_seq_pair[seq]
                temp = self.parser.dec_tup_data[seed_id]
                temp = temp[ind]
                if len(listtemp) > 1 and i < len(listtemp):
                    output += 'Location: ' + str(temp[0]) + ' | Seq: ' + str(temp[1]) + ' | PAM: ' + str(
                        temp[2]) + ' | SCR: ' + str(temp[3]) + ' | DIRA: ' + str(temp[4]) + '\n'
                else:
                    output += 'Location: ' + str(temp[0]) + ' | Seq: ' + str(temp[1]) + ' | PAM: ' + str(
                        temp[2]) + ' | SCR: ' + str(temp[3]) + ' | DIRA: ' + str(temp[4])
                i += 1
            text = self.scene2.addText(output)
            font = QtGui.QFont()
            font.setBold(True)
            font.setPointSize(9)
            text.setFont(font)
            text.setFont(font)
        self.graphicsView.setFocus()

    #creates bar graph num of repeats vs. chromsome
    #this graphs is connected to the repeats_vs_chromo.py file
    #to represent the widget space in the UI file
    def chro_bar_create(self,info):
        x1 = []
        y1 = []
        lentemp = 0
        for chromo in info[self.chromo_seed.currentText()]:
            y1.append(len(info[self.chromo_seed.currentText()][chromo]))
            x1.append(chromo)
            if(int(chromo) > lentemp):
                lentemp = int(chromo)
        #clear the old graph
        self.repeats_vs_chromo.canvas.axes.clear()
        #x_pos used to format the addition of more bars appropriately
        x_pos = [i for i, _ in enumerate(x1)]

        #loop fixes when there is too many xlabels and they start running together,
        #replaces some with an empty string to space out the labels
        if(len(x_pos) > 20):
            temp = 0
            for i in x_pos:
                if(i == 0):
                    temp += 1
                else:
                    if(temp < len(str(lentemp))+2):
                        x1[i] = ""
                        temp += 1
                    else:
                        temp = 0

        #the following statements are plottings / formatting for the graph
        self.repeats_vs_chromo.canvas.axes.bar(x_pos, y1,align='center')
        self.repeats_vs_chromo.canvas.axes.yaxis.set_major_locator(MaxNLocator(integer=True))
        self.repeats_vs_chromo.canvas.axes.set_ylim(0,max(y1)+1)
        self.repeats_vs_chromo.canvas.axes.set_xticks(x_pos)
        self.repeats_vs_chromo.canvas.axes.set_xticklabels(x1)
        self.repeats_vs_chromo.canvas.axes.set_xlabel('Chromosome')
        self.repeats_vs_chromo.canvas.axes.set_ylabel('Number of Repeats')

        #for loop below could be used to rotae labels for spacing
        #for tick in self.repeats_vs_chromo.canvas.axes.get_xticklabels():
        #   tick.set_rotation(90)

        self.repeats_vs_chromo.canvas.draw()

    #plots the sequences per Number Repeats bar graph
    #this graph is connected to the seeds_vs_repeats_bar.py file
    #to represent the wdiget space in the UI file
    def bar_seeds_vs_repeats(self):
        data = {}
        self.average = 0
        for seed in self.parser.repeats:
            self.average  += int(self.parser.repeats[seed])
            number = self.parser.repeats[seed]
            if number in data:
                data[number]+=1
            else:
                data[number] =1
        data = self.order_high_low_rep(data)
        self.average = round(self.average/(len(self.parser.repeats)))
        holder = []
        repeats = []
        max = 0
        for number in data:
            if data[number]>max:
                max = data[number]
            if (data[number]/max)>.01:
                holder.append(data[number])
                repeats.append(number)
        #clear graph space
        self.seeds_vs_repeats_bar.canvas.axes.clear()
        #xpos used to handle appropriate formatting for more bars being added in
        x_pos = [i for i, _ in enumerate(repeats)]
        #the following are plotting / formatting for the graph
        self.seeds_vs_repeats_bar.canvas.axes.bar(x_pos, holder)
        self.seeds_vs_repeats_bar.canvas.axes.set_xticks(x_pos)
        self.seeds_vs_repeats_bar.canvas.axes.set_xticklabels(repeats)
        self.seeds_vs_repeats_bar.canvas.axes.set_xlabel('Number of Repeats')
        self.seeds_vs_repeats_bar.canvas.axes.set_ylabel('Number of Sequences')
        self.seeds_vs_repeats_bar.canvas.axes.set_title('Amount of sequence per number of repeats')
        #rects are all the bar objects in the graph
        rects = self.seeds_vs_repeats_bar.canvas.axes.patches
        rect_vals = []
        #this for loop will calculate the height and create an annotation for each bar
        for rect in rects:
            height = rect.get_height()
            temp = self.seeds_vs_repeats_bar.canvas.axes.text(rect.get_x() + rect.get_width() / 2, height,
                                                        '%d' % int(height),
                                                        ha='center', va='bottom')
            temp.set_visible(False)
            rect_vals.append(temp)
        #function used for when user cursor is hovering over the bar, if hovering over a bar, the
        #height annotatin will appear above the bar, otherwise it will be hidden
        def on_plot_hover(event):
            i = 0
            for rect in rects:
                height = rect.get_height()
                if rect.contains(event)[0]:
                    rect_vals[i].set_visible(True)
                else:
                    rect_vals[i].set_visible(False)

                i = i + 1

            self.seeds_vs_repeats_bar.canvas.draw()
        #statement to detect cursor hovering over the bars
        self.seeds_vs_repeats_bar.canvas.mpl_connect('motion_notify_event', on_plot_hover)
        #must redraw after every change
        self.seeds_vs_repeats_bar.canvas.draw()

    #plots the repeats per ID number graph as line graph
    #this graph is connected to the repeats_vs_seeds_line.py file
    #to represent the widget space in the UI file
    def plot_repeats_vs_seeds(self):
        data = {}
        for seed in self.parser.repeats:
            number = self.parser.repeats[seed]
            if number in data:
                data[number]+=1
            else:
                data[number] =1

        max = 0
        y1 = []
        x1 = []
        index = 0
        time = 0
        for number in self.order(data):
            time+=1

            if int(data[number]) >max:
                max = int(data[number])
                self.mode = number

            hold = 0
            while hold<data[number]:
                if index == int(round(len(self.parser.repeats) / 2)):
                    self.median = number
                x1.append(index)
                y1.append(number)
                index= index+1
                hold +=1

        #clear axes
        self.repeats_vs_seeds_line.canvas.axes.clear()
        #the following are for plotting / formatting
        self.repeats_vs_seeds_line.canvas.axes.plot(x1,y1)
        self.repeats_vs_seeds_line.canvas.axes.set_xlabel('Seed Id Number')
        self.repeats_vs_seeds_line.canvas.axes.set_ylabel('Number of Repeats')
        self.repeats_vs_seeds_line.canvas.axes.set_title('Number of Repeats per Seed Id Number')
        #always redraw at the end
        self.repeats_vs_seeds_line.canvas.draw()

    #fills min and max dropdown windows
    def fill_min_max(self,run_seed_fill=True):
        self.ready_chromo_min_max = False
        index =1
        self.max_chromo.clear()
        self.min_chromo.clear()
        while index<self.max_repeats+1:
            self.min_chromo.addItem(str(index))
            self.max_chromo.addItem(str(self.max_repeats+1-index))
            index+=1
        self.ready_chromo_min_max = True
        if run_seed_fill:
            self.fill_seed_id_chrom()

    #fill_seed_id_chrom will fill the seed ID dropdown, and create the chromosome graph
    def fill_seed_id_chrom(self):
        self.rect_counter = 0
        self.bar_counter = 0
        self.counter = 0
        if self.ready_chromo_min_max==False:
            return
        if int(self.min_chromo.currentText())>int(self.max_chromo.currentText()):
            self.ready_chromo_min_max=False
            self.max_chromo.clear()
            self.min_chromo.clear()
            self.ready_chromo_min_max = True
            self.fill_min_max(False)
            QtWidgets.QMessageBox.question(self, "Maximum cant be less than Minimum",
                                           "The Minimum number of repeats cant be more than the Maximum",
                                           QtWidgets.QMessageBox.Ok)
            self.fill_seed_id_chrom()
            return
        self.ready_chromo_make_graph = False
        self.chromo_seed.clear()
        any = False
        seqLength = int(self.sq.endo_info[self.endo_drop.currentText()][1])
        sub_str = str(self.seed_id_str.text())
        sub_str = sub_str.replace(' ','')
        for seed in self.parser.repeats:
            if self.parser.repeats[seed] >= int(self.min_chromo.currentText()) and self.parser.repeats[seed]<=int(self.max_chromo.currentText()):
                any = True
                #temp = self.sq.compress(seed,64)
                seed_id = str(self.sq.decompress64(seed, slength=seqLength, toseq= True))
                if sub_str != '':
                    if seed_id.startswith(sub_str):
                        self.chromo_seed.addItem(seed_id)
                else:
                    self.chromo_seed.addItem(seed_id)
        if any==False:
            QtWidgets.QMessageBox.question(self, "No matches found",
                                           "No seed that is within the specifications could be found",
                                           QtWidgets.QMessageBox.Ok)
            self.ready_chromo_min_max = False
            self.max_chromo.clear()
            self.min_chromo.clear()
            self.ready_chromo_min_max = True
            self.fill_min_max(False)
            self.fill_seed_id_chrom()
            return


        self.ready_chromo_make_graph=True
        self.chro_bar_data()

    def order(self,data_par):
        data = dict(data_par)
        data2  = []
        while len(data)>0:
            max=0
            for item in data:
                if item>max:
                    max=item
            data2.append(max)
            if len(data2) ==1:
                self.max_repeats =max
            del data[max]
        return data2

    def order_high_low_rep(self,dictionary):
        data = dict(dictionary)
        data_ordered = {}
        while len(data)>0:
            max=0
            max_index=0
            for item in data:

                if data[item]>max:
                    max_index=item
                    max = data[item]

            data_ordered[max_index] = max

            del data[max_index]
        return data_ordered

    def group(self):
        self.fill_Chromo_Text(self.info, dist=int(self.group_val_box.text()))

    def reset_chromo_viewer(self):
        self.fill_Chromo_Text(self.info, dist=0)
        self.group_val_box.clear()

    def mouse_enable(self):
        self.graphicsView.setFocus()
        pen_red = QtGui.QPen(QtCore.Qt.red)
        pen_red.setWidth(3)
        self.scene2 = QtWidgets.QGraphicsScene()
        self.graphicsView_2.setScene(self.scene2)
        for i in self.bar_coords:
            x = i[0][1]
            y1 = i[0][2]
            y2 = i[0][3]
            tup = tuple([x, y1, y2])
            line = self.bars[tup]
            line.setPen(pen_red)

    def arrow_enable(self):
        self.graphicsView.setFocus()

        pen_bl = QtGui.QPen(QtCore.Qt.blue)
        pen_bl.setWidth(3)

        self.bar_counter = 0
        self.rect_counter = 0
        self.counter = 0
        line = self.bar_data[self.rect_counter][self.bar_counter]
        line.setPen(pen_bl)
        listtemp = self.bar_coords[self.counter]
        self.scene2 = QtWidgets.QGraphicsScene()
        self.graphicsView_2.setScene(self.scene2)
        output = str()
        i = 1
        for item in listtemp:
            ind = item[0]
            seq = str(self.seq_data[ind])

            seed_id = self.seed_id_seq_pair[seq]

            temp = self.parser.dec_tup_data[seed_id]
            temp = temp[ind]
            if len(listtemp) > 1 and i < len(listtemp):
                output += 'Location: ' + str(temp[0]) + ' | Seq: ' + str(temp[1]) + ' | PAM: ' + str(
                    temp[2]) + ' | SCR: ' + str(temp[3]) + ' | DIRA: ' + str(temp[4]) + '\n'
            else:
                output += 'Location: ' + str(temp[0]) + ' | Seq: ' + str(temp[1]) + ' | PAM: ' + str(
                    temp[2]) + ' | SCR: ' + str(temp[3]) + ' | DIRA: ' + str(temp[4])
            i += 1
        text = self.scene2.addText(output)
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(9)
        text.setFont(font)
        text.setFont(font)

    #connects to view->CASPER to switch back to the main CASPER window
    def changeto_main(self):
        GlobalSettings.mainWindow.show()
        self.hide()

    #connects to go back button in bottom left to switch back to the main CASPER window
    def go_back(self):
        GlobalSettings.mainWindow.show()
        self.hide()


    def export(self):
        seqLength = int(self.sq.endo_info[self.endo_drop.currentText()][1])
        groups = {}
        for coord in self.export_data:
            found = False
            for key in groups.keys():
                temp = []
                for obj in groups[key]:
                    for line in obj:
                        temp.append(line[4])
                ma = max(temp)
                mi = min(temp)
                if coord[0][1] == key or (coord[0][4] <= ma + 700 and coord[0][4] >= mi - 700):
                    groups[key].append(coord)
                    found = True
                    break
            if found == False:
                groups[coord[0][1]] = []
                groups[coord[0][1]].append(coord)

        for key in groups:
            print(key)
            print(groups[key])
            print('\n\n')




        with open('export_chromo_data.csv','w') as f:
            i = 1
            for key in groups.keys():
                seed_data = {}
                for obj in groups[key]:
                    for line in obj:
                        seed = str(self.sq.decompress64(line[6], slength=seqLength, toseq=True))
                        if line[5] not in seed_data:
                            seed_data[line[5]] = {}
                        if (line[4],seed) not in seed_data[line[5]]:
                            seed_data[line[5]][(line[4],seed)] = 1
                        else:
                            seed_data[line[5]][(line[4],seed)] += 1
                # print(seed_data)
                # print('\n\n')
                for seq in seed_data:
                    for loc in seed_data[seq]:
                        f.write('Group ' + str(i) + ',' + str(loc[0]) + ',' + str(seed_data[seq][loc]) + ',' + str(loc[1]) + '\n')
                i += 1







    #-----------------------NOT USED----------------------------#
    def get_instances(self):
            ST = SeqTranslate()
            os.chdir(path)
            f = open(self.file_name, 'r')
            while True:
                x = f.readline()
                if x == 'REPEATS\n':
                    print("reached repeat sequences")
                    break
            while True:
                t = f.readline()
                if t == 'END_OF_FILE':
                    print("reached end of repeat sequences")
                    break
                ukey = t[:-1]  # takes away the "\n" in the string
                key = ST.decompress64(ukey, slength=20, toseq=True)
                key = ST.fill_As(key, 16)
                self.BAD_instances[key] = list()
                # Add sequences and locations to the list
                v = f.readline().split('\t')[:-1]
                for item in v:
                    loctup = item.split(',')
                    chrom = loctup[0]
                    location = ST.decompress64(loctup[1])
                    seq = ST.decompress64(loctup[2][1:], slength=20, toseq=True)
                    seq = ST.fill_As(seq, 4)  # when A's get lost in the compression this fills them back in
                    mytup = (chrom, location, seq)
                    self.BAD_instances[key].append(mytup)
            f.close()
            print("currently sorting")
            for key in self.BAD_instances:
                size = len(self.BAD_instances[key])
                newtuple = (key, self.BAD_instances[key], size)  # sequence, location, size
                self.sorted_instances.append(newtuple)
    #not used
    # Returns the container self.sorted_instances but removes all "single" repeats. Old Code to fix an off-by-1 error
    def return_all_seqs(self):
        myseqs = []
        for instance in self.sorted_instances:
            if instance[2] > 1:
                myseqs.append(instance)
        return myseqs
    #not used
    def return_sorted(self):
        sorted_seqs = sorted(self.sorted_instances, key=operator.itemgetter(2), reverse=True)
        amounts = {}
        for instance in sorted_seqs:
            if instance[2] > 1:
                if instance[2] in amounts:
                    amounts[instance[2]] += 1
                else:
                    amounts[instance[2]] = 1
                print(str(instance[0]) + "," + str(instance[2]) + "," + str(instance[1]))
        for element in amounts:
            print("Number of seed sequences with " + str(element) + " appearances: " + str(amounts[element]))
    #not used
    def return_positions(self):
        positions_mapped = []  # chromosme, beginning of range, end of range, and number of hits
        for instance in self.sorted_instances:
            if instance[2] > 1:
                for pos in instance[1]:
                    chrom = pos[0]
                    loc = int(pos[1])
                    # check to see if its already in the map
                    need_new = True
                    for position in positions_mapped:
                        if chrom == position[0]:
                            if position[1] < loc < position[2]:
                                position[3] += 1
                                position[4].append(instance[0])
                                need_new = False
                                print("position added")
                    if need_new:
                        newtuple = [chrom, loc-1000, loc+1000, 1, [" ", instance[0]]]
                        positions_mapped.append(newtuple)
        sorted_positions = sorted(positions_mapped, key=operator.itemgetter(3), reverse=True)
        for element in sorted_positions:
            print(str(element[0]) + "," + str(element[1]) + "," + str(element[2]) + "," + str(element[3]))
        for element in sorted_positions:
            sequences = ""
            for sequence in element[4]:
                sequences += sequence + ","
            print(sequences)
        return sorted_positions
    #not used
    def int_to_char(self, i):
        switcher = {
            0: 'A',
            1: 'T',
            2: 'C',
            3: 'G'
        }
        return switcher[i]
    # ----------------------------------------------------------#
    # this function calls the closingWindow class.
    def closeEvent(self, event):
        GlobalSettings.mainWindow.closeFunction()
        event.accept()
