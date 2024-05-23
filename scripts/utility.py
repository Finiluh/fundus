import _thread as thread
import threading
from functools import wraps
from typing import Callable, Literal, Optional, TypeVar, overload

from typing_extensions import ParamSpec

P = ParamSpec("P")
T = TypeVar("T")


def _interrupt_handler() -> None:
    thread.interrupt_main()


@overload
def timeout(func: Callable[P, T], time: float, silent: Literal[False] = ...) -> Callable[P, T]:
    ...


@overload
def timeout(func: Callable[P, T], time: float, silent: Literal[True]) -> Callable[P, Optional[T]]:
    ...


def timeout(func: Callable[P, T], time: float, silent: bool = False) -> Callable[P, Optional[T]]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Optional[T]:
        # register interrupt handler
        timer = threading.Timer(time, _interrupt_handler)

        try:
            timer.start()
            result = func(*args, **kwargs)
        except KeyboardInterrupt as err:
            if silent:
                return None
            else:
                raise TimeoutError from err
        finally:
            timer.cancel()
        return result

    return wrapper
