from typing import Any, Optional, Union

import libplot
import matplotlib
import numpy as np
import pandas as pd
from scipy.cluster import hierarchy
from scipy.cluster.hierarchy import dendrogram, linkage

from . import core, matrix
from .svgfigure import SVGFigure

DEFAULT_HEATMAP_KWS = {'show': True, 'gridcolor':core.GRID_COLOR, 'framecolor':'black', 'col_colors':{}, 'col_color_height':0}

def add_clustermap(svg: SVGFigure,
                   df: pd.DataFrame,
                   pos: tuple[int, int] = (0, 0),
                   cell: tuple[int, int] = [50, 50],
                   lim: tuple[int, int] = matrix.DEFAULT_LIMITS,
                   cmap: matplotlib.colors.Colormap = libplot.BWR2_CMAP,
                   xticklabels: Optional[Union[list[str], bool]] = True,
                   xticklabel_colors: dict[str, str] = {},
                   yticklabels: Optional[Union[list[str], bool]] = False,
                   row_zscore=False,
                   rename_cols: dict[str, str] = {},
                   col_colors: list[tuple[str, dict[str, str]]] = [],
                   row_colors: list[tuple[str, dict[str, str]]] = [],
                   color_height=40,
                   tree_offset=15,
                   tree_height=180,
                   row_linkage: Optional[Union[linkage, str]] = None,
                   col_linkage: Optional[Union[linkage, str]] = 'auto',
                   show_col_tree=True,
                   show_row_tree=True,
                   xsplits: Optional[list[int]] = None,
                   xsplitgap=40,
                   ysplits: Optional[list[int]] = None,
                   ysplitgap=40,
                   heatmap_kws:dict[str, Any]= {}) -> dict[str, Any]:
    """_summary_

    Args:
        svg (SVGFigure): _description_
        df (pd.DataFrame): _description_
        pos (tuple[int, int], optional): _description_. Defaults to (0, 0).
        cell (tuple[int, int], optional): _description_. Defaults to heatmap.DEFAULT_CELL.
        lim (tuple[int, int], optional): _description_. Defaults to heatmap.DEFAULT_LIMITS.
        cmap (_type_, optional): _description_. Defaults to libplot.BWR2_CMAP.
        gridcolor (_type_, optional): _description_. Defaults to core.GRID_COLOR.
        showframe (bool, optional): _description_. Defaults to True.
        xticklabels (bool, optional): _description_. Defaults to True.
        xticklabel_colors (dict[str, str], optional): _description_. Defaults to {}.
        yticklabels (bool, optional): _description_. Defaults to True.
        zscore (bool, optional): _description_. Defaults to True.
        col_colors (dict[str, str], optional): _description_. Defaults to {}.
        show_col_colobar (bool, optional): _description_. Defaults to True.
        color_height (int, optional): _description_. Defaults to 40.
        tree_offset (int, optional): _description_. Defaults to 15.
        tree_height (int, optional): _description_. Defaults to 180.
        row_linkage (Optional[Union[linkage, str]], optional): _description_. Defaults to 'auto'.
        col_linkage (Optional[Union[linkage, str]], optional): _description_. Defaults to 'auto'.
        show_col_tree (bool, optional): _description_. Defaults to True.
        show_row_tree (bool, optional): _description_. Defaults to True.

    Returns:
        tuple[int, int]: width and height of plot.
    """

    x, y = pos

    _heatmap_kws = DEFAULT_HEATMAP_KWS | heatmap_kws

    print(_heatmap_kws)

    if xsplits is None:
        xsplits = [df.shape[1]]

    if ysplits is None:
        ysplits = [df.shape[0]]

    if row_zscore:
        df = matrix.zscore(df)

    if isinstance(row_linkage, str) and row_linkage == 'auto':
        row_linkage = linkage(df, method='average', metric='correlation')
        row_linkage = hierarchy.optimal_leaf_ordering(row_linkage, df)

    if isinstance(col_linkage, str) and col_linkage == 'auto':
        col_linkage = linkage(df.T, method='average', metric='correlation')
        col_linkage = hierarchy.optimal_leaf_ordering(col_linkage, df.T)

    # If row linkage
    if row_linkage is not None:
        dr = dendrogram(row_linkage, get_leaves=True, no_plot=True)
        # reorder rows
        df = df.iloc[dr['leaves'], :]

    if col_linkage is not None:
        dc = dendrogram(col_linkage, get_leaves=True, no_plot=True)
        # reorder columns
        print(len(dc['leaves']), hierarchy.optimal_leaf_ordering(col_linkage, df.T))
        df = df.iloc[:, dc['leaves']]

    #df.to_csv('reordered.tsv', sep='\t', header=True, index=True)

    mapper = matplotlib.cm.ScalarMappable(norm=matplotlib.colors.Normalize(vmin=lim[0], vmax=lim[1]),
                                          cmap=cmap)

    hx = x
    hy = y
    w = cell[0] * df.shape[1]
    h = cell[1] * df.shape[0]

    # heatmap

    meta = matrix.add_heatmap(svg=svg,
                            df=df,
                            pos=pos,
                            cell=cell,
                            lim=lim,
                            cmap=cmap,
                            show=_heatmap_kws['show'],
                            gridcolor=_heatmap_kws['gridcolor'],
                            framecolor=_heatmap_kws['framecolor'],
                            xticklabels=False,
                            yticklabels=False,
                            xsplits=xsplits,
                            xsplitgap=xsplitgap,
                            ysplits=ysplits,
                            ysplitgap=ysplitgap)

    # determine the offset of each cell relative to where it should be
    # on a normal heatmap this will be 0 for every row
    x_offset_map = {x: meta['x_map'][x]-x*cell[0] for x in range(df.shape[1])}
    y_offset_map = {x: meta['y_map'][x]-x*cell[1] for x in range(df.shape[0])}

    # col tree
    if col_linkage is not None and show_col_tree:
        icoord = np.array(dc['icoord'])
        dcoord = np.array(dc['dcoord'])

        # norm x
        ic = icoord.flatten()
        min_i = ic.min()
        range_i = ic.max() - min_i
        icoord = np.array([[(i - min_i) / range_i for i in ic]
                          for ic in icoord])

        # norm y
        ic = dcoord.flatten()
        min_i = ic.min()
        range_i = ic.max() - min_i
        dcoord = np.array([[(i - min_i) / range_i for i in ic]
                          for ic in dcoord])

        # plot col tree
        tree_width = cell[0] * (df.shape[1] - 1)

        x1 = x + cell[0] / 2
        y1 = y - tree_offset

        if len(col_colors) > 0:
            y1 -= color_height * len(col_colors) + tree_offset

        n = df.shape[1] - 1

        for i, ic in enumerate(icoord):
            dc = dcoord[i]

            # draw 3 lines connecting the 4 points k1...k4
            for j in range(0, 3):
                x2 = x1 + ic[j] * tree_width + x_offset_map[int(ic[j] * n)]
                x3 = x1 + ic[j + 1] * tree_width + x_offset_map[int(ic[j + 1] * n)]

                svg.add_line(x1=x2, y1=y1-dc[j]*tree_height, x2=x3, y2=y1-dc[j+1]*tree_height)

    # col colors

    if len(col_colors) > 0:
        y1 = y - tree_offset - color_height

        for col_color in col_colors:
            x1 = x
            xs1 = 0
            for xs2 in xsplits:
                labels = df.columns[xs1:xs2]
                x2 = x1
                for li, label in enumerate(labels):
                    if label in col_color[1]:
                        # use larger cell size to cover white gaps between adjacent elements in svg
                        svg.add_rect(x2, y1, cell[0] * 1.5 if li < len(labels)-1 else cell[0], color_height, fill=col_color[1][label])
  
                    x2 += cell[0]

                svg.add_frame(x=x1, y=y1, w=x2-x1, h=color_height)

                x1 = x2 + xsplitgap
                xs1 = xs2

            y1 -= color_height + tree_offset

    # plot row tree
    if _heatmap_kws['show']:

        if row_linkage is not None and show_row_tree:
            # row tree
            icoord = np.array(dr['icoord'])
            dcoord = np.array(dr['dcoord'])

            # norm x
            ic = icoord.flatten()
            min_i = ic.min()
            range_i = ic.max() - min_i
            icoord = np.array([[(i - min_i) / range_i for i in ic]
                            for ic in icoord])

            # norm y
            ic = dcoord.flatten()
            min_i = ic.min()
            range_i = ic.max() - min_i
            dcoord = np.array([[(i - min_i) / range_i for i in ic]
                            for ic in dcoord])

            x1 = x - tree_offset

            if len(row_colors) > 0:
                x1 -= color_height * len(row_colors) + tree_offset

            tree_width = cell[1] * (df.shape[0] - 1)
            # Render the tree so the leaves are in the middle of the cell
            y1 = y + cell[1] / 2

            # Used to take the normalized value of the tree y between 0 and 1
            # and map it to a row 0-(#rows-1)
            n = df.shape[0] - 1

            for i, ic in enumerate(icoord):
                dc = dcoord[i]

                for j in range(0, 3):
                    # calculate coordinate as normal, but also lookup the row the
                    # normalized coordinate maps to and check if it has an offset
                    # because of a split gap and add this
                    y2 = y1 + ic[j] * tree_width + y_offset_map[int(ic[j] * n)]
                    y3 = y1 + ic[j + 1] * tree_width + \
                        y_offset_map[int(ic[j + 1] * n)]

                    svg.add_line(x1=x1-dc[j]*tree_height, y1=y2,
                                x2=x1-dc[j+1]*tree_height, y2=y3)
                    
        # row colors

        if len(row_colors) > 0:
            x1 = x - tree_offset - color_height

            for row_color in row_colors:
                y1 = y
                ys1 = 0
                for ys2 in ysplits:
                    labels = df.index[ys1:ys2]
                    y2 = y1
                    for li, label in enumerate(labels):
                        if label in col_color[1]:
                            svg.add_rect(x1, y2, color_height, cell[1], fill=row_color[1][label])

                        y2 += cell[1]

                    svg.add_frame(x=x1, y=y1, w=color_height, h=x2-x1)

                    y1 = y2 + ysplitgap
                    ys1 = ys2

                x1 -= color_height + tree_offset

        # row labels

        if isinstance(yticklabels, bool):
            if yticklabels:
                yticklabels = df.columns
            else:
                yticklabels = []

        if len(yticklabels) > 0:
            #if col_linkage is not None and show_col_tree:
            #    y1 -= (tree_offset + tree_height)

            #if len(col_colors) > 0:
            #    y1 -= color_height + tree_offset

            x1 = x + df.shape[1] * cell[0] + tree_offset
            y1 = y # + cell[1]/2
            ys1 = 0
            for ys2 in ysplits:
                labels = df.index[ys1:ys2]
                # allow last minute renaming
                labels = np.array(
                    [rename_cols[x] if x in rename_cols else x for x in labels])

                matrix.add_yticklabels(svg, labels, pos=(
                    x1, y1), colors=xticklabel_colors, cell=cell)

                y1 += cell[1] * labels.size + ysplitgap
                ys1 = ys2


        # col labels

        if isinstance(xticklabels, bool):
            if xticklabels:
                xticklabels = df.columns
            else:
                xticklabels = []

        if len(xticklabels) > 0:
            x1 = x + cell[0] / 2
            y1 = y - 30

            if col_linkage is not None and show_col_tree:
                y1 -= (tree_offset + tree_height)

            if len(col_colors) > 0:
                y1 -= color_height + tree_offset

            x1 = x
            xs1 = 0
            for xs2 in xsplits:
                labels = df.columns[xs1:xs2]
                # allow last minute renaming
                labels = np.array(
                    [rename_cols[x] if x in rename_cols else x for x in labels])

                matrix.add_xticklabels(svg, labels, pos=(
                    x1, y1), colors=xticklabel_colors, cell=cell)

                x1 += cell[0] * labels.size + xsplitgap
                xs1 = xs2

    return {'w': w, 'h': h, 'df':df}
