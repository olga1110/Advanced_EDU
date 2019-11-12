#!/usr/bin/env python
# -*- coding: utf-8 -*-


from functools import update_wrapper


# class disable:
#
#     def __init__(self, enabled_func):
#         self._enabled=False
#         self._enabled_func=enabled_func
#
# 	@property
# 	def enabled(self):
# 		return self._enabled
#
# 	@enabled.setter
# 	def enabled(self, new_value):
# 		if not isinstance(new_value, bool):
# 			raise ValueError('can only be set boolean value')
# 		self._enabled=new_value
#
# 	def __call__(self, target):
# 		if self._enabled:
# 			return self._enabled_func(target)
# 		return target
# 
# countcalls=SwitchDec(countcalls)
# 
# countcalls.enabled=True


# def decorator(d):
#     '''
#         Decorate a decorator so that it inherits the docstrings
#         and stuff from the function it's decorating.
#         '''
#     def wrapper(fn):
#         return update_wrapper(d(fn), fn)
#     update_wrapper(wrapper, d)
#     return wrapper


def disable(fn):
    '''
    Disable a decorator by re-assigning the decorator's name
    to this function. For example, to turn off memoization:

    >>> memo = disable

    '''

    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)

    return wrapper


def countcalls(fn):
    '''Decorator that counts calls made to the function decorated.'''
    fn.calls = 0
    def wrapper(*args, **kwargs):
        # setattr(fn, 'calls', 0)
        fn.calls += 1
        wrapper.calls = fn.calls
        res = fn(*args, **kwargs)
        print(f'func {fn.__name__} was called {fn.calls} times')
        return res
    update_wrapper(wrapper, fn)
    return wrapper


# @decorator
def memo(fn):
    '''
        Memoize a function so that it caches all return values for
        faster future lookups.
    '''
    memo_data = {}
    def wrapper(*args, **kwargs):
        if args in memo_data:
            print('The value was get from the cache')
            return memo_data[args]
        else:
            rv = fn(*args, **kwargs)
            memo_data[args] = rv
            print('The value was calculated')
            return rv
    update_wrapper(wrapper, fn)
    return wrapper


# @decorator
def n_ary(fn):
    '''
    Given binary function f(x, y), return an n_ary function such
    that f(x, y, z) = f(x, f(y,z)), etc. Also allow f(x) = x.
    '''
    def n_ary_f(x, *args):
        return x if not args else fn(x, n_ary_f(*args))
    update_wrapper(n_ary_f, fn)
    return n_ary_f


# @decorator
def trace(param):
    '''Trace calls made to function decorated.

        @trace("____")
        def fib(n):
            ....
        >>> fib(3)
         --> fib(3)
        ____ --> fib(2)
        ________ --> fib(1)
        ________ <-- fib(1) == 1
        ________ --> fib(0)
        ________ <-- fib(0) == 1
        ____ <-- fib(2) == 2
        ____ --> fib(1)
        ____ <-- fib(1) == 1
         <-- fib(3) == 3

        '''
    def wrap(fn):
        def wrapper(*args, **kwargs):
            f_a = f'{fn.__name__}({args})'
            print(f'{param*trace.level} --> {f_a}')
            trace.level += 1
            try:
                res = fn(*args, **kwargs)
                print(f'{param*(trace.level-1)} <-- {f_a} == {res}')
                return res
            finally:
                trace.level -= 1
        trace.level = 0
        update_wrapper(wrapper, fn)
        return wrapper
    return wrap

# countcalls = disable

@memo
@countcalls
@n_ary
def foo(a, b):
    return a + b


@countcalls
@memo
@n_ary
def bar(a, b):
    return a * b


@countcalls
@n_ary
@memo
def bar(a, b):
    return a * b


@countcalls
@trace("####")
@memo
def fib(n):
    """Some doc"""
    return 1 if n <= 1 else fib(n-1) + fib(n-2)


def main():
    print(foo(4, 3))
    print(foo(4, 3, 2))
    print(foo(4, 3))
    print("foo was called", foo.calls, "times")

    print(bar(4, 3))
    print(bar(4, 3, 2))
    print(bar(4, 3, 2, 1))
    print("bar was called", bar.calls, "times")

    print(fib.__doc__)
    fib(3)
    print(fib.calls, 'calls made')


if __name__ == '__main__':
    main()
