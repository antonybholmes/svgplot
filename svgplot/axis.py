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






class Axis:
    def __init__(self,
                 lim: tuple[Union[int, float], Union[int, float]] = (0, 100),
                 label: str = '',
                 ticks: Optional[list[Union[int, float]]] = None,
                 ticklabels: Optional[list[Union[str, int, float]]] = None,
                 w: int = 100):
        

        self._lim = lim
        self._range = self._lim[1] - self._lim[0]
        self._scale_factor = w / self._range
        self._label = label
        self._ticks = []
        self._ticklabels = []
        self._w = w
        
        if isinstance(ticks, list) or isinstance(ticks, np.ndarray):
            self._ticks.extend(ticks)
        else:
            self._ticks.extend(lim)

        self._ticks = np.array(self._ticks)

        if isinstance(ticklabels, list) or isinstance(ticklabels, np.ndarray):
            self._ticklabels.extend(ticklabels)
        else:
            if self._ticks.size > 0:
                self._ticklabels.append(self._ticks[0])
            if self._ticks.size > 1:
                self._ticklabels.append(self._ticks[-1])

        self._ticklabels = np.array(self._ticklabels)

        

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
    def ticklabels(self) -> list[str]:
        return self._ticklabels

    @ticklabels.setter
    def ticklabels(self, ticklabels: list[Union[int, float, str]]):
        if isinstance(ticklabels, list) or isinstance(ticklabels, np.ndarray):
            self._ticklabels = np.array(ticklabels)

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


def auto_axis(lim: tuple[float, float] = [0, 1], label: str = '', ticks: int =6, dp: int = 2, w: int = 100):
    lower, upper = _calc_linear_scale(lim, ticks=ticks)
    ticks = [np.round(x, dp) for x in np.linspace(lower, upper, ticks)]

    return Axis(lim=[lower, upper], ticks=ticks, label=label, w=w)

def create_axis(axis: Optional[Union[Axis, tuple[float, float]]], 
        w: int = 100,
        label: str = ''
        ) -> Axis:
    if isinstance(axis, Axis):
        return axis
    elif isinstance(axis, tuple):
        return auto_axis(lim=axis, w=w, label=label)
    else:
        return auto_axis(w=w, label=label)
