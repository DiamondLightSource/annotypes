from typing import Sequence, Union

from annotypes import Anno, WithCallTypes, to_array


with Anno("The scannable axes, e.g. ['x', 'y'] or 'x'"):
    Axes = Union[Sequence[str], str]
with Anno("The scannable units, e.g. ['mm', 'deg'] or 'mm'"):
    Units = Union[Sequence[str], str]
with Anno("The first point to be generated, e.g. [0., 2.4] or 1."):
    Start = Union[Sequence[float], float]
with Anno("The final point to be generated, e.g. [-8., 6.4] or 5."):
    Stop = Union[Sequence[float], float]
with Anno("The number of points to generate, e.g. 5"):
    Size = int
with Anno("Whether to reverse on alternate runs"):
    Alternate = bool


class Long(WithCallTypes):
    def __init__(self, axes: Axes, units: Units, start: Start, stop: Stop,
                 size: Size, alternate: Alternate = False):
        self.axes = to_array(axes)
        self.units = to_array(units)
        self.start = to_array(start)
        self.stop = to_array(stop)
        assert len(self.axes) == len(self.units) == \
            len(self.start) == len(self.stop), \
            "axes %s, units %s, start %s, stop %s are not the same length" % (
                self.axes, self.units, self.start, self.stop)
        self.size = size
        self.alternate = alternate
