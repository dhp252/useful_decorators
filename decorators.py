# also available through the world wide web at this URL:
# http://opensource.org/licenses/OSL-3.0
# If you did not receive a copy of the license and are unable to obtain it
# Copyright (c) 2008 - 2013, EllisLab, Inc. (http://ellislab.com/)
# http://opensource.org/licenses/OSL-3.0 Open Software License (OSL 3.0)


import os
import time
import functools


def _repr_func(func):
    return f'{func.__name__}() in {func.__code__.co_filename}, ' \
        f'line {func.__code__.co_firstlineno}'


def chdir_back_and_forth(func):
    """ Temporarily change dir to `path` in the function, then return back to the original cwd
    wrapped function must have "path" as its first positional argument"""
    from pathlib import Path

    def wrapper(path,*agrs,**kwargs):
        old_cwd = os.getcwd()
        path    = Path(path)
        new_cwd = path.parent
        os.chdir(new_cwd)
        func(path,*agrs,**kwargs)
        os.chdir(old_cwd)
    return wrapper


def timing(func=None, *, activate=True, return_time=False, factor=1000,
           split_before=False, split_after=False, times=1):
    """Print out the running time of the function, support repeated run
    Will do nothing if activate = False
    Result is in second.

    example 1:
    >>> @timing(activate=True)
    >>> def test():
    >>>     sleep(0.1)
    >>>     return 'yay'
    >>> test()
    Runtime of test                           100.38185 ms
    'yay'

    example 2:
    >>> @timing(activate=True)
    >>> def crop(): ...
    >>>
    >>> @timing(activate=True)
    >>> def remove_text(): ...
    >>>
    >>> @timing(activate=True, split_after=True)
    >>> def full_flow(): ... # include crop() and remove_text()
    >>>
    >>> full_flow()
    Runtime of crop                           146.19160 ms
    Runtime of remove_text                   3316.30707 ms
    Runtime of full_flow                     4403.89156 ms
    ######################### 0 ##########################
    Runtime of crop                            72.94130 ms
    Runtime of remove_text                   1034.61838 ms
    Runtime of full_flow                     1443.43138 ms
    ######################### 1 ##########################
    """
    def decor_timing(func):
        time_run = 0
        @functools.wraps(func)
        def wrap_func(*args,**kwargs):
            nonlocal time_run

            time1 = time.time()
            for _ in range(times):
                ret = func(*args,**kwargs)
            time2 = time.time()
            run_time = time2 - time1

            if split_before:
                print(f"{' '+str(time_run)+' ':#^54}")
                time_run +=1

            ti = '' if times==1 else f"x{times} "
            print('Runtime of {}{:<30s}{:>10.5f} ms'.format(ti,
                func.__name__, run_time*factor))

            if split_after:
                print(f"{' '+str(time_run)+' ':#^54}")
                time_run +=1

            if return_time:
                return run_time*factor
            else:
                return ret
        if activate:
            return wrap_func
        else:
            return func

    if func is None:
        return decor_timing
    else:
        return decor_timing(func)


class Timing():

    def __init__(self, activate=True, return_time=False, factor=1000,
                 split_before=False, split_after=False, times=1):
        """Similar to timing()
        example 1:
        >>> @Timing(activate=True)
        >>> def test():
        >>>     sleep(0.1)
        >>>     return 'yay'
        >>> test()
        test() runtime:                           100.38185 ms
        'yay'

        example 2:
        >>> @Timing(activate=True, split_after=True)
        >>> def full_flow():
            ...
        Runtime of crop                           146.19160 ms
        Runtime of remove_text                   3316.30707 ms
        Runtime of full_flow                     4403.89156 ms
        ######################### 0 ##########################
        Runtime of crop                            72.94130 ms
        Runtime of remove_text                   1034.61838 ms
        Runtime of full_flow                     1443.43138 ms
        ######################### 1 ##########################
        """
        self.activate = activate
        self.return_time = return_time
        self.factor = factor
        self.time_run = 0
        self.split_before = split_before
        self.split_after = split_after
        self.times = times
    def __call__(self, func):

        @functools.wraps(func)
        def wrap_func(*args,**kwargs):
            time1 = time.time()
            for _ in range(self.times):
                ret = func(*args,**kwargs)
            time2 = time.time()
            run_time = time2 - time1

            if self.split_before:
                print(f"{' '+str(self.time_run)+' ':#^54}")
                self.time_run +=1
            ti = '' if times==1 else f"x{self.times} "
            print('Runtime of {}{:<30s}{:>10.5f} ms'.format(ti,
                func.__name__, run_time*self.factor))

            if self.split_after:
                print(f"{' '+str(self.time_run)+' ':#^54}")
                self.time_run +=1

            if self.return_time:
                return run_time*self.factor
            else:
                return ret

        if self.activate:
            return wrap_func
        else:
            return func


def deprecated(text:str=None, print_only=False):
    """Raise exception or print out the deprecated warning for the function
    example:
    >>> @deprecated('Consider to use do_sth_else')
    >>> def do_sth():
    >>>     return None
    ...
    DeprecationWarning: 'Consider to use do_sth_else'
    """
    def inner(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if print_only:
                print(f'DeprecationWarning: {_repr_func(func)}: {text}')
            else:
                raise DeprecationWarning(text)
            return func(*args, **kwargs)
        return wrapper
    return inner


def pass_except(print_exception=False):
    """Ignore exceptions raised in the function
    ! Caution: traceback printing can be delayed

    example:
    >>> @pass_except(True)
    >>> def do_sth(): assert False
    >>> do_sth()
    >>> print('this line should be printed last')
    this line should be printed last
    File "<ipython-input-73-1eb3a89b6b11>", line 10, in wrapper
        result = func(*args, **kwargs)
    File "<ipython-input-73-1eb3a89b6b11>", line 19, in do_sth
        assert False
    """
    import traceback
    def inner(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if print_exception:
                    traceback.print_tb(e.__traceback__)
        return wrapper
    return inner


def repeat(n=1):
    """Repeat a function `n` times

    example:
    >>> a = 10
    >>> @repeat(2)
    >>> def do_sth():
    >>>     global a
    >>>     a += 1
    >>>     print(a)
    >>>     return a
    >>> print('final return:',do_sth())
    11
    12
    final return: 12
    """
    assert n>=1 and isinstance(n, int)

    def inner(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = None
            for _ in range(n):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return inner


def slow_down(delay=1):
    """Pause/sleep/delay in specified seconds after the function is finished
    `delay` unit is second
    example
    >>> from general.decorator import timing, slow_down
    >>> @timing
    >>> @slow_down(1)
    >>> def do_sth():
    >>>     print('run')
    >>> do_sth()
    run
    Runtime of do_sth                        1001.39403 ms
    """
    from time import sleep
    def inner(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            sleep(delay)
            return result
        return wrapper
    return inner


def retry(n=1, exception=Exception):
    """Allow function to have `n` time errors
    example:
    >>> a = 0
    >>> @retry(3)
    >>> def do_sth():
    >>>     global a
    >>>     while a < 2:
    >>>         a+=1
    >>>         raise ValueError
    >>>     print('done')
    >>> do_sth()
    done
    """
    def inner(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(n):
                try:
                    return func(*args, **kwargs)
                except exception:
                    continue
            raise ValueError(f'{_repr_func(func)} exceeds {n} retries')
        return wrapper
    return inner


def limit_run(n=None):
    """Raise RuntimeError if a function run exceeds `n` times
    example:
    >>> @limit_run(2)
    >>> def do_sth():
    >>>     print('run')
    >>> for _ in range(3):
    >>>     do_sth()
    run
    run
    ...
    RuntimeError: do_sth in __main__ exceeds maximum run of 2 times
    """
    def inner(func):
        times_left = n
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal times_left
            if n is None:
                return func(*args, **kwargs)
            elif times_left > 0:
                times_left -= 1
                return func(*args, **kwargs)
            else:
                raise RuntimeError(f'{_repr_func(func)} '\
                    f'exceeds maximum run of {n} times')
        return wrapper
    return inner


def timeout(seconds, error_message = 'Function call timed out'):
    """ Raise RuntimeError if a function run exceeds an time interval
    example:
    >>> @timeout(1)
    >>> def a():
    >>>     sleep(1.5)
    >>> a()
    RuntimeError: Function call timed out
    """
    import signal

    def decorated(func):
        def _handle_timeout(signum, frame):
            raise RuntimeError(error_message)
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result
        return functools.wraps(func)(wrapper)
    return decorated


# TODO
def memorize():
    # check python default
    pass


def reduce_query(file_path=None, always_query=False):
    """A decorator to reduce the number of query by store in file and in memory if they are up-to-date
    Args:
        - file_path: str
            path to store temporary file
        - always_query: bool
            if true, ignore all other stuff and always execute the query
    NOTE: The decorated function must return a pandas.DataFrame

    Example:
    >>> @reduce_query("")
    >>> def query_sth():
    >>>     return df
    """
    def inner(func):
        df      = None
        df_date = None

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal file_path
            nonlocal df
            nonlocal df_date
            nonlocal always_query

            if always_query:
                return func(*args, **kwargs)

            try:
                file_date = os.path.getmtime(file_path)
                file_date = datetime.datetime.fromtimestamp(file_date).date()       
            except FileNotFoundError:
                file_date = None

            is_file_up_to_date = file_date == datetime.datetime.now().date()
            is_mem_up_to_date  = df_date   == datetime.datetime.now().date()

            if is_mem_up_to_date:
                if not is_file_up_to_date:
                    df.to_csv(file_path, index=False)
            elif is_file_up_to_date:
                df = pd.read_csv(file_path)
                df_date = file_date
            else:
                df = func(*args, **kwargs)
                df.to_csv(file_path, index=False)
                df_date = datetime.datetime.now().date()
            return df
        return wrapper
    return inner


def override_args(*override_args, **override_kwargs):
    """Override default keyword arguments of the function
    """
    def outer(f):
        def inner(*args, **kwargs):
            min_args_length = min(len(args), len(override_args))
            args = list(args)
            for i in range(min_args_length):
                args[i] = override_args[i]
            kwargs.update(override_kwargs)
            return f(*args, **kwargs)
        return inner
    return outer

"""@override('Cat', 'male', k1='0')
def my_function(animal, **kwargs):
    print(animal)
    print(kwargs)"""


def force_input_arg(*kwargs_to_force, **kwargs):
    """Raise TypeError if `kwargs_to_force` is not passed in to function as kwargs
    example:
    >>> @force_input_arg('a')
    >>> def test_func(a=None):
    >>>     print(a)
    >>> test_func(a=10)
    10
    >>> test_func()
    ...
    TypeError: Keyword argument `a` must be passed
    """

    def inner(func):
        if kwargs != {}:
            example_input = ', '.join([f"'{k}'" for k in kwargs.keys()])
            txt = f"{func.__name__}({example_input})"
            raise ValueError('Only pass positional argument as key name of '\
                             f'forced kwargs.\nExample: {txt}')

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for k in kwargs_to_force:
                if k not in kwargs.keys():
                    raise TypeError(f'Keyword argument `{k}` must be passed')
            return func(*args, **kwargs)
        return wrapper
    return inner


def accepts(*types, **kw):
    '''Function decorator. Checks decorated function's arguments are
    of the expected types.

    Parameters:
    types -- The expected types of the inputs to the decorated function.
             Must specify type for each parameter.
    kw    -- Optional specification of 'debug' level (this is the only valid
             keyword argument, no other should be given).
             debug = ( 0 | 1 | 2 )
    example:
    >>> @accepts(str)
    >>> def test(a:str):
    >>>     return a
    >>> test(1)
    "TypeWarning:  'test' method accepts (str), but was given (int)"
    '''
    if not kw:
        # default level: MEDIUM
        debug = 1
    else:
        debug = kw['debug']
    try:
        def decorator(f):
            def newf(*args):
                if debug == 0:
                    return f(*args)
                assert len(args) == len(types)
                argtypes = tuple(map(type, args))
                if argtypes != types:
                    msg = info(f.__name__, types, argtypes, 0)
                    if debug == 1:
                        print(sys.stderr, 'TypeWarning: ', msg)
                    elif debug == 2:
                        raise TypeError(msg)
                return f(*args)
            newf.__name__ = f.__name__
            return newf
        return decorator
    except KeyError(key):
        raise KeyError(key + "is not a valid keyword argument")
    except TypeError(msg):
        raise TypeError(msg)


def returns(ret_type, **kw):
    '''Function decorator. Checks decorated function's return value
    is of the expected type.

    Parameters:
    ret_type -- The expected type of the decorated function's return value.
                Must specify type for each parameter.
    kw       -- Optional specification of 'debug' level (this is the only valid
                keyword argument, no other should be given).
                debug=(0 | 1 | 2)
    example:
    >>> @accepts(str)
    >>> @returns(str)
    >>> def test(a:str):
    >>>     return a
    >>> test(1)
    "TypeWarning:  'test' method returns (str), but result is (int)"
    '''
    try:
        if not kw:
            # default level: MEDIUM
            debug = 1
        else:
            debug = kw['debug']
        def decorator(f):
            def newf(*args):
                result = f(*args)
                if debug == 0:
                    return result
                res_type = type(result)
                if res_type != ret_type:
                    msg = info(f.__name__, (ret_type,), (res_type,), 1)
                    if debug == 1:
                        print(sys.stderr, 'TypeWarning: ', msg)
                    elif debug == 2:
                        raise TypeError(msg)
                return result
            newf.__name__ = f.__name__
            return newf
        return decorator
    except KeyError(key):
        raise KeyError(key + "is not a valid keyword argument")
    except TypeError(msg):
        raise TypeError(msg)


#TODO: move this function into accepts and returns
def info(fname, expected, actual, flag):
    '''Convenience function returns nicely formatted error/warning msg.'''
    format = lambda types: ', '.join([str(t).split("'")[1] for t in types])
    expected, actual = format(expected), format(actual)
    msg = "'{}' method ".format( fname )\
          + ("accepts", "returns")[flag] + " ({}), but ".format(expected)\
          + ("was given", "result is")[flag] + " ({})".format(actual)
    return msg


def wip_warning(text:str='Unexpected behavior might occur', print_only=True):
    """Print or raise WorkInProcessWarning exception if the function is called
    example:
    >>> @wip_warning()
    >>> def do_sth():
    >>>     return None
    ...
    WorkInProcessWarning: do_sth() in ..., line ... :Unexpected behavior might occur
    """

    class WorkInProcessWarning(Exception):
        pass

    def inner(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if print_only:
                print(f'WorkInProcessWarning: {_repr_func(func)}: {text}')
            else:
                raise WorkInProcessWarning(text)
            return func(*args, **kwargs)
        return wrapper
    return inner


def protected_symbol():
    pass # warn for calling protected symbol outside module.


if __name__=='__main__':
    def do_sth(b=100):
        print('a')
        print(b)
        return "bla"

    result = timing(do_sth)('oh')
    print(result)
