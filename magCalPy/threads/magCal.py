#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""

.. moduleauthor:: Michal Ciesielski <ciesielskimm@gmail.com>


"""
from __future__ import division
import Queue
from threading import Thread
import os
import logging
import argparse
import signal
from serialcom import SerialCom
import time
import sys
import math
import random

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import numpy as np


# #########################################################################
# VARS
# #########################################################################
data = list()

vertIndex = 0
numberOfSamples = 100000
sphereRadius = 5
updating = True

# #########################################################################
# FUNCTIONS
# #########################################################################


def update():
    # UPDATE SETTINGS
    global data
    global pos3
    global vertIndex

    while 1:
        if not updating:
            break

        if vertIndex < numberOfSamples:

            # normalize
            vectorLength = math.sqrt(data[0] * data[0] +
                                     data[1] * data[1] +
                                     data[2] * data[2])
            data[0] /= vectorLength
            data[1] /= vectorLength
            data[2] /= vectorLength

            # rescale
            data[0] *= sphereRadius
            data[1] *= sphereRadius
            data[2] *= sphereRadius

            pos3[vertIndex][0] = data[0]
            pos3[vertIndex][1] = data[1]
            pos3[vertIndex][2] = data[2]

            color[vertIndex][0] = data[0] / 100
            color[vertIndex][1] = data[1] / 100
            color[vertIndex][2] = data[2] / 100

            sp3.setData(pos=pos3, color=color)
            vertIndex += 1
            print(data)
        else:
            break


def run_once(f):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return f(*args, **kwargs)
    wrapper.has_run = False
    return wrapper

# #########################################################################
# PYQT
# #########################################################################


app = QtGui.QApplication([])
w = gl.GLViewWidget()
w.opts['distance'] = 20
# w.setBackgroundColor('w')
w.show()
w.setWindowTitle('MagCalibration')

g = gl.GLGridItem()
w.addItem(g)

# pos3 = np.zeros((100, 100, 3)) # 100 arrays of 100 arrays of 3 elements
# pos3[:, :, :2] = np.mgrid[:100, :100].transpose(1, 2, 0) * [-0.1, 0.1]
# pos3 = pos3.reshape(10000, 3)
# position needs to be an array of arrays of 3 elements so this should work:
pos3 = np.zeros((numberOfSamples, 3))
# color is built similarly but for every element RGBA needs to be defined
color = np.ones((numberOfSamples, 4))

sp3 = gl.GLScatterPlotItem(pos=pos3,
                           color=(1, 1, 1, .7),
                           size=0.1,
                           pxMode=False)

w.addItem(sp3)

# this needs to be here - after all this pyqt shit above
# maybe not timer but thread so its faster
# t = QtCore.QTimer()
# t.timeout.connect(update)
t = Thread(target=update)
t.daemon = True
t.start()


# #########################################################################
# RUN
# #########################################################################
if __name__ == '__main__':
    try:
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()
        t.join()
        sys.exit()
    except:
        t.join()
        sys.exit()
