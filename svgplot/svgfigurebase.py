from optparse import Option
from typing import Mapping, Optional, Union
import svgwrite
from . import core
import re

# inches to mm
PX_TO_SVG = 1 / 72 * 254


class SVGFigureBase:
    def __init__(self,
                 file,
                 # size=('279mm', '216mm'),
                 size: tuple[float, float] = (279, 216),
                 view: Optional[tuple[int, int]] = None,  # (2790, 2160),
                 grid: tuple[int, int] = (12, 12),
                 border: int = 100):

        if view is None:
            view = (int(size[0] * 10), int(size[1] * 10))

        size = (f'{size[0]}mm', f'{size[1]}mm')

        self._svg = svgwrite.Drawing(
            file,
            size=size,
            viewBox='0 0 {} {}'.format(view[0], view[1]))
        # self._svg.add_stylesheet(
        #    href='/ifs/scratch/cancer/Lab_RDF/abh2138/scRNA/data/samples/human/10X/rdf/restricted_grch38/manuscript/svg-fig.css', title='svg-fig')
        self._view = view
        self._scale_xy = (1, 1)  # (view[0] / 2790, view[1] / 2160)
        self._border = (border * self._scale_xy[0], border * self._scale_xy[1])
        # (int(12 * self._scale_xy[0]), int(12 * self._scale_xy[1]))
        self._grid = grid
        self._int_view = (view[0] - 2 * self._border[0],
                          view[1] - 2 * self._border[1])
        self._grid_xy = (self._int_view[0] / grid[1],
                         self._int_view[1] / grid[0])
        self._subgrid_xy = (self._grid_xy[0] / grid[1],
                            self._grid_xy[1] / grid[0])
        self._offset = (0, 0)
        self._sub_offset = (0, 0)
        self._trans = [(0, 0)]
        self._mode = 'grid'
        self._font_size = core.DEFAULT_FONT_SIZE
        self._heading_font_size = core.HEADING_FONT_SIZE

    @property
    def svg(self) -> svgwrite.Drawing:
        return self._svg

    def save(self) -> None:
        self._svg.save(pretty=True)

    def add(self, tag):
        self._svg.add(tag)

    @property
    def grid_xy(self) -> tuple[float, float]:
        return self._grid_xy

    @property
    def grid(self):
        return self._grid

    @property
    def int_view(self):
        return self._int_view

    @property
    def offset(self):
        return self._offset

    # def grid_block(self, row, col, name=None):
    #    return SVGGridBlock(self, row, col, name=name)

    def unit(self, num: float) -> float:
        """Returns number with 5 dp to reduce size of svg

        Args:
            num float: number

        Returns:
            float: number rounded to 5 dp.
        """
        # * 10 #self.units #'{}{}'.format(num, self.units)
        return round(num, 5)

    def set_offset(self, x: int = 0, y: int = 0):
        self._offset = (x, y)

    def set_sub_offset(self, x: int = 0, y: int = 0):
        self._sub_offset = (x, y)

    def set_cell(self, row: int = 0, col: int = 0):
        self.set_offset(col * self._grid_xy[0], row * self._grid_xy[1])
        self.set_sub_cell(0, 0)
        self.t(0, 0)

        return self

    def set_sub_cell(self, row: int = 0, col: int = 0):
        self.set_sub_offset(
            col * self._subgrid_xy[0], row * self._subgrid_xy[1])

    def x(self, x: float = 0) -> float:
        """
        Translates x to canvas x

        Args:
            x (float): x position in dimensionless units

        Returns:
            float: x translated relative to current canvas offsets.
        """
        return self.unit(x + self._offset[0] + self._sub_offset[0] + self._trans[-1][0] + self._border[0])

    def y(self, y: float = 0) -> float:
        """
        Translates y to canvas y

        Args:
            y (float): y position in dimensionless units

        Returns:
            float: y translated relative to current canvas offsets.
        """
        return self.unit(y + self._offset[1] + self._sub_offset[1] + self._trans[-1][1] + self._border[1])

    def pos(self, pos: tuple[float, float] = (0, 0)) -> tuple[float, float]:
        """
        Adjusts a position tuple to be relative to the current figure coordinates.

        Args:
            pos: An x,y tuple.
        Returns:
            The tuple adjusted to the current coordinate system.

        """
        return (self.x(pos[0]), self.y(pos[1]))

    def inc(self, x: Optional[float] = None, y: Optional[float] = None) -> None:
        """
        Relative transition from current point.
        """
        self.t(x=x, y=y, inc=True)

    def t(self, x: Optional[float] = None, y: Optional[float] = None, inc: bool = False) -> None:
        if x is not None:
            if inc:
                x += self._trans[-1][0]
        else:
            x = self._trans[-1][0]

        if y is not None:
            if inc:
                y += self._trans[-1][1]
        else:
            y = self._trans[-1][1]

        #self._trans = (x * self._scale_xy[0], y * self._scale_xy[1])
        self._trans.append((x, y))

    def undo_t(self) -> None:
        """
        Allow transitions to be undone
        """
        if len(self._trans) > 1:
            loc = self._trans.pop()

    def rot(self, elem, rotate: Optional[float] = None) -> None:
        if rotate is None or (isinstance(rotate, int) and rotate == 0):
            return elem

        g = self._svg.g(transform=core.format_rotate(rotate))
        g.add(elem)
        return g

    def format_scale(self, x: int = 0, y: int = 0) -> str:
        return f'scale({x} {y})'

    def scale(self, elem=None, x: float = 1, y: float = 1, css: Optional[Mapping[str, str]] = None) -> None:
        css = self.css_map(css)

        #print(x, y)

        g = self._svg.g(transform=self.format_scale(x, y),
                        style=core.format_css_params(css))

        if elem is not None:
            g.add(elem)

        return g

    def add_scale(self, elem=None, x: float = 0, y: float = 0, css: Optional[Mapping[str, str]] = None) -> None:
        g = self.scale(elem=elem, x=x, y=y, css=css)
        self.add(g)
        return g

    def trans(self, elem=None, x: float = 0, y: float = 0, css: Optional[Mapping[str, str]] = None) -> None:
        css = self.css_map(css)

        print(x, y)

        g = self._svg.g(transform=self.format_translate(
            self.x(x), self.y(y)), style=core.format_css_params(css))

        if elem is not None:
            g.add(elem)

        return g

    def add_trans(self, elem=None, x: float = 0, y: float = 0, css: Optional[Mapping[str, str]] = None) -> None:
        g = self.trans(elem=elem, x=x, y=y, css=css)
        self.add(g)
        return g

    def rot_trans(self, elem, x: float = 0, y: float = 0, rotate: float = 0) -> None:
        return self.trans(self.rot(elem, rotate=rotate), x=x, y=y)

    def trans_rot(self, elem, x: float = 0, y: float = 0, rotate: float = 0) -> None:
        return self.rot(self.trans(elem, x=x, y=y), rotate=rotate)

    def add_rot_trans(self, elem, x: float = 0, y: float = 0, rotate: float = 0) -> None:
        self.add(self.rot_trans(elem, x, y, rotate))

    def set_font_size(self, size: int) -> None:
        self._font_size = size

    def set_heading_font_size(self, size: int) -> None:
        self._heading_font_size = size

    @property
    def font_scale_factor(self) -> float:
        return core.FONT_SCALE_FACTOR

    def get_scale_font_size(self, size: int) -> float:
        return size * self.font_scale_factor  # / self.font_scale_factor

    def format_translate(self, x: int = 0, y: int = 0) -> str:
        return f'translate({self.unit(x)} {self.unit(y)})'

    def get_string_width(self,
                         label: str,
                         family: str = core.DEFAULT_FONT_FAMILY,
                         size: Optional[int] = None,
                         weight: str = core.DEFAULT_FONT_WEIGHT) -> float:
        if size is None:
            size = self._font_size

        return core.get_text_metrics(label, family=family, size=size, weight=weight)[0] * PX_TO_SVG

    def _get_font_center_x(self,
                           label,
                           x,
                           w,
                           family=core.DEFAULT_FONT_FAMILY,
                           size=None,
                           weight=core.DEFAULT_FONT_WEIGHT) -> float:
        if size is None:
            size = self._font_size

        sw = self.get_string_width(
            label, family=family, size=size, weight=weight)

        return x + (w - sw) / 2

    def get_font_h(self,
                   family: str = core.DEFAULT_FONT_FAMILY,
                   size: Optional[int] = None,
                   weight: str = core.DEFAULT_FONT_WEIGHT) -> float:
        if size is None:
            size = self._font_size

        # / self.font_scale_factor
        return core.get_text_metrics('A', family=family, size=size, weight=weight)[1] * 2.7

    def get_font_y(self,
                   y: float = 0,
                   h: float = 0,
                   family: str = core.DEFAULT_FONT_FAMILY,
                   size: Optional[int] = None,
                   weight: str = core.DEFAULT_FONT_WEIGHT) -> float:
        if size is None:
            size = self._font_size

        # if h is None:
        #    h = self.get_font_h(family=family, size=size, weight=weight)

        # * (1 - (1 - get_font_h(s)) / 2)
        return y + h - (h - self.get_font_h(family=family, size=size, weight=weight)) / 2

    def text(self,
             text: str,
             x: float = 0,
             y: float = 0,
             color=core.COLOR_BLACK,
             family=core.DEFAULT_FONT_FAMILY,
             size=None,
             spacing=0,
             weight=core.DEFAULT_FONT_WEIGHT,
             css: Optional[Mapping[str, str]] = None) -> None:

        if size is None:
            size = self._font_size

        _css = {'fill': color,
                'font-family': family,
                'font-size': '{}px'.format(
                    self.get_scale_font_size(size)),
                'font-weight': weight,
                'letter-spacing': spacing}

        if css is not None:
            _css.update(css)

        return self._svg.text(text,
                              insert=(x, y),
                              style=core.format_css_params(_css))

    def add_text(self,
                 label,
                 x: float = 0,
                 y: float = 0,
                 color: str = 'black',
                 h: float = core.LABEL_HEIGHT,
                 family: str = core.DEFAULT_FONT_FAMILY,
                 size: int = None,
                 weight: str = core.DEFAULT_FONT_WEIGHT,
                 rotate: float = 0,
                 css: Optional[Mapping[str, str]] = None) -> None:
        return self.add_rot_trans(self.text(label,
                                            color=color,
                                            family=family,
                                            size=size,
                                            weight=weight,
                                            css=css),
                                  x=x,
                                  y=y,
                                  rotate=rotate,)

    def css_map(self, css: Optional[dict[str, Union[str, int, float]]]) -> dict[str, Union[str, int, float]]:
        if css is None:
            css = {}

        if 'fill' not in css:
            css['fill'] = 'black'
        if 'font-family' not in css:
            css['font-family'] = core.DEFAULT_FONT_FAMILY
        if 'font-size' not in css:
            css['font-size'] = '{}px'.format(
                self.get_scale_font_size(self._font_size))
        if 'font-weight' not in css:
            css['font-weight'] = core.DEFAULT_FONT_WEIGHT
        if 'letter-spacing' not in css:
            css['letter-spacing'] = 0
        if 'word-spacing' not in css:
            css['word-spacing'] = 0
        if 'white-space' not in css:
            css['white-space'] = 'pre'

        return css

    def group(self, css=None):
        return self._svg.g(style=core.format_css_params(self.css_map(css)))

    def tspan(self, text, css=None):
        return self._svg.tspan(text, style=core.format_css_params(self.css_map(css)))

    def add_group(self, css=None):
        g = self.group(css)
        self.add(g)
        return g

    def add_title(self,
                  text: str,
                  subtext: Optional[str] = None,
                  x: int = 0,
                  y: int = 0,
                  w: int = 500,
                  padding: int = 10,
                  color: str = 'black',
                  twolines: bool = True,
                  weight: str = 'normal') -> None:
        self.add_text_bb(text,
                         x=x,
                         y=y,
                         w=w,
                         weight=weight,
                         align='c' if twolines else 'l',
                         color=color)

        if subtext is not None:
            if twolines:
                y += self.get_font_h() + padding
            else:
                x += self.get_string_width(text) + padding

            self.add_text_bb(subtext,
                             x=x,
                             y=y,
                             w=w,
                             align='c' if twolines else 'l',
                             color=color)

    def add_section(self,
                    label:str,
                    x=0,
                    y=0,
                    h=core.LABEL_HEIGHT,
                    indent=True,
                    mode='upper',
                    weight='normal') -> None:
        self.set_sub_cell(0, 0)
        self.add_text('{}'.format(label.upper() if mode == 'upper' else label.lower()),  # upper()),
                      x=x,
                      y=self.get_font_y(
                          y, h, size=self._heading_font_size, weight=weight),
                      h=h,
                      size=self._heading_font_size,
                      weight=weight)

        if indent:
            self.add_section_indent()

    def add_section_indent(self) -> None:
        self.set_sub_cell(0, 4)

    def add_fig_name(self, id, align='l', mode='long', weight='bold') -> None:
        """
        Add a figure name to the bottom of a page. Figures are called
        Fig. x
        """

        if mode == 'short':
            self.add_fig_title('Fig. {}'.format(
                id), align=align, weight=weight)
        else:
            self.add_fig_title('Figure {}.'.format(
                id), align=align, weight=weight)

    def add_fig_title(self, title, align:str='l', size:int=10, weight:str='normal') -> None:
        """
        Add a bolded figure name to a page.

        Parameters
        ----------
        title: str
            Figure title.
        """

        if align == 'l':
            self.set_cell(self.grid[0], 0)
        else:
            self.set_cell(self.grid[0], self.grid[1] - 1)

        self.add_text(title, size=size, weight=weight)

    def add_text_bb(self,
                    label,
                    x: float = 0,
                    y: float = 0,
                    w: float = 0,
                    h: float = 0,
                    align: str = 'l',
                    color: str = core.COLOR_BLACK,
                    family: str = core.DEFAULT_FONT_FAMILY,
                    size: Optional[int] = None,
                    weight: str = core.DEFAULT_FONT_WEIGHT,
                    orientation: str = 'h',
                    frameargs={}) -> None:

        if frameargs is None:
            frameargs = {}

        if 'style' not in frameargs:
            frameargs['style'] = None
        if 'color' not in frameargs:
            frameargs['color'] = 'black'
        if 's' not in frameargs:
            frameargs['s'] = 40

        align = align.lower()
        orientation = orientation.lower()

        y1 = self.get_font_y(y, h, size=size, weight=weight)

        match orientation:
            case 'v':
                x = self.get_font_y(x, w, size=size, weight=weight)
                sw = self.get_string_width(label,
                                           family=family,
                                           size=size,
                                           weight=weight)

                match align:
                    case 'c':
                        self.add_rot_trans(self.text(label, color=color, size=size),
                                           x=x+self.get_font_h()/3,
                                           y=y-(w-sw)/2,
                                           rotate=-90)
                    case 'r':
                        self.add_text(label,
                                      x=x,
                                      y=y1 + sw,
                                      color=color,
                                      size=size,
                                      weight=weight,
                                      rotate=-90)
                    case _:
                        self.add_text(label,
                                      x=x,
                                      y=y1,
                                      color=color,
                                      size=size,
                                      weight=weight,
                                      rotate=-90)
            case 'a':
                x = self.get_font_y(x, w, size=size, weight=weight)

                self.add_text(label,
                              x=x,
                              y=y1,
                              color=color,
                              size=size,
                              weight=weight,
                              rotate=-45)
            case _:
                if align == 'r':
                    sw1 = self.get_string_width(label,
                                                family=family,
                                                size=size,
                                                weight=weight)

                    self.add_text(label,
                                  x - sw1,
                                  y=y1,
                                  size=size,
                                  color=color,
                                  weight=weight)

                    #self.add_frame(x-sw1, y-self.get_font_h(), sw1, self.get_font_h(), color='red')
                else:
                    x1 = x

                    if align == 'c':
                        x1 = self._get_font_center_x(label,
                                                     x,
                                                     w,
                                                     size=size,
                                                     weight=weight)

                    self.add_text(label,
                                  x=x1,
                                  y=y1,
                                  color=color,
                                  size=size,
                                  weight=weight)

                    #self.add_frame(x-20, y-self.get_font_h(), sw1, self.get_font_h(), color='red')

                    if frameargs['style'] is not None:
                        if frameargs['style'] == 'circle':
                            x1 = x  # + (w - frameargs['s'])
                            self.add_circle(
                                x=x1, y=y, w=frameargs['s'], color=frameargs['color'])
