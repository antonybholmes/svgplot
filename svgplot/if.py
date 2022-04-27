import os
import pandas as pd
import numpy as np
from . import svgplot
from . import svgfigure
from . import graph
from . import axis
from matplotlib import cm


def add_if(svg,
           group,
           name,
           pos: tuple[int, int] = (0, 0),
           h=200,
           ih=None,
           color=svgplot.COLOR_BLACK,
           padding=5,
           iscale=0.5):
    x, y = pos

    if ih is None:
        ih = iscale * h

    nl = name.lower()

    dir = svgplot.find_if_dir(group)

    files = os.listdir(dir)

    img8x = None

    for file in files:
        if nl in file.lower() and '20X' not in file and (file.endswith('png') or file.endswith('jpg')):
            img8x = '{}/{}'.format(dir, file)

    if img8x is None:
        return

    dir = os.path.join(dir, 'scaled')

    files = os.listdir(dir)

    for file in files:
        if nl in file.lower() and '20X' in file and (file.endswith('png') or file.endswith('jpg')):
            img20x = '{}/{}'.format(dir, file)

    if img20x is None:
        return

    w = svgplot.scaled_image_w(img8x, h)

    svg.add_image(img8x, x=x, y=y, w=w)

    iw = svgplot.scaled_image_w(img20x, ih)

    nx = x + w + padding  # - (iw * (1 - iscale))
    ny = y + (h - ih)

    # svg.add_rect(nx-padding, ny-padding, iw + 2 *
    #              padding, ih + 2 * padding, fill='white')

    svg.add_image(img20x, x=nx, y=ny, w=iw)

    svg.add_text(name, x=x+w+20, y=2*svg.get_font_h() + 20, color=color)

#    def add_if_pairs(svg,
#               group,
#               name,
#               x=0,
#               y=0,
#               h=200,
#               ih=None,
#               color=svgplot.COLOR_BLACK,
#               padding=10,
#               iscale=0.35,
#               inset=0.1):
#        if ih is None:
#            ih = iscale * h
#
#        nl = name.lower()
#
#        dir = svgplot.find_if_pairs_dir(group)
#
#        files = os.listdir(dir)
#
#        img8x = None
#        img20x1 = None
#        img20x2 = None
#
#        print(dir)
#
#        for file in files:
#            if file.lower().startswith(nl) and '20X' not in file and (file.endswith('png') or file.endswith('jpg')):
#                img8x = '{}/{}'.format(dir, file)
#
#        if img8x is None:
#            return
#
#        dir = os.path.join(dir, 'scaled')
#
#        files = os.listdir(dir)
#
#        for file in files:
#            if file.lower().startswith(nl) and '20X' in file and '_1_' in file and (file.endswith('png') or file.endswith('jpg')):
#                img20x1 = '{}/{}'.format(dir, file)
#
#        if img20x1 is None:
#            return
#
#        for file in files:
#            if file.lower().startswith(nl) and '20X' in file and '_2_' in file and (file.endswith('png') or file.endswith('jpg')):
#                img20x2 = '{}/{}'.format(dir, file)
#
#        if img20x2 is None:
#            return
#
#        w = svgplot.scaled_image_w(img8x, h)
#
#        svg.add_image(img8x, x=x, y=y, w=w)
#
#        iw1 = svgplot.scaled_image_w(img20x1, ih)
#        iw2 = svgplot.scaled_image_w(img20x2, ih)
#        nx = x + w + padding #- w * inset  # - (iw * (1 - iscale))
#
#        ny = y + (h - 2 * ih - padding)
#
#        svg.add_rect(nx-padding,
#                      ny-padding,
#                      iw1 + 2 * padding,
#                      ih + 2 * padding,
#                      fill='white')
#
#        svg.add_image(img20x1, x=nx, y=ny, w=iw1)
#
#        ny = y + (h - ih)
#
#        svg.add_rect(nx-padding,
#                      ny-padding,
#                      iw1 + 2 * padding,
#                      ih + 2 * padding,
#                      fill='white')
#
#        svg.add_image(img20x2, x=nx, y=ny, w=iw2)
#
#
#        svg.add_text(name, x=x+w+20, y=svg.get_font_h() + 20, color=color)


def add_if_pairs(svg,
                 group,
                 name,
                 pos: tuple[int, int] = (0, 0),
                 h=200,
                 ih=None,
                 color=svgplot.COLOR_BLACK,
                 padding=10,
                 labelargs=None,
                 insertargs=None,
                 weight='normal'):
    x, y = pos

    if labelargs is None:
        labelargs = {}

    if 'position' not in labelargs:
        labelargs['position'] = 'bottom left'
    if 'inside' not in labelargs:
        labelargs['inside'] = True

    if insertargs is None:
        insertargs = {}

    if 'position' not in insertargs:
        insertargs['position'] = 'top right'
    if 'border' not in insertargs:
        insertargs['border'] = 2
    if 'scale' not in insertargs:
        insertargs['scale'] = 0.3

    if ih is None:
        ih = insertargs['scale'] * h

    nl = name.lower()

    dir = svgplot.find_if_pairs_dir(group)

    files = os.listdir(dir)

    img8x = None
    img20x1 = None
    img20x2 = None

    for file in files:
        if file.lower().startswith(nl) and '20X' not in file and (file.endswith('png') or file.endswith('jpg')):
            img8x = '{}/{}'.format(dir, file)

    if img8x is None:
        return

    dir = os.path.join(dir, 'scaled')

    files = os.listdir(dir)

    for file in files:
        if file.lower().startswith(nl) and '20X' in file and '_1_' in file and (file.endswith('png') or file.endswith('jpg')):
            img20x1 = '{}/{}'.format(dir, file)

    if img20x1 is None:
        return

    for file in files:
        if file.lower().startswith(nl) and '20X' in file and '_2_' in file and (file.endswith('png') or file.endswith('jpg')):
            img20x2 = '{}/{}'.format(dir, file)

    if img20x2 is None:
        return

    w = svgplot.scaled_image_w(img8x, h)

    if not labelargs['inside']:
        svg.add_text_bb(name, x=x, y=y, w=w, color=color, align='c')
        y += svg.get_font_h() + padding

    svg.add_image(img8x, x=x, y=y, w=w)

    if labelargs['inside']:
        position = labelargs['position'].split(' ')

        if len(position) == 0:
            position.append('bottom')
        if len(position) == 1:
            position.append('left')

        if position[0] == 'top':
            if position[1] == 'right':
                sw = svg.get_string_width(name, weight=weight)
                svg.add_text_bb(name,
                                x=x+w-sw-2*padding,
                                y=y+svg.get_font_h()+padding,
                                w=w,
                                color='white',
                                weight=weight)
            elif position[1] == 'left':
                svg.add_text_bb(name,
                                x=x+2*padding,
                                y=y+svg.get_font_h()+padding,
                                w=w,
                                color='white',
                                weight=weight)
            else:
                svg.add_text_bb(name,
                                x=x,
                                y=y+svg.get_font_h()+padding,
                                w=w,
                                color='white',
                                weight=weight,
                                align='c')
        else:
            if position[1] == 'right':
                sw = svg.get_string_width(name, weight=weight)
                svg.add_text_bb(name,
                                x=x+w-sw-2*padding,
                                y=y+h-svg.get_font_h()-padding,
                                w=w,
                                color='white',
                                weight=weight)
            else:
                svg.add_text_bb(name,
                                x=x+2*padding,
                                y=y+h-svg.get_font_h()-padding,
                                w=w,
                                color='white',
                                weight=weight)

    iw1 = svgplot.scaled_image_w(img20x1, ih)

    ih2 = svgplot.scaled_image_h(img20x2, iw1)

    position = insertargs['position'].split(' ')

    if len(position) == 0:
        position.append('top')
    if len(position) == 1:
        position.append('right')
    if len(position) == 2:
        position.append('vert')

    if position[0] == 'top':
        if position[1] == 'right':
            if 'vert' in position[2]:
                nx = x + w - iw1
                ny = y

                svg.add_rect(nx - insertargs['border'],
                             ny - insertargs['border'],
                             iw1 + 2 * insertargs['border'],
                             ih + 2 * insertargs['border'],
                             fill='white')
                svg.add_image(img20x1, x=nx, y=ny, w=iw1)

                ny += ih + insertargs['border']

                svg.add_rect(nx - insertargs['border'],
                             ny - insertargs['border'],
                             iw1 + 2 * insertargs['border'],
                             ih + 2 * insertargs['border'],
                             fill='white')

                svg.add_image(img20x2,
                              x=nx,
                              y=ny,
                              w=iw1)
            else:
                nx = x + w - 2 * iw1 - insertargs['border']
                ny = y

                svg.add_rect(nx - insertargs['border'],
                             ny - insertargs['border'],
                             iw1 + 2 * insertargs['border'],
                             ih + 2 * insertargs['border'],
                             fill='white')
                svg.add_image(img20x1, x=nx, y=ny, w=iw1)

                nx += iw1 + insertargs['border']

                svg.add_rect(nx - insertargs['border'],
                             ny - insertargs['border'],
                             iw1 + 2 * insertargs['border'],
                             ih + 2 * insertargs['border'],
                             fill='white')

                svg.add_image(img20x2,
                              x=nx,
                              y=ny,
                              w=iw1)
        else:
            if 'vert' in position[2]:
                nx = x
                ny = y

                svg.add_rect(nx - insertargs['border'],
                             ny - insertargs['border'],
                             iw1 + 2 * insertargs['border'],
                             ih + 2 * insertargs['border'],
                             fill='white')
                svg.add_image(img20x1, x=nx, y=ny, w=iw1)

                ny += ih + insertargs['border']

                svg.add_rect(nx - insertargs['border'],
                             ny - insertargs['border'],
                             iw1 + 2 * insertargs['border'],
                             ih + 2 * insertargs['border'],
                             fill='white')

                svg.add_image(img20x2,
                              x=nx,
                              y=ny,
                              w=iw1)
    else:
        y += h + insertargs['border']
        svg.add_image(img20x1, x=x, y=y, w=iw1)
        svg.add_image(img20x2, x=x+iw1+insertargs['border'], y=y, w=iw1)

    return (w, y)


def add_if_counts(svg, group, table, pos: tuple[int, int] = (0, 0), bar_width=80, padding=10):
    x, y = pos

    print(svgplot.find_if_file(group, table))

    df = pd.read_csv(svgplot.find_if_file(group, table),
                     sep='\t', header=0, index_col=0)

    means = df.mean(axis=0)
    sds = df.std(axis=0)

    w, h = svg.add_image(svgplot.find_if_file(group, 'bar_plot', sub='trimmed'),
                         x=x,
                         y=y,
                         w=bar_width * df.shape[1])

    svg.add_y_axis(x=x, y=h, w=h)

    xd = w / df.shape[1]
    yd = h / 100

    x = 0
    for i in range(0, df.shape[1]):
        y = h - means[i] * yd - sds[i] * yd - svg.get_font_h()

        svg.add_text_bb('{}%'.format(
            round(means[i], 1)), x=x, y=y, w=xd, align='c')

        x += xd

    rows = df.columns[0].replace('+', '').replace('-', '').split(' ')

    d = np.empty((len(rows), df.shape[1]), dtype=object)

    for j in range(0, df.shape[1]):
        names = df.columns[j].split(' ')

        for i in range(0, len(names)):
            name = names[i]

            if '+' in name:
                d[i, j] = '+'
            else:
                d[i, j] = '-'

    svg.inc(y=380)

    svg.set_font_size(svgplot.DEFAULT_FONT_SIZE)

    for i in range(0, len(rows)):
        svg.add_text_bb(rows[i], x=-20, align='r')

        x1 = 0

        for j in range(0, df.shape[1]):
            svg.add_text_bb(d[i, j], x=x1, w=xd, align='c')
            #svg.add_frame(x, 0, xd, 20, color='red')
            x1 += xd

        svg.inc(y=svg.get_font_h() + 10)


def add_if_plot(svg,
                group,
                table,
                pos: tuple[int, int] = (0, 0),
                h=400,
                bar_width=60,
                bar_padding=10,
                bar_color='#cccccc',
                ylim=[0, 100],
                padding=10,
                whisker=20,
                tick_size=svgplot.TICK_SIZE):
    x, y = pos

    df = pd.read_csv(svgplot.find_if_file(group, table),
                     sep='\t', header=0, index_col=0)

    means = df.mean(axis=0)
    sds = df.std(axis=0)

    block_size = bar_width + 2 * bar_padding

    #w = means.size * block_size

    #xaxis = axis.Axis(lim=[0, df.shape[1]], w=w)
    yaxis = axis.Axis(lim=ylim, w=h)

    y2 = y + h

    # draw bars

    x1 = x + bar_padding

    for i in range(0, means.size):
        y1 = y2 - yaxis.scale(means[i])

        svg.add_rect(x1, y1, bar_width, y2 - y1 + 1, fill=bar_color)
        svg.add_rect(x1, y1, bar_width, y2 - y1 + 1, color='black')

        x1 += block_size

    # draw sd

    x1 = x + bar_padding + bar_width / 2

    for i in range(0, means.size):
        y1 = y2 - yaxis.scale(means[i])

        ysd = yaxis.scale(sds[i])

        yb1 = y1 - ysd

        # stop bars dropping below x axis
        yb2 = min(y2, y1 + ysd)

        svg.add_line(x1=x1, y1=yb1, x2=x1, y2=yb2)

        xb1 = x1 - whisker / 2
        xb2 = xb1 + whisker

        svg.add_line(x1=xb1, y1=yb1, x2=xb2, y2=yb1)

        if (y1 + ysd) < y2 - 20:
            svg.add_line(x1=xb1, y1=yb2, x2=xb2, y2=yb2)

        x1 += block_size

    graph.add_y_axis(svg, axis=yaxis, y=y+h, ticks=[0, 50, 100], label='% cells')

    # draw xaxis
    svg.add_line(x1=x, y1=y+h, x2=x + df.shape[1] * block_size, y2=y+h)

    x1 = x
    for i in range(0, df.shape[1]):
        y1 = h - yaxis.scale(means[i]) - yaxis.scale(sds[i]) - svg.get_font_h()

        svg.add_text_bb('{}%'.format(
            round(means[i], 1)), x=x1, y=y1, w=block_size, align='c')

        x1 += block_size

    rows = df.columns[0].replace('+', '').replace('-', '').split(' ')

    d = np.empty((len(rows), df.shape[1]), dtype=object)

    for j in range(0, df.shape[1]):
        names = df.columns[j].split(' ')

        for i in range(0, len(names)):
            name = names[i]

            if '+' in name:
                d[i, j] = '+'
            else:
                d[i, j] = '-'

    svg.inc(y=y2 + 50)

    svg.set_font_size(svgplot.DEFAULT_FONT_SIZE)

    for i in range(0, len(rows)):
        svg.add_text_bb(rows[i], x=0, align='r')

        x1 = 0

        for j in range(0, df.shape[1]):
            svg.add_text_bb(d[i, j], x=x1, w=block_size, align='c')
            #svg.add_frame(x, 0, xd, 20, color='red')
            x1 += block_size

        svg.inc(y=svg.get_font_h() + 10)


def add_if_pairs_plot(svg,
                      group,
                      table,
                      pos: tuple[int, int] = (0, 0),
                      h=400,
                      bar_width=40,
                      bar_padding=10,
                      bar_colors=None,
                      ylim=[0, 60],
                      yticks=[0, 20, 40, 60, 80, 100],
                      padding=10,
                      whisker=12,
                      tick_size=svgplot.TICK_SIZE,
                      bar_border_color=None,
                      stroke=3):
    x, y = pos

    if bar_colors is None:
        bar_colors = [svgplot.rgbatohex(cm.get_cmap('Paired')(0)),
                      svgplot.rgbatohex(cm.get_cmap('Paired')(1))]
        # bar_colors = ['#cccccc','#808080']

    df = pd.read_csv(svgplot.find_if_pairs_file(group, table),
                     sep='\t', header=0, index_col=0)

    means = df.mean(axis=0)
    sds = df.std(axis=0)

    #w = means.size * block_size

    #xaxis = axis.Axis(lim=[0, df.shape[1]], w=w)
    yaxis = axis.Axis(lim=ylim, w=h)

    y2 = y + h

    # draw bars

    x1 = x + bar_padding

    for i in range(0, means.size):
        y1 = y2 - yaxis.scale(means[i])

        fill = bar_colors[0] if i % 2 == 0 else bar_colors[1]

        svg.add_rect(x1, y1, bar_width, y2 - y1 + 1, fill=fill)

        if bar_border_color is not None:
            svg.add_rect(x1, y1, bar_width, y2 - y1, color=bar_border_color)

        x1 += bar_width + (2 * bar_padding if i % 2 == 1 else 0)

    # draw sd

    x1 = x + bar_padding + bar_width / 2

    for i in range(0, means.size):
        fill = bar_colors[0] if i % 2 == 0 else bar_colors[1]

        y1 = y2 - yaxis.scale(means[i])

        ysd = yaxis.scale(sds[i])

        yb1 = y1 - ysd

        # stop bars dropping below x axis
        yb2 = min(y2, y1 + ysd)  # y1

        # color=fill, stroke=stroke)
        svg.add_line(x1=x1, y1=yb1, x2=x1, y2=yb2, stroke=stroke)

        xb1 = x1 - whisker / 2
        xb2 = xb1 + whisker

        # color=fill, stroke=stroke)
        svg.add_line(x1=xb1, y1=yb1, x2=xb2, y2=yb1, stroke=stroke)

        if (y1 + ysd) < y2 - 10:
            svg.add_line(x1=xb1, y1=yb2, x2=xb2, y2=yb2, stroke=stroke)

        x1 += bar_width + (2 * bar_padding if i % 2 == 1 else 0)

    svg.add_y_axis(axis=yaxis, y=y+h, ticks=yticks, label='% cells')

    # draw xaxis
    svg.add_line(x1=x,
                 y1=y+h,
                 x2=x + padding + 2 * padding *
                 (df.shape[1] / 2 - 1) + bar_width * df.shape[1],
                 y2=y+h)

    # mean labels

    x1 = x + padding
    for i in range(0, df.shape[1]):
        fill = bar_colors[0] if i % 2 == 0 else bar_colors[1]

        y1 = h - yaxis.scale(means[i]) - yaxis.scale(sds[i]) - svg.get_font_h()

        p = round(means[i], 1)

        if p > 1:
            p = int(p)

        #svg.add_text_bb('{}%'.format(p), x=x1, y=y1, w=bar_width, align='c')
        svg.add_text_bb('{}'.format(p), x=x1, y=y1, w=bar_width, align='c')

        x1 += bar_width + (2 * bar_padding if i % 2 == 1 else 0)

    rows = df.columns[0].replace('+', '').replace('-', '').split(';')

    d = np.empty((len(rows), df.shape[1]), dtype=object)

    for j in range(0, df.shape[1]):
        names = df.columns[j].split(';')

        for i in range(0, len(names)):
            name = names[i]

            if '+' in name:
                d[i, j] = '+'
            else:
                d[i, j] = '-'

    svg.inc(y=y2 + 50)

    for i in range(0, len(rows)):
        svg.add_text_bb(rows[i], x=0, align='r')

        x1 = padding

        for j in range(0, df.shape[1]):
            svg.add_text_bb(d[i, j], x=x1, w=bar_width, align='c')
            ##svg.add_frame(x1, y, bar_width, 20, color='red')
            x1 += bar_width + (2 * bar_padding if j % 2 == 1 else 0)

        svg.inc(y=svg.get_font_h() + 10)


def if_arrow(svg: svgfigure.SVGFigure,
             pos: tuple[float, float] = (0, 0),
             color=None,
             fill='white',
             rotate=None):
    """
    Creates a large arrow for highlighting items

    Args:
    x: float, optional
        x location
    y: float, optional
        y location
    color: str, optional
        Hex color
    fill: str, optional
        Hex fill color
    rotate: int, optional
        Degree of rotation anticlockwise where
        3 oclock/east = 0 degrees
    """

    x, y = pos

    points = [(0, -5),
              (20, -5),
              (20, -15),
              (40, 0),
              (20, 15),
              (20, 5),
              (0, 5)]

    return svg.trans(svg.rot(svg.base_polygon(points, color=color, fill=fill), rotate=rotate),
                     x=x, y=y)


def add_if_arrow(svg: svgfigure.SVGFigure,
                 x=0,
                 y=0,
                 color=None,
                 fill='white',
                 rotate=None):
    """
    Add a large arrow for highlighting items to svg canvas.

    Parameters
    ----------
    x: float, optional
        x location
    y: float, optional
        y location
    color: str, optional
        Hex color
    fill: str, optional
        Hex fill color
    rotate: int, optional
        Degree of rotation anticlockwise where
    """

    svg.add(svg.if_arrow(x=x, y=y, color=color, fill=fill, rotate=rotate))


def add_if_plot_v2(svg,
                   dir,
                   name,
                   x=0,
                   y=0,
                   w=200,
                   h=None,
                   color=svgplot.COLOR_BLACK,
                   padding=10,
                   labelargs={},
                   insertargs={},
                   scalebarargs={},
                   frame=False,
                   weight='normal'):
    if labelargs is None:
        labelargs = {}

    if 'position' not in labelargs:
        labelargs['position'] = 'bottom left'
    if 'inside' not in labelargs:
        labelargs['inside'] = True

    if insertargs is None:
        insertargs = {}

    if 'position' not in insertargs:
        insertargs['position'] = 'top right vertical inside'
    if 'border' not in insertargs:
        insertargs['border'] = 4
    if 'scale' not in insertargs:
        insertargs['scale'] = 0.27

    if scalebarargs is None:
        scalebarargs = {}

    if 'position' not in scalebarargs:
        scalebarargs['position'] = 'top right'
    if 'scale' not in scalebarargs:
        scalebarargs['scale'] = '100 um'

    scalebarargs['bar-image-scale'] = 158 / 1046

    nl = name.lower()

    files = os.listdir(dir)

    # order by jpg and png first

    tmp = []

    for file in files:
        if file.endswith('jpg'):
            tmp.append(file)

    for file in files:
        if file.endswith('png'):
            tmp.append(file)

    files = tmp

    img8x = None
    img20x1 = None
    img20x2 = None
    img20x3 = None

    # print(files)

    for file in files:
        if file.lower().startswith(nl) and '20X' not in file and (file.endswith('png') or file.endswith('jpg')):
            img8x = '{}/{}'.format(dir, file)
            break

    if img8x is None:
        return

    if h is not None:
        w = svgplot.scaled_image_w(img8x, h)
    else:
        h = svgplot.scaled_image_h(img8x, w)

    if 'w' not in insertargs:
        insertargs['w'] = w * insertargs['scale']

    iw = insertargs['w']

    h1 = -1
    h2 = -1
    h3 = -1

    for file in files:
        if file.lower().startswith(nl) and '_1.' in file and (file.endswith('png') or file.endswith('jpg')):
            img20x1 = '{}/{}'.format(dir, file)
            h1 = svgplot.scaled_image_h(img20x1, iw)
            break

    for file in files:
        if file.lower().startswith(nl) and '_2.' in file and (file.endswith('png') or file.endswith('jpg')):
            img20x2 = '{}/{}'.format(dir, file)
            h2 = svgplot.scaled_image_h(img20x2, iw)
            break

    for file in files:
        if file.lower().startswith(nl) and '_3.' in file and (file.endswith('png') or file.endswith('jpg')):
            img20x3 = '{}/{}'.format(dir, file)
            h3 = svgplot.scaled_image_h(img20x3, iw)
            break

    if not labelargs['inside']:
        svg.add_text_bb(name, x=x, y=y, w=w, color=color, align='c')
        y += svg.get_font_h() + padding

    print(img8x)
    svg.add_image(img8x, x=x, y=y, w=w)

    if labelargs['inside']:
        position = labelargs['position'].split(' ')

        if len(position) == 0:
            position.append('bottom')
        if len(position) == 1:
            position.append('left')

        if position[0] == 'top':
            if position[1] == 'right':
                sw = svg.get_string_width(name, weight=weight)
                svg.add_text_bb(name,
                                x=x+w-sw-padding,
                                y=y+svg.get_font_h()+padding,
                                w=w,
                                color='white',
                                weight=weight)
            elif position[1] == 'left':
                svg.add_text_bb(name,
                                x=x+padding,
                                y=y+svg.get_font_h()+padding,
                                w=w,
                                color='white',
                                weight=weight)
            else:
                svg.add_text_bb(name,
                                x=x,
                                y=y+svg.get_font_h()+padding,
                                w=w,
                                color='white',
                                weight=weight,
                                align='c')
        else:
            if position[1] == 'right':
                sw = svg.get_string_width(name, weight=weight)
                svg.add_text_bb(name,
                                x=x+w-sw-padding,
                                y=y+h-svg.get_font_h(),
                                w=w,
                                color='white',
                                weight=weight)
            else:
                svg.add_text_bb(name,
                                x=x+padding,
                                y=y+h-svg.get_font_h(),
                                w=w,
                                color='white',
                                weight=weight)

    if frame:
        svg.add_frame(x, y, w, h)

    position = insertargs['position'].split(' ')

    if len(position) == 0:
        position.append('top')
    if len(position) == 1:
        position.append('right')
    if len(position) == 2:
        position.append('vert')
    if len(position) == 3:
        position.append('inside')

    print(position)

    if position[0] == 'top':
        if position[1] == 'right':
            if 'vert' in position[2]:
                if 'inside' in position[3]:
                    nx = x + w - iw  # - insertargs['border']
                else:
                    nx = x + w + 1.1 * insertargs['border']

                ny = y

                if img20x1 is not None:
                    if 'inside' in position[3]:
                        svg.add_rect(nx - insertargs['border'],
                                     ny - 2 * insertargs['border'],
                                     iw + 3 * insertargs['border'],
                                     h1 + 3 * insertargs['border'],
                                     fill='white')

                    svg.add_image(img20x1, x=nx, y=ny, w=iw)

                    ny += h1 + insertargs['border']

                if img20x2 is not None:
                    if 'inside' in position[3]:
                        svg.add_rect(nx - insertargs['border'],
                                     ny - insertargs['border'],
                                     iw + 2 * insertargs['border'],
                                     h2 + 2 * insertargs['border'],
                                     fill='white')

                    svg.add_image(img20x2, x=nx, y=ny, w=iw)

                    ny += h2 + insertargs['border']

                if img20x3 is not None:
                    if 'inside' in position[3]:
                        svg.add_rect(nx - insertargs['border'],
                                     ny - insertargs['border'],
                                     iw + 2 * insertargs['border'],
                                     h3 + 2 * insertargs['border'],
                                     fill='white')

                    svg.add_image(img20x3, x=nx, y=ny, w=iw)

                    ny += h3 + insertargs['border']
    else:
        if position[1] == 'right':
            if 'vert' in position[2]:
                if 'inside' in position[3]:
                    nx = x + w - iw  # - insertargs['border']
                else:
                    nx = x + w + insertargs['border']

                ny = y + h + insertargs['border']

                if img20x1 is not None:
                    ny -= h1 + insertargs['border']

                if img20x2 is not None:
                    ny -= h2 + insertargs['border']

                if img20x3 is not None:
                    ny -= h3 + insertargs['border']

                if img20x1 is not None:
                    if 'inside' in position[3]:
                        bw = 3 if img20x2 is None and img20x3 is None else 2
                        svg.add_rect(nx - insertargs['border'],
                                     ny - insertargs['border'],
                                     iw + bw * insertargs['border'],
                                     h1 + 3 * insertargs['border'],
                                     fill='white')

                    svg.add_image(img20x1, x=nx, y=ny, w=iw)

                    ny += h1 + insertargs['border']

                if img20x2 is not None:
                    if 'inside' in position[3]:
                        bw = 3 if img20x3 is None else 2
                        svg.add_rect(nx - insertargs['border'],
                                     ny - insertargs['border'],
                                     iw + bw * insertargs['border'],
                                     h2 + 3 * insertargs['border'],
                                     fill='white')

                    svg.add_image(img20x2, x=nx, y=ny, w=iw)

                    ny += h2 + insertargs['border']

                if img20x3 is not None:
                    if 'inside' in position[3]:
                        svg.add_rect(nx - insertargs['border'],
                                     ny - insertargs['border'],
                                     iw + 3 * insertargs['border'],
                                     h3 + 3 * insertargs['border'],
                                     fill='white')

                    svg.add_image(img20x3, x=nx, y=ny, w=iw)

                    ny += h3 + insertargs['border']
            else:
                if 'inside' in position[3]:
                    nx = x + w - insertargs['border']

                    if img20x1 is not None:
                        nx -= iw
                    if img20x2 is not None:
                        nx -= iw
                    if img20x3 is not None:
                        nx -= iw

                    ny = y + w - max(h1, max(h2, h3))

                    if img20x1 is not None:
                        if 'inside' in position[3]:
                            bw = 3 if img20x2 is None and img20x3 is None else 2
                            svg.add_rect(nx - insertargs['border'],
                                         ny - insertargs['border'],
                                         iw + bw * insertargs['border'],
                                         h1 + 3 * insertargs['border'],
                                         fill='white')

                        svg.add_image(img20x1, x=nx, y=ny, w=iw)

                        nx += iw + insertargs['border']

                    if img20x2 is not None:
                        if 'inside' in position[3]:
                            bw = 3 if img20x3 is None else 2
                            svg.add_rect(nx - insertargs['border'],
                                         ny - insertargs['border'],
                                         iw + bw * insertargs['border'],
                                         h2 + 3 * insertargs['border'],
                                         fill='white')

                        svg.add_image(img20x2, x=nx, y=ny, w=iw)

                        nx += iw + insertargs['border']

                    if img20x3 is not None:
                        if 'inside' in position[3]:
                            svg.add_rect(nx - insertargs['border'],
                                         ny - insertargs['border'],
                                         iw + 3 * insertargs['border'],
                                         h3 + 3 * insertargs['border'],
                                         fill='white')

                        svg.add_image(img20x3, x=nx, y=ny, w=iw)

                        nx += iw + insertargs['border']

    #
    # Scale bar
    #

    position = scalebarargs['position'].split(' ')

    if len(position) == 0:
        position.append('top')
    if len(position) == 1:
        position.append('right')

    print(position)

    sw = w * scalebarargs['bar-image-scale']

    if position[0] == 'top':
        ny = y + svg.get_font_h() + insertargs['border']

        if position[1] == 'right':
            nx = x + w - sw - 6 * insertargs['border']

            svg.add_text_bb(
                scalebarargs['scale'], x=nx+sw/2, y=ny, align='c', color='white', weight=weight)

            ny += 20

            svg.add_line(x1=nx, y1=ny, x2=nx+sw, y2=ny,
                         color='white', stroke=3)

            svg.add_line(x1=nx, y1=ny-5, x2=nx, y2=ny +
                         5, color='white', stroke=3)
            svg.add_line(x1=nx+sw, y1=ny-5, x2=nx+sw,
                         y2=ny+5, color='white', stroke=3)
        elif position[1] == 'left':
            nx = x + 6 * insertargs['border']

            svg.add_text_bb(
                scalebarargs['scale'], x=nx+sw/2, y=ny, align='c', color='white', weight=weight)

            ny += 20

            svg.add_line(x1=nx, y1=ny, x2=nx+sw, y2=ny,
                         color='white', stroke=3)

            svg.add_line(x1=nx, y1=ny-5, x2=nx, y2=ny +
                         5, color='white', stroke=3)
            svg.add_line(x1=nx+sw, y1=ny-5, x2=nx+sw,
                         y2=ny+5, color='white', stroke=3)
        else:
            pass
    elif position[0] == 'bottom':
        ny = y + h - svg.get_font_h() - 20

        if position[1] == 'right':
            nx = x + w - sw - 6 * insertargs['border']

            svg.add_text_bb(
                scalebarargs['scale'], x=nx+sw/2, y=ny, align='c', color='white', weight=weight)

            ny += 20

            svg.add_line(x1=nx, y1=ny, x2=nx+sw, y2=ny,
                         color='white', stroke=3)

            svg.add_line(x1=nx, y1=ny-5, x2=nx, y2=ny +
                         5, color='white', stroke=3)
            svg.add_line(x1=nx+sw, y1=ny-5, x2=nx+sw,
                         y2=ny+5, color='white', stroke=3)
        elif position[1] == 'left':
            nx = x + 6 * insertargs['border']

            svg.add_text_bb(
                scalebarargs['scale'], x=nx+sw/2, y=ny, align='c', color='white', weight=weight)

            ny += 20

            svg.add_line(x1=nx, y1=ny, x2=nx+sw, y2=ny,
                         color='white', stroke=3)

            svg.add_line(x1=nx, y1=ny-5, x2=nx, y2=ny +
                         5, color='white', stroke=3)
            svg.add_line(x1=nx+sw, y1=ny-5, x2=nx+sw,
                         y2=ny+5, color='white', stroke=3)
        else:
            pass
    else:
        pass

    return (w, h)


def add_if_counts_v2(svg,
                     dir,
                     x=0,
                     y=0,
                     h=250,
                     bar_width=32,
                     bar_gap=10,
                     bar_colors=None,
                     ylim=[0, 80],
                     yticks=[0, 20, 40, 60, 80, 100],
                     padding=10,
                     whisker=16,
                     tick_size=svgplot.TICK_SIZE,
                     bar_border_color=None,  # 'black',
                     stroke=3,
                     ytitle='% cells'):

    if bar_border_color is None:
        bar_border_color = [svgplot.rgbatohex(cm.get_cmap('tab20c')(0)),
                            svgplot.rgbatohex(cm.get_cmap('tab20c')(4)),
                            svgplot.rgbatohex(cm.get_cmap('tab20c')(8)),
                            svgplot.rgbatohex(cm.get_cmap('tab20c')(12))]

        bar_border_color = ['black']

    if bar_colors is None:
        #            bar_colors = [svgplot.rgbatohex(cm.get_cmap('tab20c')(18)),
        #                          svgplot.rgbatohex(cm.get_cmap('Paired')(0))]
        #
        #            bar_colors = [svgplot.rgbatohex(cm.get_cmap('tab20c')(3)),
        #                          svgplot.rgbatohex(cm.get_cmap('tab20c')(3 + 4)),
        #                          svgplot.rgbatohex(cm.get_cmap('tab20c')(3 + 8)),
        #                          svgplot.rgbatohex(cm.get_cmap('tab20c')(3 + 12))]

        bar_colors = [svgplot.rgbatohex(cm.get_cmap('tab20c')(2))]

        # bar_colors = ['#cccccc','#808080']

    print(os.path.join(dir, 'table.txt'))
    df = pd.read_csv(os.path.join(dir, 'table.txt'),
                     sep='\t', header=0, index_col=0)

    means = df.mean(axis=0)
    sds = df.std(axis=0)

    #w = means.size * block_size

    #xaxis = axis.Axis(lim=[0, df.shape[1]], w=w)
    yaxis = axis.Axis(lim=ylim, w=h)

    y2 = y + h

    block_width = bar_width + 2 * bar_gap

    # draw bars

    x1 = x + bar_gap

    for i in range(0, means.size):
        y1 = y2 - yaxis.scale(means[i])

        #fill = bar_colors[0]

        svg.add_rect(x1,
                     y1,
                     bar_width,
                     y2 - y1 + 1,
                     fill=bar_colors[i % len(bar_border_color)])

        if bar_border_color is not None:
            #                svg.add_rect(x1,
            #                              y1,
            #                              bar_width,
            #                              y2 - y1 - stroke / 4,
            #                              color=bar_border_color[i % len(bar_border_color)],
            #                              stroke=stroke)

            svg.add_line(x1=x1,
                         y1=y1-stroke/2,
                         x2=x1,
                         y2=y2,
                         color=bar_border_color[i % len(bar_border_color)],
                         stroke=stroke)

            svg.add_line(x1=x1+bar_width,
                         y1=y1-stroke/2,
                         x2=x1+bar_width,
                         y2=y2,
                         color=bar_border_color[i % len(bar_border_color)],
                         stroke=stroke)

            svg.add_line(x1=x1,
                         y1=y1,
                         x2=x1+bar_width,
                         y2=y1,
                         color=bar_border_color[i % len(bar_border_color)],
                         stroke=stroke)

        x1 += block_width

    # draw sd

    x1 = x + bar_gap + bar_width / 2

    for i in range(0, means.size):
        #fill = bar_colors[0] if i % 2 == 0 else bar_colors[1]

        y1 = y2 - yaxis.scale(means[i])

        ysd = yaxis.scale(sds[i])

        yb1 = y1 - ysd

        # stop bars dropping below x axis
        yb2 = y1  # min(y2, y1 + ysd) #y1

        svg.add_line(x1=x1,
                     y1=yb1,
                     x2=x1,
                     y2=yb2,
                     color=bar_border_color[i % len(bar_border_color)],
                     stroke=stroke)

        xb1 = x1 - whisker / 2
        xb2 = xb1 + whisker

        svg.add_line(x1=xb1,
                     y1=yb1,
                     x2=xb2,
                     y2=yb1,
                     color=bar_border_color[i % len(bar_border_color)],
                     stroke=stroke)
#
#            if (y1 + ysd) < y2 - 10:
#                svg.add_line(x1=xb1,
#                              y1=yb2,
#                              x2=xb2,
#                              y2=yb2,
#                              color=bar_border_color,
#                              stroke=stroke)

        x1 += block_width

    graph.add_y_percent_axis(svg, axis=yaxis, y=y+h, ticks=yticks, label=ytitle)

    # draw xaxis
    svg.add_line(x1=x-svgplot.AXIS_STROKE/2,
                 y1=y+h,
                 x2=x + block_width * df.shape[1],
                 y2=y+h,
                 stroke=svgplot.AXIS_STROKE)

    # mean labels

    x1 = x + padding
    for i in range(0, df.shape[1]):
        y1 = h - yaxis.scale(means[i]) - yaxis.scale(sds[i]) - svg.get_font_h()

        # if means[i] >= 1:
        p = int(round(means[i], 0))
        # else:
        #   p = round(means[i], 1)

        print(means[i], p)

        #svg.add_text_bb('{}%'.format(p), x=x1, y=y1, w=bar_width, align='c')
        svg.add_text_bb('{}'.format(p), x=x1, y=y1, w=bar_width, align='c')

        x1 += block_width

    # svg.set_font_size(svgplot.DEFAULT_FONT_SIZE)

    # annotations

    rows = df.columns[0].replace('+', '').replace('-', '').split(';')

    d = np.empty((len(rows), df.shape[1]), dtype=object)

    for j in range(0, df.shape[1]):
        if ';' in df.columns[j]:
            names = df.columns[j].split(';')
        else:
            names = df.columns[j].split(' ')

        for i in range(0, len(names)):
            name = names[i]

            if '+' in name:
                d[i, j] = '+'
            else:
                d[i, j] = '-'

    svg.inc(y=y2 + 40)

    # svg.set_font_size(svgplot.DEFAULT_FONT_SIZE)

    for i in range(0, len(rows)):
        svg.add_text_bb(rows[i], x=0, align='r')

        x1 = padding

        for j in range(0, df.shape[1]):
            svg.add_text_bb(d[i, j], x=x1, w=bar_width, align='c')
            ##svg.add_frame(x1, y, bar_width, 20, color='red')
            x1 += block_width

        svg.inc(y=svg.get_font_h() + 10)
