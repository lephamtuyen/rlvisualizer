from __future__ import print_function
import matplotlib as mpl
mpl.use('Qt4Agg',force=True)
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtCore
from PyQt4.uic import loadUiType
from matplotlib.lines import Line2D
from matplotlib.figure import Figure
from art_window import *
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
import matplotlib.cm as cm
from matplotlib.colors import rgb2hex
import matplotlib.animation as animation
from matplotlib.widgets import RectangleSelector
import time
import os
from collections import deque
import math
import random
import pickle
import matplotlib.pyplot as plt
random.seed(123)

# Ui_MainWindow, QMainWindow = loadUiType('art.ui')

class Main(QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super(Main, self).__init__()
        self.setupUi(self)

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        QObject.connect(self.about, SIGNAL("triggered()"), self, SLOT("slotAbout()"))
        QObject.connect(self.open, SIGNAL("triggered()"), self, SLOT("slotOpen()"))
        QObject.connect(self.saveAnimation, SIGNAL("triggered()"), self, SLOT("saveAnimationSlot()"))
        QObject.connect(self.saveData, SIGNAL("triggered()"), self, SLOT("saveDataSlot()"))
        QObject.connect(self.savePresets, SIGNAL("triggered()"), self, SLOT("savePresets()"))
        QObject.connect(self.storePresets, SIGNAL("triggered()"), self, SLOT("restorePresets()"))
        QObject.connect(self.addTitle, SIGNAL("triggered()"), self, SLOT("addTitleSlot()"))
        QObject.connect(self.selectArea, SIGNAL("triggered()"), self, SLOT("selectAreaSlot()"))
        QObject.connect(self.hideFlag, SIGNAL("triggered()"), self, SLOT("hideFlagSlot()"))
        QObject.connect(self.hideBorder, SIGNAL("triggered()"), self, SLOT("hideBorderSlot()"))
        QObject.connect(self.hideAuthors, SIGNAL("triggered()"), self, SLOT("hideAuthorsSlot()"))
        QObject.connect(self.backgroundColor, SIGNAL("triggered()"), self, SLOT("pickBackgroundColorSlot()"))
        QObject.connect(self.rainbowColor, SIGNAL("triggered()"), self, SLOT("rainbowColorSetSlot()"))
        QObject.connect(self.rangeColor, SIGNAL("triggered()"), self, SLOT("rangeColorSetSlot()"))
        # QObject.connect(self.trainingTimeOrder, SIGNAL("triggered()"), self, SLOT("trainingTimeOrderSlot()"))
        # QObject.connect(self.locationOrder, SIGNAL("triggered()"), self, SLOT("locationOrderSlot()"))
        QObject.connect(self.deleteSelectedLine, SIGNAL("triggered()"), self, SLOT("deleteSelectedLineSlot()"))
        QObject.connect(self.deleteUnselectedLine, SIGNAL("triggered()"), self, SLOT("deleteUnselectedLineSlot()"))

        QObject.connect(self.pickColor, SIGNAL("triggered()"), self, SLOT("pickColorSlot()"))
        self.pickColor.idx = 0
        self.exit.triggered.connect(sys.exit)

        HEADERS = ("Name", "Value")
        self.treeWidget.setColumnCount(2)
        self.treeWidget.setHeaderLabels(HEADERS)
        rightSelmodel = self.treeWidget.selectionModel()
        rightSelmodel.selectionChanged.connect(self.rightHandleSelection)

        self.leftTreeWidget.setColumnCount(2)
        self.leftTreeWidget.setHeaderLabels(HEADERS)
        leftSelmodel = self.leftTreeWidget.selectionModel()
        leftSelmodel.selectionChanged.connect(self.leftHandleSelection)

        self.fig = plt.figure()
        self.plots = None
        self.deletedLines = None
        self.addmpl(self.fig)
        self.selectedPlot = False
        self.checkedArea = False
        self.checkedFlag = True
        self.checkedBorder = False
        self.checkedAuthors = False
        self.pickedLines = None
        self.selectedAreaPlot = None
        self.selectedBatchPlot = None
        self.trajectory = None
        self.titleAnnotate = None
        self.alphaValue = 1.0
        self.colorSetIdx = 0
        self.trajectoryOrderIdx = 0
        self.ctrlKey = False
        self.rightTreeItem = None
        self.areaBtn = None
        self.recentColors = deque(maxlen=10)

        self.pickedBackgroundColor = 'white'
        plt.gcf().set_facecolor(self.pickedBackgroundColor)
        self.openFilePath = './'
        self.openPresetFilePath = './'

        self.selectedBatchColors = []
        self.selectedBatchColor = []
        self.colorBtns = []
        self.areaPlots = []
        self.areaTrajectories = []
        self.selectedAreaColor = []
        self.selectedAreaColors = []

    def get_start_end(self, idx):
        N = len(self.plots)
        numOfBatch = self.batchSpinBox.value()
        batchSize = int(np.ceil(N / numOfBatch))
        if (idx == 0):
            start_line = 0
            end_line = N - 1
        else:
            real_idx = idx - 1
            if (real_idx == 0):
                start_line = real_idx * batchSize
            else:
                start_line = real_idx * batchSize + 1

            if (real_idx == numOfBatch - 1):
                end_line = N - 1
            else:
                end_line = (real_idx + 1) * batchSize

        return start_line, end_line

    @pyqtSlot()
    def slotAbout(self):
        QMessageBox.about(self, "About", "Credit: Le Pham Tuyen\nDesigned by Qt4 Designer")

    def openFileFromPath(self, filepath):
        isFile = os.path.isfile(str(filepath))
        if (isFile == False):
            return

        self.statusBar.showMessage(filepath)

        dir = os.path.dirname(str(filepath))
        mpl.rcParams["savefig.directory"] = dir
        mpl.rcParams["savefig.format"] = "pdf"

        set_min_max = False
        data = self.restore_plot_data(str(filepath))
        if (len(data) > 2):
            self.trajectory = data
            self.goal = None
            self.radius = None
            set_min_max = True
        else:
            self.trajectory = np.asarray(data[0])
            self.goal = data[1][0]
            self.radius = data[1][1]

            if (len(data[1]) > 2):
                self.xmin = data[1][2]
                self.xmax = data[1][3]
                self.ymin = data[1][4]
                self.ymax = data[1][5]
            else:
                set_min_max = True

        plt.style.use('bmh')
        mpl.rcParams['xtick.labelsize'] = 5
        mpl.rcParams['ytick.labelsize'] = 5

        plt.gcf().set_facecolor(self.pickedBackgroundColor)
        mpl.rcParams['axes.facecolor'] = self.pickedBackgroundColor

        plt.clf()

        plt.gca().axes.set_xticks([])
        plt.gca().axes.set_yticks([])

        self.plots = [None] * self.trajectory.shape[0]
        self.deletedLines = [0] * self.trajectory.shape[0]

        colors = self.assignColorSet()
        self.random_draw_sequence = np.random.permutation(range(self.trajectory.shape[0]))

        if (set_min_max == True):
            self.xmin = 10000
            self.ymin = 10000
            self.xmax = -10000
            self.ymax = -10000
        for episode in range(self.trajectory.shape[0]):
            current_plot = plt.plot(
                self.trajectory[episode, 0],
                self.trajectory[episode, 1], linewidth=1.0, picker=5)
            current_plot[0].set_color(colors[episode])
            self.plots[self.random_draw_sequence[episode]] = current_plot

            if (set_min_max == True):
                x_values = self.trajectory[episode, 0]
                y_values = self.trajectory[episode, 1]

                if (len(x_values) > 0):
                    x_min_value = np.min(x_values)
                    if (self.xmin > x_min_value):
                        self.xmin = x_min_value

                    x_max_value = np.max(x_values)
                    if (self.xmax < x_max_value):
                        self.xmax = x_max_value

                if (len(y_values) > 0):
                    y_min_value = np.min(y_values)
                    if (self.ymin > y_min_value):
                        self.ymin = y_min_value

                    y_max_value = np.max(y_values)
                    if (self.ymax < y_max_value):
                        self.ymax = y_max_value

        # if (set_min_max == True):
        #     ratioIdx = ChooseRatioDialog(self).getIdx()
        #
        #     width = self.xmax - self.xmin
        #     height = self.ymax - self.ymin
        #
        #     if (ratioIdx == 0):  # 43
        #         top = 4
        #         down = 3
        #     elif (ratioIdx == 1):  # 34
        #         top = 3
        #         down = 4
        #     elif (ratioIdx == 2):  # 32
        #         top = 3
        #         down = 2
        #     elif (ratioIdx == 3):  # 32
        #         top = 2
        #         down = 3
        #     elif (ratioIdx == 4):  # 169
        #         top = 16
        #         down = 9
        #     elif (ratioIdx == 5):  # 169
        #         top = 9
        #         down = 16
        #     else:  # 11
        #         top = 1
        #         down = 1
        #
        #     self.ratio = top / down
        #
        #     if width < height*top/down:
        #         middle = (self.xmax + self.xmin) / 2
        #         new_width = height*top/down
        #         self.xmin = middle - new_width / 2
        #         self.xmax = middle + new_width / 2
        #     else:
        #         middle = (self.ymax + self.ymin) / 2
        #         new_height = height * down / top
        #         self.ymin = middle - new_height / 2
        #         self.ymax = middle + new_height / 2

        plt.gca().axes.set_xlim(left=self.xmin, right=self.xmax)
        plt.gca().axes.set_ylim(bottom=self.ymin, top=self.ymax)

        self.authorAnnotate = plt.gca().axes.annotate('Designed by Chung TaeChoong (tcchung@khu.ac.kr) and Le Pham Tuyen (tuyenple@khu.ac.kr) Dept. of Computer Engineering, KyungHee University',
                                xy=(0.5, 0), xycoords='axes fraction',
                                fontsize=5,
                                xytext=(0, -0.5), textcoords='offset points',
                                ha='center', va='top')

        #####################################################################
        self.flags = []
        if (self.goal is not None):
            t = np.linspace(0, 2 * np.pi, 100)
            r = self.radius
            xc = self.goal[0]
            yc = self.goal[1]
            x = xc + r * np.cos(t)
            y = yc + r * np.sin(t)
            self.flags.append(plt.plot(x, y, 'black', linewidth=1.0))

            t = np.linspace(0, np.pi, 100)
            r = self.radius
            xc = self.goal[0]
            yc = self.goal[1]
            x1 = xc + r * np.cos(t)
            y1 = yc + r * np.sin(t)
            x1 = np.reshape(x1, [-1, 1])
            y1 = np.reshape(y1, [-1, 1])
            xy1 = np.concatenate((x1, y1), axis=1)

            t = np.linspace(np.pi, 0, 50)
            r = self.radius / 2.0
            xc = self.goal[0] - r
            yc = self.goal[1]
            x2 = xc + r * np.cos(t)
            y2 = yc + r * np.sin(t)
            x2 = np.reshape(x2, [-1, 1])
            y2 = np.reshape(y2, [-1, 1])
            xy2 = np.concatenate((x2, y2), axis=1)

            t = np.linspace(np.pi, 2 * np.pi, 50)
            r = self.radius / 2.0
            xc = self.goal[0] + r
            yc = self.goal[1]
            x3 = xc + r * np.cos(t)
            y3 = yc + r * np.sin(t)
            x3 = np.reshape(x3, [-1, 1])
            y3 = np.reshape(y3, [-1, 1])
            xy3 = np.concatenate((x3, y3), axis=1)

            t = np.linspace(2 * np.pi, np.pi, 100)
            r = self.radius
            xc = self.goal[0]
            yc = self.goal[1]
            x4 = xc + r * np.cos(t)
            y4 = yc + r * np.sin(t)
            x4 = np.reshape(x4, [-1, 1])
            y4 = np.reshape(y4, [-1, 1])
            xy4 = np.concatenate((x4, y4), axis=1)

            topHalfData = np.concatenate((xy1, xy2, xy3))
            topHalf = plt.Polygon(topHalfData, color='red')
            plt.gcf().gca().add_artist(topHalf)
            self.flags.append(topHalf)

            bottomHalfData = np.concatenate((xy2, xy3, xy4))
            bottomHalf = plt.Polygon(bottomHalfData, color='blue')
            plt.gcf().gca().add_artist(bottomHalf)
            self.flags.append(bottomHalf)
        #####################################################################

        self.rmmpl()
        self.addmpl(self.fig, self.xmax - self.xmin, self.ymax - self.ymin)
        self.selectedPlot = True
        self.fig.tight_layout()

        self.selectedBox = RectangleSelector(plt.gca(),
                                             self.line_select_callback,
                                             drawtype='box', useblit=True,
                                             minspanx=5, minspany=5,
                                             spancoords='pixels')

        self.resetSlot()

    def usingPresets(self, preset):
        import matplotlib.pyplot as plt

        if (len(preset[0]) == 1):
            self.pickedBackgroundColor = preset[0]
            self.colorSetIdx = 2
        else:
            self.pickedBackgroundColor = preset[0][0]
            self.colorSetIdx = preset[0][1]

        thickness = preset[1]
        alpha = preset[2]
        self.alphaValue = alpha

        plt.style.use('bmh')
        mpl.rcParams['xtick.labelsize'] = 5
        mpl.rcParams['ytick.labelsize'] = 5

        plt.gcf().set_facecolor(self.pickedBackgroundColor)
        mpl.rcParams['axes.facecolor'] = self.pickedBackgroundColor

        plt.clf()

        plt.gca().axes.set_xticks([])
        plt.gca().axes.set_yticks([])

        self.plots = [None] * self.trajectory.shape[0]
        colors = cm.rainbow(np.linspace(0, 1, self.trajectory.shape[0]))
        colors[:,3] = 1.0
        for episode in range(self.trajectory.shape[0]):
            current_plot = plt.plot(
                self.trajectory[self.random_draw_sequence[episode], 0],
                self.trajectory[self.random_draw_sequence[episode], 1], linewidth=thickness, picker=5)

            current_plot[0].set_color(colors[self.random_draw_sequence[episode]])
            self.plots[self.random_draw_sequence[episode]] = current_plot

        self.authorAnnotate = plt.gca().axes.annotate(
            'Designed by Chung TaeChoong (tcchung@khu.ac.kr) and Le Pham Tuyen (tuyenple@khu.ac.kr) Dept. of Computer Engineering, KyungHee University',
            xy=(0.5, 0), xycoords='axes fraction',
            fontsize=5,
            xytext=(0, -0.5), textcoords='offset points',
            ha='center', va='top')

        #####################################################################
        self.flags = []
        if (self.goal is not None):
            t = np.linspace(0, 2 * np.pi, 100)
            r = self.radius
            xc = self.goal[0]
            yc = self.goal[1]
            x = xc + r * np.cos(t)
            y = yc + r * np.sin(t)
            self.flags.append(plt.plot(x, y, 'black', linewidth=1.0))

            t = np.linspace(0, np.pi, 100)
            r = self.radius
            xc = self.goal[0]
            yc = self.goal[1]
            x1 = xc + r * np.cos(t)
            y1 = yc + r * np.sin(t)
            x1 = np.reshape(x1, [-1, 1])
            y1 = np.reshape(y1, [-1, 1])
            xy1 = np.concatenate((x1, y1), axis=1)

            t = np.linspace(np.pi, 0, 50)
            r = self.radius / 2.0
            xc = self.goal[0] - r
            yc = self.goal[1]
            x2 = xc + r * np.cos(t)
            y2 = yc + r * np.sin(t)
            x2 = np.reshape(x2, [-1, 1])
            y2 = np.reshape(y2, [-1, 1])
            xy2 = np.concatenate((x2, y2), axis=1)

            t = np.linspace(np.pi, 2 * np.pi, 50)
            r = self.radius / 2.0
            xc = self.goal[0] + r
            yc = self.goal[1]
            x3 = xc + r * np.cos(t)
            y3 = yc + r * np.sin(t)
            x3 = np.reshape(x3, [-1, 1])
            y3 = np.reshape(y3, [-1, 1])
            xy3 = np.concatenate((x3, y3), axis=1)

            t = np.linspace(2 * np.pi, np.pi, 100)
            r = self.radius
            xc = self.goal[0]
            yc = self.goal[1]
            x4 = xc + r * np.cos(t)
            y4 = yc + r * np.sin(t)
            x4 = np.reshape(x4, [-1, 1])
            y4 = np.reshape(y4, [-1, 1])
            xy4 = np.concatenate((x4, y4), axis=1)

            topHalfData = np.concatenate((xy1, xy2, xy3))
            topHalf = plt.Polygon(topHalfData, color='red')
            plt.gcf().gca().add_artist(topHalf)
            self.flags.append(topHalf)

            bottomHalfData = np.concatenate((xy2, xy3, xy4))
            bottomHalf = plt.Polygon(bottomHalfData, color='blue')
            plt.gcf().gca().add_artist(bottomHalf)
            self.flags.append(bottomHalf)
        #####################################################################

        if (self.selectedPlot == True):
            self.isAnimated = False
            self.selectedBatchPlot = [0]

            colors[:, 3] = alpha
            if (self.colorSetIdx == 2):
                self.selectedBatchColor = preset[3]
                self.selectedBatchColors.append(self.selectedBatchColor)

                for color in self.selectedBatchColor:
                    self.recentColors.append(color)

                start_line, end_line = self.get_start_end(self.selectedBatchPlot[0])
                i = start_line
                while (i <= end_line):
                    self.plots[self.random_draw_sequence[i]][0].set_visible(True)
                    self.plots[self.random_draw_sequence[i]][0].set_linewidth(thickness)
                    self.plots[self.random_draw_sequence[i]][0].set_linestyle('solid')
                    self.plots[self.random_draw_sequence[i]][0].set_xdata(self.trajectory[i, 0])
                    self.plots[self.random_draw_sequence[i]][0].set_ydata(self.trajectory[i, 1])
                    color = random.choice(self.selectedBatchColor)
                    self.plots[self.random_draw_sequence[i]][0].set_color(color)
                    i+=1

                self.areaPlots = []
                self.areaTrajectories = []
                self.selectedAreaColors = []
                self.selectedAreaColor = []
            elif (self.colorSetIdx == 1):
                self.matplotlib_color1 = preset[3][0]
                self.matplotlib_color2 = preset[3][1]

                start_line, end_line = self.get_start_end(self.selectedBatchPlot[0])

                r1, g1, b1 = self.matplotlib_color1[0], self.matplotlib_color1[1], self.matplotlib_color1[2]
                r2, g2, b2 = self.matplotlib_color2[0], self.matplotlib_color2[1], self.matplotlib_color2[2]

                colors = []
                steps = end_line - start_line + 1
                rdelta, gdelta, bdelta = (r2 - r1) / steps, (g2 - g1) / steps, (b2 - b1) / steps
                for step in range(steps):
                    r1 += rdelta
                    g1 += gdelta
                    b1 += bdelta
                    if (r1 > 1):
                        r1 = 1
                    if (g1 > 1):
                        g1 = 1
                    if (b1 > 1):
                        b1 = 1

                    if (r1 < 0):
                        r1 = 0
                    if (g1 < 0):
                        g1 = 0
                    if (b1 < 0):
                        b1 = 0

                    colors.append([r1, g1, b1, 1.0])

                j = 0
                i = start_line
                while (i <= end_line):
                    plt = self.plots[self.random_draw_sequence[i]][0]
                    color = colors[j]
                    plt.set_color(color)
                    j += 1
                    i+=1

            self.hideFlagMode()
            self.treeWidget.clear()
            self.addTreeWidgetItems()
            self.leftTreeWidget.clear()
            self.refreshLeftTreeWidgetItems()
            self.selectedAreaPlot = None
            self.selectedBatchPlot = None

            self.canvas.draw()

    def updateBackgroundColor(self):
        plt.style.use('bmh')
        mpl.rcParams['xtick.labelsize'] = 5
        mpl.rcParams['ytick.labelsize'] = 5

        plt.gcf().set_facecolor(self.pickedBackgroundColor)
        mpl.rcParams['axes.facecolor'] = self.pickedBackgroundColor

        plt.clf()

        plt.gca().axes.set_xticks([])
        plt.gca().axes.set_yticks([])

        self.plots = [None] * self.trajectory.shape[0]

        colors = self.assignColorSet()

        for episode in range(self.trajectory.shape[0]):
            current_plot = plt.plot(
                self.trajectory[episode, 0],
                self.trajectory[episode, 1], linewidth=1.0, picker=5)
            current_plot[0].set_color(colors[episode])
            self.plots[self.random_draw_sequence[episode]] = current_plot

        self.authorAnnotate = plt.gca().axes.annotate(
            'Designed by Chung TaeChoong (tcchung@khu.ac.kr) and Le Pham Tuyen (tuyenple@khu.ac.kr) '
            'Dept. of Computer Engineering, KyungHee University',
            xy=(0.5, 0), xycoords='axes fraction',
            fontsize=5,
            xytext=(0, -0.5),
            textcoords='offset points',
            ha='center', va='top')

        #####################################################################
        self.flags = []
        if (self.goal is not None):
            t = np.linspace(0, 2 * np.pi, 100)
            r = self.radius
            xc = self.goal[0]
            yc = self.goal[1]
            x = xc + r * np.cos(t)
            y = yc + r * np.sin(t)
            self.flags.append(plt.plot(x, y, 'black', linewidth=1.0))

            t = np.linspace(0, np.pi, 100)
            r = self.radius
            xc = self.goal[0]
            yc = self.goal[1]
            x1 = xc + r * np.cos(t)
            y1 = yc + r * np.sin(t)
            x1 = np.reshape(x1, [-1, 1])
            y1 = np.reshape(y1, [-1, 1])
            xy1 = np.concatenate((x1, y1), axis=1)

            t = np.linspace(np.pi, 0, 50)
            r = self.radius / 2.0
            xc = self.goal[0] - r
            yc = self.goal[1]
            x2 = xc + r * np.cos(t)
            y2 = yc + r * np.sin(t)
            x2 = np.reshape(x2, [-1, 1])
            y2 = np.reshape(y2, [-1, 1])
            xy2 = np.concatenate((x2, y2), axis=1)

            t = np.linspace(np.pi, 2 * np.pi, 50)
            r = self.radius / 2.0
            xc = self.goal[0] + r
            yc = self.goal[1]
            x3 = xc + r * np.cos(t)
            y3 = yc + r * np.sin(t)
            x3 = np.reshape(x3, [-1, 1])
            y3 = np.reshape(y3, [-1, 1])
            xy3 = np.concatenate((x3, y3), axis=1)

            t = np.linspace(2 * np.pi, np.pi, 100)
            r = self.radius
            xc = self.goal[0]
            yc = self.goal[1]
            x4 = xc + r * np.cos(t)
            y4 = yc + r * np.sin(t)
            x4 = np.reshape(x4, [-1, 1])
            y4 = np.reshape(y4, [-1, 1])
            xy4 = np.concatenate((x4, y4), axis=1)

            topHalfData = np.concatenate((xy1, xy2, xy3))
            topHalf = plt.Polygon(topHalfData, color='red')
            plt.gcf().gca().add_artist(topHalf)
            self.flags.append(topHalf)

            bottomHalfData = np.concatenate((xy2, xy3, xy4))
            bottomHalf = plt.Polygon(bottomHalfData, color='blue')
            plt.gcf().gca().add_artist(bottomHalf)
            self.flags.append(bottomHalf)

        #####################################################################

        if (self.selectedPlot == True):
            self.isAnimated = False
            self.selectedBatchPlot = [0]

            colors[:, 3] = self.alphaSpinBox.value()

            if (len(self.selectedBatchColor)>0):
                start_line, end_line = self.get_start_end(self.selectedBatchPlot[0])

                i = start_line
                while (i <= end_line):
                    self.plots[self.random_draw_sequence[i]][0].set_visible(True)
                    self.plots[self.random_draw_sequence[i]][0].set_linewidth(self.lineSpinBox.value())
                    self.plots[self.random_draw_sequence[i]][0].set_linestyle('solid')
                    self.plots[self.random_draw_sequence[i]][0].set_xdata(self.trajectory[i, 0])
                    self.plots[self.random_draw_sequence[i]][0].set_ydata(self.trajectory[i, 1])
                    color = random.choice(self.selectedBatchColor)
                    self.plots[self.random_draw_sequence[i]][0].set_color(color)
                    i+=1

            self.canvas.draw()

            self.areaPlots = []
            self.areaTrajectories = []

            self.selectedAreaColors = []
            self.selectedAreaColor = []
            self.selectedBatchPlot = None
            self.selectedAreaPlot = None

            self.treeWidget.clear()
            self.addTreeWidgetItems()
            self.leftTreeWidget.clear()
            self.refreshLeftTreeWidgetItems()

    @pyqtSlot()
    def slotOpen(self):
        dir = os.path.dirname(str(self.openFilePath))
        # filename = os.path.basename(str(self.openFilePath))
        filepath = QtGui.QFileDialog.getOpenFileName(self,
                                                     'Open File',
                                                     dir,
                                                     '*.npy')
        isFile = os.path.isfile(str(filepath))

        if (isFile == False):
            return
        else:
            self.openFilePath = filepath

        self.openFileFromPath(self.openFilePath)

    def line_select_callback(self, eclick, erelease):
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        print("(%3.2f, %3.2f) --> (%3.2f, %3.2f)" % (x1, y1, x2, y2))

        if (self.selectedPlot == False):
            return

        if (self.pickedLines is not None):
            if (type(self.pickedLines) == int):
                plt = self.plots[self.random_draw_sequence[self.pickedLines]][0]
                plt.set_linestyle('solid')
                self.treeWidget.clear()
            elif (type(self.pickedLines) == list):
                for idx in self.pickedLines:
                    plt = self.plots[self.random_draw_sequence[idx]][0]
                    plt.set_linestyle('solid')
                    self.treeWidget.clear()
            self.pickedLines = None

        areaPlot = []
        areaTrajectory = []
        for i in range(len(self.plots)):
            if self.deletedLines[i]==False:
                if (len(self.trajectory[i, 0]) > 0):
                    if (self.checkedAreaByStart):
                            x = self.trajectory[i, 0][0]
                            y = self.trajectory[i, 1][0]
                    else:
                        x = self.trajectory[i, 0][len(self.trajectory[i,0])-1]
                        y = self.trajectory[i, 1][len(self.trajectory[i,1])-1]
                else:
                    x = None
                    y = None
                if (x is not None and y is not None and x > x1-5.0 and x < x2+5.0 and y > y1-5.0 and y < y2+5.0):
                    areaPlot.append(self.plots[self.random_draw_sequence[i]])
                    areaTrajectory.append(self.trajectory[i])
                    self.plots[self.random_draw_sequence[i]][0].set_visible(True)
                    color = self.plots[self.random_draw_sequence[i]][0].get_color()
                    color[3] = 1.0
                    self.plots[self.random_draw_sequence[i]][0].set_color(color)

        self.areaPlots.append(areaPlot)
        self.areaTrajectories.append(areaTrajectory)
        self.selectedAreaPlot = [len(self.areaPlots)-1]
        self.selectedAreaColors.append([])
        self.selectedAreaColor = self.selectedAreaColors[self.selectedAreaPlot[0]]

        self.treeWidget.clear()
        self.addTreeWidgetItems()
        self.leftTreeWidget.clear()
        self.refreshLeftTreeWidgetItems()
        self.canvas.draw()

    def addmpl(self, fig, x = None, y = None):
        self.canvas = FigureCanvas(fig)

        if (x is not None): # 800, 725
            self.canvas.setFixedSize(x, y)
            new_ratio = x / y
            if (new_ratio >= 0):
                self.canvas.setFixedSize(700.,700./new_ratio)
            else:
                self.canvas.setFixedSize(600 * new_ratio, 600)

        self.pickEvent = self.canvas.mpl_connect('pick_event', self.onPick)
        self.mplvl.addWidget(self.canvas)
        self.canvas.draw()

        self.plot_toolbar = NavigationToolbar(self.canvas, self, coordinates=False)
        self.addToolBar(self.plot_toolbar)
        self.addToolBarBreak(Qt.TopToolBarArea)

        self.custom_toolbar = self.addToolBar('custom')

        self.custom_toolbar.addWidget(QtGui.QLabel("Num of batchs"))
        self.batchSpinBox = QtGui.QSpinBox()
        self.batchSpinBox.setMinimum(2)
        self.batchSpinBox.setMaximum(100)
        self.batchSpinBox.setValue(10)
        self.custom_toolbar.addWidget(self.batchSpinBox)
        QObject.connect(self.batchSpinBox, SIGNAL("valueChanged(int)"), self, SLOT("batchChanged(int)"))

        self.custom_toolbar.addWidget(QtGui.QLabel("Speed"))
        self.speedSpinBox = QtGui.QSpinBox()
        self.speedSpinBox.setMinimum(1)
        self.speedSpinBox.setMaximum(999)
        self.speedSpinBox.setValue(100)
        self.custom_toolbar.addWidget(self.speedSpinBox)

        self.intervalSpinBox = QtGui.QSpinBox()
        self.intervalSpinBox.setMinimum(1)
        self.intervalSpinBox.setMaximum(100)
        self.intervalSpinBox.setValue(1)

        self.animateBtn = QtGui.QPushButton("Animate")
        self.animateBtn.connect(self.animateBtn, SIGNAL("clicked()"), self, SLOT("animateBtnClickedSlot()"))
        self.custom_toolbar.addWidget(self.animateBtn)

        self.deleteLinesBtn = QtGui.QPushButton("Delete Lines")
        self.deleteLinesBtn.connect(self.deleteLinesBtn, SIGNAL("clicked()"), self, SLOT("deleteSelectedLineSlot()"))
        self.custom_toolbar.addWidget(self.deleteLinesBtn)

        self.deleteUnselectedLinesBtn = QtGui.QPushButton("Delete Unselected Lines")
        self.deleteUnselectedLinesBtn.connect(self.deleteUnselectedLinesBtn, SIGNAL("clicked()"), self, SLOT("deleteUnselectedLineSlot()"))
        self.custom_toolbar.addWidget(self.deleteUnselectedLinesBtn)

        self.areaBtn = QtGui.QPushButton("Area by Start")
        self.checkedAreaByStart = True
        self.areaBtn.connect(self.areaBtn, SIGNAL("clicked()"), self, SLOT("areaBtnClickedSlot()"))
        self.custom_toolbar.addWidget(self.areaBtn)

        self.resetBtn = QtGui.QPushButton("Reset")
        self.resetBtn.connect(self.resetBtn, SIGNAL("clicked()"), self, SLOT("resetSlot()"))
        self.custom_toolbar.addWidget(self.resetBtn)

    def animateBatch(self):

        plot = self.plots[self.random_draw_sequence[self.idxForAnimate]][0]

        if (len(self.animateData[self.idxForAnimate, 0]) == len(self.trajectory[self.idxForAnimate, 0])):
            self.animateData[self.idxForAnimate, 0] = self.trajectory[self.idxForAnimate, 0]
            self.animateData[self.idxForAnimate, 1] = self.trajectory[self.idxForAnimate, 1]
        else:
            new_length = self.speedSpinBox.value() + len(self.animateData[self.idxForAnimate, 0])
            if (new_length > len(self.trajectory[self.idxForAnimate, 0])):
                new_length = len(self.trajectory[self.idxForAnimate, 0])

            self.animateData[self.idxForAnimate, 0] = self.trajectory[self.idxForAnimate, 0][:new_length]
            self.animateData[self.idxForAnimate, 1] = self.trajectory[self.idxForAnimate, 1][:new_length]

        plot.set_xdata(self.animateData[self.idxForAnimate, 0])
        plot.set_ydata(self.animateData[self.idxForAnimate, 1])
        # plot.set_linewidth(2.0)

        if (len(self.animateData[self.idxForAnimate, 0]) == len(self.trajectory[self.idxForAnimate, 0])):
            # plot.set_linewidth(1.0)

            self.idxForAnimate = self.idxForAnimate + self.intervalSpinBox.value()

        self.canvas.draw()

        if (self.idxForAnimate <= self.end_line and self.isAnimated == True):
            QtCore.QTimer.singleShot(1, self.animateBatch)
        else:
            self.treeWidget.setEnabled(True)
            self.leftTreeWidget.setEnabled(True)
            self.speedSpinBox.setEnabled(True)
            self.intervalSpinBox.setEnabled(True)
            self.animateBtn.setEnabled(True)
            self.isAnimated = False

    def animateArea(self):
        if (self.selectedAreaPlot is None or len(self.selectedAreaPlot) > 1):
            return

        plot = self.areaPlots[self.selectedAreaPlot[0]][self.idxForAnimateArea][0]
        trajectories = self.areaTrajectories[self.selectedAreaPlot[0]]
        if (len(self.animateData[self.idxForAnimateArea, 0]) == len(trajectories[self.idxForAnimateArea][0])):
            self.animateData[self.idxForAnimateArea, 0] = trajectories[self.idxForAnimateArea][0]
            self.animateData[self.idxForAnimateArea, 1] = trajectories[self.idxForAnimateArea][1]
        else:
            new_length = self.speedSpinBox.value() + len(self.animateData[self.idxForAnimateArea, 0])
            if (new_length > len(trajectories[self.idxForAnimateArea][0])):
                new_length = len(trajectories[self.idxForAnimateArea][0])

            self.animateData[self.idxForAnimateArea, 0] = trajectories[self.idxForAnimateArea][0][:new_length]
            self.animateData[self.idxForAnimateArea, 1] = trajectories[self.idxForAnimateArea][1][:new_length]

        plot.set_xdata(self.animateData[self.idxForAnimateArea, 0])
        plot.set_ydata(self.animateData[self.idxForAnimateArea, 1])
        # plot.set_linewidth(2.0)

        if (len(self.animateData[self.idxForAnimateArea, 0]) == len(trajectories[self.idxForAnimateArea][0])):
            # plot.set_linewidth(1.0)

            self.idxForAnimateArea = self.idxForAnimateArea + self.intervalSpinBox.value()

        self.canvas.draw()

        if (self.idxForAnimateArea < len(self.areaPlots[self.selectedAreaPlot[0]]) and self.isAnimated == True):
            QtCore.QTimer.singleShot(1, self.animateArea)
        else:
            self.treeWidget.setEnabled(True)
            self.leftTreeWidget.setEnabled(True)
            self.speedSpinBox.setEnabled(True)
            self.intervalSpinBox.setEnabled(True)
            self.animateBtn.setEnabled(True)
            self.isAnimated = False

    @pyqtSlot()
    def saveFileSlot(self):

        filePath = QFileDialog.getSaveFileName(self, 'Save File', "./", '*.pdf')

        if filePath == "":
            return

        if ".pdf" not in filePath:
            filePath = filePath + ".pdf"

            filePath = str(filePath)

        self.fig.savefig(filePath)

    @pyqtSlot()
    def addTitleSlot(self):
        title = AddTitleDialog(self).getTitle()

        if (self.selectedPlot == False):
            return

        if title == "":
            return

        if (self.titleAnnotate is not None):
            self.titleAnnotate.remove()

        self.titleAnnotate = plt.gca().axes.annotate("Title: " + title, xy=(0, 1), xycoords='axes fraction',
                                fontsize=10,
                                xytext=(0, 10.0), textcoords='offset points',
                                ha='left', va='top')
        self.canvas.draw()

    @pyqtSlot()
    def hideFlagSlot(self):
        if (self.selectedPlot == False):
            return

        if self.checkedFlag == False:
            self.hideFlagMode()
        else:
            self.unHideFlagMode()

        self.canvas.draw()

    def hideFlagMode(self):
        if (self.goal is None):
            return

        self.flags[0][0].set_visible(False)
        self.flags[1].set_visible(False)
        self.flags[2].set_visible(False)

        self.hideFlag.setText("Show Flag")
        self.checkedFlag = True

    def unHideFlagMode(self):
        if (self.goal is None):
            return

        self.flags[0][0].set_visible(True)
        self.flags[1].set_visible(True)
        self.flags[2].set_visible(True)

        self.hideFlag.setText("Hide Flag")
        self.checkedFlag = False

    @pyqtSlot()
    def hideBorderSlot(self):
        if (self.selectedPlot == False):
            return

        if self.checkedBorder == False:
            self.hideBorderMode()
        else:
            self.unHideBorderMode()

        self.canvas.draw()

    def hideBorderMode(self):
        plt.axis('off')

        self.hideBorder.setText("Show Border")
        self.checkedBorder = True

    def unHideBorderMode(self):
        plt.axis('on')

        self.hideBorder.setText("Hide Border")
        self.checkedBorder = False

    def assignColorSet(self):
        if (self.trajectory is None):
            return

        colors = cm.rainbow(np.linspace(0, 1, self.trajectory.shape[0]))
        colors[:, 3] = 1.0

        return colors

    @pyqtSlot()
    def rainbowColorSetSlot(self):
        if self.selectedPlot == False :
            return

        self.colorSetIdx = 0

        if (self.checkedArea and self.selectedAreaPlot is not None and len(self.selectedAreaPlot)==1):
            colors = cm.rainbow(np.linspace(0, 1, len(self.areaPlots[self.selectedAreaPlot[0]])))
            colors[:, 3] = 1.0

            for i in range(len(self.areaPlots[self.selectedAreaPlot[0]])):
                plt = self.areaPlots[self.selectedAreaPlot[0]][i][0]
                color = colors[i]
                plt.set_color(color)
        elif (type(self.pickedLines) == int):
            pass
        elif (type(self.pickedLines) == list):
            colors = cm.rainbow(np.linspace(0, 1, len(self.pickedLines)))
            colors[:, 3] = 1.0
            j = 0
            for idx in self.pickedLines:
                plt = self.plots[self.random_draw_sequence[idx]][0]
                color = colors[j]
                plt.set_color(color)
                j+=1
        elif (not self.checkedArea and self.selectedBatchPlot is not None):
            if (self.trainingOrder == 0):
                start_line, end_line = self.get_start_end(self.selectedBatchPlot[0])

                colors = cm.rainbow(np.linspace(0, 1, end_line - start_line + 1))
                colors[:, 3] = 1.0
                j = 0
                i = start_line
                while (i <= end_line):
                    plt = self.plots[self.random_draw_sequence[i]][0]
                    color = colors[j]
                    plt.set_color(color)
                    j += 1
                    i+=1
            elif(self.trainingOrder == 1):
                numOfBatch = self.batchSpinBox.value()
                idx = self.selectedBatchPlot[0]
                if (idx == 0):
                    x_idx = 0
                    y_idx = 0
                else:
                    x_idx = idx // numOfBatch
                    y_idx = idx % numOfBatch

                x1 = self.xmin + x_idx * (self.xmax - self.xmin) / numOfBatch
                x2 = self.xmin + (x_idx + 1) * (self.xmax - self.xmin) / numOfBatch
                y1 = self.ymin + y_idx * (self.ymax - self.ymin) / numOfBatch
                y2 = self.ymin + (y_idx + 1) * (self.ymax - self.ymin) / numOfBatch

                plots = []
                for i in range(len(self.plots)):
                    x = self.trajectory[i, 0][0]
                    y = self.trajectory[i, 1][0]
                    if (x > x1 and x < x2 and y > y1 and y < y2):
                        plots.append(self.plots[self.random_draw_sequence[i]][0])

                colors = cm.rainbow(np.linspace(0, 1, len(plots)))
                colors[:, 3] = 1.0
                j = 0
                for plt in plots:
                    color = colors[j]
                    plt.set_color(color)
                    j += 1

        self.treeWidget.clear()
        self.addTreeWidgetItems()
        self.canvas.draw()

    @pyqtSlot()
    def rangeColorSetSlot(self):
        if self.selectedPlot == False :
            return

        self.colorSetIdx = 1

        color1 = QtGui.QColorDialog.getColor()
        self.matplotlib_color1 = str(color1.name()).lstrip('#')
        self.matplotlib_color1 = [int(self.matplotlib_color1[i:i + 2], 16) for i in (0, 2, 4)]
        self.matplotlib_color1 = np.array(self.matplotlib_color1) / 255.0

        color2 = QtGui.QColorDialog.getColor()
        self.matplotlib_color2 = str(color2.name()).lstrip('#')
        self.matplotlib_color2 = [int(self.matplotlib_color2[i:i + 2], 16) for i in (0, 2, 4)]
        self.matplotlib_color2 = np.array(self.matplotlib_color2) / 255.0

        r1, g1, b1 = self.matplotlib_color1[0], self.matplotlib_color1[1], self.matplotlib_color1[2]
        r2, g2, b2 = self.matplotlib_color2[0], self.matplotlib_color2[1], self.matplotlib_color2[2]

        if (self.checkedArea == True and self.selectedAreaPlot is not None and len(self.selectedAreaPlot)==1):
            colors = []
            steps = len(self.areaPlots[self.selectedAreaPlot[0]])
            rdelta, gdelta, bdelta = (r2 - r1) / steps, (g2 - g1) / steps, (b2 - b1) / steps
            for step in range(steps):
                r1 += rdelta
                g1 += gdelta
                b1 += bdelta

                if (r1 > 1):
                    r1 = 1
                if (g1 > 1):
                    g1 = 1
                if (b1 > 1):
                    b1 = 1

                if (r1 < 0):
                    r1 = 0
                if (g1 < 0):
                    g1 = 0
                if (b1 < 0):
                    b1 = 0
                colors.append([r1, g1, b1, 1.0])

            for i in range(len(self.areaPlots[self.selectedAreaPlot[0]])):
                plt = self.areaPlots[self.selectedAreaPlot[0]][i][0]
                color = colors[i]
                plt.set_color(color)
        elif (type(self.pickedLines) == int):
            pass
        elif(type(self.pickedLines) == list):
            colors = []
            steps = len(self.pickedLines)
            rdelta, gdelta, bdelta = (r2 - r1) / steps, (g2 - g1) / steps, (b2 - b1) / steps
            for step in range(steps):
                r1 += rdelta
                g1 += gdelta
                b1 += bdelta
                if (r1 > 1):
                    r1 = 1
                if (g1 > 1):
                    g1 = 1
                if (b1 > 1):
                    b1 = 1

                if (r1 < 0):
                    r1 = 0
                if (g1 < 0):
                    g1 = 0
                if (b1 < 0):
                    b1 = 0

                colors.append([r1, g1, b1, 1.0])

            j = 0
            for idx in self.pickedLines:
                plt = self.plots[self.random_draw_sequence[idx]][0]
                color = colors[j]
                plt.set_color(color)
                j += 1
        elif (self.selectedBatchPlot is not None):
            if (self.trainingOrder == 0):
                start_line, end_line = self.get_start_end(self.selectedBatchPlot[0])

                colors = []
                steps = end_line - start_line + 1
                rdelta, gdelta, bdelta = (r2 - r1) / steps, (g2 - g1) / steps, (b2 - b1) / steps
                for step in range(steps):
                    r1 += rdelta
                    g1 += gdelta
                    b1 += bdelta
                    if (r1 > 1):
                        r1 = 1
                    if (g1 > 1):
                        g1 = 1
                    if (b1 > 1):
                        b1 = 1

                    if (r1 < 0):
                        r1 = 0
                    if (g1 < 0):
                        g1 = 0
                    if (b1 < 0):
                        b1 = 0

                    colors.append([r1, g1, b1, 1.0])

                j = 0
                for i in range(len(self.plots)):
                    if (i >= start_line and i <= end_line):
                        plt = self.plots[self.random_draw_sequence[i]][0]
                        color = colors[j]
                        plt.set_color(color)
                        j += 1
            elif(self.trainingOrder == 1):
                numOfBatch = self.batchSpinBox.value()
                idx = self.selectedBatchPlot[0]
                if (idx == 0):
                    x_idx = 0
                    y_idx = 0
                else:
                    x_idx = idx // numOfBatch
                    y_idx = idx % numOfBatch

                x1 = self.xmin + x_idx * (self.xmax - self.xmin) / numOfBatch
                x2 = self.xmin + (x_idx + 1) * (self.xmax - self.xmin) / numOfBatch
                y1 = self.ymin + y_idx * (self.ymax - self.ymin) / numOfBatch
                y2 = self.ymin + (y_idx + 1) * (self.ymax - self.ymin) / numOfBatch

                plots = []
                for i in range(len(self.plots)):
                    x = self.trajectory[i, 0][0]
                    y = self.trajectory[i, 1][0]
                    if (x > x1 and x < x2 and y > y1 and y < y2):
                        plots.append(self.plots[self.random_draw_sequence[i]][0])

                colors = []
                steps = len(plots)
                rdelta, gdelta, bdelta = (r2 - r1) / steps, (g2 - g1) / steps, (b2 - b1) / steps
                for step in range(steps):
                    r1 += rdelta
                    g1 += gdelta
                    b1 += bdelta
                    if (r1 > 1):
                        r1 = 1
                    if (g1 > 1):
                        g1 = 1
                    if (b1 > 1):
                        b1 = 1

                    if (r1 < 0):
                        r1 = 0
                    if (g1 < 0):
                        g1 = 0
                    if (b1 < 0):
                        b1 = 0

                    colors.append([r1, g1, b1, 1.0])

                j = 0
                for plot in plots:
                    color = colors[j]
                    plot.set_color(color)
                    j += 1

        self.treeWidget.clear()
        self.addTreeWidgetItems()
        self.canvas.draw()

    @pyqtSlot()
    def trainingTimeOrderSlot(self):
        if (self.selectedPlot == False):
            return

        self.trainingOrder = 0

        self.batchSpinBox.setMinimum(2)
        self.batchSpinBox.setMaximum(100)
        self.batchSpinBox.setValue(10)

    @pyqtSlot()
    def locationOrderSlot(self):
        if (self.selectedPlot == False):
            return

        self.trainingOrder = 1

        self.batchSpinBox.setMinimum(1)
        self.batchSpinBox.setMaximum(10)
        self.batchSpinBox.setValue(1)

    @pyqtSlot()
    def deleteSelectedLineSlot(self):
        if (self.selectedPlot == False):
            return

        if (self.checkedArea == True and self.selectedAreaPlot is not None):
            for area_idx in self.selectedAreaPlot:
                for j in range(len(self.areaPlots[area_idx])):
                    plt = self.areaPlots[area_idx][j][0]
                    idx = int(plt.get_label().replace("_line", ""))
                    plt.set_visible(False)
                    self.deletedLines[idx] = True

                del self.areaPlots[area_idx]

            self.selectedAreaPlot = None

        elif (self.pickedLines is not None):
            if (type(self.pickedLines) == int):
                plt = self.plots[self.random_draw_sequence[self.pickedLines]][0]
                plt.set_visible(False)
                self.deletedLines[self.pickedLines] = True
            elif (type(self.pickedLines) == list):
                for idx in self.pickedLines:
                    plt = self.plots[self.random_draw_sequence[idx]][0]
                    plt.set_visible(False)
                    self.deletedLines[idx] = True
            self.pickedLines = None
        elif(not self.checkedArea and self.selectedBatchPlot is not None):
            for batch_idx in self.selectedBatchPlot:
                start_line, end_line = self.get_start_end(batch_idx)
                i = start_line
                while i <= end_line:
                    plt = self.plots[self.random_draw_sequence[i]][0]
                    plt.set_visible(False)
                    self.deletedLines[i] = True

                    i += 1
                if (batch_idx == 0):
                    break

        self.leftTreeWidget.clear()
        self.treeWidget.clear()
        self.addTreeWidgetItems()
        self.refreshLeftTreeWidgetItems()
        self.canvas.draw()

    @pyqtSlot()
    def deleteUnselectedLineSlot(self):
        if (self.selectedPlot == False):
            return

        if (self.checkedArea == True and self.selectedAreaPlot is not None):
            # Keep lines
            keep_lines = []
            for area_idx in self.selectedAreaPlot:
                for j in range(len(self.areaPlots[area_idx])):
                    plt = self.areaPlots[area_idx][j][0]
                    idx = int(plt.get_label().replace("_line", ""))
                    keep_lines.append(idx)

            for i in range(len(self.plots)):
                if (i not in keep_lines):
                    plt = self.plots[self.random_draw_sequence[i]][0]
                    plt.set_visible(False)
                    self.deletedLines[i] = True

            temp = []
            for area_idx in self.selectedAreaPlot:
                temp.append(self.areaPlots[area_idx])
            self.areaPlots = temp
        elif (self.pickedLines is not None):
            if (type(self.pickedLines) == int):
                start_line, end_line = self.get_start_end(self.selectedBatchPlot)
                i = start_line
                while i <= end_line:
                    if(i != self.pickedLines):
                        plt = self.plots[self.random_draw_sequence[i]][0]
                        plt.set_visible(False)
                        self.deletedLines[i] = True
                    i += 1
            elif (type(self.pickedLines) == list):
                start_line, end_line = self.get_start_end(self.selectedBatchPlot)
                i = start_line
                while i <= end_line:
                    if (i not in self.pickedLines):
                        plt = self.plots[self.random_draw_sequence[i]][0]
                        plt.set_visible(False)
                        self.deletedLines[i] = True
                    i += 1
        elif (self.selectedBatchPlot is not None):
            numOfBatch = self.batchSpinBox.value()
            for batch_idx in range(numOfBatch + 1):
                start_line, end_line = self.get_start_end(batch_idx)
                if (batch_idx not in self.selectedBatchPlot and batch_idx != 0):
                    i = start_line
                    while i <= end_line:
                        plt = self.plots[self.random_draw_sequence[i]][0]
                        plt.set_visible(False)
                        self.deletedLines[i] = True
                        i += 1

        self.treeWidget.clear()
        self.addTreeWidgetItems()
        self.canvas.draw()

    @pyqtSlot()
    def hideAuthorsSlot(self):
        if (self.selectedPlot == False):
            return

        if self.checkedAuthors == False:
            self.hideAuthorsMode()
        else:
            self.unHideAuthorsMode()

        self.canvas.draw()

    def hideAuthorsMode(self):
        self.authorAnnotate.remove()

        self.hideAuthors.setText("Show Authors")
        self.checkedAuthors = True

    def unHideAuthorsMode(self):
        self.authorAnnotate = plt.gca().axes.annotate(
            'Designed by Chung TaeChoong (tcchung@khu.ac.kr) and Le Pham Tuyen (tuyenple@khu.ac.kr) Dept. of Computer Engineering, KyungHee University',
            xy=(0.5, 0), xycoords='axes fraction',
            fontsize=5,
            xytext=(0, -0.5), textcoords='offset points',
            ha='center', va='top')

        self.hideAuthors.setText("Hide Authors")
        self.checkedAuthors = False

    @pyqtSlot()
    def areaBtnClickedSlot(self):
        if (self.checkedAreaByStart):
            self.areaBtn.setText("Area by End")
            self.checkedAreaByStart = False
        else:
            self.areaBtn.setText("Area by Start")
            self.checkedAreaByStart = True

    @pyqtSlot()
    def selectAreaSlot(self):
        if (self.selectedPlot == False):
            return

        if self.checkedArea == False:
            self.selectAreaMode()
        else:
            self.unselectAreaMode()

        self.canvas.draw()

    def selectAreaMode(self):
        self.selectArea.setText("Unselect Area")
        self.checkedArea = True

        self.selectedBox.set_visible(True)
        self.selectedBox.set_active(True)
        self.canvas.mpl_disconnect(self.pickEvent)
        self.leftTreeWidget.clear()
        self.refreshLeftTreeWidgetItems()

        for i in range(len(self.plots)):
            if self.deletedLines[i] == False:
                self.plots[self.random_draw_sequence[i]][0].set_visible(True)
                self.plots[self.random_draw_sequence[i]][0].set_linewidth(1.0)
                self.plots[self.random_draw_sequence[i]][0].set_linestyle('solid')
                color = self.plots[self.random_draw_sequence[i]][0].get_color()
                color[3] = 0.1
                self.plots[self.random_draw_sequence[i]][0].set_color(color)

        for areaPlot in self.areaPlots:
            for i in range(len(areaPlot)):
                color = areaPlot[i][0].get_color()
                color[3] = 1.0
                areaPlot[i][0].set_color(color)

    def unselectAreaMode(self):
        self.selectArea.setText("Select Area")
        self.checkedArea = False
        self.selectedBox.set_visible(False)
        self.selectedBox.set_active(False)
        self.pickEvent = self.canvas.mpl_connect('pick_event', self.onPick)

        for i in range(len(self.plots)):
            if self.deletedLines[i] == False:
                self.plots[self.random_draw_sequence[i]][0].set_visible(True)
                self.plots[self.random_draw_sequence[i]][0].set_linewidth(1.0)
                self.plots[self.random_draw_sequence[i]][0].set_linestyle('solid')
                color = self.plots[self.random_draw_sequence[i]][0].get_color()
                color[3] = 1.0
                self.plots[self.random_draw_sequence[i]][0].set_color(color)

        self.leftTreeWidget.clear()
        self.refreshLeftTreeWidgetItems()

    @pyqtSlot()
    def saveAnimationSlot(self):
        if (self.plots is None):
            return

        videoFilePath = QFileDialog.getSaveFileName(self, 'Save Animation File', "./", '*.mp4')

        if videoFilePath == "":
            return

        if ".mp4" not in videoFilePath:
            videoFilePath = videoFilePath + ".mp4"

        videoFilePath = str(videoFilePath)

        if (not self.checkedArea and self.selectedBatchPlot is not None and len(self.selectedBatchPlot) == 1):

            self.start_line, self.end_line = self.get_start_end(self.selectedBatchPlot[0])

            self.animateData = np.array(self.trajectory)
            j=0
            current_idx = self.start_line
            total_line = self.end_line - self.start_line + 1
            for i in range(len(self.plots)):
                self.animateData[i, 0] = []
                self.animateData[i, 1] = []
                plot = self.plots[self.random_draw_sequence[i]][0]
                if (i >= self.start_line and i <= self.end_line):
                    if ((current_idx - self.start_line) % self.intervalSpinBox.value()) == 0:
                        self.plots[self.random_draw_sequence[i]][0].set_visible(True)
                        current_idx = current_idx + self.intervalSpinBox.value()
                    else:
                        self.plots[self.random_draw_sequence[i]][0].set_visible(False)
                    j=j+1
                else:
                    self.plots[self.random_draw_sequence[i]][0].set_visible(False)

                plot.set_xdata(self.animateData[i, 0])
                plot.set_ydata(self.animateData[i, 1])

            FFMpegWriter = animation.writers['ffmpeg']
            plt.rcParams['animation.ffmpeg_path'] = 'ffmpeg.exe'
            metadata = dict(title='Trajectory Animation', artist='Trajectory Animation')
            movie = FFMpegWriter(fps=15, metadata=metadata)
            with movie.saving(self.fig, videoFilePath, 200):
                i = self.start_line
                line_count = 0
                while (i >= self.start_line and i <= self.end_line):

                    plot = self.plots[self.random_draw_sequence[i]][0]
                    if (len(self.animateData[i, 0]) == len(self.trajectory[i, 0])):
                        self.animateData[i, 0] = self.trajectory[i, 0]
                        self.animateData[i, 1] = self.trajectory[i, 1]
                    else:
                        new_length = self.speedSpinBox.value() + len(self.animateData[i, 0])
                        if (new_length > len(self.trajectory[i, 0])):
                            new_length = len(self.trajectory[i, 0])

                        self.animateData[i, 0] = self.trajectory[i, 0][:new_length]
                        self.animateData[i, 1] = self.trajectory[i, 1][:new_length]

                    plot.set_xdata(self.animateData[i, 0])
                    plot.set_ydata(self.animateData[i, 1])

                    movie.grab_frame()

                    if (len(self.animateData[i, 0]) == len(self.trajectory[i, 0])):
                        i = i + self.intervalSpinBox.value()
                        line_count += 1.0
                        print("Percent completed: ", line_count * 100 / total_line)

                for i in range(100):
                    movie.grab_frame()
        elif (self.checkedArea and self.selectedAreaPlot is not None and len(self.selectedAreaPlot)==1):
            self.animateData = np.array(self.areaTrajectories[self.selectedAreaPlot[0]])
            for i in range(len(self.plots)):
                self.plots[self.random_draw_sequence[i]][0].set_visible(False)

            for i in range(len(self.areaPlots[self.selectedAreaPlot[0]])):
                self.animateData[i, 0] = []
                self.animateData[i, 1] = []
                plot = self.areaPlots[self.selectedAreaPlot[0]][i][0]
                plot.set_xdata(self.animateData[i, 0])
                plot.set_ydata(self.animateData[i, 1])

                self.areaPlots[self.selectedAreaPlot[0]][i][0].set_visible(True)

            FFMpegWriter = animation.writers['ffmpeg']
            plt.rcParams['animation.ffmpeg_path'] = 'ffmpeg.exe'
            metadata = dict(title='Trajectory Animation', artist='Trajectory Animation')
            movie = FFMpegWriter(fps=15, metadata=metadata)
            trajectories = self.areaTrajectories[self.selectedAreaPlot[0]]
            with movie.saving(self.fig, videoFilePath, 100):
                i = 0
                batch_size = len(self.areaPlots[self.selectedAreaPlot[0]])
                while i < batch_size:
                    plot = self.areaPlots[self.selectedAreaPlot[0]][i][0]

                    if (len(self.animateData[i, 0]) == len(trajectories[i][0])):
                        self.animateData[i, 0] = trajectories[i][0]
                        self.animateData[i, 1] = trajectories[i][1]
                    else:
                        new_length = self.speedSpinBox.value() + len(self.animateData[i, 0])
                        if (new_length > len(trajectories[i][0])):
                            new_length = len(trajectories[i][0])

                        self.animateData[i, 0] = trajectories[i][0][:new_length]
                        self.animateData[i, 1] = trajectories[i][1][:new_length]

                    plot.set_xdata(self.animateData[i, 0])
                    plot.set_ydata(self.animateData[i, 1])

                    movie.grab_frame()

                    if (len(self.animateData[i, 0]) == len(trajectories[i][0])):
                        i = i + 1
                        print("Percent completed: ", i * 100 / batch_size)

                for i in range(100):
                    movie.grab_frame()

    @pyqtSlot()
    def saveDataSlot(self):
        if (self.plots is None):
            return

        filePath = QFileDialog.getSaveFileName(self, 'Save Visible Data', "./", '*.npy')

        if filePath == "":
            return

        if ".npy" not in filePath:
            filePath = filePath + ".npy"

        filePath = str(filePath)

        data = []
        for episode in range(self.trajectory.shape[0]):
            if (self.deletedLines[episode] == False):
                data.append(self.trajectory[episode, :])

        if (self.goal is None):
            self.save_plot_data(filePath, [data, [None,
                                                  None,
                                                  self.xmin,
                                                  self.xmax,
                                                  self.ymin,
                                                  self.ymax]])
        else:
            self.save_plot_data(filePath, [data, [np.array([self.goal[0], self.goal[1]]),
                                                  self.radius,
                                                  self.xmin,
                                                  self.xmax,
                                                  self.ymin,
                                                  self.ymax]])

        # xlim = plt.gca().axes.get_xlim()
        # ylim = plt.gca().axes.get_ylim()
        # self.save_plot_data(filePath, [data, [np.array([self.goal[0],self.goal[1]]),
        #                                       self.radius,
        #                                       xlim[0],
        #                                       xlim[1],
        #                                       ylim[0],
        #                                       ylim[1]]])

    @pyqtSlot()
    def restorePresets(self):
        if (self.plots is None):
            return

        dir = os.path.dirname(str(self.openPresetFilePath))
        filepath = QtGui.QFileDialog.getOpenFileName(self,
                                                     'Open File',
                                                     dir)
        isFile = os.path.isfile(str(filepath))

        if (isFile == False):
            return
        else:
            self.openPresetFilePath = filepath

        isFile = os.path.isfile(str(filepath))
        if (isFile == False):
            return

        f = open(str(filepath), 'rb')
        data = pickle.load(f, encoding='latin1')
        f.close()
        self.usingPresets(data)

    @pyqtSlot()
    def savePresets(self):
        if (self.plots is None):
            return

        preset = []
        # background color
        preset.append([self.pickedBackgroundColor, self.colorSetIdx])
        # thickness
        preset.append(self.lineSpinBox.value())
        # alpha
        preset.append(self.alphaSpinBox.value())

        # colors
        if (self.colorSetIdx == 2):
            if (self.selectedBatchColor is not None and len(self.selectedBatchColor) > 0):
                preset.append(self.selectedBatchColor)
            else:
                preset.append(None)
        elif (self.colorSetIdx == 1):
            preset.append([self.matplotlib_color1, self.matplotlib_color2])

        filePath = QFileDialog.getSaveFileName(self, 'Save File', "./")

        if filePath == "":
            return

        filePath = str(filePath)
        f = open(filePath, 'wb')
        pickle.dump(preset, f)
        f.close()

    @pyqtSlot()
    def resetSlot(self):
        if (self.selectedPlot == True):
            self.deletedLines = [0] * self.trajectory.shape[0]

            self.isAnimated = False
            self.selectedBatchPlot = [0]
            colors = cm.rainbow(np.linspace(0, 1, self.trajectory.shape[0]))
            colors[:, 3] = 1.0
            for i in range(len(self.plots)):
                self.plots[self.random_draw_sequence[i]][0].set_visible(True)
                self.plots[self.random_draw_sequence[i]][0].set_linewidth(1.0)
                self.plots[self.random_draw_sequence[i]][0].set_linestyle('solid')
                self.plots[self.random_draw_sequence[i]][0].set_xdata(self.trajectory[i, 0])
                self.plots[self.random_draw_sequence[i]][0].set_ydata(self.trajectory[i, 1])
                self.plots[self.random_draw_sequence[i]][0].set_color(colors[self.random_draw_sequence[i]])

            self.canvas.draw()

            self.areaPlots = []
            self.areaTrajectories = []
            self.selectedBatchColors = []
            self.selectedAreaColors = []
            self.selectedBatchColor = []
            self.selectedAreaColor = []
            self.colorBtns = []
            self.pickColor.idx = 0
            self.colorSetIdx = 0
            self.trainingOrder = 0

            self.selectedAreaPlot = None
            self.selectedBatchPlot = None
            self.treeWidget.clear()
            self.addTreeWidgetItems()

            self.leftTreeWidget.clear()
            self.refreshLeftTreeWidgetItems()

            self.unselectAreaMode()
            self.hideFlagMode()

    @pyqtSlot()
    def animateBtnClickedSlot(self):
        if (self.selectedPlot == True):
            self.treeWidget.setEnabled(False)
            self.leftTreeWidget.setEnabled(False)
            self.speedSpinBox.setEnabled(False)
            self.intervalSpinBox.setEnabled(False)
            self.animateBtn.setEnabled(False)

            self.isAnimated = True


            if (self.pickedLines is not None or
                    (not self.checkedArea and self.selectedBatchPlot is not None and len(self.selectedBatchPlot)==1)):
                if (type(self.pickedLines) == int):
                    self.start_line = self.pickedLines
                    self.end_line = self.pickedLines
                else:
                    self.start_line, self.end_line = self.get_start_end(self.selectedBatchPlot[0])

                self.animateData = np.array(self.trajectory)
                j = 0
                current_idx = self.start_line
                for i in range(len(self.plots)):
                    self.animateData[i, 0] = []
                    self.animateData[i, 1] = []
                    plot = self.plots[self.random_draw_sequence[i]][0]
                    if (i >= self.start_line and i <= self.end_line):

                        if ((current_idx - self.start_line) % self.intervalSpinBox.value()) == 0:
                            self.plots[self.random_draw_sequence[i]][0].set_visible(True)
                            current_idx = current_idx + self.intervalSpinBox.value()
                        else:
                            self.plots[self.random_draw_sequence[i]][0].set_visible(False)
                        j = j + 1
                    else:
                        self.plots[self.random_draw_sequence[i]][0].set_visible(False)

                    plot.set_xdata(self.animateData[i, 0])
                    plot.set_ydata(self.animateData[i, 1])

                self.idxForAnimate = self.start_line
                self.animateBatch()
            elif(self.checkedArea and self.selectedAreaPlot is not None and len(self.selectedAreaPlot)==1):
                self.animateData = np.array(self.areaTrajectories[self.selectedAreaPlot[0]])

                for i in range(len(self.plots)):
                    self.plots[self.random_draw_sequence[i]][0].set_visible(False)

                for i in range(len(self.areaPlots[self.selectedAreaPlot[0]])):
                    self.animateData[i, 0] = []
                    self.animateData[i, 1] = []
                    plot = self.areaPlots[self.selectedAreaPlot[0]][i][0]
                    plot.set_xdata(self.animateData[i, 0])
                    plot.set_ydata(self.animateData[i, 1])

                    self.areaPlots[self.selectedAreaPlot[0]][i][0].set_visible(True)

                self.idxForAnimateArea = 0
                self.animateArea()

    def keyPressEvent(self, e):
        print(e.key())
        if e.key() == QtCore.Qt.Key_Control:
            self.ctrlKey = True
            print("ctrlKeyPressEvent")

        if e.key() == QtCore.Qt.Key_Delete:
            print("deleteKeyPressEvent")

            if (self.rightTreeItem is not None and 'Color' in self.rightTreeItem.text(0)):
                color_idx = int(self.rightTreeItem.text(0)[6:]) - 1
                if (self.checkedArea and len(self.selectedAreaColor) > 1):
                    del self.selectedAreaColor[color_idx]
                    for i in range(len(self.areaPlots[self.selectedAreaPlot[0]])):
                        plt = self.areaPlots[self.selectedAreaPlot[0]][i][0]
                        color = random.choice(self.selectedAreaColor)
                        plt.set_color(color)
                elif (not self.checkedArea and len(self.selectedBatchColor) > 1):
                    del self.selectedBatchColor[color_idx]

                    start_line, end_line = self.get_start_end(self.selectedBatchPlot[0])
                    i = start_line
                    while i <= end_line:
                        plt = self.plots[self.random_draw_sequence[i]][0]
                        color = random.choice(self.selectedBatchColor)
                        plt.set_color(color)
                        i += 1

                self.rightTreeItem = None

                self.canvas.draw()
                self.treeWidget.clear()
                self.addTreeWidgetItems()
        e.accept()

    def keyReleaseEvent(self, e):
        print(e.key())
        if e.key() == QtCore.Qt.Key_Control:
            self.ctrlKey = False
            print("ctrlKeyReleaseEvent")
        e.accept()

    def onPick(self, event):
        if (self.isAnimated == True):
            return

        plot = event.artist
        idx = int(plot.get_label().replace("_line", ""))

        plt = self.plots[self.random_draw_sequence[idx]][0]
        if (plt.get_visible() == False):
            return

        if (self.ctrlKey == True):
            if (self.pickedLines is not None):
                if (type(self.pickedLines) == int):
                    temp_line = self.pickedLines
                    self.pickedLines = [temp_line]
                elif(type(self.pickedLines) == list):
                    pass
                else: #numpy array
                    self.pickedLines = []
            else:
                self.pickedLines = []

            self.pickedLines.append(idx)
            plt.set_linestyle((0, (5, 1)))
        else:
            if (self.pickedLines is not None):
                if (type(self.pickedLines) == int):
                    plt_old = self.plots[self.random_draw_sequence[self.pickedLines]][0]
                    plt_old.set_linestyle('solid')
                elif(type(self.pickedLines) == list):
                    for i in self.pickedLines:
                        plt_old = self.plots[self.random_draw_sequence[i]][0]
                        plt_old.set_linestyle('solid')
                    self.pickedLines = []
                else: #numpy array
                    pass
            else:
                self.pickedLines = []

            self.pickedLines = idx
            plt.set_linestyle((0, (5, 1)))

        self.canvas.draw()
        self.treeWidget.clear()
        self.addTreeWidgetItems()

    def refreshLeftTreeWidgetItems(self):
        if (self.selectedPlot == False):
            return

        self.leftTreeWidget.clear()
        if (self.checkedArea == True):
            if(len(self.areaPlots) > 0):
                items = []
                for i in range(len(self.areaPlots)):
                    # Line number
                    item = QtGui.QTreeWidgetItem(self.leftTreeWidget)
                    item.setText(0, "Area " + str(i+1))
                    items.append(item)
                self.leftTreeWidget.addTopLevelItems(items)
        else:
            if (self.trainingOrder == 0):
                N = len(self.plots)
                numOfBatch = self.batchSpinBox.value()
                batchSize = int(np.ceil(N / numOfBatch))

                self.selectedBatchColors = []
                for i in range(numOfBatch + 1):
                    self.selectedBatchColors.append([])
                self.selectedBatchColor = self.selectedBatchColors[0]

                item = QtGui.QTreeWidgetItem(self.leftTreeWidget)
                item.setText(0, "All lines")
                self.leftTreeWidget.setItemWidget(item, 1, QtGui.QLabel(""))

                for idx in range(numOfBatch):
                    if (idx == 0):
                        start_line = idx * batchSize
                    else:
                        start_line = idx * batchSize + 1

                    if (idx == numOfBatch - 1):
                        end_line = N - 1
                    else:
                        end_line = (idx + 1) * batchSize

                    item = QtGui.QTreeWidgetItem(self.leftTreeWidget)
                    item.setText(0, "Line ")
                    self.leftTreeWidget.setItemWidget(item, 1,
                                                      QtGui.QLabel(str(start_line) + " ~ " + str(end_line)))
            elif (self.trainingOrder == 1):
                numOfBatch = self.batchSpinBox.value() ** 2

                self.selectedBatchColors = []
                for i in range(numOfBatch):
                    self.selectedBatchColors.append([])
                self.selectedBatchColor = self.selectedBatchColors[0]

                for idx in range(numOfBatch):
                    item = QtGui.QTreeWidgetItem(self.leftTreeWidget)
                    item.setText(0, "Area ")
                    self.leftTreeWidget.setItemWidget(item, 1,
                                                      QtGui.QLabel(str(idx + 1)))

            if (self.selectedBatchPlot is None):
                self.selectedBatchPlot = [0]

            # self.leftTreeWidget.setItemSelected(self.leftTreeWidget.topLevelItem(self.selectedBatchPlot), True)

    def updateSelectedBatchPlots(self):
        if (self.selectedBatchPlot is None):
            return

        if (self.checkedArea == True):
            return

        if (self.trainingOrder == 0):
            if (len(self.selectedBatchPlot) == 1):
                self.selectedBatchColor = self.selectedBatchColors[self.selectedBatchPlot[0]]
            else:
                self.selectedBatchColor = None

            if (self.pickedLines is not None):
                if (type(self.pickedLines) == int):
                    plt = self.plots[self.random_draw_sequence[self.pickedLines]][0]
                    plt.set_linestyle('solid')
                    self.treeWidget.clear()
                elif(type(self.pickedLines) == list):
                    for idx in self.pickedLines:
                        plt = self.plots[self.random_draw_sequence[idx]][0]
                        plt.set_linestyle('solid')
                        self.treeWidget.clear()
                self.pickedLines = None

            numOfBatch = self.batchSpinBox.value()
            for batch_idx in range(numOfBatch+1):
                start_line, end_line = self.get_start_end(batch_idx)
                if (batch_idx in self.selectedBatchPlot):
                    i = start_line
                    while i <= end_line:
                        if (self.deletedLines[i] == False):
                            self.plots[self.random_draw_sequence[i]][0].set_visible(True)
                        i += 1
                    if (batch_idx == 0):
                        break
                else:
                    i = start_line
                    while i <= end_line:
                        if (self.deletedLines[i] == False):
                            self.plots[self.random_draw_sequence[i]][0].set_visible(False)
                        i += 1

        elif(self.trainingOrder == 1):
            pass
            # numOfBatch = self.batchSpinBox.value()
            # if (self.selectedAreaPlot == 0):
            #     x_idx = 0
            #     y_idx = 0
            # else:
            #     x_idx = self.selectedAreaPlot//numOfBatch
            #     y_idx = self.selectedAreaPlot%numOfBatch
            #
            # x1 = self.xmin + x_idx * (self.xmax - self.xmin) / numOfBatch
            # x2 = self.xmin + (x_idx+1) * (self.xmax - self.xmin) / numOfBatch
            # y1 = self.ymin + y_idx * (self.ymax - self.ymin) / numOfBatch
            # y2 = self.ymin + (y_idx + 1) * (self.ymax - self.ymin) / numOfBatch
            #
            # self.selectedBatchColor = self.selectedBatchColors[self.selectedAreaPlot]
            #
            # if (self.pickedLines is not None):
            #     if (type(self.pickedLines) == int):
            #         plt = self.plots[self.random_draw_sequence[self.pickedLines]][0]
            #         plt.set_linestyle('solid')
            #         self.treeWidget.clear()
            #     elif(type(self.pickedLines) == list):
            #         for idx in self.pickedLines:
            #             plt = self.plots[self.random_draw_sequence[idx]][0]
            #             plt.set_linestyle('solid')
            #             self.treeWidget.clear()
            #     self.pickedLines = None
            #
            # self.selectedBatchPlot = [self.selectedAreaPlot]
            #
            # for i in range(len(self.plots)):
            #     x = self.trajectory[i, 0][0]
            #     y = self.trajectory[i, 1][0]
            #     if (x > x1 and x < x2 and y > y1 and y < y2 and self.deletedLines[i] == False):
            #         self.plots[self.random_draw_sequence[i]][0].set_visible(True)
            #     else:
            #         self.plots[self.random_draw_sequence[i]][0].set_visible(False)

        self.canvas.draw()
        self.treeWidget.clear()
        self.addTreeWidgetItems()
        self.setFocus(Qt.ActiveWindowFocusReason)

    def updateSelectedAreaPlots(self):
        if (self.selectedAreaPlot is not None and len(self.selectedAreaPlot) == 1):
            self.selectedAreaColor = self.selectedAreaColors[self.selectedAreaPlot[0]]
        else:
            self.selectedAreaColor = None

        for i in range(len(self.areaPlots)):
            for j in range(len(self.areaPlots[i])):
                plt = self.areaPlots[i][j][0]

                if (i in self.selectedAreaPlot):
                    plt.set_linestyle((0, (5, 1)))
                else:
                    plt.set_linestyle('solid')

        self.canvas.draw()
        self.treeWidget.clear()
        self.addTreeWidgetItems()
        self.setFocus(Qt.ActiveWindowFocusReason)

    def leftHandleSelection(self, selected, deselected):
        if (self.checkedArea == True):
            self.selectedAreaPlot = []
            selectedItems = self.leftTreeWidget.selectedItems()
            for item in selectedItems:
                index = self.leftTreeWidget.indexFromItem(item)
                self.selectedAreaPlot.append(int(index.row()))
                print('SEL: row: %s, col: %s, text: %s' % (
                    index.row(), index.column(), item.text(0)))

            self.updateSelectedAreaPlots()
        else:
            self.selectedBatchPlot = []
            selectedItems = self.leftTreeWidget.selectedItems()
            for item in selectedItems:
                index = self.leftTreeWidget.indexFromItem(item)
                self.selectedBatchPlot.append(int(index.row()))
                print('SEL: row: %s, col: %s, text: %s' % (
                    index.row(), index.column(), item.text(0)))

            self.updateSelectedBatchPlots()

    def rightHandleSelection(self, selected, deselected):
        for index in selected.indexes():
            self.rightTreeItem = self.treeWidget.itemFromIndex(index)
            print(self.rightTreeItem.text(0))

    def addTreeWidgetItems(self):
        if (self.selectedPlot == True):
            if (self.checkedArea == True and
                        self.selectedAreaPlot is not None and
                        len(self.selectedAreaPlot)==1):
                # Thickness
                item = QtGui.QTreeWidgetItem(self.treeWidget)
                item.setText(0, "Thickness")
                self.lineSpinBox = QtGui.QDoubleSpinBox()
                self.lineSpinBox.setValue(1.0)
                QObject.connect(self.lineSpinBox, SIGNAL("valueChanged(double)"), self,
                                SLOT("valueChanged(double)"))
                self.treeWidget.setItemWidget(item, 1, self.lineSpinBox)

                # Alpha
                item = QtGui.QTreeWidgetItem(self.treeWidget)
                item.setText(0, "Alpha")
                self.alphaSpinBox = QtGui.QDoubleSpinBox()
                self.alphaSpinBox.setMaximum(1.0)
                self.alphaSpinBox.setMinimum(0.1)
                self.alphaSpinBox.setValue(1.0)
                QObject.connect(self.alphaSpinBox, SIGNAL("valueChanged(double)"), self,
                                SLOT("valueAlphaChanged(double)"))
                self.treeWidget.setItemWidget(item, 1, self.alphaSpinBox)

                # Color
                if (self.colorSetIdx == 0):
                    # Color
                    item = QtGui.QTreeWidgetItem(self.treeWidget)
                    item.setText(0, "Rainbow")
                    self.treeWidget.setItemWidget(item, 1, None)
                elif (self.colorSetIdx == 1):
                    # Color
                    item = QtGui.QTreeWidgetItem(self.treeWidget)
                    item.setText(0, "Begin")
                    beginBtn = QtGui.QPushButton()
                    beginBtn.setStyleSheet("QWidget { background-color: %s}" % rgb2hex(self.matplotlib_color1))
                    self.treeWidget.setItemWidget(item, 1, beginBtn)

                    item = QtGui.QTreeWidgetItem(self.treeWidget)
                    item.setText(0, "End")
                    endBtn = QtGui.QPushButton()
                    endBtn.setStyleSheet("QWidget { background-color: %s}" % rgb2hex(self.matplotlib_color2))
                    self.treeWidget.setItemWidget(item, 1, endBtn)
                else:
                    counter = 0
                    for color in self.selectedAreaColor:
                        # Color
                        item = QtGui.QTreeWidgetItem(self.treeWidget)
                        item.setText(0, "Color " + str(counter + 1))

                        coBtn = QtGui.QPushButton(str(counter + 1), self)
                        coBtn.color_idx = counter
                        coBtn.setStyleSheet("QWidget { background-color: %s}" % rgb2hex(color))
                        coBtn.connect(coBtn, SIGNAL("clicked()"), self, SLOT("pickColorSlot()"))
                        self.treeWidget.setItemWidget(item, 1, coBtn)

                        counter += 1
            elif (type(self.pickedLines) == int):
                plt = self.plots[self.random_draw_sequence[self.pickedLines]][0]

                # Line number
                item = QtGui.QTreeWidgetItem(self.treeWidget)
                item.setText(0, "Line")

                self.lineNumber = QtGui.QLabel(str(self.pickedLines))
                self.treeWidget.setItemWidget(item, 1, self.lineNumber)

                # isHidden
                item = QtGui.QTreeWidgetItem(self.treeWidget)
                item.setText(0, "isHidden")
                self.lineCheckBox = QtGui.QCheckBox()
                self.lineCheckBox.setCheckState(QtCore.Qt.Unchecked)
                QtCore.QObject.connect(self.lineCheckBox, SIGNAL("stateChanged(int)"), self, SLOT("checkedSlot(int)"))
                self.treeWidget.setItemWidget(item, 1, self.lineCheckBox)

                # Thickness
                item = QtGui.QTreeWidgetItem(self.treeWidget)
                item.setText(0, "Thickness")
                self.lineSpinBox = QtGui.QDoubleSpinBox()
                self.lineSpinBox.setValue(plt.get_linewidth())
                self.lineSpinBox.setMaximum(200)
                QObject.connect(self.lineSpinBox, SIGNAL("valueChanged(double)"), self, SLOT("valueChanged(double)"))
                self.treeWidget.setItemWidget(item, 1, self.lineSpinBox)

                # Alpha
                item = QtGui.QTreeWidgetItem(self.treeWidget)
                item.setText(0, "Alpha")
                self.alphaSpinBox = QtGui.QDoubleSpinBox()
                self.alphaSpinBox.setMaximum(1.0)
                self.alphaSpinBox.setMinimum(0.1)
                self.alphaSpinBox.setValue(self.alphaValue)
                QObject.connect(self.alphaSpinBox, SIGNAL("valueChanged(double)"), self,
                                SLOT("valueAlphaChanged(double)"))
                self.treeWidget.setItemWidget(item, 1, self.alphaSpinBox)

                # Color
                item = QtGui.QTreeWidgetItem(self.treeWidget)
                item.setText(0, "Color")
                self.colorBtn = QtGui.QPushButton()
                color = rgb2hex(plt.get_color())

                self.colorBtn.setStyleSheet("QWidget { background-color: %s}" % color)
                self.colorBtn.connect(self.colorBtn, SIGNAL("clicked()"), self, SLOT("pickColorSlot()"))
                self.treeWidget.setItemWidget(item, 1, self.colorBtn)
            elif (type(self.pickedLines) == list):
                plt = self.plots[self.random_draw_sequence[self.pickedLines[0]]][0]

                # Thickness
                item = QtGui.QTreeWidgetItem(self.treeWidget)
                item.setText(0, "Thickness")
                self.lineSpinBox = QtGui.QDoubleSpinBox()
                self.lineSpinBox.setValue(plt.get_linewidth())
                self.lineSpinBox.setMaximum(200)
                QObject.connect(self.lineSpinBox, SIGNAL("valueChanged(double)"), self, SLOT("valueChanged(double)"))
                self.treeWidget.setItemWidget(item, 1, self.lineSpinBox)

                # Alpha
                item = QtGui.QTreeWidgetItem(self.treeWidget)
                item.setText(0, "Alpha")
                self.alphaSpinBox = QtGui.QDoubleSpinBox()
                self.alphaSpinBox.setMaximum(1.0)
                self.alphaSpinBox.setMinimum(0.1)
                self.alphaSpinBox.setValue(self.alphaValue)
                QObject.connect(self.alphaSpinBox, SIGNAL("valueChanged(double)"), self,
                                SLOT("valueAlphaChanged(double)"))
                self.treeWidget.setItemWidget(item, 1, self.alphaSpinBox)

                # Color
                item = QtGui.QTreeWidgetItem(self.treeWidget)
                item.setText(0, "Color")
                self.colorBtn = QtGui.QPushButton()
                self.colorBtn.connect(self.colorBtn, SIGNAL("clicked()"), self, SLOT("pickColorSlot()"))
                self.treeWidget.setItemWidget(item, 1, self.colorBtn)

            elif(self.checkedArea == False and
                         self.selectedBatchPlot is not None and
                         len(self.selectedBatchPlot)==1):
                start_line, end_line = self.get_start_end(self.selectedBatchPlot[0])

                # Line number
                item = QtGui.QTreeWidgetItem(self.treeWidget)
                item.setText(0, "Line")

                self.lineNumber = QtGui.QLabel(str(start_line) + "~" + str(end_line))
                self.treeWidget.setItemWidget(item, 1, self.lineNumber)

                # Thickness
                item = QtGui.QTreeWidgetItem(self.treeWidget)
                item.setText(0, "Thickness")
                self.lineSpinBox = QtGui.QDoubleSpinBox()
                plt = self.plots[self.random_draw_sequence[start_line]][0]
                self.lineSpinBox.setValue(plt.get_linewidth())
                self.lineSpinBox.setMaximum(200)
                QObject.connect(self.lineSpinBox, SIGNAL("valueChanged(double)"), self,
                                SLOT("valueChanged(double)"))
                self.treeWidget.setItemWidget(item, 1, self.lineSpinBox)

                # Alpha
                item = QtGui.QTreeWidgetItem(self.treeWidget)
                item.setText(0, "Alpha")
                self.alphaSpinBox = QtGui.QDoubleSpinBox()
                self.alphaSpinBox.setMaximum(1.0)
                self.alphaSpinBox.setMinimum(0.1)
                self.alphaSpinBox.setValue(self.alphaValue)
                QObject.connect(self.alphaSpinBox, SIGNAL("valueChanged(double)"), self,
                                SLOT("valueAlphaChanged(double)"))
                self.treeWidget.setItemWidget(item, 1, self.alphaSpinBox)

                # Color
                if (self.colorSetIdx == 0):
                    # Color
                    item = QtGui.QTreeWidgetItem(self.treeWidget)
                    item.setText(0, "Rainbow")
                    self.treeWidget.setItemWidget(item, 1, None)
                elif (self.colorSetIdx == 1):
                    # Color
                    item = QtGui.QTreeWidgetItem(self.treeWidget)
                    item.setText(0, "Begin")
                    beginBtn = QtGui.QPushButton()
                    beginBtn.setStyleSheet("QWidget { background-color: %s}" % rgb2hex(self.matplotlib_color1))
                    self.treeWidget.setItemWidget(item, 1, beginBtn)

                    item = QtGui.QTreeWidgetItem(self.treeWidget)
                    item.setText(0, "End")
                    endBtn = QtGui.QPushButton()
                    endBtn.setStyleSheet("QWidget { background-color: %s}" % rgb2hex(self.matplotlib_color2))
                    self.treeWidget.setItemWidget(item, 1, endBtn)
                else:
                    counter = 0
                    for color in self.selectedBatchColor:
                        # Color
                        item = QtGui.QTreeWidgetItem(self.treeWidget)
                        item.setText(0, "Color " + str(counter + 1))

                        coBtn = QtGui.QPushButton(str(counter+1), self)
                        coBtn.color_idx = counter
                        coBtn.setStyleSheet("QWidget { background-color: %s}" % rgb2hex(color))
                        coBtn.connect(coBtn, SIGNAL("clicked()"), self, SLOT("pickColorSlot()"))
                        self.treeWidget.setItemWidget(item, 1, coBtn)

                        counter += 1

            recentColorTree = QtGui.QTreeWidgetItem(self.treeWidget, ["Recents"])
            counter = 0
            for color in self.recentColors:
                colorItem = QtGui.QTreeWidgetItem(recentColorTree)

                coBtn = QtGui.QPushButton("", self)
                coBtn.color_idx = counter
                counter+=1
                coBtn.setStyleSheet("QWidget { background-color: %s}" % rgb2hex(color))
                coBtn.connect(coBtn, SIGNAL("clicked()"), self, SLOT("recentColorSlot()"))
                self.treeWidget.setItemWidget(colorItem, 0, coBtn)

    @pyqtSlot()
    def recentColorSlot(self):
        color_idx = self.sender().color_idx
        color = self.recentColors[color_idx]

        if (self.checkedArea and
                    self.selectedAreaPlot is not None and
                    len(self.selectedAreaPlot)==1):
            self.selectedAreaColor.append(color)

            for i in range(len(self.areaPlots[self.selectedAreaPlot[0]])):
                plt = self.areaPlots[self.selectedAreaPlot[0]][i][0]
                color = random.choice(self.selectedAreaColor)
                plt.set_color(color)
        elif (type(self.pickedLines) == int):
            # self.colorBtn.setStyleSheet("QWidget { background-color: %s}" % color.name())
            plt = self.plots[self.random_draw_sequence[self.pickedLines]][0]
            plt.set_color(color)
        elif (type(self.pickedLines) == list):
            # self.colorBtn.setStyleSheet("QWidget { background-color: %s}" % color.name())
            for idx in self.pickedLines:
                plt = self.plots[self.random_draw_sequence[idx]][0]
                plt.set_color(color)
        elif (not self.checkedArea and
                      self.selectedBatchPlot is not None and
                      len(self.selectedBatchPlot)==1):
            if (self.trainingOrder == 0):
                self.selectedBatchColor.append(color)

                start_line, end_line = self.get_start_end(self.selectedBatchPlot[0])
                i = start_line
                while (i <= end_line):
                    plt = self.plots[self.random_draw_sequence[i]][0]
                    color = random.choice(self.selectedBatchColor)
                    plt.set_color(color)
                    i+=1

            elif (self.trainingOrder == 1):
                pass

        self.canvas.draw()
        self.treeWidget.clear()
        self.addTreeWidgetItems()

    @pyqtSlot()
    def pickColorSlot(self):
        if (self.selectedPlot == True):
            self.colorSetIdx = 2
            self.treeWidget.clear()
            self.addTreeWidgetItems()

            color = QtGui.QColorDialog.getColor()
            matplotlib_color = str(color.name()).lstrip('#')
            matplotlib_color = [int(matplotlib_color[i:i + 2], 16) for i in (0, 2, 4)]
            matplotlib_color.append(255.0)
            matplotlib_color = np.array(matplotlib_color) / 255.0
            self.recentColors.append(matplotlib_color)

            if (self.checkedArea and self.selectedAreaPlot is not None and len(self.selectedAreaPlot)==1):
                if hasattr(self.sender(), 'color_idx'):
                    self.selectedAreaColor[self.sender().color_idx] = matplotlib_color
                else:
                    self.selectedAreaColor.append(matplotlib_color)

                for i in range(len(self.areaPlots[self.selectedAreaPlot[0]])):
                    plt = self.areaPlots[self.selectedAreaPlot[0]][i][0]
                    color = random.choice(self.selectedAreaColor)
                    plt.set_color(color)
            elif (type(self.pickedLines) == int):
                self.colorBtn.setStyleSheet("QWidget { background-color: %s}" % color.name())
                plt = self.plots[self.random_draw_sequence[self.pickedLines]][0]
                plt.set_color(matplotlib_color)
            elif(type(self.pickedLines) == list):
                self.colorBtn.setStyleSheet("QWidget { background-color: %s}" % color.name())
                for idx in self.pickedLines:
                    plt = self.plots[self.random_draw_sequence[idx]][0]
                    plt.set_color(matplotlib_color)
            elif (not self.checkedArea and self.selectedBatchPlot is not None and len(self.selectedBatchPlot) == 1):
                if (self.trainingOrder == 0):
                    if hasattr(self.sender(), 'color_idx'):
                        self.selectedBatchColor[self.sender().color_idx] = matplotlib_color
                    else:
                        self.selectedBatchColor.append(matplotlib_color)

                    start_line, end_line = self.get_start_end(self.selectedBatchPlot[0])
                    i = start_line
                    while (i <= end_line):
                        plt = self.plots[self.random_draw_sequence[i]][0]
                        color = random.choice(self.selectedBatchColor)
                        plt.set_color(color)
                        i+=1

                elif(self.trainingOrder == 1):
                    numOfBatch = self.batchSpinBox.value()
                    idx = self.selectedBatchPlot[0]
                    if (idx == 0):
                        x_idx = 0
                        y_idx = 0
                    else:
                        x_idx = idx // numOfBatch
                        y_idx = idx % numOfBatch

                    x1 = self.xmin + x_idx * (self.xmax - self.xmin) / numOfBatch
                    x2 = self.xmin + (x_idx + 1) * (self.xmax - self.xmin) / numOfBatch
                    y1 = self.ymin + y_idx * (self.ymax - self.ymin) / numOfBatch
                    y2 = self.ymin + (y_idx + 1) * (self.ymax - self.ymin) / numOfBatch

                    for i in range(len(self.plots)):
                        x = self.trajectory[i, 0][0]
                        y = self.trajectory[i, 1][0]
                        if (x > x1 and x < x2 and y > y1 and y < y2):
                            plt = self.plots[self.random_draw_sequence[i]][0]
                            color = random.choice(self.selectedBatchColor)
                            plt.set_color(color)

            self.canvas.draw()
            self.treeWidget.clear()
            self.addTreeWidgetItems()

    @pyqtSlot()
    def pickBackgroundColorSlot(self):
        if (self.plots is None):
            return

        color = QtGui.QColorDialog.getColor()

        self.pickedBackgroundColor = str(color.name())
        self.updateBackgroundColor()

    @pyqtSlot('int')
    def batchChanged(self, value):
        if (self.selectedPlot == False):
            return

        self.selectedBatchPlot = None
        self.leftTreeWidget.clear()
        self.refreshLeftTreeWidgetItems()

    @pyqtSlot('double')
    def valueChanged(self, value):
        if (self.selectedPlot == True):
            if (self.checkedArea and self.selectedAreaPlot is not None and len(self.selectedAreaPlot)==1):
                for i in range(len(self.areaPlots[self.selectedAreaPlot[0]])):
                    plt = self.areaPlots[self.selectedAreaPlot[0]][i][0]
                    plt.set_linewidth(value)
            elif (type(self.pickedLines) == int):
                plt = self.plots[self.random_draw_sequence[self.pickedLines]][0]
                plt.set_linewidth(value)
            elif(type(self.pickedLines) == list):
                for idx in self.pickedLines:
                    plt = self.plots[self.random_draw_sequence[idx]][0]
                    plt.set_linewidth(value)
            elif (not self.checkedArea and self.selectedBatchPlot is not None):
                start_line, end_line = self.get_start_end(self.selectedBatchPlot[0])
                i = start_line
                while (i <= end_line):
                    plt = self.plots[self.random_draw_sequence[i]][0]
                    plt.set_linewidth(value)
                    i+=1

            self.canvas.draw()

    @pyqtSlot('double')
    def valueAlphaChanged(self, value):
        if (self.selectedPlot == True):
            if (type(self.pickedLines) == int):
                plt = self.plots[self.random_draw_sequence[self.pickedLines]][0]
                color = plt.get_color()
                color[3] = value
                plt.set_color(color)
            elif(type(self.pickedLines) == list):
                for idx in self.pickedLines:
                    plt = self.plots[self.random_draw_sequence[idx]][0]
                    color = plt.get_color()
                    color[3] = value
                    plt.set_color(color)
            elif (not self.checkedArea and self.selectedBatchPlot is not None):
                start_line, end_line = self.get_start_end(self.selectedBatchPlot[0])
                i = start_line
                while (i <= end_line):
                    plt = self.plots[self.random_draw_sequence[i]][0]
                    color = plt.get_color()
                    color[3] = value
                    plt.set_color(color)
                    i+=1
            elif (self.checkedArea and self.selectedAreaPlot is not None and len(self.selectedAreaPlot)==1):
                for i in range(len(self.areaPlots[self.selectedAreaPlot[0]])):
                    plt = self.areaPlots[self.selectedAreaPlot[0]][i][0]
                    color = plt.get_color()
                    color[3] = value
                    plt.set_color(color)

            self.canvas.draw()

    @pyqtSlot(int)
    def checkedSlot(self, state):
        if (self.selectedPlot == True and self.pickedLines is not None):
            plt = self.plots[self.random_draw_sequence[self.pickedLines]][0]
            if state == QtCore.Qt.Checked:
                print ("checked")
                plt.set_visible(False)

            if state == QtCore.Qt.Unchecked:
                print ("unchecked")
                plt.set_visible(True)

            self.canvas.draw()

    def rmmpl(self, ):
        self.mplvl.removeWidget(self.canvas)
        self.canvas.close()
        self.mplvl.removeWidget(self.plot_toolbar)
        self.plot_toolbar.close()
        self.mplvl.removeWidget(self.custom_toolbar)
        self.custom_toolbar.close()

        self.treeWidget.clear()
        self.selectedPlot = False
        self.selectedBatchPlot = None
        self.pickedLines = None

    def save_plot_data(self, filename, data):
        data = np.save(filename, data)
        return data

    def restore_plot_data(self, filename):
        data = np.load(filename, encoding='latin1')
        return data

class AddTitleDialog(QDialog):
    def __init__(self, parent=None):
        super(AddTitleDialog, self).__init__(parent)

        layout = QVBoxLayout(self)
        self.title = QLineEdit(self)
        layout.addWidget(self.title)

        # OK and Cancel buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def getTile(self):
        return self.title.text()

    @staticmethod
    def getTitle(parent=None):
        dialog = AddTitleDialog(parent)
        dialog.exec_()
        return dialog.getTile()

class ChooseRatioDialog(QDialog):
    def __init__(self, parent=None):
        super(ChooseRatioDialog, self).__init__(parent)

        layout = QVBoxLayout(self)

        self.comboBox = QComboBox()
        self.comboBox.addItem("4:3")
        self.comboBox.addItem("3:4")
        self.comboBox.addItem("3:2")
        self.comboBox.addItem("2:3")
        self.comboBox.addItem("16:9")
        self.comboBox.addItem("9:16")
        self.comboBox.addItem("1:1")
        self.comboBox.setCurrentIndex(0)
        # self.comboBox.connect(self.comboBox,
        #                       SIGNAL("currentIndexChanged(int)"),
        #                       self, SLOT("ratioIndexChange(int)"))
        layout.addWidget(self.comboBox)

        # OK and Cancel buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # @pyqtSlot(int)
    # def ratioIndexChange(self, idx):
    #     pass

    def getRatioIdx(self):
        return self.comboBox.currentIndex()

    @staticmethod
    def getIdx(parent=None):
        dialog = ChooseRatioDialog(parent)
        dialog.exec_()
        return dialog.getRatioIdx()

if __name__ == '__main__':
    import sys
    from PyQt4 import QtGui
    import numpy as np

    app = QtGui.QApplication(sys.argv)
    main = Main()

    main.show()
    sys.exit(app.exec_())