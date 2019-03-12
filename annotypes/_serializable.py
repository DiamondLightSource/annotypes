from collections import OrderedDict

from ._calltypes import WithCallTypes
from ._typing import TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Type, Dict, Any, Union, Sequence, List, Tuple


def serialize_object(o, dict_cls=OrderedDict):
    try:
        # This will do all the sub layers for us
        return o.to_dict(dict_cls)
    except AttributeError:
        if isinstance(o, dict):
            # Need to recurse down in case we have a serializable object in the
            # dict or somewhere further down the tree
            d = dict_cls()
            for k, v in o.items():
                d[k] = serialize_object(v, dict_cls)
            return d
        # Compare on classname is cheaper than a subclass check...
        elif o.__class__.__name__ == "Array" and hasattr(o.typ, "to_dict"):
            # Arrays might be of serializable objects, if so then recurse
            # down.
            return [x.to_dict(dict_cls) for x in o]
        else:
            # Hope it's serializable!
            return o


T = TypeVar("T")


def deserialize_object(ob, type_check=None):
    # type: (Any, Union[Type[T], Tuple[Type[T], ...]]) -> T
    if isinstance(ob, dict):
        subclass = Serializable.lookup_subclass(ob)
        ob = subclass.from_dict(ob)
    if type_check is not None:
        assert isinstance(ob, type_check), \
            "Expected %s, got %r" % (type_check, type(ob))
    return ob


class Serializable(WithCallTypes):
    """Base class for serializable objects"""

    # This will be set by subclasses calling cls.register_subclass()
    typeid = None

    # dict mapping typeid name -> cls
    _subcls_lookup = {}  # type: Dict[str, Serializable]

    __slots__ = []  # type: List[str]

    def __getitem__(self, item):
        """Dictionary access to attr data"""
        if item in self.call_types:
            try:
                return getattr(self, item)
            except (AttributeError, TypeError):
                raise KeyError(item)
        else:
            raise KeyError(item)

    def __iter__(self):
        return iter(self.call_types)

    def to_dict(self, dict_cls=OrderedDict):
        # type: (Type[dict]) -> Dict[str, Any]
        """Create a dictionary representation of object attributes

        Returns:
            OrderedDict serialised version of self
        """

        d = dict_cls()
        if self.typeid:
            d["typeid"] = self.typeid

        for k in self.call_types:
            # check_camel_case(k)
            d[k] = serialize_object(getattr(self, k), dict_cls)

        return d

    @classmethod
    def from_dict(cls, d, ignore=()):
        """Create an instance from a serialized version of cls

        Args:
            d(dict): Endpoints of cls to set
            ignore(tuple): Keys to ignore

        Returns:
            Instance of this class
        """
        filtered = {}
        for k, v in d.items():
            if k == "typeid":
                assert v == cls.typeid, \
                    "Dict has typeid %s but %s has typeid %s" % \
                    (v, cls, cls.typeid)
            elif k not in ignore:
                filtered[k] = v
        try:
            inst = cls(**filtered)
        except TypeError as e:
            raise TypeError("%s raised error: %s" % (cls.typeid, str(e)))
        return inst

    @classmethod
    def register_subclass(cls, typeid):
        """Register a subclass so from_dict() works

        Args:
            typeid (str): Type identifier for subclass
        """
        def decorator(subclass):
            cls._subcls_lookup[typeid] = subclass
            subclass.typeid = typeid
            return subclass
        return decorator

    @classmethod
    def lookup_subclass(cls, d):
        """Look up a class based on a serialized dictionary containing a typeid

        Args:
            d (dict): Dictionary with key "typeid"

        Returns:
            Serializable subclass

        Raises:
            TypeError: on bad typeid
        """
        try:
            typeid = d["typeid"]
        except KeyError:
            raise TypeError("typeid not present in keys %s" % list(d))

        subclass = cls._subcls_lookup.get(typeid, None)
        if not subclass:
            raise TypeError("'%s' not a valid typeid" % typeid)
        else:
            return subclass
