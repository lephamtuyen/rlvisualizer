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
import math
import random
import pickle
import matplotlib.pyplot as plt


f = open("/home/tuyen/Desktop/preset_2", 'rb')
# data = pickle.load(f)
data = pickle.load(f, encoding='latin1')
f.close()

data[0] = '#FBEFC2'

f = open("/home/tuyen/Desktop/preset_3", 'wb')
pickle.dump(data, f)
f.close()