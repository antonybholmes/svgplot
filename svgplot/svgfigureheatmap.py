#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 09:36:28 2019

@author: antony
"""
import collections
import re
import numpy as np
import libplot
import matplotlib
import yaml
import lib10x
import pandas as pd

from . import svgplot
from .svgfigureplot import SVGFigurePlot


DEFAULT_CELL = [30, 26]
DEFAULT_LIMITS = [-2, 2]


class SVGFigureHeatmap(SVGFigurePlot):
    def __init__(self,
                 file,
                 size=('11in', '8.5in'),  # size=('279mm', '216mm'),
                 view=(2790, 2160),
                 grid=(12, 12),
                 subgrid=(12, 12),
                 border=100):
        super().__init__(file,
                         size=size,
                         view=view,
                         grid=grid,
                         subgrid=subgrid,
                         border=border)

    def heatmap_color_cols(self,
                           df,
                           clusters,
                           x=0,
                           y=0,
                           w=0,
                           labels=True,
                           orientation='auto',
                           label_mode='short',
                           padding=10,
                           ignore={},
                           frame=False,
                           weight='normal'):
        df_heatmap = df  # df.iloc[:, :-1]

        xs = w / df_heatmap.shape[1]
        #ys = h / df_heatmap.shape[0]

        group_map = collections.defaultdict(set)

        gy = y - 2 * svgplot.LABEL_COLOR_BLOCK_SIZE

        for i in range(0, df_heatmap.shape[1]):
            name = df_heatmap.columns[i]

            if not re.match(r'C\d+', name):
                continue

            cluster = int(name[1:])

            altId = clusters.find(cluster)

            color = clusters.get_color(altId)

            self.add_rect(x + i * xs, gy, xs,
                          svgplot.LABEL_COLOR_BLOCK_SIZE, fill=color)

            if i > 0:
                x1 = x + i * xs
                self.add_line(x1=x1,
                              y1=gy,
                              x2=x1,
                              y2=gy+svgplot.LABEL_COLOR_BLOCK_SIZE,
                              color='white')

            if frame:
                self.add_frame(x + i * xs, gy, xs,
                               svgplot.LABEL_COLOR_BLOCK_SIZE,
                               color='black')

            group = altId  # re.sub(r' .+', '', altId)

            if label_mode == 'short':
                group = clusters.get_short_group(group)
            elif label_mode == 'group':
                group = clusters.get_group(group)
            else:
                pass

            group_map[group].add(i)

        if labels:
            gy = y - 4 * svgplot.LABEL_COLOR_BLOCK_SIZE
            gy2 = y - 2.5 * svgplot.LABEL_COLOR_BLOCK_SIZE

            for g in group_map:
                if g in ignore:
                    continue

                s = min(group_map[g])
                e = max(group_map[g])

                gx = x + s * xs
                gw = (e - s + 1) * xs
                color = clusters.get_block_color(g)

                if ((orientation == 'auto') and (len(group_map[g]) < 3 and len(g) > 2)) or orientation == 'v':
                    self.add_text_bb(g,
                                     gx,
                                     gy,
                                     w=gw,
                                     color=color,
                                     orientation='v',
                                     weight=weight)
                else:
                    self.add_text_bb(g,
                                     gx,
                                     gy,
                                     w=gw,
                                     align='c',
                                     color=color,
                                     weight=weight)

                if len(group_map[g]) > 1:
                    self.add_line(x1=gx + padding,
                                  y1=gy2,
                                  x2=gx + gw - padding,
                                  y2=gy2,
                                  color=color)

    def heatmap_color_cols_v(self,
                             file,
                             df,
                             clusters,
                             x=0,
                             y=0,
                             h=0,
                             labels=True,
                             label_mode='short',
                             padding=10,
                             weight='normal'):
        df_heatmap = df  # df.iloc[:, :-1]

        xs = h / df_heatmap.shape[1]
        #ys = h / df_heatmap.shape[0]

        group_map = collections.defaultdict(set)

        for i in range(0, df_heatmap.shape[1]):
            name = df_heatmap.columns[i]

            if not re.match(r'C\d+', name):
                continue

            cluster = int(name[1:])

            altId = clusters.find(cluster)

            color = clusters.get_color(altId)

            self.add_rect(x,
                          y + i * xs,
                          svgplot.LABEL_COLOR_BLOCK_SIZE,
                          xs,
                          fill=color)
            self.add_frame(x,
                           y + i * xs,
                           svgplot.LABEL_COLOR_BLOCK_SIZE,
                           xs,
                           color='black')

            group = altId  # re.sub(r' .+', '', altId)

            if label_mode == 'short':
                group = clusters.get_short_group(group)
            elif label_mode == 'group':
                group = clusters.get_group(group)
            else:
                pass

            group_map[group].add(i)

        if labels:
            for g in group_map:
                s = min(group_map[g])
                e = max(group_map[g])

                gx = y + s * xs + self.get_font_h() / 2
                gw = (e - s + 1) * xs
                color = clusters.get_color(g)

                self.add_text_bb(g, x=x + 2 * svgplot.LABEL_COLOR_BLOCK_SIZE,
                                 y=gx, w=gw, color=color, weight=weight)

    def heatmap_color_rows(self,
                           file,
                           df,
                           clusters,
                           x=0,
                           y=0,
                           w=0,
                           h=None,
                           gap=10,
                           framecolor=None):
        if h is None:
            h = svgplot.scaled_image_h(file, w)

        ys = h / df.shape[0]

        used = set()
        ids = []

        for i in range(0, df.shape[0]):
            cluster = df['Cluster'][i]

            if cluster not in used:
                ids.append(cluster)
                used.add(cluster)

        gx = x  # - 2 * svgplot.LABEL_COLOR_BLOCK_SIZE

        c = 0

        for id in ids:
            #cluster = int(name[1:])

            altId = clusters.find(id)
            color = clusters.get_color(altId)

            idx = np.where(df['Cluster'] == id)[0]

            print('color rows', id, idx.size)

            hc = idx.size * ys

            self.add_rect(gx,
                          y,
                          svgplot.LABEL_COLOR_BLOCK_SIZE,
                          hc,
                          fill=color)

            if c > 0 and gap == 0:
                y2 = y + hc
                self.add_line(
                    x1=gx, y1=y2, x2=gx+svgplot.LABEL_COLOR_BLOCK_SIZE, y2=y2, color='white')

            if framecolor is not None:
                self.add_frame(gx, y, svgplot.LABEL_COLOR_BLOCK_SIZE,
                               hc, color=framecolor)

            y += hc + gap
            c += 1

    def heatmap_label_rows(self,
                           file,
                           df,
                           genes,
                           clusters,
                           x=0,
                           y=0,
                           w=None,
                           h=None,
                           gap=10,
                           padding=10,
                           show_ticks=True):
        if w is None and h is None:
            return

        if w is None:
            w = svgplot.scaled_image_w(file, h)

        if h is None:
            h = svgplot.scaled_image_h(file, w)

        ys = h / df.shape[0]

        #self.set_font_size(svgplot.FIGURE_FONT_SIZE)

        gx = x

        if show_ticks:
            gx += 30
        else:
            gx += 10

        for gene_block in genes:
            for i in range(0, len(gene_block)):
                gene_row = gene_block[i]

                gene = gene_row[0]

                idx = np.where(df.index == gene)[0]

                if idx.size > 0:
                    if i == 0:
                        #print(gene, idx)

                        idx = idx[0]

                        if show_ticks:
                            gy = y + ys * idx + ys / 2

                            self.add_line(gx - 20,
                                          gy,
                                          gx - 10,
                                          gy,
                                          color='black')

                        gy = self.get_font_y(y + ys * idx, ys)

                    self.add_text(', '.join(gene_row), x=gx, y=gy)

                gy += self.get_font_h() + padding

        #self.set_font_size(svgplot.DEFAULT_FONT_SIZE)


    def add_heatmap(self,
                    df,
                    x=0,
                    y=0,
                    cell=DEFAULT_CELL,
                    lim=DEFAULT_LIMITS,
                    cmap=libplot.BWR2_CMAP,
                    gridcolor=svgplot.GRID_COLOR,
                    showgrid=True,
                    showframe=True):

        mapper = matplotlib.cm.ScalarMappable(norm=matplotlib.colors.Normalize(vmin=lim[0], vmax=lim[1]),
                                              cmap=cmap)

        hx = x
        hy = y

        for i in range(0, df.shape[0]):
            hx = x

            for j in range(0, df.shape[1]):
                v = df.iloc[i, j]
                color = svgplot.rgbatohex(mapper.to_rgba(v))

                self.add_rect(hx, hy, cell[0], cell[1], fill=color)

                hx += cell[0]

            hy += cell[1]

        w = cell[0] * df.shape[1]
        h = cell[1] * df.shape[0]

        if showgrid:
            self.add_grid(x=x,
                          y=y,
                          w=w,
                          h=h,
                          rows=df.shape[0],
                          cols=df.shape[1],
                          color=gridcolor)

        if showframe:
            self.add_frame(x=x, y=y, w=w, h=h)

        return (w, h)

    def add_scaled_heatmap(self,
                           df,
                           clusters,
                           x=0,
                           y=0,
                           w=100,
                           h=200,
                           lim=DEFAULT_LIMITS,
                           gap=10,
                           cmap=libplot.BWR2_CMAP,
                           gridcolor=svgplot.GRID_COLOR,
                           framecolor='black'):

        #df_heatmap = df.iloc[:, 0:-1]

        df_heatmap = df.iloc[:, np.where(df.columns.str.contains('fold'))[0]]

        mapper = matplotlib.cm.ScalarMappable(norm=matplotlib.colors.Normalize(vmin=lim[0], vmax=lim[1]),
                                              cmap=cmap)

        offset_map = collections.defaultdict(int)

        for i in range(0, df.shape[0]):
            cluster = df['Cluster'][i]
            offset_map[cluster] = max(offset_map[cluster], i)

        hx = x
        hy = y

        dw = w / df_heatmap.shape[1]
        dh = h / df_heatmap.shape[0]

        cw = max(1, dw)
        ch = max(1, dh)

        r1 = 0
        r2 = 0

        print(offset_map)

        print('map', hx, hy, cw, ch)

        for id in clusters.get_clusters():
            cluster = clusters.find(id)
            starty = hy

            r2 = offset_map[cluster]

            dfc = df_heatmap.iloc[r1:(r2+1), :]

            print(cluster, r2, dfc.shape)

            for i in range(0, dfc.shape[0]):
                hx = x

                for j in range(0, dfc.shape[1]):
                    v = dfc.iloc[i, j]
                    color = svgplot.rgbatohex(mapper.to_rgba(v))

                    self.add_rect(hx, hy, cw, ch, fill=color)

                    hx += dw

                hy += dh

            if gridcolor is not None:
                self.add_grid(x=x,
                              y=y,
                              w=w,
                              h=h,
                              rows=dfc.shape[0],
                              cols=dfc.shape[1],
                              color=gridcolor,
                              drawrows=False)

            if framecolor is not None:
                self.add_frame(x=x, y=starty, w=w, h=dh *
                               dfc.shape[0], color=framecolor)

            hy += gap
            r1 = r2 + 1

        return (w, h + gap * (clusters.size - 1))

    def heatmap_color_cols_scaled(self,
                                  df,
                                  clusters,
                                  x=0,
                                  y=0,
                                  w=0,
                                  labels=True,
                                  orientation='a',
                                  label_mode='short',
                                  padding=10,
                                  ignore={},
                                  frame=False,
                                  weight='normal'):
        # df_heatmap = df  # df.iloc[:, :-1]

        xs = w / df.shape[1]
        #ys = h / df_heatmap.shape[0]

        group_map = collections.defaultdict(set)

        gy = y - 2 * svgplot.LABEL_COLOR_BLOCK_SIZE

        for i in range(0, df.shape[1]):
            name = df.columns[i]

            matcher = re.search(r'^([a-zA-Z]+( [a-z])?)', name)

            cluster = matcher.group(1)  # int(name[1:])

            altId = cluster

            color = clusters.get_color(altId)

            self.add_rect(x + i * xs, gy, xs,
                          svgplot.LABEL_COLOR_BLOCK_SIZE, fill=color)

            if i > 0:
                x1 = x + i * xs
                self.add_line(x1=x1,
                              y1=gy,
                              x2=x1,
                              y2=gy+svgplot.LABEL_COLOR_BLOCK_SIZE,
                              color='white')

            if frame:
                self.add_frame(x + i * xs, gy, xs,
                               svgplot.LABEL_COLOR_BLOCK_SIZE,
                               color='black')

            group = altId  # re.sub(r' .+', '', altId)

            if label_mode == 'short':
                group = clusters.get_short_group(group)
            elif label_mode == 'group':
                group = clusters.get_group(group)
            else:
                pass

            group_map[group].add(i)

        if labels:
            gy = y - 4 * svgplot.LABEL_COLOR_BLOCK_SIZE
            gy2 = y - 2.5 * svgplot.LABEL_COLOR_BLOCK_SIZE

            for g in group_map:
                if g in ignore:
                    continue

                s = min(group_map[g])
                e = max(group_map[g])

                gx = x + s * xs
                gw = (e - s + 1) * xs
                color = clusters.get_block_color(g)

                if (orientation != 'a' and (len(group_map[g]) < 3 and len(g) > 2) or orientation == 'v'):
                    self.add_text_bb(g,
                                     gx,
                                     gy,
                                     w=gw,
                                     color=color,
                                     orientation='v',
                                     weight=weight)
                else:
                    gx1 = gx

                    if orientation == 'a':
                        gx1 -= self.get_font_h() * 0.4

                    self.add_text_bb(g,
                                     gx1,
                                     gy,
                                     w=gw,
                                     align='c',
                                     color=color,
                                     orientation=orientation,
                                     weight=weight)

                if len(group_map[g]) > 1:
                    self.add_line(x1=gx + padding,
                                  y1=gy2,
                                  x2=gx + gw - padding,
                                  y2=gy2,
                                  color=color)

    def heatmap_label_rows_scaled(self,
                                  file,
                                  df,
                                  genes,
                                  clusters,
                                  x=0,
                                  y=0,
                                  w=None,
                                  h=None,
                                  gap=10,
                                  padding=10,
                                  show_ticks=True):
        if w is None and h is None:
            return

        if w is None:
            w = svgplot.scaled_image_w(file, h)

        if h is None:
            h = svgplot.scaled_image_h(file, w)

        #df_heatmap = df.iloc[:, 0:-1]
        df_heatmap = df.iloc[:, np.where(df.columns.str.contains('fold'))[0]]

        ys = h / df_heatmap.shape[0]

        #self.set_font_size(svgplot.FIGURE_FONT_SIZE)

        gx = x

        if show_ticks:
            gx += 30
        else:
            gx += 10

        offset_map = collections.defaultdict(int)

        for i in range(0, df.shape[0]):
            cluster = df['Cluster'][i]
            offset_map[cluster] = max(offset_map[cluster], i)

        r1 = 0
        r2 = 0

        tables = []

        for id in clusters.get_clusters():
            cluster = clusters.find(id)
            r2 = offset_map[cluster]
            dfc = df_heatmap.iloc[r1:(r2+1), :]
            tables.append(dfc)
            r1 = r2 + 1

        for gene_block in genes:
            for i in range(0, len(gene_block)):
                gene_row = gene_block[i]

                gene = gene_row[0]

                starty = y + ys / 2

                for ti in range(0, len(tables)):
                    dfc = tables[ti]

                    idx = np.where(dfc.index == gene)[0]

                    if idx.size > 0:
                        idx = idx[0]
                        # self.get_font_y(starty + ys * idx, ys)
                        gy = starty + ys * idx

                        if i == 0:
                            #print(gene, idx)

                            if show_ticks:
                                self.add_line(gx - 20,
                                              gy,
                                              gx - 10,
                                              gy,
                                              color='black')

                        # make sure genes exists in table
                        labels = []
                        for gene in gene_row:
                            #idx = np.where(dfc.index == gene)[0]
                            idx = np.where(df_heatmap.index == gene)[0]
                            if idx.size > 0:
                                labels.append(gene)

                        self.add_text_bb(','.join(labels), x=gx, y=gy)

                        break

                    starty += ys * dfc.shape[0] + gap

                #gy += self.get_font_h() + padding

        #self.set_font_size(svgplot.DEFAULT_FONT_SIZE)

    def add_split_heatmap(self,
                          expfiles,
                          cluster_pairs,
                          rf,
                          cf,
                          x=0,
                          y=0,
                          cell=DEFAULT_CELL,
                          lim=DEFAULT_LIMITS,
                          indexmatch='Gene',
                          colmatch='tpm',
                          cmap=libplot.BWR2_CMAP,
                          gridcolor=svgplot.GRID_COLOR,
                          hspace=10,
                          block_gap=160,
                          splits={},
                          padding=10,
                          showgrid=True,
                          frame=False,
                          labelcolors=None,
                          headings=[],
                          weight='normal'):
        """ 
        A heatmap split into row and column blocks

        Args:
            
        """

        if splits is None:
            splits = {}

        splits.add(0)

        df1 = pd.read_csv(expfiles[0], sep='\t', header=0)
        df_exp1 = df1.iloc[:, np.where(df1.columns.str.contains(colmatch))[0]]
        df_exp1 = df_exp1.set_index(df1[indexmatch])

        df2 = pd.read_csv(expfiles[1], sep='\t', header=0)
        df_exp2 = df2.iloc[:, np.where(df2.columns.str.contains(colmatch))[0]]
        df_exp2 = df_exp2.set_index(df2[indexmatch])
        df_exp = pd.concat([df_exp1, df_exp2], axis=1)

        df_z = lib10x.scale(df_exp)
        df_fc_clipped = df_z.copy()
        df_fc_clipped[df_fc_clipped > 2] = 2
        df_fc_clipped[df_fc_clipped < -2] = -2

        df1 = df_fc_clipped.iloc[:, 0:df_exp1.shape[1]]
        df2 = df_fc_clipped.iloc[:, df_exp1.shape[1]:]

        row_sets = yaml.load(open(rf), Loader=yaml.SafeLoader)
        col_sets = yaml.load(open(cf), Loader=yaml.SafeLoader)

        df1.columns = [x.replace('Cluster ', '').replace(
            ' log2 fold change', '').replace(' avg log2(tpm + 1)', '') for x in df1.columns]
        df2.columns = [x.replace('Cluster ', '').replace(
            ' log2 fold change', '').replace(' avg log2(tpm + 1)', '') for x in df2.columns]

        mapper = matplotlib.cm.ScalarMappable(norm=matplotlib.colors.Normalize(vmin=lim[0], vmax=lim[1]),
                                              cmap=cmap)

        block_width = block_gap

        for col_set in col_sets:
            block_width += len(col_set) * cell[0]

        block_width += hspace * (len(col_sets) - 1)

        #
        # Col labels
        #

        hx = x
        hy = y - cell[1] / 2 - padding

        for split in splits:
            for i in range(0, len(col_sets)):
                col_set = col_sets[i]

                w = len(col_set) * cell[0]
                hx2 = hx

                sw = 0

                c = 0

                for col in col_set:
                    cluster, group = col

                    #print(cluster, group)

                    if group == 1 or group == 'a':
                        search = cluster_pairs[0].find(cluster)
                    else:
                        search = cluster_pairs[1].find(cluster)

                    if isinstance(labelcolors, list):
                        if group == 1 or group == 'a':
                            color = labelcolors[0]
                        else:
                            color = labelcolors[1]
                    else:
                        color = 'black'

                    self.add_text_bb(search,
                                     x=hx2,
                                     y=hy-2*padding,
                                     w=cell[0],
                                     color=color,
                                     orientation='v')

                    sw = max(sw, self.get_string_width(search, weight=weight))

                    if group == 1 or group == 'a':
                        color = cluster_pairs[0].get_color(search)
                    else:
                        color = cluster_pairs[1].get_color(search)

                    self.add_rect(
                        hx2, hy, cell[0], svgplot.LABEL_COLOR_BLOCK_SIZE, fill=color)

                    if c > 0 or (i > 0 and 'nospace-after' in headings[i - 1]):
                        self.add_line(x1=hx2,
                                      y1=hy-2,
                                      x2=hx2,
                                      y2=hy+svgplot.LABEL_COLOR_BLOCK_SIZE+2,
                                      color='white')

                    if frame:
                        self.add_frame(
                            x=hx2, y=hy, w=cell[0], h=svgplot.LABEL_COLOR_BLOCK_SIZE)

                    hx2 += cell[0]

                    c += 1

                # headings if any

                if i < len(headings):
                    heading = headings[i]['name']
                    color = headings[i]['color']

                    hy2 = hy-80

                    if len(col_set) == 1:
                        #                        self.add_line(x1=hx+w/2,
                        #                                      y1=hy2,
                        #                                      x2=hx+w/2,
                        #                                      y2=hy2+svgplot.BRACKET_SIZE,
                        #                                      color=color)
                        pass
                    else:
                        self.add_line(x1=hx + padding,
                                      y1=hy2,
                                      x2=hx + w - padding,
                                      y2=hy2,
                                      color=color)
#                        self.add_line(x1=hx + padding,
#                                      y1=hy2,
#                                      x2=hx + padding,
#                                      y2=hy2+svgplot.BRACKET_SIZE,
#                                      color=color)
#                        self.add_line(x1=hx + w - padding,
#                                      y1=hy2,
#                                      x2=hx + w - padding,
#                                      y2=hy2 + svgplot.BRACKET_SIZE,
#                                      color=color)

                    hy2 -= 2 * padding

                    if 'split' in headings[i] and headings[i]['split']:
                        words = heading.split(' ')
                        #  Put the last word on a newline
                        words = [' '.join(words[0:-1]), words[-1]]
                    else:
                        words = [heading]

                    hx2 = hx + w / 2 - 0.5 * \
                        (self.get_font_h() + padding) * (len(words) - 1)

                    for word in words:
                        self.add_text_bb(word,
                                         x=hx2,
                                         y=hy2,
                                         color=color,
                                         orientation='v',
                                         weight=weight)
                        hx2 += self.get_font_h() + padding

                hx += w

                if i >= len(headings) or \
                    'nospace-after' not in headings[i] or \
                        not headings[i]['nospace-after']:
                    hx += hspace

            hx += block_gap

        #
        # heatmap
        #

        hx = x
        hy = y

        for i in range(0, len(row_sets)):
            if i > 0 and i in splits:
                hy = y
                hx += block_width
                # pass

            hx2 = hx

            row_set = row_sets[i]

            if isinstance(row_set, dict):
                genes = row_set['genes']
            else:
                genes = row_set

            h = len(genes) * cell[1]

            labels = []

            for j in range(0, len(col_sets)):
                col_set = col_sets[j]

                w = len(col_set) * cell[0]
                hx3 = hx2

                for col in col_set:
                    hy2 = hy

                    cluster, group = col

                    for gene in genes:
                        if group == 1 or group == 'a':
                            ri = np.where(df1.index == gene)[0][0]
                            ci = np.where(
                                df1.columns == 'C{}'.format(cluster))[0][0]
                            v = df1.iloc[ri, ci]
                        else:
                            ri = np.where(df2.index == gene)[0][0]
                            ci = np.where(
                                df2.columns == 'C{}'.format(cluster))[0][0]
                            v = df2.iloc[ri, ci]

                        color = svgplot.rgbatohex(mapper.to_rgba(v))
                        self.add_rect(hx3, hy2, cell[0], cell[1], fill=color)

                        hy2 += cell[1]

                    hx3 += cell[0]

                # if showgrid:
                self.add_grid(x=hx2,
                              y=hy,
                              w=w,
                              h=h,
                              rows=len(genes),
                              cols=len(col_set),
                              color=gridcolor)

                # print(col_set)

                # if showframe:
                if j == 0 or ('nospace-after' not in headings[j] and 'nospace-after' not in headings[j - 1]):
                    self.add_frame(x=hx2, y=hy, w=w, h=h)
                    # pass
                else:
                    if 'nospace-after' in headings[j - 1]:
                        self.add_line(x1=hx2, y1=hy, x2=hx2, y2=hy+h,
                                      stroke=svgplot.GRID_STROKE, color=gridcolor)
                        hx3 = hx2 - len(col_sets[j - 1]) * cell[0]
                        w2 = len(col_sets[j - 1]) * cell[0] + w
                        self.add_frame(x=hx3, y=hy, w=w2, h=h)

                hx2 += w

                if j >= len(headings) or \
                    'nospace-after' not in headings[j] or \
                        not headings[j]['nospace-after']:
                    hx2 += hspace

            hy += h + padding

        w = hx2
        h = hy

        #
        # Row labels
        #

        #self.set_font_size(svgplot.FIGURE_FONT_SIZE)

        hy = y
        hx = x

        for col_set in col_sets:
            hx += len(col_set) * cell[0]

        for i in range(0, len(col_sets) - 1):
            if i >= len(headings) or \
                'nospace-after' not in headings[i] or \
                    not headings[i]['nospace-after']:
                hx += hspace

        hx += padding

        for i in range(0, len(row_sets)):
            row_set = row_sets[i]

            if i > 0 and i in splits:
                hy = y
                hx += block_width

            if isinstance(row_set, dict):
                genes = row_set['genes']
            else:
                genes = row_set

            h = len(genes) * cell[1]

            labels = []

            for gene in genes:
                ri = np.where(df1.index == gene)[0][0]
                labels.append(df1.index[ri])

            hy2 = hy + svgplot.LABEL_COLOR_BLOCK_SIZE

            for label in labels:
                self.add_text_bb(label, x=hx, y=hy2)
                hy2 += cell[1]

            hy += h + padding

        #
        # block labels
        #

        #self.set_font_size(svgplot.FIGURE_FONT_SIZE)

        hy = y
        hx = x - 2 * padding

        for i in range(0, len(row_sets)):
            row_set = row_sets[i]

            if i > 0 and i in splits:
                hy = y
                hx += block_width

            if isinstance(row_set, dict):
                name = row_set['name']
                genes = row_set['genes']
            else:
                name = None
                genes = row_set

            if name is not None:
                h = len(genes) * cell[1]
                self.add_text_bb(name, x=hx, y=hy + h, w=h,
                                 align='c', orientation='v')

            hy += h + padding

        #self.set_font_size(svgplot.DEFAULT_FONT_SIZE)

        return (w, h)


    def add_single_split_heatmap(self,
                                 expfile,
                                 clusters,
                                 rf,
                                 cf,
                                 x=0,
                                 y=0,
                                 cell=DEFAULT_CELL,
                                 lim=DEFAULT_LIMITS,
                                 splits=None,
                                 block_gap=140,
                                 indexmatch='Gene',
                                 colmatch='fold change',  # 'tpm',
                                 norm='none',  # 'z-score',
                                 cmap=libplot.BWR2_CMAP,
                                 gridcolor=svgplot.GRID_COLOR,
                                 padding=10,
                                 showgrid=True,
                                 showframe=True,
                                 labelargs=None):
        """ 
        A heatmap split into row and column blocks

        Parameter
        ---------
        rf : str
            Rows to plot yaml file.
        cf : str
            Cols to plot yaml file.
        gf: str, optional
            YAML gene set file

        """

        if splits is None:
            splits = set()

        splits.add(0)

        if labelargs is None:
            labelargs = {}

        if 'mode' not in labelargs:
            labelargs['mode'] = 'bars,cluster,short'
        if 'orientation' not in labelargs:
            labelargs['orientation'] = 'h'
        if 'bold' not in labelargs:
            labelargs['bold'] = False
        if 'grouporientation' not in labelargs:
            labelargs['grouporientation'] = 'h'
        if 'showlabels' not in labelargs:
            labelargs['showlabels'] = True
        if 'showsinglegroups' not in labelargs:
            labelargs['showsinglegroups'] = False
        if 'split' not in labelargs:
            labelargs['split'] = False
        if 'remap' not in labelargs:
            labelargs['remap'] = {}
        if 'rowfontsize' not in labelargs:
            labelargs['rowfontsize'] = svgplot.FIGURE_FONT_SIZE

        row_sets = yaml.load(open(rf), Loader=yaml.SafeLoader)
        col_sets = yaml.load(open(cf), Loader=yaml.SafeLoader)

        # Extract the expression columns of interest
        df1 = pd.read_csv(expfile, sep='\t', header=0)
        df_exp1 = df1.iloc[:, np.where(df1.columns.str.contains(colmatch))[0]]
        df_exp1 = df_exp1.set_index(df1[indexmatch])
        df_exp1.to_csv('data.txt', sep='\t', header=True, index=True)

        if norm == 'z-score':
            df_z = lib10x.scale(df_exp1)
            df_z.to_csv('z.txt', sep='\t', header=True, index=True)
            df_fc_clipped = df_z.copy()
        else:
            df_fc_clipped = df_exp1.copy()

        df_fc_clipped[df_fc_clipped > lim[1]] = lim[1]
        df_fc_clipped[df_fc_clipped < lim[0]] = lim[0]

        df1 = df_fc_clipped  # df_fc_clipped.iloc[:, 0:df_exp1.shape[1]]

        df1.columns = [x.replace('Cluster ', '').replace(' log2 fold change', '').replace(
            ' avg log2(tpm + 1)', '').replace('Avg log2(tpm + 1) in ', '') for x in df1.columns]

        mapper = matplotlib.cm.ScalarMappable(norm=matplotlib.colors.Normalize(vmin=lim[0], vmax=lim[1]),
                                              cmap=cmap)

        hx = x

        block_width = block_gap

        for col_set in col_sets:
            block_width += len(col_set) * cell[0] + padding

        for split in splits:
            self.heatmap_label_cols(clusters,
                                    col_sets,
                                    x=hx,
                                    y=y,
                                    cell=cell,
                                    modes=labelargs['mode'],
                                    orientation=labelargs['orientation'],
                                    grouporientation=labelargs['grouporientation'],
                                    showsinglegroups=labelargs['showsinglegroups'],
                                    split=labelargs['split'],
                                    bold=labelargs['bold'],
                                    remap=labelargs['remap'])

            hx += block_width

        #
        # heatmap
        #

        hx = x

        for col_set in col_sets:
            hy = y

            w = len(col_set) * cell[0]

            labels = []

            for i in range(0, len(row_sets)):
                row_set = row_sets[i]

                if isinstance(row_set, dict):
                    name = row_set['name']
                    genes = row_set['genes']
                else:
                    name = None
                    genes = row_set

                if i > 0 and i in splits:
                    hy = y
                    hx += block_width

                h = len(genes) * cell[1]
                hx2 = hx

                for col in col_set:
                    hy2 = hy

                    for gene in genes:
                        print(gene, col, df1.columns)
                        ri = np.where(df1.index == gene)[0][0]
                        ci = np.where((df1.columns == col) | (
                            df1.columns == 'C{}'.format(col)))[0][0]
                        v = df1.iloc[ri, ci]

                        color = svgplot.rgbatohex(mapper.to_rgba(v))
                        self.add_rect(hx2, hy2, cell[0], cell[1], fill=color)

                        hy2 += cell[1]

                    hx2 += cell[0]

                if showgrid:
                    self.add_grid(x=hx,
                                  y=hy,
                                  w=w,
                                  h=h,
                                  rows=len(genes),
                                  cols=len(col_set),
                                  color=gridcolor)

                if showframe:
                    self.add_frame(x=hx, y=hy, w=w, h=h)

                hy += h + padding

            hx += w + padding

        w = hx - padding
        h = hy - padding

        #
        # Row labels
        #

        #self.set_font_size(labelargs['rowfontsize'])

        hy = y
        hx = x

        for col_set in col_sets:
            hx += len(col_set) * cell[0] + padding

        for i in range(0, len(row_sets)):
            row_set = row_sets[i]

            if isinstance(row_set, dict):
                name = row_set['name']
                genes = row_set['genes']
            else:
                name = None
                genes = row_set

            if i > 0 and i in splits:
                hy = y
                hx += block_width

            h = len(genes) * cell[1]

            labels = []

            for gene in genes:
                ri = np.where(df1.index == gene)[0][0]
                labels.append(df1.index[ri])

            hy2 = hy + cell[1] / 2

            for label in labels:
                self.add_text_bb(label, x=hx, y=hy2)
                hy2 += cell[1]

            hy += h + padding

        #
        # block labels
        #

        #self.set_font_size(svgplot.FIGURE_FONT_SIZE)

        hy = y
        hx = x - 2 * padding

        for i in range(0, len(row_sets)):
            row_set = row_sets[i]

            if i > 0 and i in splits:
                hy = y
                hx += block_width

            if isinstance(row_set, dict):
                name = row_set['name']
                genes = row_set['genes']
            else:
                name = None
                genes = row_set

            if name is not None:
                h = len(genes) * cell[1]
                self.add_text_bb(name, x=hx, y=hy + h, w=h,
                                 align='c', orientation='v')

            hy += h + padding

        #self.set_font_size(svgplot.DEFAULT_FONT_SIZE)

        return (w, h)

    def heatmap_label_cols(self,
                           clusters,
                           col_sets,
                           x=0,
                           y=0,
                           cell=DEFAULT_CELL,
                           orientation='h',
                           grouporientation='auto',
                           modes='short,bars',
                           padding=10,
                           linespacing=10,
                           ignore={},
                           split=False,
                           frame=False,
                           showunclass=True,
                           showsinglegroups=False,
                           bold=False,
                           remap={},
                           size=svgplot.HEATMAP_HEADING_FONT_SIZE,
                           weight='normal'):
        """
        Label a heat map

        Parameters
        ----------
        split: bool, optional
            True if labels should be split on space to form newlines
        """

        if isinstance(modes, str):
            modes = modes.split(',')

        modes = set(modes)

        # Since we can rename groups, we store the colors separately to
        # the main cluster objects
        group_map = collections.defaultdict(
            lambda: collections.defaultdict(set))
        color_map = {}
        block_color_map = {}

        hx = x
        hy = y

        h = svgplot.LABEL_COLOR_BLOCK_SIZE  # cell[1] / 2


        for col_set in col_sets:
            w = len(col_set) * cell[0]
            hx2 = hx

            for i in range(0, len(col_set)):
                col = col_set[i]

                altId = clusters.find(
                    col) if clusters is not None else str(col)

                color = clusters.get_color(
                    altId) if clusters is not None else 'black'

                for mode in modes:
                    if mode == 'short':
                        group = clusters.get_short_group(
                            altId) if clusters is not None else str(col)
                    elif mode == 'group':
                        group = clusters.get_group(
                            altId) if clusters is not None else str(col)
                    else:
                        group = altId

                    color = clusters.get_color(
                        group) if clusters is not None else 'black'
                    block_color = clusters.get_block_color(
                        group) if clusters is not None else 'black'

                    if group in remap:
                        group = remap[group]

                    group_map[mode][group].add(i)
                    color_map[group] = color
                    block_color_map[group] = block_color

                hx2 += cell[0]

            gy = hy - padding

            #
            # plot color bar
            #

            if 'bars' in group_map:
                gy -= h
                gx = x  # + cell[0] / 2

                # keep track of longest string to work out how much
                # vertical space to allocate
                sw = 0

                c = 0

                for g in group_map['bars']:
                    if g not in ignore:
                        color = color_map[g]

                        self.add_rect(gx, gy, cell[0], h, fill=color)

                        if c > 0:
                            self.add_line(x1=gx, y1=gy-2, x2=gx,
                                          y2=gy+h+2, color='white')

                        if frame:
                            self.add_frame(gx, gy, cell[0], h)

                    gx += cell[0]

                    c += 1

                gy -= padding

            #
            # plot cluster id first
            #

            if 'clusters' in group_map:
                gy -= padding
                gx = x  # + cell[0] / 2

                # keep track of longest string to work out how much
                # vertical space to allocate
                sw = 0

                weight = 'normal'  # 'bold' if bold else 'normal'

                for g in group_map['clusters']:
                    if g not in ignore:
                        color = color_map[g]

                        if orientation == 'v':
                            self.add_text_bb(g,
                                             x=gx,
                                             y=gy,
                                             w=cell[0],
                                             color=color,
                                             orientation='v',
                                             weight=weight)

                            sw = max(sw, self.get_string_width(g))
                        else:
                            self.add_text_bb(g,
                                             gx,
                                             gy,
                                             w=cell[0],
                                             color=color,
                                             orientation='h',
                                             weight=weight)

                            sw = self.get_font_h()

                    gx += cell[0]

                gy -= sw

            #
            # Plot group label second
            #

            if 'short' in group_map:
                gy2 = gy  # - svgplot.BRACKET_SIZE
                gy = gy2 - 2 * padding

                for g in group_map['short']:
                    if g in ignore:
                        continue

                    if not showsinglegroups and len(group_map['short'][g]) < 2:
                        continue

                    s = min(group_map['short'][g])
                    e = max(group_map['short'][g])

                    gx = x + s * cell[0]
                    gw = (e - s + 1) * cell[0]

                    color = block_color_map[g]

                    if grouporientation == 'a':
                        # plot at 45 deg angle
                        gx2 = gx - self.get_font_h() * 0.5
                        self.add_text_bb(g,
                                         x=gx2,
                                         y=gy,
                                         w=gw,
                                         color=color,
                                         orientation='a',
                                         weight=weight)
                    elif ((grouporientation == 'auto') and (len(group_map['short'][g]) < 3 and len(g) > 1)) or grouporientation == 'v':
                        if not showunclass and 'unclass' in g.lower():
                            continue

                        if isinstance(split, bool) and split:
                            words = g.split(' ')
                            words = [' '.join(words[0:-1]), words[-1]]
                        elif isinstance(split, set) and g in split:
                            words = g.split(' ')
                            words = [' '.join(words[0:-1]), words[-1]]
                        else:
                            words = [g]

                        gx2 = gx - (self.get_font_h() +
                                    linespacing) / 2 * (len(words) - 1)

                        for word in words:
                            self.add_text_bb(word,
                                             x=gx2,
                                             y=gy,
                                             w=gw,
                                             color=color,
                                             orientation='v',
                                             weight=weight)
                            gx2 += self.get_font_h() + linespacing

                    else:
                        # horizontal labels
                        if showunclass or 'unclass' not in g.lower():
                            self.add_text_bb(g,
                                             gx,
                                             gy,
                                             w=gw,
                                             align='c',
                                             color=color,
                                             weight=weight)

                    if len(group_map['short'][g]) == 1:
                        pass
                    else:
                        self.add_line(x1=gx + padding,
                                      y1=gy2,
                                      x2=gx + gw - padding,
                                      y2=gy2,
                                      color=color)

            hx += w + padding


    def heatmap_label_rows_ext(self,
                           clusters,
                           col_sets,
                           x=0,
                           y=0,
                           cell=DEFAULT_CELL,
                           orientation='h',
                           grouporientation='auto',
                           modes='short,bars',
                           padding=10,
                           linespacing=10,
                           ignore={},
                           split=False,
                           frame=False,
                           showunclass=True,
                           showsinglegroups=False,
                           bold=False,
                           remap={},
                           size=svgplot.HEATMAP_HEADING_FONT_SIZE,
                           weight='normal'):
        """
        Label a heat map

        Parameters
        ----------
        split: bool, optional
            True if labels should be split on space to form newlines
        """

        if isinstance(modes, str):
            modes = modes.split(',')

        modes = set(modes)

        # Since we can rename groups, we store the colors separately to
        # the main cluster objects
        group_map = collections.defaultdict(
            lambda: collections.defaultdict(set))
        color_map = {}
        block_color_map = {}

        hx = x
        hy = y

        w = svgplot.LABEL_COLOR_BLOCK_SIZE  # cell[1] / 2


        for col_set in col_sets:
            h = len(col_set) * cell[1]
            hy2 = hy

            for i in range(0, len(col_set)):
                col = col_set[i]

                altId = clusters.find(
                    col) if clusters is not None else str(col)

                color = clusters.get_color(
                    altId) if clusters is not None else 'black'

                for mode in modes:
                    if mode == 'short':
                        group = clusters.get_short_group(
                            altId) if clusters is not None else str(col)
                    elif mode == 'group':
                        group = clusters.get_group(
                            altId) if clusters is not None else str(col)
                    else:
                        group = altId

                    color = clusters.get_color(
                        group) if clusters is not None else 'black'
                    block_color = clusters.get_block_color(
                        group) if clusters is not None else 'black'

                    if group in remap:
                        group = remap[group]

                    group_map[mode][group].add(i)
                    color_map[group] = color
                    block_color_map[group] = block_color

                hy2 += cell[1]

            gx = hx + padding

            #
            # plot color bar
            #

            if 'bars' in group_map:
                gx += w
                gy = y  # + cell[0] / 2

                # keep track of longest string to work out how much
                # vertical space to allocate
                sw = 0

                c = 0

                for g in group_map['bars']:
                    if g not in ignore:
                        color = color_map[g]

                        self.add_rect(gx, gy, w, cell[1], fill=color)

                        if c > 0:
                            self.add_line(x1=gx, y1=gy, x2=gx+w,
                                          y2=gy, color='white')

                        if frame:
                            self.add_frame(gx, gy, w, cell[1])

                    gy += cell[1]

                    c += 1

                gx += padding

            #
            # plot cluster id first
            #

            if 'clusters' in group_map:
                gx += padding
                gy = y  # + cell[0] / 2

                # keep track of longest string to work out how much
                # vertical space to allocate
                sw = 0

                weight = 'normal'  # 'bold' if bold else 'normal'

                for g in group_map['clusters']:
                    if g not in ignore:
                        color = color_map[g]

                        if orientation == 'v':
                            self.add_text_bb(g,
                                             x=gx,
                                             y=gy,
                                             h=cell[1],
                                             color=color,
                                             weight=weight)

                            sw = max(sw, self.get_string_width(g))
                        else:
                            self.add_text_bb(g,
                                             gx,
                                             gy,
                                             h=cell[1],
                                             color=color,
                                             weight=weight)

                            sw = self.get_font_h()

                    gy += cell[1]

                gx += sw

            #
            # Plot group label second
            #

            if 'short' in group_map:
                gx2 = gx  # - svgplot.BRACKET_SIZE
                gx = gx2 + 2 * padding

                for g in group_map['short']:
                    if g in ignore:
                        continue

                    if not showsinglegroups and len(group_map['short'][g]) < 2:
                        continue

                    s = min(group_map['short'][g])
                    e = max(group_map['short'][g])

                    gy = y + s * cell[1]
                    gh = (e - s + 1) * cell[1]

                    color = block_color_map[g]

                    if grouporientation == 'a':
                        # plot at 45 deg angle
                        gy2 = gy - self.get_font_h() * 0.5
                        self.add_text_bb(g,
                                         x=gx,
                                         y=gy2,
                                         h=gh,
                                         color=color,
                                         weight=weight)
                    elif ((grouporientation == 'auto') and (len(group_map['short'][g]) < 3 and len(g) > 1)) or grouporientation == 'v':
                        if not showunclass and 'unclass' in g.lower():
                            continue

                        if isinstance(split, bool) and split:
                            words = g.split(' ')
                            words = [' '.join(words[0:-1]), words[-1]]
                        elif isinstance(split, set) and g in split:
                            words = g.split(' ')
                            words = [' '.join(words[0:-1]), words[-1]]
                        else:
                            words = [g]

                        gy2 = gy - (self.get_font_h() +
                                    linespacing) / 2 * (len(words) - 1)

                        for word in words:
                            self.add_text_bb(word,
                                             x=gx,
                                             y=gy2,
                                             w=gh,
                                             color=color,
                                             weight=weight)
                            gy2 += self.get_font_h() + linespacing

                    else:
                        # horizontal labels
                        if showunclass or 'unclass' not in g.lower():
                            self.add_text_bb(g,
                                             gx,
                                             gy,
                                             w=gh,
                                             color=color,
                                             weight=weight)

                    if len(group_map['short'][g]) == 1:
                        pass
                    else:
                        self.add_line(x1=gx2,
                                      y1=gy + padding,
                                      x2=gx2 ,
                                      y2=gy + gh - padding,
                                      color=color)



    def pathway_heatmap(self,
                        file,
                        clusters,
                        x=0,
                        y=0,
                        gene_sets=[],
                        cell=DEFAULT_CELL,
                        lim=DEFAULT_LIMITS,
                        cluster_sets=None,
                        gridcolor='black',  # svgplot.GRID_COLOR,
                        # 'red', #'#aaaaaa',
                        pathwaycolor=['darkgray', 'dimgray'],
                        padding=10,
                        showgrid=True,
                        showframe=True,
                        labelargs=None,
                        showunclass=True,
                        labelrows=True,
                        ignore={},
                        labelcase='upper'):
        """ 
        A heatmap split into row and column blocks

        Parameter
        ---------
        gf: str, optional
            YAML gene set file

        """

        if labelargs is None:
            labelargs = {}

        if 'mode' not in labelargs:
            labelargs['mode'] = 'cluster,bars,short'
        if 'orientation' not in labelargs:
            labelargs['orientation'] = 'h'
        if 'showlabels' not in labelargs:
            labelargs['showlabels'] = True
        if 'showsinglegroups' not in labelargs:
            labelargs['showsinglegroups'] = False
        if 'grouporientation' not in labelargs:
            labelargs['grouporientation'] = 'h'
        if 'split' not in labelargs:
            labelargs['split'] = False

        if isinstance(file, str):
            file = [file]

        files = np.array(file)

        if cluster_sets is None:
            cluster_sets = []

        for f in files:
            df = pd.read_csv(f, sep='\t', header=0)

            for c in df['Gene Set'].values:
                if c not in gene_sets and c.lower() not in ignore:
                    gene_sets.append(c)

            # for c in df['Cluster'].values:
            #     if c not in cluster_sets:
            #         cluster_sets.append(c)

        cluster_sets = np.array(cluster_sets)

        gene_sets = np.array(gene_sets)

        d = np.zeros((gene_sets.size, cluster_sets.size), dtype=int)

        c = 1

        for f in files:
            df = pd.read_csv(f, sep='\t', header=0)

            for i in range(0, gene_sets.size):
                for j in range(0, cluster_sets.size):
                    # convert display to to cluster id
                    print(j, cluster_sets[j])
                    cid = clusters.display_id_to_id(cluster_sets[j])

                    #print(cid, cluster_sets[j])

                    d[i, j] += c if np.where((df['Gene Set'] == gene_sets[i]) & (
                        df['Cluster'] == 'C{}'.format(cid)))[0].size > 0 else 0

            c += 1

        print(labelargs['mode'])

        self.heatmap_label_cols(clusters,
                                np.array([cluster_sets]),
                                x=x,
                                y=y,
                                cell=cell,
                                modes=labelargs['mode'],
                                split=labelargs['split'],
                                orientation='v',
                                grouporientation=labelargs['grouporientation'],
                                showunclass=showunclass,
                                showsinglegroups=labelargs['showsinglegroups'])

        #
        # heatmap
        #

        hy = y

        for i in range(0, gene_sets.size):
            hx = x

            for j in range(0, cluster_sets.size):
                v = d[i, j]

                if v == 1:
                    # svgplot.rgbatohex(mapper.to_rgba(v))
                    color = pathwaycolor[0]
                    self.add_rect(hx, hy, cell[0], cell[1], fill=color)
                elif v == 2:
                    # svgplot.rgbatohex(mapper.to_rgba(v))
                    color = pathwaycolor[1]
                    self.add_rect(hx, hy, cell[0], cell[1], fill=color)
                elif v == 3:
                    color = pathwaycolor[0]
                    self.add_rect(hx, hy, cell[0]/2, cell[1], fill=color)
                    color = pathwaycolor[1]
                    self.add_rect(hx+cell[0]/2, hy,
                                  cell[0]/2, cell[1], fill=color)
                else:
                    color = 'white'
                    self.add_rect(hx, hy, cell[0], cell[1], fill=color)

                hx += cell[0]

            hy += cell[1]

        if showgrid:
            self.add_grid(x=x,
                          y=y,
                          w=hx,
                          h=hy,
                          rows=d.shape[0],
                          cols=d.shape[1],
                          color=gridcolor)

        if showframe:
            self.add_frame(x=x, y=y, w=hx, h=hy)

        w = hx
        h = hy

        #
        # Row labels
        #

        if labelrows:
            #self.set_font_size(svgplot.FIGURE_FONT_SIZE)

            hx = w + padding
            hy = y + cell[1] / 2

            for gene_set in gene_sets:
                gene_set = gene_set.replace('HALLMARK', 'HM')
                gene_set = gene_set.replace('KEGG', 'KG')
                gene_set = gene_set.replace('_PATHWAY', '')
                #gene_set = gene_set.replace('RESPONSE', 'RESP')
                gene_set = gene_set.replace('SIGNALING', 'SIGNAL')
                #gene_set = gene_set.replace('PHOSPHORYLATION', 'PHOS')
                #gene_set = gene_set.replace('REPAIR', 'REP')
                #gene_set = gene_set.replace('REPLICATION', 'REP')
                gene_set = gene_set.replace('NUCLEOTIDE', 'NT')
                #gene_set = gene_set.replace('APOPTOSIS', 'APOPT')

                if labelcase == 'lower':
                    gene_set = gene_set.lower()

                if labelcase == 'upper':
                    gene_set = gene_set.upper()

                self.add_text_bb(gene_set, x=hx, y=hy)
                hy += cell[1]

            #self.set_font_size(svgplot.DEFAULT_FONT_SIZE)

        return (w, h)


    def pathway_heatmap_vert(self,
                            file,
                            clusters,
                            x=0,
                            y=0,
                            gene_sets=[],
                            cell=DEFAULT_CELL,
                            lim=DEFAULT_LIMITS,
                            cluster_sets=None,
                            gridcolor='black',  # svgplot.GRID_COLOR,
                            # 'red', #'#aaaaaa',
                            pathwaycolor=['darkgray', 'dimgray'],
                            padding=10,
                            showgrid=True,
                            showframe=True,
                            labelargs=None,
                            showunclass=True,
                            labelcols=True,
                            ignore={},
                            labelcase='upper'):
        """ 
        A heatmap split into row and column blocks

        Parameter
        ---------
        gf: str, optional
            YAML gene set file

        """

        if labelargs is None:
            labelargs = {}

        if 'mode' not in labelargs:
            labelargs['mode'] = 'cluster,bars,short'
        if 'orientation' not in labelargs:
            labelargs['orientation'] = 'h'
        if 'showlabels' not in labelargs:
            labelargs['showlabels'] = True
        if 'showsinglegroups' not in labelargs:
            labelargs['showsinglegroups'] = False
        if 'grouporientation' not in labelargs:
            labelargs['grouporientation'] = 'h'
        if 'split' not in labelargs:
            labelargs['split'] = False

        if isinstance(file, str):
            file = [file]

        files = np.array(file)

        if cluster_sets is None:
            cluster_sets = []

        for f in files:
            df = pd.read_csv(f, sep='\t', header=0)

            for c in df['Gene Set'].values:
                if c not in gene_sets and c.lower() not in ignore:
                    gene_sets.append(c)

            # for c in df['Cluster'].values:
            #     if c not in cluster_sets:
            #         cluster_sets.append(c)

        cluster_sets = np.array(cluster_sets)

        gene_sets = np.array(gene_sets)

        d = np.zeros((cluster_sets.size, gene_sets.size), dtype=int)

        c = 1

        for f in files:
            df = pd.read_csv(f, sep='\t', header=0)

            for i in range(0, cluster_sets.size):
                for j in range(0, gene_sets.size):
                    # convert display to to cluster id
                    print(j, cluster_sets[i])
                    cid = clusters.display_id_to_id(cluster_sets[i])

                    #print(cid, cluster_sets[j])

                    d[i, j] += c if np.where((df['Gene Set'] == gene_sets[j]) & (
                        df['Cluster'] == 'C{}'.format(cid)))[0].size > 0 else 0

            c += 1

        

        #
        # heatmap
        #

        hy = y

        for i in range(0, cluster_sets.size):
            hx = x

            for j in range(0, gene_sets.size):
                v = d[i, j]

                if v == 1:
                    # svgplot.rgbatohex(mapper.to_rgba(v))
                    color = pathwaycolor[0]
                    self.add_rect(hx, hy, cell[0], cell[1], fill=color)
                elif v == 2:
                    # svgplot.rgbatohex(mapper.to_rgba(v))
                    color = pathwaycolor[1]
                    self.add_rect(hx, hy, cell[0], cell[1], fill=color)
                elif v == 3:
                    color = pathwaycolor[0]
                    self.add_rect(hx, hy, cell[0]/2, cell[1], fill=color)
                    color = pathwaycolor[1]
                    self.add_rect(hx+cell[0]/2, hy,
                                  cell[0]/2, cell[1], fill=color)
                else:
                    color = 'white'
                    self.add_rect(hx, hy, cell[0], cell[1], fill=color)

                hx += cell[0]

            hy += cell[1]

        if showgrid:
            self.add_grid(x=x,
                          y=y,
                          w=hx,
                          h=hy,
                          rows=d.shape[0],
                          cols=d.shape[1],
                          color=gridcolor)

        if showframe:
            self.add_frame(x=x, y=y, w=hx, h=hy)

        w = hx
        h = hy

        #
        # Label rows
        #

        self.heatmap_label_rows_ext(clusters,
                                np.array([cluster_sets]),
                                x=x+w-cell[1]+15,
                                y=y,
                                cell=cell,
                                modes=labelargs['mode'],
                                split=labelargs['split'],
                                orientation='v',
                                grouporientation=labelargs['grouporientation'],
                                showunclass=showunclass,
                                showsinglegroups=labelargs['showsinglegroups'])

        #
        # Row labels
        #

        if labelcols:
            hx = x + cell[0] / 2 #w + padding
            hy = y -20 #+ cell[1] / 2

            for gene_set in gene_sets:
                gene_set = gene_set.replace('HALLMARK', 'HM')
                gene_set = gene_set.replace('KEGG', 'KG')
                gene_set = gene_set.replace('_PATHWAY', '')
                #gene_set = gene_set.replace('RESPONSE', 'RESP')
                gene_set = gene_set.replace('SIGNALING', 'SIGNAL')
                #gene_set = gene_set.replace('PHOSPHORYLATION', 'PHOS')
                #gene_set = gene_set.replace('REPAIR', 'REP')
                #gene_set = gene_set.replace('REPLICATION', 'REP')
                gene_set = gene_set.replace('NUCLEOTIDE', 'NT')
                #gene_set = gene_set.replace('APOPTOSIS', 'APOPT')

                if labelcase == 'lower':
                    gene_set = gene_set.lower()

                if labelcase == 'upper':
                    gene_set = gene_set.upper()

                self.add_text_bb(gene_set, x=hx, y=hy, orientation='v')
                hx += cell[0]


        return (w, h)


    def cluster_label_rows(self,
                           row_labels,
                           clusters,
                           x=0,
                           y=0,
                           h=0,
                           w=svgplot.LABEL_COLOR_BLOCK_SIZE,
                           padding=5,
                           showgroups=True,
                           frame=True,
                           framecolor='white',
                           stroke=svgplot.STROKE_SIZE,
                           showlabels=True,
                           showblocks=True,
                           mingroupsize=2,
                           weight='normal',
                           invert_x=False,
                           align='left'):
        startx = x
        starty = y

        c = 0

        for group in row_labels:
            c += len(group['items'])

        yd = h / c

        y = 0

        if invert_x:
            x = startx + 30 - w
        else:
            x = startx - 30

        mtw = 0

        c = 0

        for group in row_labels:
            h = yd * len(group['items'])

            for item in group['items']:
                color = clusters.get_color(item)

                if showblocks:
                    self.add_rect(x, y, w, yd, fill=color)

                    if frame:
                        #self.add_frame(x, y, w, yd, color=framecolor)

                        if c > 0:
                            self.add_line(x1=x-padding,
                                          y1=y,
                                          x2=x+w+padding,
                                          y2=y,
                                          color=framecolor,
                                          stroke=stroke)

                if showlabels:
                    tw = self.get_string_width(item)

                    mtw = max(mtw, tw)

                    if align == 'left':
                        self.add_text_bb(item,
                                        x=x - tw - 10,
                                        y=y,
                                        h=yd,
                                        color=color)
                    else:
                        self.add_text_bb(item,
                                        x=x + w + 10,
                                        y=y,
                                        h=yd,
                                        color=color)

                y += yd

                c += 1

        if showgroups:
            y = starty + yd / 2

            for group in row_labels:
                n = len(group['items'])

                x = -mtw - 50
                h = (n - 1) * yd
                color = clusters.get_block_color(group['name'])

                if n > 1:
                    self.add_line(x,
                                  y - self.get_font_h() / 2 + padding / 2,
                                  x,
                                  y + h + self.get_font_h() / 2 - padding / 2,
                                  color=color)

#                self.add_line(x,
#                              y,
#                              x + svgplot.BRACKET_SIZE,
#                              y,
#                              color=color)
#
#                self.add_line(x,
#                              y + h,
#                              x + svgplot.BRACKET_SIZE,
#                              y + h,
#                              color=color)

                names = group['name'].split(' ')

                if group['name'] == 'Plasmablasts':
                    names = ['Plasma', 'blasts']

                if n >= mingroupsize:
                    if len(names) == 2:
                        tw = self.get_string_width(names[0])
                        self.add_text(names[0], x=x-60, y=y + h / 2 + tw/2, h=yd,
                                      color=color, rotate=-90, weight=weight)
                        tw = self.get_string_width(names[1])
                        self.add_text(names[1], x=x-20, y=y + h / 2 + tw/2, h=yd,
                                      color=color, rotate=-90, weight=weight)
                    else:
                        tw = self.get_string_width(group['name'])
                        self.add_text(names[0],
                                      x=x-20,
                                      y=y + h / 2 + tw/2,
                                      h=yd,
                                      color=color,
                                      rotate=-90,
                                      weight=weight)

                y += n * yd

    def cluster_label_cols(self,
                           row_labels,
                           clusters,
                           x=0,
                           y=0,
                           w=0,
                           h=15,
                           padding=5,
                           showgroups=True,
                           frame=True):
        c = 0

        for group in row_labels:
            c += len(group['items'])

        xd = w / c

        x = 0

        y = y + 20

        mtw = 0

        c = 0

        for group in row_labels:
            w = xd * len(group['items'])

            for item in group['items']:

                color = clusters.get_color(item)
                self.add_rect(x, y, xd, h, fill=color)

                if frame:
                    #self.add_frame(x, y, xd, h)

                    if c > 0:
                        self.add_line(x1=x, y1=y-padding, x2=x,
                                      y2=y+h+padding, color='white')

                tw = self.get_string_width(item)

                mtw = max(mtw, tw)

                self.add_text_bb(item,
                                 x=x,
                                 y=y + self.get_font_h() + padding,
                                 w=xd,
                                 color=color,
                                 align='c')

                x += xd

                c += 1

    def add_grid(self,
                 x=0,
                 y=0,
                 w=0,
                 h=0,
                 rows=0,
                 cols=0,
                 color=svgplot.GRID_COLOR,
                 stroke=svgplot.GRID_STROKE,
                 drawrows=True,
                 drawcols=True):
        """
        Add grid lines to a figure. Mostly used for enhancing heat maps.
        """

        startx = x
        starty = y

        dx = w / cols
        dy = h / rows

        if drawrows:
            #x += dx
            y += dy

            for i in range(1, rows):
                self.add_line(x1=x, y1=y, x2=x+w, y2=y,
                              color=color, stroke=stroke)

                y += dy

        if drawcols:
            y = starty
            x += dx

            for i in range(1, cols):
                self.add_line(x1=x, y1=y, x2=x, y2=y+h,
                              color=color, stroke=stroke)

                x += dx
