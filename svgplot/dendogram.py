import numpy as np
import libplot
import matplotlib
import pandas as pd
import lib10x
from scipy.cluster.hierarchy import linkage, dendrogram
from . import heatmap
from . import svgplot

def add_dendrogram(svg,
                   df: pd.DataFrame,
                   pos: tuple[int, int] = (0, 0),
                   cell: tuple[int, int] = heatmap.DEFAULT_CELL,
                   lim: tuple[int, int] = heatmap.DEFAULT_LIMITS,
                   cmap=libplot.BWR2_CMAP,
                   gridcolor=svgplot.GRID_COLOR,
                   showgrid=True,
                   showframe=True,
                   xticklabels=True,
                   yticklabels=True,
                   zscore=True,
                   row_colors={},
                   col_colors={},
                   color_height=40,
                   tree_offset=15,
                   tree_height=180,
                   row_linkage=None,
                   col_linkage=None,
                   show_col_tree=True,
                   show_row_tree=True):

    x, y = pos

    if zscore:
        df = lib10x.scale(df)

    if row_linkage is None:
        row_linkage = linkage(df, method='average', metric='correlation')

    if col_linkage is None:
        col_linkage = linkage(df.T, method='average', metric='correlation')

    dr = dendrogram(row_linkage, get_leaves=True, no_plot=True)
    dc = dendrogram(col_linkage, get_leaves=True, no_plot=True)

    # reorder
    df = df.iloc[dr['leaves'], dc['leaves']]

    df.to_csv('reordered.tsv', sep='\t', header=True, index=True)

    mapper = matplotlib.cm.ScalarMappable(norm=matplotlib.colors.Normalize(vmin=lim[0], vmax=lim[1]),
                                          cmap=cmap)

    hx = x
    hy = y
    w = cell[0] * df.shape[1]
    h = cell[1] * df.shape[0]

    # col tree

    icoord = np.array(dc['icoord'])
    dcoord = np.array(dc['dcoord'])

    # norm x
    ic = icoord.flatten()
    min_i = ic.min()
    max_i = ic.max()
    range_i = max_i - min_i
    icoord = np.array([[(i - min_i) / range_i for i in ic] for ic in icoord])

    # norm y
    ic = dcoord.flatten()
    min_i = ic.min()
    max_i = ic.max()
    range_i = max_i - min_i
    dcoord = np.array([[(i - min_i) / range_i for i in ic] for ic in dcoord])

    # plot col tree
    
    if show_col_tree:
        tree_width = cell[0] * (df.shape[1] - 1)

        x1 = x + cell[0] / 2
        y1 = y - tree_offset

        if len(col_colors) > 0:
            y1 -= color_height + tree_offset

        for i, ic in enumerate(icoord):
            dc = dcoord[i]

            for j in range(0, 3):
                svg.add_line(x1=x1+ic[j]*tree_width, y1=y1-dc[j]*tree_height,
                            x2=x1+ic[j+1]*tree_width, y2=y1-dc[j+1]*tree_height)

    # col colors

    if len(col_colors) > 0:
        x1 = x
        y1 = y - tree_offset - color_height

        for c in df.columns:
            for name in col_colors:
                if name in c:
                    svg.add_rect(x1, y1, w - x1, color_height,
                                 fill=col_colors[name])
                    break
            x1 += cell[0]

        svg.add_frame(x=x, y=y1, w=w, h=color_height)

    # plot row tree

    # row tree
    icoord = np.array(dr['icoord'])
    dcoord = np.array(dr['dcoord'])

    # norm x
    ic = icoord.flatten()
    min_i = ic.min()
    max_i = ic.max()
    range_i = max_i - min_i
    icoord = np.array([[(i - min_i) / range_i for i in ic] for ic in icoord])

    # norm y
    ic = dcoord.flatten()
    min_i = ic.min()
    max_i = ic.max()
    range_i = max_i - min_i
    dcoord = np.array([[(i - min_i) / range_i for i in ic] for ic in dcoord])

    

    if show_row_tree:
        x1 = x - tree_offset
        tree_width = cell[1] * (df.shape[0] - 1)
        y1 = y + cell[1] / 2

        for i, ic in enumerate(icoord):
            dc = dcoord[i]

            for j in range(0, 3):
                svg.add_line(x1=x1-dc[j]*tree_height, y1=y1+ic[j]*tree_width,
                            x2=x1-dc[j+1]*tree_height, y2=y1+ic[j+1]*tree_width)

    # heatmap

    heatmap.add_heatmap(svg=svg,
                df=df,
                pos=pos,
                cell=cell,
                lim=lim,
                cmap=cmap,
                gridcolor=gridcolor,
                showgrid=showgrid,
                showframe=showframe,
                xticklabels=False,
                yticklabels=xticklabels)

    # for i in range(0, df.shape[0]):
    #     hx = x

    #     for j in range(0, df.shape[1]):
    #         v = df.iloc[i, j]
    #         color = svgplot.rgbatohex(mapper.to_rgba(v))

    #         svg.add_rect(hx, hy, cell[0], cell[1], fill=color)

    #         hx += cell[0]

    #     hy += cell[1]

    # if showgrid:
    #     add_grid(svg,
    #              pos=pos,
    #              size=(w, h),
    #              shape=df.shape,
    #              color=gridcolor)

    # if showframe:
    #     svg.add_frame(x=x, y=y, w=w, h=h)

    if yticklabels:
        y1 = y + cell[1] / 2

        for name in df.index:
            svg.add_text_bb(name, x=w+20, y=y1)
            y1 += cell[1]

    if xticklabels:
        x1 = x + cell[0] / 2
        y1 = y - 30 
        
        if show_col_tree:
            y1 -= (tree_offset + tree_height)

        for name in df.columns:
            svg.add_text_bb(name, x=x1, y=y1, orientation='v')
            x1 += cell[0]

    return (w, h)