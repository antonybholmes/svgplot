from typing import Optional, Union
import numpy as np

def _calc_linear_scale(lim: tuple[float, float] = [0, 1], ticks=6):
    if lim[0] == lim[1]:
        lim[0] -= 10
        lim[1] += 10


    range = lim[1] - lim[0]

    if ticks < 2:
        ticks = 2
    if ticks > 2:
        ticks -= 1

    tempStep = range/(ticks - 1)
    #Calculate pretty step value
    mag = np.floor(np.log10(tempStep))
    magPow = np.power(10,mag)
    magMsd = (int)(tempStep/magPow + 0.5)
    stepSize = magMsd*magPow
    upper = stepSize * np.ceil(1 + lim[1] / stepSize)
    lower = stepSize * np.floor(lim[0] / stepSize)
    
    return (lower, upper)

def auto_axis(lim: tuple[float, float] = [0, 1], label: str = '', ticks: int =6, dp: int = 2, w: int = 100):
    lower, upper = _calc_linear_scale(lim, ticks=ticks)
    ticks = [np.round(x, dp) for x in np.linspace(lower, upper, ticks)]

    print(lim, lower, upper, ticks)
    return Axis(lim=[lower, upper], ticks=ticks, label=label, w=w)

class Axis:
    def __init__(self,
                 lim: tuple[Union[int, float], Union[int, float]] = None,
                 label: str = '',
                 ticks: Optional[list[Union[int, float]]] = None,
                 ticklabels: Optional[list[Union[int, float, str]]] = None,
                 w: int = 100):
        if lim is not None:
            self._lim = lim
        else:
            self._lim = (0, 100)

        self._range = self._lim[1] - self._lim[0]
        self._scale_factor = w / self.range
        self._w = w
        self._label = label

        if ticks is not None:
            self._ticks = ticks
        else:
            self._ticks = np.array(
                range(int(self._lim[0]), int(self._lim[1]) + 1))

        if ticklabels is not None:
            self._ticklabels = ticklabels
        else:
            self._ticklabels = self._ticks

    @property
    def scale_factor(self) -> Union[int, float]:
        return self._scale_factor

    @property
    def w(self) -> int:
        return self._w

    @w.setter
    def w(self, w):
        self._w = w

    @property
    def range(self) -> Union[int, float]:
        return self._range

    @property
    def lim(self) -> tuple[Union[int, float], Union[int, float]]:
        return self._lim

    @property
    def ticks(self) -> list[Union[int, float]]:
        return self._ticks

    @ticks.setter
    def ticks(self, ticks):
        self._ticks = ticks

    @property
    def ticklabels(self) -> list[Union[int, float, str]]:
        return self._ticklabels

    @ticklabels.setter
    def ticklabels(self, ticklabels: list[Union[int, float, str]]):
        self._ticklabels = ticklabels

    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, label: str):
        self._label = label

    def scale(self, x: float, clip: bool = False) -> float:
        #print(x, self.__lim[0], self.__lim[1], self.__scale_factor)
        #print(x, self.__lim[0])

        if clip:
            x = max(min(x, self.lim[1]), self.lim[0])

        return (x - self._lim[0]) * self._scale_factor

    def scale_clip(self, x: float) -> float:
        return self.scale(x, clip=True)
