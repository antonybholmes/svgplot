from abc import ABC, abstractmethod
from typing import Optional
from .svgfigureplot import SVGFigurePlot


class SVGFigure(SVGFigurePlot):
    def __init__(self,
                 file,
                 size: tuple[float, float] = (279, 216),
                 view: Optional[tuple[int, int]] = None, #(2790, 2160),
                 grid=(12, 12),
                 border=40):
        super().__init__(file,
                         size=size,
                         view=view,
                         grid=grid,
                         border=border)


class FigureFactory(ABC):
    @abstractmethod
    def get_figure(file: str, name: str = None, size: tuple[float, float] = None) -> SVGFigure:
        pass


class JournalFigureFactory(FigureFactory):
    def get_figure(file: str, name: str = None, size: tuple[float, float] = None) -> SVGFigure:
        match name:
            case 'portrait':
                size = (216, 279)
            case 'jem':
                size = (int(round(7*25.4)), int(round(9*25.4)))
            case 'frontier':
                size = (180, 279)
            case _:
                size = (279, 216)

        return SVGFigure(file, size=size)


class FigureFactoryProducer:
    def get_factory(name: str):
        match name:
            case 'journal':
                return JournalFigureFactory


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
