from abc import ABC, abstractmethod
from .svgfiguregenes import SVGFigureGenes


class SVGFigure(SVGFigureGenes):
    def __init__(self,
                 file,
                 size=('11in', '8.5in'),  # size=('279mm', '216mm'),
                 view=(2790, 2160),
                 grid=(12, 12),
                 subgrid=(12, 12),
                 border=40):
        super().__init__(file,
                         size=size,
                         view=view,
                         grid=grid,
                         subgrid=subgrid,
                         border=border)


class FigureFactory(ABC):
    @abstractmethod
    def get_figure(file: str, name: str = None, size: tuple[float, float] = None) -> SVGFigure:
        pass


class JournalFigureFactory(FigureFactory):
    def get_figure(file: str, name: str = None, size: tuple[float, float] = None) -> SVGFigure:
        match name:
            case 'portrait':
                size = (8.5, 11)
            case 'jem':
                size = (7, 9)
            case 'frontier':
                size = (180/25.4, 279/25.4)
            case _:
                size = (11, 8.5)

        return SVGFigure(file, size=('{}in'.format(size[0]), '{}in'.format(size[1])), view=(int(size[0] * 254), int(size[1] * 254)))


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
