from functools import wraps

import errno


def enoent_means_false(func):
    """Return False if function raises IOError with errno == ENOENT."""
    @wraps(func)
    def _func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IOError as e:
            if e.errno == errno.ENOENT:
                return False
            else:
                raise
    return _func
