import asyncio
import concurrent.futures
from functools import partial
import inspect
from modulefinder import ModuleFinder
import os
import sys
import __main__


class Collector:

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)

    """
    Modules collector
    """

    __filter__ = [
        "tf",  # Tensorflow
        "torch",  # PyTorch
        "sklearn",  # Scikit
        "keras",  # Keras
        "mxnet",  # MXNet
        "numpy",  # NumPy
        "scipy",  # SciPy
        "sklearn",  # Scikit,
        "theano",  # Theano
        "pandas",  # Pandas
    ]

    @staticmethod
    async def get_cfp(real: bool = False) -> str:
        frame = inspect.stack()[1]
        p = frame[0].f_code.co_filename
        if real:
            return os.path.realpath(p)
        return p

    @classmethod
    async def apply_filter(cls, modules):
        result = list()
        for i in cls.__filter__:
            for j in modules:
                if i in j:
                    result.append(i)
                    break
        return result

    @classmethod
    async def run_async(cls, func, *args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        if executor is None:
            executor = cls.executor
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)

    @staticmethod
    def _fallback():
        for m in sys.modules.values():
            if m:
                yield m.__name__

    @classmethod
    async def indirect(cls, file=None, use_cfp=False, f_simplify=True):
        if file is None:
            if not use_cfp:
                file = __main__.__file__
            else:
                file = await cls.get_cfp()
        try:
            finder = ModuleFinder()
            await cls.run_async(finder.run_script, file)
            m = finder.modules.keys()
        except AttributeError:
            # try to bypass 40350/84530 ns mod issue
            # pls see following for details

            # https://bugs.python.org/issue40350
            # https://github.com/python/cpython/issues/84530
            # https://github.com/python/cpython/pull/19917
            # https://github.com/python/cpython/pull/29196
            m = await cls.run_async(cls._fallback)
        if f_simplify:
            mods = await cls.apply_filter(m)
        else:
            mods = m
        for name in mods:
            await asyncio.sleep(0)
            yield name

    @classmethod
    async def get_imports(cls):
        return [i async for i in cls.indirect()]
