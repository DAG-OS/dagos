import functools
import inspect


def yield_step(f):
    """Required because pytest-bdd does not correctly implement pytest fixtures.
    See: https://github.com/pytest-dev/pytest-bdd/issues/392"""

    @functools.wraps(f)
    def wrapper(request, *args, **kwargs):
        gen = f(*args, **kwargs)

        request.addfinalizer(lambda: next(gen))

        return next(gen)

    # Add the parameter "request" to the signature of the wrapper function, so that it will be injected
    sig = inspect.signature(f)
    request_param = inspect.Parameter(
        "request", kind=inspect.Parameter.POSITIONAL_OR_KEYWORD
    )
    sig = sig.replace(parameters=list(sig.parameters.values()) + [request_param])
    wrapper.__signature__ = sig

    return wrapper
