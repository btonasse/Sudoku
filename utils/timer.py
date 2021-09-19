import time
from typing import Callable

def timefunc(func: Callable, *args, **kwargs) -> float:
    '''
    Wrapper around a function that returns execution time instead of return value
    '''
    start = time.perf_counter()
    func(*args, **kwargs)
    stop = time.perf_counter()
    runtime = stop-start
    return runtime

