from typing import Sequence

from annotypes import Anno, WithCallTypes


with Anno("The scannable axes, e.g. ['x', 'y'] or 'x'"):
    Axes = Sequence[str]

with Anno("The scannable units, e.g. ['mm', 'deg'] or 'mm'"):
    Units = Sequence[str]

with Anno("The first point to be generated, e.g. [0., 2.4] or 1."):
    Start = Sequence[float]

with Anno("The final point to be generated, e.g. [-8., 6.4] or 5."):
    Stop = Sequence[float]

with Anno("The number of points to generate, e.g. 5"):
    Size = int

with Anno("Whether to reverse on alternate runs"):
    Alternate = bool


class Long(WithCallTypes):
    def __init__(self,
                 axes,  # type: Axes
                 units,  # type: Units
                 start,  # type: Start
                 stop,  # type: Stop
                 size,  # type: Size
                 alternate=False  # type: Alternate
                 ):
        # type: (...) -> None
        self.axes = axes
        self.units = units
        self.start = start
        self.stop = stop
        self.size = size
        self.alternate = alternate
