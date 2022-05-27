from typing import Optional
from .svgfiguredraw import SVGFigureDraw
from enum import Enum


class SVGFigure(SVGFigureDraw):
    def __init__(self,
                 file,
                 size: tuple[float, float] = (279, 216),
                 view: Optional[tuple[int, int]] = None,  # (2790, 2160),
                 grid=(12, 12),
                 border=40):
        super().__init__(file,
                         size=size,
                         view=view,
                         grid=grid,
                         border=border)


class FigureSize(Enum):
    LETTER = 1
    JEM = 2
    FRONTIER = 3

class Orientation(Enum):
    PORTRAIT = 1
    LANDSCAPE = 2


class FigureFactory:
    def create_figure(file: str,
        size: FigureSize = FigureSize.LETTER, 
        orientation: Orientation = Orientation.LANDSCAPE) -> SVGFigure:

        match size:
            case FigureSize.JEM:
                size = (int(round(7*25.4)), int(round(9*25.4)))
            case FigureSize.FRONTIER:
                size = (180, 279)
            case _:
                # landscape
                size = (216, 279)

        if orientation == Orientation.LANDSCAPE:
            size = (size[1], size[0])

        return SVGFigure(file, size=size)

    def letter(file: str, landscape:bool=False):
        return FigureFactory.create_figure(file, orientation=Orientation.LANDSCAPE if landscape else Orientation.PORTRAIT)

    def portrait(file: str):
        return FigureFactory.create_figure(file, orientation=Orientation.PORTRAIT)

    def landscape(file: str):
        return FigureFactory.create_figure(file, orientation=Orientation.LANDSCAPE)

    def frontier(file: str, orientation=Orientation.PORTRAIT):
        return FigureFactory.create_figure(file, size=FigureSize.FRONTIER, orientation=orientation)

    def jem(file: str, orientation=Orientation.PORTRAIT):
        return FigureFactory.create_figure(file, size=FigureSize.JEM, orientation=orientation)

# def make_panel():
#     svg = SVGFigure('panel.svg',
#                     size=('5.5in', '4.25in'),
#                     view=(int(2790/2), int(2160/2)),
#                     grid=(6, 6),
#                     subgrid=(6, 6))

#     return svg


# def make_full_panel():
#     svg = SVGFigure('panel.svg',
#                     size=('5.5in', '8.5in'),
#                     view=(2790//2, 2160),
#                     grid=(6, 12),
#                     subgrid=(6, 12))

#     return svg


# def make_full_width_panel():
#     svg = SVGFigure('panel.svg',
#                     size=('11in', '4.25in'),
#                     view=(2790, 2160//2),
#                     grid=(12, 6),
#                     subgrid=(12, 6))

#     return svg
