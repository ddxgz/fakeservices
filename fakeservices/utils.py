import logging
import time
import math
from datetime import datetime, timedelta, tzinfo
# import cProfile, pstats, cStringIO
import functools
import inspect
import os
import sys

try:
    from . import config as conf
except:
    print('cannot import config')
    # import config as conf


def advance_logger(loglevel):
    def get_line_number():
        return inspect.currentframe().f_back.f_back.f_lineno

    def _basic_log(func, result, *args, **kwargs):
        print('function   = %s' % func.__name__)
        print('    arguments = {0}  {1}'.format(args, kwargs))
        print('    return    = {0}'.format(result))

    def info_log_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            _basic_log(func, result, args, kwargs)

        return wrapper

    def debug_log_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            time_start = time.time()
            result = func(*args, **kwargs)
            time_end = time.time()
            _basic_log(func, result, args, kwargs)
            print('   time    = %.6f sec' % (time_end - time_start))
            print('   called_from_line : %s' % str(get_line_number()))

        return wrapper

    if loglevel is 'debug':
        return debug_log_decorator
    else:
        return info_log_decorator


def mylogger(log_name):
    # import logging.config
    gLogger = logging.getLogger(log_name)
    if hasattr(conf, 'LOG_LEVEL'):
        if conf.LOG_LEVEL == 'DEBUG':
            level = logging.DEBUG
        elif conf.LOG_LEVEL == 'INFO':
            level = logging.INFO
        elif conf.LOG_LEVEL == 'ERROR':
            level = logging.ERROR
        elif conf.LOG_LEVEL == 'WARNING':
            level = logging.WARNING
        elif conf.LOG_LEVEL == 'CRITICAL':
            level = logging.CRITICAL
        elif conf.LOG_LEVEL == 'NOTSET':
            level = logging.NOTSET
        else:
            level = logging.ERROR
        gLogger.setLevel(level)

        # hostname = get_host_info()
        hostname = 'local'
        logging_format = '[' + hostname + ']' + '[%(levelname)s] %(message)s [%(filename)s]' + \
            '[line:%(lineno)d] %(asctime)s '
        formatter = logging.Formatter(logging_format)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        gLogger.addHandler(handler)
        # formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s')
        if hasattr(conf, 'LOG_FILENAME'):
            logdir = "log/"
            logfile = conf.LOG_FILENAME + ".log"
            os.system("mkdir -p " + logdir)
            log_file = "./%s/%s" % (logdir, logfile)
            handler = logging.handlers.RotatingFileHandler(log_file)
            handler.setFormatter(formatter)
            gLogger.addHandler(handler)
    return gLogger


# TODO: utilize different return values to raise different exceptions, based on the exceptions to determine if need retry
# Retry decorator with exponential backoff
def retry(tries=3, delay=1, backoff=2):
    '''Retries a function or method until it returns True.

    delay sets the initial delay in seconds, and backoff sets the factor by which
    the delay should lengthen after each failure. backoff must be greater than 1,
    or else it isn't really a backoff. tries must be at least 0, and delay
    greater than 0.

    Source: https://wiki.python.org/moin/PythonDecoratorLibrary#Retry
    '''

    if backoff <= 1:
        raise ValueError("backoff must be greater than 1")

    tries = math.floor(tries)
    if tries < 0:
        raise ValueError("tries must be 0 or greater")

    if delay <= 0:
        raise ValueError("delay must be greater than 0")

    def deco_retry(f):
        @functools.wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay  # make mutable
            rv = f(*args, **kwargs)  # first attempt
            while mtries > 0:
                logger.debug(
                    'retry func:{} return:{}, No.{} time, retry:{} ...'.format(
                        f.__name__, rv, tries - mtries + 1,
                        kwargs.get('retry', True)))
                if rv:  # Done on success
                    # if rv is True: # Done on success
                    return True
                if not kwargs.get('retry', True):
                    return False

                mtries -= 1  # consume an attempt
                time.sleep(mdelay)  # wait...
                mdelay *= backoff  # make future wait longer

                rv = f(*args, **kwargs)  # Try again
            return False  # Ran out of tries :-(

        return f_retry  # true decorator -> decorated function

    return deco_retry  # @retry(arg[, ...]) -> true decorator


# logger = mylogger(__name__)

if __name__ == '__main__':
    # print(get_host_info())
    # print(queue_name('rpc', 'create'))
    print(time.localtime())
    print(time.timezone)
    print(time.time())
""" ------------------------------ """


class GMT8(tzinfo):
    delta = timedelta(hours=8)

    def utcoffset(self, dt):
        return self.delta

    def tzname(self, dt):
        return "GMT+8"

    def dst(self, dt):
        return self.delta


class GMT(tzinfo):
    delta = timedelta(0)

    def utcoffset(self, dt):
        return self.delta

    def tzname(self, dt):
        return "GMT+0"

    def dst(self, dt):
        return self.delta


# from_tzinfo=GMT()# +0 timezone
# local_tzinfo=GMT8()# +8 timezone
# gmt_time = datetime.strptime('2011-08-15 21:17:14', '%Y-%m-%d %H:%M:%S')
# gmt_time = gmt_time.replace(tzinfo=from_tzinfo)
# local_time = gmt_time.astimezone(local_tzinfo)
