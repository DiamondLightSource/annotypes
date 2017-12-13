from typing import List

from annotypes import add_call_types, WithCallTypes, Anno
from .simple import Simple, Exposure, Path


with Anno("The path prefix for the list of writers"):
    Prefix = str


@add_call_types
def composition_func(exposure: Exposure, prefix: Prefix) -> List[Simple]:
    ret = [Simple(exposure, prefix + suff) for suff in ["/one", "/two"]]
    return ret


class CompositionClass(WithCallTypes):
    def __init__(self, exposure: Exposure, path: Path):
        self.exposure = exposure
        self.path = path
        self.child = Simple(exposure, path)

    def write_hello(self):
        self.child.write_data("hello")
