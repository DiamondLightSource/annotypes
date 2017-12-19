from __future__ import absolute_import, unicode_literals

import abc
import functools
import sys
import collections as collections_abc


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


def _get_type_vars(types, tvars):
    for t in types:
        if isinstance(t, TypingMeta) or isinstance(t, _TypingBase):
            t._get_type_vars(tvars)


def _type_vars(types):
    tvars = []
    _get_type_vars(types, tvars)
    return tuple(tvars)


def _eval_type(t, globalns, localns):
    if isinstance(t, TypingMeta) or isinstance(t, _TypingBase):
        return t._eval_type(globalns, localns)
    return t


def _type_check(arg, msg):
    """Check that the argument is a type, and return it (internal helper).

    As a special case, accept None and return type(None) instead.
    Also, _TypeAlias instances (e.g. Match, Pattern) are acceptable.

    The msg argument is a human-readable error message, e.g.

        "Union[arg, ...]: arg should be a type."

    We append the repr() of the actual value (truncated to 100 chars).
    """
    if arg is None:
        return type(None)
    if (
        isinstance(arg, _TypingBase) and type(arg).__name__ == '_ClassVar' or
        not isinstance(arg, (type, _TypingBase)) and not callable(arg)
    ):
        raise TypeError(msg + " Got %.100r." % (arg,))
    # Bare Union etc. are not valid as type arguments
    if (
        type(arg).__name__ in ('_Union', '_Optional') and
        not getattr(arg, '__origin__', None) or
        isinstance(arg, TypingMeta) and _gorg(arg) in (Generic,)
    ):
        raise TypeError("Plain %s is not valid as type argument" % arg)
    return arg


class TypeVar(_TypingBase):
    """Type variable.

    Usage::

      T = TypeVar('T')  # Can be anything
      A = TypeVar('A', str, bytes)  # Must be str or bytes

    Type variables exist primarily for the benefit of static type
    checkers.  They serve as the parameters for generic types as well
    as for generic function definitions.  See class Generic for more
    information on generic types.  Generic functions work as follows:

      def repeat(x: T, n: int) -> List[T]:
          '''Return a list containing n references to x.'''
          return [x]*n

      def longest(x: A, y: A) -> A:
          '''Return the longest of two strings.'''
          return x if len(x) >= len(y) else y

    The latter example's signature is essentially the overloading
    of (str, str) -> str and (bytes, bytes) -> bytes.  Also note
    that if the arguments are instances of some subclass of str,
    the return type is still plain str.

    At runtime, isinstance(x, T) and issubclass(C, T) will raise TypeError.

    Type variables defined with covariant=True or contravariant=True
    can be used do declare covariant or contravariant generic types.
    See PEP 484 for more details. By default generic types are invariant
    in all type variables.

    Type variables can be introspected. e.g.:

      T.__name__ == 'T'
      T.__constraints__ == ()
      T.__covariant__ == False
      T.__contravariant__ = False
      A.__constraints__ == (str, bytes)
    """

    __metaclass__ = TypingMeta
    __slots__ = ('__name__', '__bound__', '__constraints__',
                 '__covariant__', '__contravariant__')

    def __init__(self, name, *constraints, **kwargs):
        super(TypeVar, self).__init__(name, *constraints, **kwargs)
        bound = kwargs.get('bound', None)
        covariant = kwargs.get('covariant', False)
        contravariant = kwargs.get('contravariant', False)
        self.__name__ = name
        if covariant and contravariant:
            raise ValueError("Bivariant types are not supported.")
        self.__covariant__ = bool(covariant)
        self.__contravariant__ = bool(contravariant)
        if constraints and bound is not None:
            raise TypeError("Constraints cannot be combined with bound=...")
        if constraints and len(constraints) == 1:
            raise TypeError("A single constraint is not allowed")
        msg = "TypeVar(name, constraint, ...): constraints must be types."
        self.__constraints__ = tuple(_type_check(t, msg) for t in constraints)
        if bound:
            self.__bound__ = _type_check(bound, "Bound must be a type.")
        else:
            self.__bound__ = None

    def _get_type_vars(self, tvars):
        if self not in tvars:
            tvars.append(self)

    def __instancecheck__(self, instance):
        raise TypeError("Type variables cannot be used with isinstance().")

    def __subclasscheck__(self, cls):
        raise TypeError("Type variables cannot be used with issubclass().")


# Some unconstrained type variables.  These are used by the container types.
# (These are not for export.)
T = TypeVar('T')  # Any type.
T_co = TypeVar('T_co', covariant=True)  # Any type covariant containers.


def _replace_arg(arg, tvars, args):
    """An internal helper function: replace arg if it is a type variable
    found in tvars with corresponding substitution from args or
    with corresponding substitution sub-tree if arg is a generic type.
    """

    if tvars is None:
        tvars = []
    if isinstance(arg, TypeVar):
        for i, tvar in enumerate(tvars):
            if arg == tvar:
                return args[i]
    return arg


# Special typing constructs Union, Optional, Generic, Callable and Tuple
# use three special attributes for internal bookkeeping of generic types:
# * __parameters__ is a tuple of unique free type parameters of a generic
#   type, for example, Dict[T, T].__parameters__ == (T,);
# * __origin__ keeps a reference to a type that was subscripted,
#   e.g., Union[T, int].__origin__ == Union;
# * __args__ is a tuple of all arguments used in subscripting,
#   e.g., Dict[T, int].__args__ == (T, int).




def _check_generic(cls, parameters):
    # Check correct count for parameters of a generic cls (internal helper).
    if not cls.__parameters__:
        raise TypeError("%s is not a generic class" % repr(cls))
    alen = len(parameters)
    elen = len(cls.__parameters__)
    if alen != elen:
        raise TypeError("Too %s parameters for %s; actual %s, expected %s" %
                        ("many" if alen > elen else "few", repr(cls), alen, elen))


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
    __slots__ = ('__parameters__', '__args__', '__origin__', '__tree_hash__')

    def __new__(cls, parameters=None, origin=None, *args, **kwds):
        self = super(_Union, cls).__new__(cls, parameters, origin, *args, **kwds)
        if origin is None:
            self.__parameters__ = None
            self.__args__ = None
            self.__origin__ = None
            self.__tree_hash__ = hash(frozenset(('Union',)))
            return self
        if not isinstance(parameters, tuple):
            raise TypeError("Expected parameters=<tuple>")
        if origin is Union:
            # It's not a union if there's only one type left.
            if len(parameters) == 1:
                return parameters[0]
        self.__parameters__ = _type_vars(parameters)
        self.__args__ = parameters
        self.__origin__ = origin
        return self

    def _eval_type(self, globalns, localns):
        if self.__args__ is None:
            return self
        ev_args = tuple(_eval_type(t, globalns, localns) for t in self.__args__)
        ev_origin = _eval_type(self.__origin__, globalns, localns)
        if ev_args == self.__args__ and ev_origin == self.__origin__:
            # Everything is already evaluated.
            return self
        return self.__class__(ev_args, ev_origin, _root=True)

    def _get_type_vars(self, tvars):
        if self.__origin__ and self.__parameters__:
            _get_type_vars(self.__parameters__, tvars)

    @_tp_cache
    def __getitem__(self, parameters):
        if parameters == ():
            raise TypeError("Cannot take a Union of no types.")
        if not isinstance(parameters, tuple):
            parameters = (parameters,)
        if self.__origin__ is None:
            msg = "Union[arg, ...]: each arg must be a type."
        else:
            msg = "Parameters to generic types must be types."
        parameters = tuple(_type_check(p, msg) for p in parameters)
        if self is not Union:
            _check_generic(self, parameters)
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
        arg = _type_check(arg, "Optional[t] requires a single type.")
        return Union[arg, type(None)]


Optional = _Optional()


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
                tvars=None, args=None, origin=None, extra=None, orig_bases=None):
        """Create a new generic class. GenericMeta.__new__ accepts
        keyword arguments that are used for internal bookkeeping, therefore
        an override should pass unused keyword arguments to super().
        """
        if tvars is not None:
            # Called from __getitem__() below.
            assert origin is not None
            assert all(isinstance(t, TypeVar) for t in tvars), tvars
        else:
            # Called from class statement.
            assert tvars is None, tvars
            assert args is None, args
            assert origin is None, origin

            # Get the full set of tvars from the bases.
            tvars = _type_vars(bases)
            # Look for Generic[T1, ..., Tn].
            # If found, tvars must be a subset of it.
            # If not found, tvars is it.
            # Also check for and reject plain Generic,
            # and reject multiple Generic[...].
            for base in bases:
                if (isinstance(base, GenericMeta) and
                        base.__origin__ is Generic):
                    tvars = base.__parameters__

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

        self.__parameters__ = tvars
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

    def _get_type_vars(self, tvars):
        if self.__origin__ and self.__parameters__:
            _get_type_vars(self.__parameters__, tvars)

    @_tp_cache
    def __getitem__(self, params):
        if not isinstance(params, tuple):
            params = (params,)
        msg = "Parameters to generic types must be types."
        params = tuple(_type_check(p, msg) for p in params)
        if self is Generic:
            tvars = params
            args = params
        else:
            # Subscripting a regular Generic subclass.
            _check_generic(self, params)
            tvars = _type_vars(params)
            args = params

        prepend = (self,) if self.__origin__ is None else ()
        return self.__class__(self.__name__,
                              prepend + self.__bases__,
                              dict(self.__dict__),
                              tvars=tvars,
                              args=args,
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


class Generic(object):
    __metaclass__ = GenericMeta
    __slots__ = ()

    def __new__(cls, *args, **kwds):
        return _generic_new(cls.__next_in_mro__, cls, *args, **kwds)


def _overload_dummy(*args, **kwds):
    raise NotImplementedError()


def overload(func):
    return _overload_dummy


class Iterable(Generic[T_co]):
    __slots__ = ()
    __extra__ = collections_abc.Iterable


class Container(Generic[T_co]):
    __slots__ = ()
    __extra__ = collections_abc.Container


class Sequence(collections_abc.Sized, Iterable[T_co], Container[T_co]):
    __slots__ = ()
    __extra__ = collections_abc.Sequence


TYPE_CHECKING = False
