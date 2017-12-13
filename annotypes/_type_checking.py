# don't depend on the typing module to see if we are type checking
try:
    from typing import TYPE_CHECKING
except ImportError:
    # If there is no typing module we're definitely not type checking!
    TYPE_CHECKING = False
