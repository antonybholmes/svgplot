from typing import List, Optional, Union
from . import svgplot
from .svgfigurebase import SVGFigureBase
from .axis import Axis

import re
import numpy as np
import json
import matplotlib
import math

"""
Add features for drawing to base class
"""

PIE_START_ANGLE = 3 / 2 * math.pi
TWO_PI_RADS = 2 * math.pi


class SVGFigureDraw(SVGFigureBase):
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

    def arc(self,
            angle1=0,
            angle2=0,
            x=0,
            y=0,
            w=200,
            h=200,
            color='black',
            fill='red',
            stroke=svgplot.STROKE_SIZE):

        # angle1 = math.pi/4 #- PIE_START_ANGLE
        # angle2 = math.pi/4 # - PIE_START_ANGLE

        r = w / 2

        x2 = r * math.sin(angle2 / 360 * TWO_PI_RADS)
        y2 = -r * math.cos(angle2 / 360 * TWO_PI_RADS)

        large_arc = 1 if angle2 - angle1 >= 180 else 0

        return self.rot_trans(self._svg.path(d=f"M 0 -{r} A {r} {r} 0 {large_arc} 1 {x2} {y2} L 0 0 Z",
                                             style=SVGFigureDraw.polygon_params(color=color, fill=fill, stroke=stroke)),
                              x=x,
                              y=y,
                              rotate=(angle1, 0, 0))

    def add_arc(self,
                angle1=0,
                angle2=0,
                x=0,
                y=0,
                w=200,
                h=200,
                color='black',
                fill='red',
                stroke=1):
        self.add(self.arc(angle1=angle1, angle2=angle2, x=x, y=y,
                 w=w, h=h, color=color, fill=fill, stroke=stroke))

    def line(self,
             x1:float=0,
             y1:float=0,
             x2:Optional[float]=None,
             y2:Optional[float]=None,
             color:str='black',
             stroke:int=svgplot.STROKE_SIZE,
             dashed:bool=False):

        if x2 is None:
            x2 = x1

        if y2 is None:
            y2 = y1

        if dashed:
            style = svgplot.css_params(
                'stroke', color, 'stroke-width', stroke, 'stroke-dasharray', 10)
        else:
            style = svgplot.css_params('stroke', color, 'stroke-width', stroke)

        return self._svg.line((self.x(x1), self.y(y1)),
                              (self.x(x2), self.y(y2)),
                              style=style)

    def add_line(self,
                 x1:float=0,
                 y1:float=0,
                 x2:Optional[float]=None,
                 y2:Optional[float]=None,
                 color:str='black',
                 stroke:int=svgplot.STROKE_SIZE,
                 dashed:bool=False):
        self.add(self.line(x1, y1, x2, y2, color=color,
                 stroke=stroke, dashed=dashed))

    def polyline(self, points,
                 color='black',
                 stroke=svgplot.STROKE_SIZE,
                 fill='none',
                 fill_opacity=1):
        points = [[self.x(point[0]), self.y(point[1])] for point in points]
        style = svgplot.css_params(
            'stroke', color, 'stroke-width', stroke, 'fill', fill, 'fill-opacity', fill_opacity)

        return self._svg.polyline(points, style=style)

    def add_polyline(self, points, color='black', stroke=svgplot.STROKE_SIZE, fill_opacity=1, fill='none'):
        self.add(self.polyline(points, color=color, stroke=stroke,
                               fill=fill, fill_opacity=fill_opacity))

    def rect(self,
             x=0,
             y=0,
             w=0,
             h=0,
             color='none',
             fill='none',
             fill_opacity=1,
             stroke=svgplot.STROKE_SIZE,
             dashed=False,
             rounding=0):

        if dashed:
            style = svgplot.css_params('fill', fill, 'fill-opacity', fill_opacity,
                                       'stroke', color, 'stroke-width', stroke, 'stroke-dasharray', 10)
        else:
            style = svgplot.css_params(
                'fill', fill, 'fill-opacity', fill_opacity, 'stroke', color, 'stroke-width', stroke)

        return self.trans(self._svg.rect(insert=(0, 0),
                                         size=(self.unit(w), self.unit(h)),
                                         style=style,
                                         rx=rounding,
                                         ry=rounding),
                          x=x,
                          y=y)
        # return self._svg.rect(insert=(self.x(x), self.y(y)),
        #                      size=(self.unit(w), self.unit(h)),
        #                      style=SVGFigureDraw.polygon_params(color=color, fill=fill, stroke=stroke))

    def add_rect(self, x=0, y=0, w=0, h=0, color='none', fill='none', fill_opacity=1, stroke=svgplot.STROKE_SIZE, dashed=False, rounding: int = 0):
        self.add(self.rect(x, y, w, h, color=color, fill=fill,
                 fill_opacity=fill_opacity, stroke=stroke, dashed=dashed, rounding=rounding))

    def circle(self,
               x=0,
               y=0,
               w=0,
               color='none',
               fill='none',
               fill_opacity=1,
               stroke=svgplot.STROKE_SIZE):
        r = w / 2

        return self.trans(self._svg.circle(center=(0, 0),
                                           r=self.unit(r),
                                           style=SVGFigureDraw.polygon_params(color=color, fill=fill, stroke=stroke, fill_opacity=fill_opacity)),
                          x=x,
                          y=y)

    def add_circle(self,
                   x=0,
                   y=0,
                   w=0,
                   color='none',
                   fill='none',
                   fill_opacity=1,
                   stroke=svgplot.STROKE_SIZE):
        self.add(self.circle(x, y, w, color=color, fill=fill,
                 fill_opacity=fill_opacity, stroke=stroke))

    def ellipse(self,
                x=0,
                y=0,
                w=0,
                h=0,
                color='none',
                fill='none',
                stroke=svgplot.STROKE_SIZE):

        return self.trans(self._svg.ellipse(center=(0, 0),
                                            r=(self.unit(w/2), self.unit(h/2)),
                                            style=SVGFigureDraw.polygon_params(color=color, fill=fill, stroke=stroke)),
                          x=x,
                          y=y)

    def add_ellipse(self,
                    x=0,
                    y=0,
                    w=0,
                    h=0,
                    color='none',
                    fill='none',
                    stroke=svgplot.STROKE_SIZE):
        self.add(self.ellipse(x, y, w, h, color=color, fill=fill, stroke=stroke))

    @staticmethod
    def polygon_params(color='none', fill='none', fill_opacity=1, stroke=svgplot.STROKE_SIZE):
        if color is None:
            stroke = 0

        return svgplot.css_params('fill', fill, 'fill-opacity', fill_opacity, 'stroke', color, 'stroke-width', stroke)

    def base_polygon(self, points, color='none', fill='none', fill_opacity=1, stroke=svgplot.STROKE_SIZE):
        return self._svg.polygon(points=points, style=SVGFigureDraw.polygon_params(color=color, fill=fill, stroke=stroke, fill_opacity=fill_opacity))

    def polygon(self, points, x=0, y=0, color='none', fill='none', fill_opacity=1, stroke=svgplot.STROKE_SIZE):
        return self.trans(self.base_polygon(points=points, color=color, fill=fill, fill_opacity=fill_opacity, stroke=stroke), x=x, y=y)

    def add_polygon(self, points, x=0, y=0, color='none', fill='none', fill_opacity=1, stroke=svgplot.STROKE_SIZE):
        return self.add(self.polygon(points, x, y, color=color, fill=fill, fill_opacity=fill_opacity, stroke=stroke))

    def lr_triangle(self, x=0, y=0, w=0, h=0, color='none', fill='none'):
        points = np.array([(0, h),
                           (w, h),
                           (w, 0)], dtype=float)

        return self.trans(self.base_polygon(points, color=color, fill=fill), x=x, y=y)

    def add_lr_triangle(self, x=0, y=0, w=0, h=0, color='none', fill='none'):
        self.add(self.lr_triangle(x=x, y=y, w=w, h=h, color=color, fill=fill))

    def arrow(self, x=0, y=0, color='none', fill='none', scale=1, rotate=None):
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

        points = np.array([(0, -20),
                           (20, -20),
                           (20, -40),
                           (70, 0),
                           (20, 40),
                           (20, 20),
                           (0, 20)], dtype=float)

        points *= scale

        return self.trans(self.rot(self.base_polygon(points, color=color, fill=fill), rotate=rotate), x=x, y=y)

    def add_arrow(self,
                  x=0,
                  y=0,
                  color='none',
                  fill='none',
                  rotate=None,
                  scale=1):
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
            Degree of rotation anticlockwise where.
        scale: float, optional
            How much to scale the arrow by
        """

        self.add(self.arrow(x=x, y=y, color=color,
                 fill=fill, rotate=rotate, scale=scale))

    def _axis_arrow_head(self, stroke=svgplot.STROKE_SIZE, color=svgplot.COLOR_BLACK):
        """
        Adds an arrow tip onto an axis line.

        Parameters
        ----------
        color: str, optional
            Hex color
        """

        return self.base_polygon(points=[(0, -7), (0, 7), (12, 0)], fill=color, stroke=stroke)

    def add_label_axis(self,
                       label,
                       x=0,
                       y=0,
                       dim='x',
                       size=svgplot.DEFAULT_FONT_SIZE,
                       color=svgplot.COLOR_BLACK,
                       w=svgplot.ARROW_LENGTH,
                       padding=20,
                       margin=10,
                       position='middle',
                       arrow=True,
                       weight='normal'):
        dim = dim.lower()

        sw = self.get_string_width(label, weight=weight)

        if dim == 'x':
            if position == 'top':
                self.add_text_bb(label, y=y, w=w, align='c')
                y += self.get_font_h()

                x1 = padding + (w - sw) / 2 - margin

                self.add_line(x + padding, y, x + w - padding, y, color=color)
                self.add_trans(self._axis_arrow_head(
                    color=color), x=x + w - padding, y=y)
            elif position == 'bottom':
                self.add_line(x + padding, y, x + w - padding, y, color=color)
                self.add_trans(self._axis_arrow_head(
                    color=color), x=x + w - padding, y=y)
                self.add_text(label,
                              self._get_font_center_x(label, x, w),
                              y=y + self.get_font_h(size=size) + 10,
                              color=color,
                              size=size,
                              weight=weight)
            else:
                # middle
                sw = self.get_string_width(label)
                self.add_text_bb(label, y=y, w=w, align='c')

                x1 = (w - sw) / 2 - margin
                self.add_line(x1=x+padding, y1=y, x2=x1, y2=y, color=color)

                self.add_line(x1=x1 + sw + margin, y1=y, x2=x +
                              w-padding, y2=y, color=color)
                self.add_trans(self._axis_arrow_head(
                    color=color), x=x + w - padding, y=y)

        else:
            if position == 'top':
                self.add_line(x, y - padding, x, y - w + padding, color=color)

                if arrow:
                    self.add_rot_trans(self._axis_arrow_head(
                        color=color), x=x, y=y - w + padding, rotate=-90)

                self.add_rot_trans(self.text(label,
                                             color=color,
                                             size=size,
                                             weight=weight),
                                   x=x-10,
                                   y=y - (w - sw) / 2,
                                   rotate=-90)
            else:
                y2 = y - (w - sw) / 2 + margin

                self.add_line(x1=x, y1=y-padding, x2=x, y2=y2, color=color)
                self.add_line(x1=x, y1=y2 - sw - 2 * margin,
                              x2=x, y2=y-w+padding, color=color)

                if arrow:
                    self.add_rot_trans(self._axis_arrow_head(
                        color=color), x=x, y=y - w + padding, rotate=-90)

                self.add_rot_trans(self.text(label,
                                             color=color,
                                             size=size,
                                             weight=weight),
                                   x=x+self.get_font_h()/3,
                                   y=y-(w-sw)/2,
                                   rotate=-90)

    def add_axis(self,
                 label,
                 x=0,
                 y=0,
                 dim='x',
                 size=svgplot.DEFAULT_FONT_SIZE,
                 color=svgplot.COLOR_BLACK,
                 w=svgplot.ARROW_LENGTH,
                 stroke=svgplot.AXIS_STROKE):
        dim = dim.lower()

        if dim == 'x':
            #svg = self.svgplot.add(self.svgplot.svg(x=self.unit(x), y=self.unit(y + 5), width=w, height=w, viewBox='0 0 10 10'))
            self.add_line(x, y, x + w, y, color=color, stroke=stroke)
            self.add_trans(self._axis_arrow_head(
                color=color, stroke=stroke), x=x+w, y=y)
            self.add_text(label, x, y + self.get_font_h(size=size) +
                          10, color=color, size=size)  # , rotate=(-90, 0, 0))
        else:
            #svg = self.svgplot.add(self.svgplot.svg(x=self.unit(x - 5), y=self.unit(y), width=w, height=w, viewBox='0 0 10 10'))
            self.add_line(x, y, x, y - w, color=color, stroke=stroke)
            self.add_rot_trans(self._axis_arrow_head(
                color=color, stroke=stroke), x, y - w, rotate=-90)
            self.add_rot_trans(self.text(label, color=color,
                                         size=size), x - 10, y, rotate=-90)

    def add_axes(self,
                 labelx='',
                 labely='',
                 x=0,
                 y=0,
                 color=svgplot.COLOR_BLACK,
                 w=svgplot.ARROW_LENGTH,
                 size=svgplot.DEFAULT_FONT_SIZE):
        self.add_axis(labelx, x, y, dim='x', color=color, size=size, w=w)
        self.add_axis(labely, x, y, dim='y', color=color, size=size, w=w)

    def add_frame(self,
                  x=0,
                  y=0,
                  w=0,
                  h=0,
                  padding=0,
                  color=svgplot.COLOR_BLACK,
                  fill='none',
                  shape='rect',
                  stroke=svgplot.STROKE_SIZE):
        """
        Print a frame either outlined or filled.
        """

        shape = shape.lower()

        p2 = padding * 2

        if shape == 'c' or shape == 'circle':
            self.add_circle(x - padding,
                            y - padding,
                            w + p2,
                            color=color,
                            fill=fill,
                            stroke=stroke)
        if shape == 'e':
            self.add_ellipse(x - padding,
                             y - padding,
                             w + p2,
                             h + p2,
                             color=color,
                             fill=fill,
                             stroke=stroke)
        else:
            self.add_rect(x - padding,
                          y - padding,
                          w + p2,
                          h + p2,
                          color=color,
                          fill=fill,
                          stroke=stroke)

    def add_bullet(self,
                   label,
                   x=0,
                   y=0,
                   color=svgplot.COLOR_BLACK,
                   s=svgplot.BULLET_SIZE,
                   h=svgplot.LABEL_HEIGHT,
                   text_color=None,
                   text_offset=10,
                   font_size=svgplot.DEFAULT_FONT_SIZE,
                   shape='c',
                   outline=None,
                   stroke=2):
        """

        Parameters
        ----------
        color: tuple or string, optional
            Either an rgb tuple or a hex color string.
        s: int, optional
            size of bullet.
        h: int, optional
            size of row.
        """

        if text_color is None:
            text_color = color

        if shape == 'c':
            self.add_circle(x=x, y=y, w=s,
                            color=outline, fill=color, stroke=stroke)
        else:
            self.add_rect(x=x, y=y-s/2, w=s,
                          h=s, color=outline, fill=color, stroke=stroke)

        # For testing only
        #self.add_frame(x, y, 200, h)

        self.add_text_bb(label,
                         x=x + s * 1.5,
                         y=y,
                         color=text_color)

    def base_image(self, file, w=None, h=None):
        if w is None and h is None:
            return

        if w is None:
            w = svgplot.scaled_image_w(file, h)

        if h is None:
            h = svgplot.scaled_image_h(file, w)

        image = self._svg.image(href=file,
                                insert=(0, 0),
                                width=self.unit(w),
                                height=self.unit(h),
                                preserveAspectRatio='none')
        return w, h, image

    def image(self, file, x=0, y=0, w=None, h=None):
        if w is None and h is None:
            return

        if w is None:
            w = svgplot.scaled_image_w(file, h)

        if h is None:
            h = svgplot.scaled_image_h(file, w)

        w, h, image = self.base_image(file, w=self.unit(w), h=self.unit(h))

        # preserveAspectRatio='xMinYMin meet'))
        image = self.trans(image, x=x, y=y)

        return w, h, image

    def add_image(self,
                  file,
                  x=0,
                  y=0,
                  w=None,
                  h=None,
                  title='',
                  subtitle='',
                  titleposition='bottom',
                  frame=False,
                  padding=30,
                  weight='normal'):
        starty = y

        if titleposition == 'top' and title != '':
            self.add_text_bb(title, x=x, y=y, w=w, align='c', weight=weight)

            y += self.get_font_h() + padding

            if subtitle != '':
                self.add_text_bb(subtitle, x=x, y=y, w=w, align='c')

                y += self.get_font_h() + padding

        print(file)
        w, h, image = self.image(file, x, y, w=w, h=h)
        self.add(image)

        if frame:
            self.add_frame(x, y, w, h, color='black')

        if titleposition == 'bottom' and title != '':
            self.add_text_bb(title, x=x, y=y + h + padding, w=w, align='c')

            h += self.get_font_h() + 20

            if subtitle != '':
                self.add_text_bb(subtitle, x=x, y=y + h +
                                 padding, w=w, align='c')

                h += self.get_font_h() + padding

            #h += self.get_font_h() + padding

        return w, h + (y - starty)

    def add_leg(self,
                id,
                defaultpos: bool = True,
                size=10,
                align='l',
                mode='main',
                weight='normal'):

        if align == 'l':
            self.set_cell(self.grid[0], 0)
        elif align == 'm':
            self.set_cell(self.grid[0], self.grid[1] / 2)
        else:
            self.set_cell(align[0], align[1])

        if mode == 'main':
            f = open(
                '/ifs/scratch/cancer/Lab_RDF/abh2138/scRNA/data/samples/human/10X/rdf/restricted_grch38/manuscript/v6/legends_v2.json', 'r')
        else:
            f = open('/ifs/scratch/cancer/Lab_RDF/abh2138/scRNA/data/samples/human/10X/rdf/restricted_grch38/manuscript/v6/supp_legends.json', 'r')

        data = json.load(f)

        self.add_text('{}'.format(data[id]), css={'font-weight': weight})

    def add_sup_fig(self,
                    id,
                    defaultpos=True,
                    size=10,
                    newlines=[],
                    spacings=[],
                    showtitle=True,
                    showtext=True,
                    top=False,
                    weight='normal'):
        """
        Add a bolded figure name to a page.

        Parameters
        ----------
        title: str
            Figure title.
        """

        # load legends

        legends = {}
        titles = {}

        f = open('/ifs/scratch/cancer/Lab_RDF/abh2138/scRNA/data/samples/human/10X/rdf/restricted_grch38/manuscript/v6/supp_legends_v2.txt', 'r')

        r = 0

        for line in f:
            line = line.strip()

            if r % 3 == 0:
                matcher = re.search(r'(S\d+). (.+)\.', line)
                fid = matcher.group(1)
                title = line  # matcher.group(2)
                titles[fid] = title
            elif r % 3 == 1:
                legends[fid] = line
            else:
                pass

            r += 1

        f.close()

        if id not in legends:
            return

        text = legends[id]
        title = titles[id]

        self.set_font_size(11)

        lines = []

        if showtext:
            #            s1 = 0
            #            s2 = 0
            #
            #            for newline in newlines:
            #                tokens = newline.split(':')
            #
            #                t = tokens[0]
            #
            #                if len(tokens) > 1:
            #                    n = int(tokens[1])
            #                else:
            #                    n = 1
            #
            #                s4 = s1
            #
            #                for i in range(0, n):
            #                    s2 = text.index('{}'.format(t), s4) + 1
            #                    s4 = s2 + len(t)
            #
            #                s3 = s2 + len(t)
            #                sub = text[s1:s3]
            #
            #                if len(sub) > 0:
            #                    lines.append(sub.strip())
            #
            #                s1 = s3
            #
            #            sub = text[s1:]
            #
            #            if len(sub) > 0:
            #                lines.append(sub.strip())
            #
            #
            #            lines = []

            sp = 0
            s2 = text.find(' ')
            s3 = 0
            while s2 != -1:
                sub = text[s3:s2]

                l = self.get_string_width(sub, size=11)

                if l >= self.int_view[0]:
                    if l >= self.int_view[0] + 100:
                        sub = text[s3:sp]
                        s3 = sp + 1
                    else:
                        s3 = s2 + 1

                    lines.append(sub)

                sp = s2
                s2 = text.find(' ', s2 + 1)

            if s3 != -1:
                lines.append(text[s3:])

        # calc spacing

#
#        for line in lines:
#            n = len(re.findall(r' ', line))
#            print(n)
#            spacings.append((ml / self.get_string_width(line) - 1) / n * spacing)
#
#        spacings[-1] = 0

        offset = 0  # (self.__int_view[0] - ml)

        if top:
            self.set_cell(0, 0)
        else:
            self.set_cell(self.grid[0], 0)
            self.inc(x=offset, y=-(len(lines) * self.get_font_h() * 1.6))

        if showtitle:
            self.add_text('{}'.format(title), css={'font-weight': weight})
        else:
            self.add_text('Figure {}.'.format(id), css={'font-weight': weight})

        self.inc(y=self.get_font_h() * 1.6)

        for i in range(0, len(lines)):
            line = lines[i]
            panels = re.findall(r'\([A-Z]\)', line)

            css = {}

            if len(spacings) > i:
                css['word-spacing'] = '{}'.format(spacings[i])  # '5em'

            #print(i, css)

            p = self.add_trans()  # add_group()
            a = self.text()

            s1 = 0
            s2 = 0

            for panel in panels:
                s2 = line.index(panel, s1)

                sub = line[s1:s2]

                if len(sub) > 0:
                    a.add(self.tspan(sub, css=css))

                a.add(self.tspan(panel, css={'font-weight': weight}))

                s1 = s2 + len(panel)

            sub = line[s1:]

            if len(sub) > 0:
                a.add(self.tspan(sub, css=css))

            p.add(a)

            #self.add_line(x1=0, y1=0, x2=self.get_string_width(line), y2=0, color='red')

            self.inc(y=self.get_font_h() * 1.6)

        self.set_font_size(svgplot.DEFAULT_FONT_SIZE)




    