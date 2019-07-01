import sys
import os


def find_caller_class(filename):
    print(filename)
    """
    Find the stack frame of the caller
    """
    f = sys._getframe(1)
    while hasattr(f, "f_code"):
        co = f.f_code
        this_file = os.path.normcase(co.co_filename)
        if filename == this_file:
            f = f.f_back
            continue
        break

    result = f.f_locals['self']
    return result
