from __future__ import absolute_import, unicode_literals

import abc
import functools
import sys
import collections


class TypingMeta(type):
    def __new__(cls, name, bases, namespace):
        return super(TypingMeta, cls).__new__(cls, str(name), bases, namespace)

    def __init__(self, *args, **kwds):
        pass


class _TypingBase(object):
    """Internal indicator of special typing constructs."""
    __metaclass__ = TypingMeta
    __slots__ = ('__weakref__',)

    def __init__(self, *args, **kwds):
        pass


class TypeVar(_TypingBase):
    __metaclass__ = TypingMeta


# Some unconstrained type variables.  These are used by the container types.
# (These are not for export.)
T = TypeVar('T')  # Any type.
KT = TypeVar('KT')  # Key type.
VT_co = TypeVar('VT_co', covariant=True)  # Value type covariant containers.


_cleanups = []


def _tp_cache(func):
    maxsize = 128
    cache = {}
    _cleanups.append(cache.clear)

    @functools.wraps(func)
    def inner(*args):
        key = args
        try:
            return cache[key]
        except TypeError:
            # Assume it's an unhashable argument.
            return func(*args)
        except KeyError:
            value = func(*args)
            if len(cache) >= maxsize:
                # If the cache grows too much, just start over.
                cache.clear()
            cache[key] = value
            return value

    return inner


class _Union(_TypingBase):
    __metaclass__ = TypingMeta
    __slots__ = ('__args__', '__origin__')

    def __new__(cls, parameters=None, origin=None, *args, **kwds):
        self = super(_Union, cls).__new__(cls, parameters, origin, *args, **kwds)
        if origin is None:
            self.__args__ = None
            self.__origin__ = None
            return self
        if not isinstance(parameters, tuple):
            raise TypeError("Expected parameters=<tuple>")
        if origin is Union:
            # It's not a union if there's only one type left.
            if len(parameters) == 1:
                return parameters[0]
        self.__args__ = parameters
        self.__origin__ = origin
        return self

    @_tp_cache
    def __getitem__(self, parameters):
        if not isinstance(parameters, tuple):
            parameters = (parameters,)
        return self.__class__(parameters, origin=self, _root=True)


Union = _Union()


class _Optional(_TypingBase):
    """Optional type.

    Optional[X] is equivalent to Union[X, None].
    """

    __metaclass__ = TypingMeta
    __slots__ = ()

    @_tp_cache
    def __getitem__(self, arg):
        return Union[arg, type(None)]


Optional = _Optional()


class _Any(_TypingBase):
    """Special type indicating an unconstrained type.

    - Any is compatible with every type.
    - Any assumed to have all methods.
    - All values assumed to be instances of Any.

    Note that all the above statements are true from the point of view of
    static type checkers. At runtime, Any should not be used with instance
    or class checks.
    """
    __metaclass__ = TypingMeta
    __slots__ = ()

    def __instancecheck__(self, obj):
        raise TypeError("Any cannot be used with isinstance().")

    def __subclasscheck__(self, cls):
        raise TypeError("Any cannot be used with issubclass().")


Any = _Any()


def _gorg(a):
    """Return the farthest origin of a generic class (internal helper)."""
    assert isinstance(a, GenericMeta)
    while a.__origin__ is not None:
        a = a.__origin__
    return a


def _next_in_mro(cls):
    """Helper for Generic.__new__.

    Returns the class after the last occurrence of Generic or
    Generic[...] in cls.__mro__.
    """
    next_in_mro = object
    # Look for the last occurrence of Generic or Generic[...].
    for i, c in enumerate(cls.__mro__[:-1]):
        if isinstance(c, GenericMeta) and _gorg(c) is Generic:
            next_in_mro = cls.__mro__[i + 1]
    return next_in_mro


def _make_subclasshook(cls):
    """Construct a __subclasshook__ callable that incorporates
    the associated __extra__ class in subclass checks performed
    against cls.
    """
    if isinstance(cls.__extra__, abc.ABCMeta):
        # The logic mirrors that of ABCMeta.__subclasscheck__.
        # Registered classes need not be checked here because
        # cls and its extra share the same _abc_registry.
        def __extrahook__(cls, subclass):
            res = cls.__extra__.__subclasshook__(subclass)
            if res is not NotImplemented:
                return res
            if cls.__extra__ in getattr(subclass, '__mro__', ()):
                return True
            for scls in cls.__extra__.__subclasses__():
                # If we have fake typing and typing detect by module name
                if scls.__class__.__module__ == "typing":
                    continue
                if isinstance(scls, GenericMeta):
                    continue
                if issubclass(subclass, scls):
                    return True
            return NotImplemented
    else:
        # For non-ABC extras we'll just call issubclass().
        def __extrahook__(cls, subclass):
            if cls.__extra__ and issubclass(subclass, cls.__extra__):
                return True
            return NotImplemented
    return classmethod(__extrahook__)


class GenericMeta(TypingMeta, abc.ABCMeta):
    """Metaclass for generic types.

    This is a metaclass for typing.Generic and generic ABCs defined in
    typing module. User defined subclasses of GenericMeta can override
    __new__ and invoke super().__new__. Note that GenericMeta.__new__
    has strict rules on what is allowed in its bases argument:
    * plain Generic is disallowed in bases;
    * Generic[...] should appear in bases at most once;
    * if Generic[...] is present, then it should list all type variables
      that appear in other bases.
    In addition, type of all generic bases is erased, e.g., C[int] is
    stripped to plain C.
    """

    def __new__(cls, name, bases, namespace,
                args=None, origin=None, extra=None, orig_bases=None):
        """Create a new generic class. GenericMeta.__new__ accepts
        keyword arguments that are used for internal bookkeeping, therefore
        an override should pass unused keyword arguments to super().
        """
        initial_bases = bases
        if extra is None:
            extra = namespace.get('__extra__')
        if extra is not None and type(extra) is abc.ABCMeta and extra not in bases:
            bases = (extra,) + bases
        bases = tuple(_gorg(b) if isinstance(b, GenericMeta) else b for b in bases)

        # remove bare Generic from bases if there are other generic bases
        if any(isinstance(b, GenericMeta) and b is not Generic for b in bases):
            bases = tuple(b for b in bases if b is not Generic)
        namespace.update({'__origin__': origin, '__extra__': extra})
        self = super(GenericMeta, cls).__new__(cls, name, bases, namespace)

        self.__args__ = args
        # Speed hack (https://github.com/python/typing/issues/196).
        self.__next_in_mro__ = _next_in_mro(self)
        # Preserve base classes on subclassing (__bases__ are type erased now).
        if orig_bases is None:
            self.__orig_bases__ = initial_bases

        # This allows unparameterized generic collections to be used
        # with issubclass() and isinstance() in the same way as their
        # collections.abc counterparts (e.g., isinstance([], Iterable)).
        if (
            '__subclasshook__' not in namespace and extra or
            # allow overriding
            getattr(self.__subclasshook__, '__name__', '') == '__extrahook__'
        ):
            self.__subclasshook__ = _make_subclasshook(self)

        return self

    def __init__(self, *args, **kwargs):
        super(GenericMeta, self).__init__(*args, **kwargs)
        if isinstance(self.__extra__, abc.ABCMeta):
            self._abc_registry = self.__extra__._abc_registry
            self._abc_cache = self.__extra__._abc_cache
        elif self.__origin__ is not None:
            self._abc_registry = self.__origin__._abc_registry
            self._abc_cache = self.__origin__._abc_cache

    # _abc_negative_cache and _abc_negative_cache_version
    # realised as descriptors, since GenClass[t1, t2, ...] always
    # share subclass info with GenClass.
    # This is an important memory optimization.
    @property
    def _abc_negative_cache(self):
        if isinstance(self.__extra__, abc.ABCMeta):
            return self.__extra__._abc_negative_cache
        return _gorg(self)._abc_generic_negative_cache

    @_abc_negative_cache.setter
    def _abc_negative_cache(self, value):
        if self.__origin__ is None:
            if isinstance(self.__extra__, abc.ABCMeta):
                self.__extra__._abc_negative_cache = value
            else:
                self._abc_generic_negative_cache = value

    @property
    def _abc_negative_cache_version(self):
        if isinstance(self.__extra__, abc.ABCMeta):
            return self.__extra__._abc_negative_cache_version
        return _gorg(self)._abc_generic_negative_cache_version

    @_abc_negative_cache_version.setter
    def _abc_negative_cache_version(self, value):
        if self.__origin__ is None:
            if isinstance(self.__extra__, abc.ABCMeta):
                self.__extra__._abc_negative_cache_version = value
            else:
                self._abc_generic_negative_cache_version = value

    @_tp_cache
    def __getitem__(self, params):
        if not isinstance(params, tuple):
            params = (params,)
        prepend = (self,) if self.__origin__ is None else ()
        return self.__class__(self.__name__,
                              prepend + self.__bases__,
                              dict(self.__dict__),
                              args=params,
                              origin=self,
                              extra=self.__extra__,
                              orig_bases=self.__orig_bases__)

    def __subclasscheck__(self, cls):
        if self.__origin__ is not None:
            if sys._getframe(1).f_globals['__name__'] not in ['abc', 'functools']:
                raise TypeError("Parameterized generics cannot be used with class "
                                "or instance checks")
            return False
        if self is Generic:
            raise TypeError("Class %r cannot be used with class "
                            "or instance checks" % self)
        return super(GenericMeta, self).__subclasscheck__(cls)

    def __instancecheck__(self, instance):
        # Since we extend ABC.__subclasscheck__ and
        # ABC.__instancecheck__ inlines the cache checking done by the
        # latter, we must extend __instancecheck__ too. For simplicity
        # we just skip the cache check -- instance checks for generic
        # classes are supposed to be rare anyways.
        if not isinstance(instance, type):
            return issubclass(instance.__class__, self)
        return False


# Prevent checks for Generic to crash when defining Generic.
Generic = None


def _generic_new(base_cls, cls, *args, **kwds):
    # Assure type is erased on instantiation,
    # but attempt to store it in __orig_class__
    if cls.__origin__ is None:
        return base_cls.__new__(cls)
    else:
        origin = _gorg(cls)
        obj = base_cls.__new__(origin)
        try:
            obj.__orig_class__ = cls
        except AttributeError:
            pass
        obj.__init__(*args, **kwds)
        return obj


class Generic(object):  # type: ignore
    __metaclass__ = GenericMeta
    __slots__ = ()

    def __new__(cls, *args, **kwds):
        return _generic_new(cls.__next_in_mro__, cls, *args, **kwds)


def _overload_dummy(*args, **kwds):
    raise NotImplementedError()


def overload(func):
    return _overload_dummy


class Iterable(Generic[T]):  # type: ignore
    __slots__ = ()
    __extra__ = collections.Iterable


class Container(Generic[T]):  # type: ignore
    __slots__ = ()
    __extra__ = collections.Container


class Sequence(collections.Sized, Iterable[T], Container[T]):  # type: ignore
    __slots__ = ()
    __extra__ = collections.Sequence


# NOTE: It is only covariant in the value type.
class Mapping(collections.Sized, Iterable[KT], Container[KT], Generic[KT, VT_co]):
    __slots__ = ()
    __extra__ = collections.Mapping


TYPE_CHECKING = False
