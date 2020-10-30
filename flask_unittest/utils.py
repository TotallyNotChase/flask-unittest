import functools


def _partialclass(cls, *args, **kwds):
    '''
    Return a partially constructed class from given class

    Essentially the same `functools.partial` but for classes
    
    from: https://stackoverflow.com/a/38911383/10305477
    '''
    class NewCls(cls):
        __init__ = functools.partialmethod(cls.__init__, *args, **kwds)

    return NewCls
