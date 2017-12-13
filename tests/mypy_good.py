from annotypes.py2_examples.simple import Simple
from annotypes.py2_examples.long import Long
from annotypes.py2_examples.composition import CompositionClass
from annotypes.py2_examples.enumtaker import EnumTaker, Status

a = Simple(32)
b = Simple(45, "")
c = Long(["x"], ["mm"], [0], [1], 10)
d = CompositionClass(2.0, "/tmp")
e = EnumTaker(Status.bad)
