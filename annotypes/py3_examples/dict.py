from annotypes import Anno, WithCallTypes, Mapping

from .table import LayoutTable

with Anno("Layouts for objects"):
    PartLayout = Mapping[str, LayoutTable]


class LayoutManager(WithCallTypes):
    def __init__(self, part_layout: PartLayout):
        self.part_layout = part_layout
