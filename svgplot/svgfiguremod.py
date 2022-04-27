from typing import Optional
from .svgfigure import SVGFigure

class SVGFigureModule:
    def __init__(self, svg:SVGFigure):
        self._svg = svg
    
    @property
    def svg(self):
        return self._svg

    def t(self, x:Optional[float]=None, y:Optional[float]=None, inc:bool=False):
        self._svg.t(x=x, y=y, inc=inc)