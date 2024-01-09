#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 31 17:15:07 2018

@author: antony
"""
import math
import os

import matplotlib
import numpy as np

ALPHA = 0.8
MARKER_SIZE = 10
BLACK_RGB = (0, 0, 0)

TRANS_GRAY = (0.5, 0.5, 0.5, 0.5)

DEFAULT_WIDTH = 8
DEFAULT_HEIGHT = 8

NORM_3 = matplotlib.colors.Normalize(vmin=-3, vmax=3, clip=True)
NORM_2_5 = matplotlib.colors.Normalize(vmin=-2.5, vmax=2.5, clip=True)

NORM_STD_1 = matplotlib.colors.Normalize(vmin=0, vmax=1, clip=True)

# #0066cf
BWR_MATCALC_CMAP = matplotlib.colors.LinearSegmentedColormap.from_list('bwr', ['#0044aa', '#ffffff', '#ff0000'])
BWR_CMAP = matplotlib.colors.LinearSegmentedColormap.from_list('bwr', ['#0066cf', '#ffffff', '#ff0000'])
BWR2_CMAP = matplotlib.colors.LinearSegmentedColormap.from_list('bwr', ['#002266', '#ffffff', '#ff0000'], N=255)
REDS_CMAP = matplotlib.colors.LinearSegmentedColormap.from_list('reds', ['#ffd5d5', '#ff0000'], N=255)
BLUES_CMAP = matplotlib.colors.LinearSegmentedColormap.from_list('blues', ['#e6f0ff', '#003d99'], N=255)