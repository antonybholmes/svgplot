# -*- coding: utf-8 -*-
"""
Created on Sat May  8 21:12:57 2021

@author: Antony
"""
from typing import Mapping, Optional, Tuple, Union
import numpy as np
import pandas as pd
from . import core
from .svgfiguredraw import SVGFigureDraw
from .axis import Axis
import libplot
import matplotlib
from scipy.stats import zscore
import math
import lib10x


class SVGFigurePlot(SVGFigureDraw):
    def __init__(self,
                 file,
                 size: tuple[float, float] = (279, 216),
                 view: Optional[tuple[int, int]] = None, #(2790, 2160),
                 grid=(12, 12),
                 border=100):
        super().__init__(file,
                         size=size,
                         view=view,
                         grid=grid,
                         border=border)

    def dot_plot(self,
                 df_data,
                 df_coldata,
                 genes,
                 groups=[],
                 groupby='Phenotype',
                 use_zscore=True,
                 cmap=libplot.BWR2_CMAP,
                 vlim=[-0.5, 0.5],
                 min_exp=0,
                 fraction_groups=[0.25, 0.5, 0.75, 1],
                 dot_sizes=[8, 26],
                 x=0,
                 y=0,
                 gap=[40, 28],
                 title_offset=40,
                 linecolor='black',
                 show_row_labels=False,
                 show_col_labels=False,
                 label_colors={},
                 row_color="black",
                 frac_file="fractions.txt",
                 stroke=core.STROKE_SIZE,
                 showframe=True,
                 frac_filter=None,
                 mode='exp',
                 df_exp=None):
        # self.set_font_size(core.FIGURE_FONT_SIZE)
        
        if frac_filter is None:
            frac_filter = {g:0 for g in groups}

        data_mode = 'as.is'

        if df_exp is None:
            data_mode = 'calc'
            df_exp = df_data.copy()

        if not isinstance(groups[0], dict):
            groups = [{'name': 'All', 'items': groups}]

        genes = np.array(genes)

        ncols = np.sum([len(g['items']) for g in groups])

        #df_exp = df_exp.iloc[np.where(df_exp.sum(axis=1) > 0)[0], :]

        idx = []

        for g in genes:
            i = np.where(df_data.index == g)[0]

            if i.size > 0:
                i = i[0]
                idx.append(i)
            else:
                #print('ugh', g, i)
                pass

        
        df_data = df_data.iloc[idx, :]

        # make sure in same order
        idx = np.array([np.where(df_exp.index == g)[0][0] for g in df_data.index])
        df_exp = df_exp.iloc[idx, :]
        
        df_group_exp_avg = np.zeros((df_data.shape[0], ncols))

        i = 0
        colnames = []

        for group in groups:
            for g in group['items']:
                colnames.append(g)
                
                if data_mode == 'as.is':
                    idx = np.where(df_data.columns == g)[0][0]
                    m = df_data.iloc[:, idx].values
                else:
                    idx = np.where(df_coldata[groupby] == g)[0]
                    t = df_exp.iloc[:, idx]
                    m = t.mean(axis=1)
                
                df_group_exp_avg[:, i] = m
                i += 1

        colnames = np.array(colnames)

        z_group = zscore(df_group_exp_avg, axis=1)
        df_z_group = pd.DataFrame(z_group, index=df_exp.index, columns=colnames)

        

        #z = zscore(df_exp, axis=1)
        #df_z = pd.DataFrame(z, index=df_exp.index, columns=df_exp.columns)

        # custom z score based on klein, califano 2003 transcriptional analysis
        m = 0
        sd = 0
        for g in colnames:
            if data_mode == 'as.is':
                idx = np.where(df_data.columns == g)[0][0]
                m += df_data.iloc[:, idx].values
                sd += df_data.iloc[:, idx].values
            else:
                idx = np.where(df_coldata[groupby] == g)[0]    
                t = df_exp.iloc[:, idx].values
                m += np.mean(t, axis=1)
                sd += np.std(t, axis=1)
        
        m /= colnames.size 
        sd /= colnames.size

        z = df_data.subtract(m, axis=0).divide(sd, axis=0)
        df_z = pd.DataFrame(z, index=df_data.index, columns=df_data.columns)

        
        tables = {}
        fractions = {}

        c = 0
        for group in groups:
            for g in group['items']:
                idx = np.where(df_coldata[groupby] == g)[0]


                t = df_exp.iloc[:, idx]
                m = np.zeros(t.shape, dtype=int)
                m[t > min_exp] = 1
                f = np.sum(m, axis=1) / m.shape[1]
                fractions[g] = f

                if data_mode == 'as.is':
                    idx = np.where(df_data.columns == g)[0][0]
                    t = df_data.iloc[:, idx].values

                if use_zscore:
                    if mode == 'group':
                        tables[g] = df_z_group.iloc[:, c]
                    else:
                        tables[g] = np.mean(df_z.iloc[:, idx].values, axis=1)

                else:
                    tables[g] = t

                c += 1

        #
        # filter fractions
        #

        idx = np.array([], dtype=int) #range(0, df_data.shape[0]))

        
        print('filter 1', idx.size)
        

        for g in frac_filter:
            if g in fractions:
                print(g, fractions[g], fractions[g].size)
                idx = np.union1d(idx, np.where(fractions[g] >= frac_filter[g]))

        idx = np.sort(idx)
        
        print(idx)

        print('filter 2', idx.size)


        df_data = df_data.iloc[idx, :]
        df_exp = df_exp.iloc[idx, :]

        for g in fractions:
            fractions[g] = fractions[g][idx]
        
        for g in tables:
            tables[g] = tables[g][idx]

        norm=matplotlib.colors.Normalize(vmin=vlim[0], vmax=vlim[1])

        # sort

        fracs = fractions[colnames[0]]
        m = np.array([norm(x) for x in tables[colnames[0]]])

        s = 2 * m + fracs

        idx = np.argsort(s)[::-1]
        print(idx)

        # df_data = df_data.iloc[idx, :]
        # df_exp = df_exp.iloc[idx, :]

        # for g in fractions:
        #     fractions[g] = fractions[g][idx]
        
        # for g in tables:
        #     tables[g] = tables[g][idx]



        mapper = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)

        dot_range = dot_sizes[1] - dot_sizes[0]

        x1 = x

        

        #group_index = 0

        for group in groups:
            for g in group['items']:
                y1 = y

                m = tables[g]
                fracs = fractions[g]
                #m = t.mean(axis=1)

                if show_col_labels:
                    if g in label_colors:
                        color = label_colors[g]
                    else:
                        color = 'black'

                    self.add_text_bb(g, x1, y1 - title_offset,
                                     orientation='v', color=color)

                for gene_index in range(0, m.size):
                    #gene = t.index[gene_index]

                    v = m[gene_index]

                    print(g, gene_index, v)

                    # if use_zscore:
                    #    v = df_z.iloc[gene_index, group_index]
                    # else:
                    #    v = df_group_exp_avg[gene_index, group_index]

                    # use mean for color
                    # m[gene_index]))
                    color = core.rgbatohex(mapper.to_rgba(v))

                    dot_size = max(
                        dot_sizes[0], fracs[gene_index] * dot_sizes[1])

                    self.add_circle(x1, y1, dot_size,
                                    fill=color, color=linecolor, stroke=stroke)

                    #if group_index == ncols - 1 and show_row_labels:
                    #    self.add_text_bb(gene, x1+label_offset,
                    #                     y1, color=row_color)

                    y1 += gap[1]

                x1 += gap[0]

                #group_index += 1

            # add some separation between groups
            x1 += gap[0] / 2

        n = df_data.shape[0] - 1 #tables[0].shape[0] - 1
        # reverse labels as axis draw opposite to rendering direction
        yaxis = Axis(lim=[0, n], ticklabels=np.array(list(reversed(df_data.index.values))), w=n*gap[1])


        # plot gene names from Table 0 as all tables are the same
        if show_row_labels:
            self.add_y_axis(x=x1-gap[0],
                        y=y+yaxis.w,
                        axis=yaxis, 
                        showline=not showframe,
                        side='r',
                        tickcolor=row_color)
        
        #if showframe:
        #    self.add_rect(x=x-gap[0], y=y-gap[0], w=x1, h=yaxis.w+gap[0], color='black', stroke=core.AXIS_STROKE)

            #for gene in tables[0].index:
            #    self.add_text_bb(gene, x1+label_offset, y1, color=row_color)
            #    y1 += gap[1]

        y1 += 50

        x1 = x

        if len(fraction_groups) > 0:
            for f in fraction_groups:
                dot_size = max(dot_sizes[0], f * dot_sizes[1])
                self.add_circle(x1, y1, dot_size, fill='gray', color=linecolor)
                self.add_text_bb(str(int(f * 100)), x1,
                                 y1+title_offset, align='c')
                x1 += 50

            x1 += 50

            #self.add_num_colorbar_z(x=x1, y=y1, name='bwr2', z=1, align='l')

            #self.add_svg_colorbar(x=x1, y=y1, cmap=libplot.BWR2_CMAP, ticks=[0, 0.5, 1], ticklabels=[vlim[0], 0.0, vlim[1]], align='l')

        # self.set_font_size(core.DEFAULT_FONT_SIZE)

        tables = []
        for group in groups:
            df_frac = pd.DataFrame(index=df_data.index)
            for c in colnames:
                df_frac[c] = fractions[c]
            
            print(df_frac)

            #print(colnames, np.concatenate([fractions[g] for g in colnames]))
            #df_frac = pd.DataFrame(np.concatenate([fractions[g] for g in colnames], axis=1), index=genes, columns = colnames)
            df_frac *= 100
            tables.append(df_frac)

        df_frac = pd.concat(tables, axis=1)
        df_frac.round(2).to_csv(frac_file, sep='\t', header=True, index=True)

        return df_exp


    def dot_plot_legend(self,
                        x=0,
                        y=0,
                        fraction_groups=[0.25, 0.5, 0.75, 1],
                        dot_sizes=[8, 30],
                        linecolor='black'):

        x1 = x

        for f in fraction_groups:
            dot_size = max(dot_sizes[0], f * dot_sizes[1])
            self.add_circle(x1, y, dot_size, fill='gray', color=linecolor)
            self.add_text_bb('{}%'.format(int(f * 100)), x1,
                             y+dot_sizes[1]+10, align='c')
            x1 += 70

        # self.set_font_size(core.DEFAULT_FONT_SIZE)

    

    
            

    def add_lineplot(self,
                     data,
                     x=0,
                     y=0,
                     w=5,
                     h=None,
                     padding=core.TICK_SIZE,
                     xoffset=0,
                     stroke=4,
                     title='',
                     xlabel='',
                     ylabel='',
                     xlim=[0, 100],
                     ylim=[0, 100],
                     xticks=range(0, 110, 20),
                     yticks=range(0, 110, 20),
                     xticklabels=None,
                     yticklabels=None,
                     color='black'):
        """
        Add a gsea plot onto a page. This method adds axes labels to reduce
        scaling effect on fonts.

        Parametrers
        -----------
        file: str
            GSEA png plot to insert. It is assumed the plot contains no text
            and has been trimmed to remove whitespace.
        """

        if h is None:
            h = w

        xaxis = Axis(lim=xlim, w=w)
        yaxis = Axis(lim=ylim, w=h)

        # leading edge
        points = [
            [xoffset + xaxis.scale(d[0]), y + h - yaxis.scale(d[1])] for d in data]
        self.add_polyline(points, color=color,
                          stroke=stroke, fill_opacity=0.2)

        # label axes

        # if ymax > 0:
        #     ticks[2] = round(2 * ticks[1] - ticks[0], 1)
        # else:
        #     ticks[0] = round(2 * ticks[1] - ticks[2], 1)

        if title != '':
            self.add_text_bb(title, x=xoffset + w / 2, y=y-40, align='c')

        if xticks is not None:
            self.add_x_axis(x=xoffset,
                            y=y+h,
                            axis=xaxis,
                            ticks=xticks,
                            ticklabels=xticklabels,
                            padding=core.TICK_SIZE,
                            showticks=True)

        if xlabel != '':
            self.add_text_bb(xlabel, x=xoffset + w / 2, y=y+h+60, align='c')

        if yticks is not None:
            self.add_y_axis(x=xoffset,
                            y=y+h,
                            axis=yaxis,
                            ticks=yticks,
                            ticklabels=yticklabels,
                            padding=core.TICK_SIZE,
                            showticks=True)

        if ylabel != '':
            self.add_text_bb(ylabel, x=xoffset - 60, y=y +
                             h/2, align='c', orientation='v')

        return w, h


    


    def plot_heatmap(self,
                     df,
                     x=0,
                     y=0,
                     cell=[32, 32],
                     lim=[-3, 3],
                     splits=None,
                     block_gap=140,
                     indexmatch='Gene',
                     colmatch='fold change',  # 'tpm',
                     norm='none',  # 'z-score',
                     cmap=libplot.BWR2_CMAP,
                     gridcolor=core.GRID_COLOR,
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
            labelargs['rowfontsize'] = core.FIGURE_FONT_SIZE

        if norm == 'z-score':
            df_z = lib10x.scale(df)
            df_z.to_csv('z.txt', sep='\t', header=True, index=True)
            df_fc_clipped = df_z.copy()
        else:
            df_fc_clipped = df.copy()

        df_fc_clipped[df_fc_clipped > lim[1]] = lim[1]
        df_fc_clipped[df_fc_clipped < lim[0]] = lim[0]

        df1 = df_fc_clipped  # df_fc_clipped.iloc[:, 0:df_exp1.shape[1]]

        mapper = matplotlib.cm.ScalarMappable(norm=matplotlib.colors.Normalize(vmin=lim[0], vmax=lim[1]),
                                              cmap=cmap)

        #
        # heatmap
        #

        hx = x
        hy = y

        for i in range(0, df1.shape[0]):
            hx = x

            for j in range(0, df1.shape[1]):
                v = df1.iloc[i, j]
                color = core.rgbatohex(mapper.to_rgba(v))
                self.add_rect(hx, hy, cell[0], cell[1], fill=color)

                hx += cell[0]

            hy += cell[1]

        w = cell[0] * df1.shape[1]
        h = cell[1] * df1.shape[0]

        # labels

        hy = y + cell[1] / 2

        for i in range(0, df1.shape[0]):
            self.add_text_bb(df1.index[i], x=w+20, y=hy)
            hy += cell[1]

        hx = x + cell[0] / 2

        for i in range(0, df1.shape[1]):
            self.add_text_bb(df1.columns[i], x=hx, y=-30, orientation='v')
            hx += cell[1]

        if showgrid:
            self.add_grid(x=x,
                          y=y,
                          w=w,
                          h=h,
                          rows=df1.shape[0],
                          cols=df1.shape[1],
                          color=gridcolor)

        if showframe:
            self.add_frame(x=x, y=y, w=w, h=h)

        return (w, h)
