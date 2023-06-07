# -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 17:40:38 2019

@author: antony
"""

#import matplotlib
# matplotlib.use('agg')
#import matplotlib.pyplot as plt
#import numpy as np
#import pandas as pd

from typing import Any, Mapping, Optional
import matplotlib
import pandas as pd
import numpy as np
import os
from PIL import Image
from svgwrite import cm, mm
import sys
from PIL import ImageFont
import re
import tkinter as Tkinter
import tkinter.font as tkFont
sys.path.append(
    "/ifs/scratch/cancer/Lab_RDF/abh2138/scRNA/data/samples/human/10X/rdf/restricted_grch38/manuscript/")

L1 = 's'
L2 = '^'
L3 = 'v'

DEFAULT_FONT_FAMILY = 'Arial'
DEFAULT_FONT_SIZE = 10
DEFAULT_FONT_WEIGHT = 'normal'

HEADING_FONT_SIZE = 14

FIGURE_FONT_SIZE = 8

HEATMAP_HEADING_FONT_SIZE = 9


BULLET_SIZE = 25

LABEL_HEIGHT = 30

BORDER_TOP = 50
BORDER_LEFT = 50

SEP_CLUST_LABEL_HEIGHT = 20
SEP_CLUST_OFFSET = 20

DEFAULT_IMAGE_SIZE = 300

STROKE_SIZE = 2 #2


COLORBAR_DIR = '/Users/Antony/OneDrive/Documents/work/shared/cumc/katia/manuscript/components/colorbar'
UMAP_DIR = '/ifs/scratch/cancer/Lab_RDF/abh2138/scRNA/data/samples/human/10X/rdf/restricted_grch38/manuscript/components/umap'
MONOCLE_DIR = '/ifs/scratch/cancer/Lab_RDF/abh2138/scRNA/data/samples/human/10X/rdf/restricted_grch38/manuscript/components/monocle'
IF_DIR = '/ifs/scratch/cancer/Lab_RDF/abh2138/scRNA/data/samples/human/10X/rdf/restricted_grch38/manuscript/components/if'
IF_PAIRS_DIR = '/ifs/scratch/cancer/Lab_RDF/abh2138/scRNA/data/samples/human/10X/rdf/restricted_grch38/manuscript/components/if/pairs'

LABEL_S_G2_M = 'S+G2+M'
LABEL_G0_G1 = 'G0+G1'

PADDING = 10
LEGEND_TEXT_OFFSET = 10
LEGEND_BRACKET_OFFSET = 140
LEGEND_GROUP_OFFSET = LEGEND_BRACKET_OFFSET + 10
BRACKET_SIZE = 15


COLOR_WHITE = 'white'
COLOR_BLACK = 'black'
NONE = 'none'

# mm per pt to get sizing
FONT_SCALE_FACTOR = 254 / 72 #3.52777763324264 #3.54166641  # 1 #0.35432 3.51852 #

AXIS_LENGTH = 100

ARROW_LENGTH = 90

#CLUSTER_COLORS = figures.ClusterColors()

LABEL_COLOR_BLOCK_SIZE = 12

GRID_STROKE = STROKE_SIZE
GRID_COLOR = 'gainsboro' #'Gainsboro'
TICK_SIZE = 10
MINOR_TICK_SIZE = TICK_SIZE - 4

AXIS_STROKE = 2

MINOR_TICK_STROKE = 2

# initialize Tk so that font metrics will work

def kws(kws: dict[str, Any], user_kws: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    if user_kws is not None:
        kws.update(user_kws)
    return kws

def clamp(x): 
    return max(0, min(int(x * 255), 255))

def rgbtohex(rgba):
    return '#{:02x}{:02x}{:02x}'.format(clamp(rgba[0]), clamp(rgba[1]), clamp(rgba[2]))

def rgbatohex(rgba):
    return '#{:02x}{:02x}{:02x}'.format(clamp(rgba[0]), clamp(rgba[1]), clamp(rgba[2]), clamp(rgba[3]))

def hexcolortrans(hexcolor, trans=0.5):
    return '{}{:02x}'.format(hexcolor, clamp(trans))



ABC_COLORS = {'ABC':'red', 'GCB':'green', 'Unclass':'blue'}


CMAP = matplotlib.cm.get_cmap('tab10', 10)
SHIPP_COLORS = {'C1':CMAP(0), 'C2':CMAP(1), 'C3':CMAP(2), 'C4':CMAP(3), 'C5':CMAP(4), 'Unclassified':'gray'}

DHIT_COLORS = {'DHITsig-pos':rgbatohex(matplotlib.cm.get_cmap('tab20c')(16)), 
               'DHITsig-neg':rgbatohex(matplotlib.cm.get_cmap('tab20c')(18)),
               'n/a': 'none'} # 'lightgray'{'DHITsig-pos':'dimgray', 'DHITsig-neg':'silver'}

SURVIVAL_Y_LABEL = 'PFS'
OS_SURVIVAL_Y_LABEL = 'OS'


def css_param(name:str, value:str) -> str:
    # if isinstance(value, str) and value != 'none' and re.search('\d+', value) is None:
    #    value = "'{}'".format(value)

    return '{}: {}'.format(name, value)


def css_params(*params):
    return '; '.join([css_param(params[i], params[i + 1]) for i in range(0, len(params), 2)])


def format_css_params(params:Mapping[str, str]) -> str:
    return '; '.join([css_param(param, params[param]) for param in sorted(params)])


def img_dim(f):
    """
    Returns the size of an image in pixels.
    """

    return Image.open(f).size


def img_w(f):
    return img_dim(f)[0]


def scaled_image_h(f, w):
    """
    Return the unitless scaled height of an image given its width.

    Parameters
    ----------
    f : str
        Filename
    w : int
        Image width
    """

    iw, ih = img_dim(f)

    # ratio of real width to w
    r = float(w) / iw

    return round(ih * r, 3)


def scaled_image_w(f, h):
    """
    Return the unitless scaled height of an image given its width.

    Parameters
    ----------
    f : str
        Filename
    h : int
        Image height
    """

    iw, ih = img_dim(f)

    # ratio of real width to w
    r = float(h) / ih

    return round(iw * r, 3)


def find_gene_exp_dir(group, colormap='bgy'):
    dir = find_umap_dir(group)

    dir = os.path.join(dir, 'GeneExp', colormap, 'trimmed')

    return dir


def find_gene_exp_file(group, c):
    dir = find_gene_exp_dir(group)

    for n in os.listdir(dir):
        d = os.path.join(dir, n)
        if c in d and 'png' in d:
            return d

    return None


def find_exp_file(name, dir):
    #dir = '{}/GeneExp/trimmed'.format(dir)

    files = os.listdir(dir)
    
    matches = []
    
    for file in files:
        if name in file and 'trimmed' in file and 'BGY' not in file:
            matches.append(os.path.join(dir, file))
            
    ret = None
    
    for file in sorted(matches):
        if file.endswith('jpg'):
            ret = file
            break
        
    if ret is None:
        for file in sorted(matches):
            if file.endswith('png'):
                ret = file
                break
        
    print('Found exp file', ret)

    return ret


def find_sep_clust_files(name, dir, method='umap'):
    ret = []

    files = os.listdir(dir)

    for file in sorted(files):
        print(file, name)
        if '_{}_'.format(name) in file and 'trimmed' in file and method in file and 'sep_clust' in file and 'png' in file:
            ret.append(os.path.join(dir, file))

    return ret


def get_text_metrics(text,
                     size=DEFAULT_FONT_SIZE,
                     family=DEFAULT_FONT_FAMILY,
                     weight=DEFAULT_FONT_WEIGHT):
    #font = tkFont.Font(family=family, size=size, weight=weight)
    #(w, h) = (font.measure(text), font.metrics('linespace'))
    # return (w, h)

    family = family  + '.ttf'

#    f = ImageFont.truetype(family, size)
#
#    w = 0
#    h = 0
#
#    for c in text:
#        s = f.getsize(c)
#        w += s[0]
#        h = max(h, s[1])

    # Gets spacing with 1 wrong
    #text = text.replace('1', '8')
    
    t2 = ''
    
    for l in text:
        if re.match(r'[A-Z0-9]', l):
            t2 += 'A'
        else:
            t2 += 'a'

    text = text.replace('c', 'a')
    imf = ImageFont.truetype(family, size)
    s = imf.getsize(text)
    w = np.sum([imf.getsize(c)[0] for c in text])
    
    return [s[0], s[1]] #ImageFont.truetype(family, size).getsize(text) #''.join(['a'] * len(text))) #text.upper())

#    tk_root = Tkinter.Tk()
#    key = (family, size, weight)
#    print(key)
#    font = tkFont.Font(family=family, size=size, weight=weight)
#    (w, h) = (font.measure(text), font.metrics('linespace'))
#    return (w, h)


def format_rotate(rot):
    if rot is None:
        rot = 0

    if isinstance(rot, tuple) or isinstance(rot, list):
        return 'rotate({} {} {})'.format(rot[0], rot[1], rot[2])
    elif isinstance(rot, int) or isinstance(rot, float):
        return 'rotate({} 0 0)'.format(rot)
    else:
        return 'rotate(0 0 0)'


def format_translate(x, y):
    return 'translate({}, {})'.format(round(x, 3), round(y, 3))


def rot_trans(rotate=0, x=0, y=0):
    return '{} {}'.format(format_rotate(rotate), format_translate(x, y))


def scale_viewbox(w, h, vw=10):
    return '0 0 {} {}'.format(vw, round(vw * h / w, 3))


def find_dir(dir, name):
    for n in os.listdir(dir):
        d = os.path.join(dir, n)
        if os.path.isdir(d) and n == name:
            return d

    return None


def find_umap_dir(name):
    return find_dir(UMAP_DIR, name)


def find_umap_png(dir, name):
    print('find', name)
    for f in os.listdir(dir):
        print(f)
        if 'umap' in f and 'png' in f and name in f:
            print(f, name)
            return os.path.join(dir, f)

    return None


def find_monocle_dir(name):
    return find_dir(MONOCLE_DIR, name)


def find_monocle_png(dir):
    for f in os.listdir(dir):
        f = os.path.join(dir, f)
        if 'ptime' in f and 'edges' not in f and 'png' in f:
            return f

    return None


def find_sep_clust_dir(group, type='umap'):
    if type == 'monocle':
        dir = find_monocle_dir(group)
    else:
        dir = find_umap_dir(group)

    dir = os.path.join(dir, 'sep_clust', 'trimmed')

    return dir


def find_sep_clust_file(group, c, type='umap'):
    dir = find_sep_clust_dir(group, type=type)

    for n in os.listdir(dir):
        f = os.path.join(dir, n)
        if ('c{}.'.format(c) in f or 'c{}_'.format(c) in f) and 'png' in f:
            return f

    return None


def find_if_dir(name, sub=''):
    return os.path.join(find_dir(IF_DIR, name), sub)

def find_if_file(group, name, sub=''):
    dir = find_if_dir(group, sub=sub)

    nl = name.lower()

    for file in os.listdir(dir):
        p = os.path.join(dir, file)
        if nl in file.lower():
            return p

    return None

def find_if_pairs_dir(name, sub=''):
    return os.path.join(find_dir(IF_PAIRS_DIR, name), sub)

def find_if_pairs_file(group, name, sub=''):
    dir = find_if_pairs_dir(group, sub=sub)

    nl = name.lower()

    for file in os.listdir(dir):
        p = os.path.join(dir, file)
        if nl in file.lower():
            return p

    return None
