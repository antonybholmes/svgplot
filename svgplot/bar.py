from typing import Mapping, Optional, Union, Any
from .axis import Axis
from .svgfigure import SVGFigure
from . import svgfiguredraw
import numpy as np
import math
from . import graph
from . import hatch as phatch
from enum import Enum
import pandas

def add_barplot(svg: SVGFigure,
                data:pandas.DataFrame,
                x:str='x',
                y:str='y',
                hue:Optional[str] = None,
                order:Optional[list[str]] = None,
                hue_order:Optional[list[str]] = None,
                x_palette:dict[str, str] = {},
                hue_palette:dict[str, str] = {},
                pos:tuple[int, int] = (0, 0),
                height=400,
                bar_width=60,
                x_gap:int=10,
                hue_gap:int=0,
                bar_color='#cccccc',
                ylim=[0, 100],
                yticks=[0, 50, 100],
                xlabel='',
                ylabel='% cells',
                rename:dict[str, str] = {}):

    xp, yp = pos

    yaxis = Axis(lim=ylim, w=height)

    #w = means.size * block_size

    #xaxis = axis.Axis(lim=[0, df.shape[1]], w=w)

    y2 = yp + height

    if order is None:
      order = sorted(data[x].unique())

    order = np.array(order)

    if hue is None:
        hue = x
        hue_order = ['']
 
    if hue_order is None:
      hue_order = order #sorted(data[hue].unique())

    hue_order = np.array(hue_order)




    # draw bars

    x1 = xp

    for xo in order:
      print('xo', xo)
      dfx = data[data[x] == xo]

      color = ''
      hatch = 'solid'

      
      if xo in x_palette:
        p = x_palette[xo]
        if ':' in p:
          color, hatch = p.split(':')[0:2]
        else:
          color = p
      
      w = len(hue_order) * bar_width + (len(hue_order) - 1) * hue_gap

      svg.add_text_bb(rename.get(xo, xo), x=x1+w/2, y=y2, orientation='v', align='r')

      for ho in hue_order:
        if ho != '':
          dfh = dfx[dfx[hue] == ho]
        else:
          dfh = dfx

        mean = dfh[y].mean()
        sd = dfh[y].std()

        h = yaxis.scale(mean)
        sdh = yaxis.scale(sd)
        h1 = h - sdh
        h2 = h + sdh

        if ho in hue_palette:
          p = hue_palette[ho]

          if ':' in p:
            c1, hatch = p.split(':')[0:2]
          else:
            c1 = p

          if c1 != '':
            color = c1

          if color == '':
            color = bar_color

        y1 = y2 - h

        phatch.add_hatch(svg, x1, y1, bar_width, h, hatch=hatch, color=color)

        svg.add_rect(x1, y1, bar_width, h, color='black')

        x1 += bar_width + hue_gap
      
      x1 += x_gap

    graph.add_y_axis(svg, axis=yaxis, pos=(xp - x_gap, yp), ticks=yticks, label=ylabel)



def add_stacked_bar(svg: SVGFigure,
                    tables,
                    bar_colors={},
                    x=0,
                    y=0,
                    height=400,
                    bar_width=60,
                    bar_padding=10,
                    bar_color='#cccccc',
                    ylim=[0, 100],
                    yticks=[0, 50, 100],
                    xlabel='',
                    ylabel='% cells',
                    padding=10,
                    whisker=20,
                    as_pc=True):
    # self.set_font_size(svgplot.FIGURE_FONT_SIZE)

    if as_pc:
        pc_tables = [(t / t.sum(axis=0) * 100) for t in tables]
        yaxis = Axis(lim=[0, 100], w=height)
    else:
        pc_tables = tables
        yaxis = Axis(lim=ylim, w=height)

    block_size = bar_width + 2 * bar_padding

    #w = means.size * block_size

    #xaxis = axis.Axis(lim=[0, df.shape[1]], w=w)

    y2 = y + height

    # draw bars

    x1 = x + bar_padding

    for t in pc_tables:
        for c in range(0, t.shape[1]):
            y3 = y2
            for r in range(t.shape[0] - 1, -1, -1):
                h = yaxis.scale(t.iloc[r, c])
                y1 = y3 - h

                bar_name = str(t.index[r])

                if bar_name in bar_colors:
                    bar_color = bar_colors[bar_name]
                else:
                    bar_color = 'gray'

                svg.add_rect(x1, y1, bar_width, h, fill=bar_color)
                svg.add_rect(x1, y1, bar_width, h, color='black')
                y3 -= h
            x1 += block_size

    graph.add_y_axis(svg, axis=yaxis, pos=(0, 0), ticks=yticks, label=ylabel)
