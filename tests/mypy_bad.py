from annotypes import Array
from annotypes.py2_examples.simple import Simple
from annotypes.py2_examples.manyargs import ManyArgs
from annotypes.py2_examples.composition import CompositionClass
from annotypes.py2_examples.enumtaker import EnumTaker
from annotypes.py2_examples.table import LayoutTable, Manager
from annotypes.py2_examples.dict import LayoutManager

a = Simple("bad")
b = Simple(45, 46)
c = ManyArgs("x", 0, "1", 10, [33])
d = CompositionClass("/tmp")
e = EnumTaker("bad")
layout = LayoutTable(Array(["BLOCK"]),
                     Array[str](["MRI"]),
                     Array[str](["0.5"]),
                     [2.5],
                     True)
Manager().set_layout(None)
LayoutManager(dict(part=32))
