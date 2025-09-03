import contextlib
import functools
import logging
import os
import time
from datetime import datetime
from typing import Generator

FMT = "%(asctime)s %(filename)s:%(lineno)d: %(message)s"
DATEFMT = "%y-%m-%d %H:%M:%S"


class TimerInfo:
    def __init__(
        self,
        func_name: str,
        time_diff: float,
        start_time: str = "",
        end_time: str = "",
        first_token_time: float = 0,
    ):
        self.__func_name = func_name
        self.__time_diff = time_diff
        self.__start_time = start_time
        self.__end_time = end_time
        self.__first_token_time = first_token_time

    def push_gateway_dict_list(self):
        return [{"observe_name": self.__func_name, "observe_value": self.__time_diff}]

    def __str__(self):
        _extra_ls = []
        if self.__start_time is not None:
            _extra_ls.append(f"开始时间: {self.__start_time}")
        if self.__end_time is not None:
            _extra_ls.append(f"结束时间: {self.__end_time}")
        if self.__first_token_time is not None:
            _extra_ls.append(f"首token时长: {self.__first_token_time:.4f}s")
        _extra_info = " (" + " ".join(_extra_ls) + ")" if len(_extra_ls) > 0 else " "
        return f"【{self.__func_name}: {round(self.__time_diff, 3)}s{_extra_info}】"

    def __repr__(self):
        return self.__str__()


def get_logger(name=None, log_file=None, log_level=logging.INFO):
    """concise log"""
    logger = logging.getLogger(name)
    logging.basicConfig(format=FMT, datefmt=DATEFMT)
    if log_file is not None:
        log_file_folder = os.path.split(log_file)[0]
        if log_file_folder:
            os.makedirs(log_file_folder, exist_ok=True)
        fh = logging.FileHandler(log_file, "w", encoding="utf-8")
        fh.setFormatter(logging.Formatter(FMT, DATEFMT))
        logger.addHandler(fh)
    logger.setLevel(log_level)
    return logger


def log_df_basic_info(df, comments="", logger=None):
    if logger is None:
        logger = get_logger()
    if comments:
        logger.info(f"comments {comments}")
    logger.info(f"df.shape {df.shape}")
    logger.info(f"df.columns {df.columns.to_list()}")
    logger.info(f"df.head()\n{df.head()}")
    logger.info(f"df.tail()\n{df.tail()}")


def func_time_print(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        t0 = time.time()
        res = func(*args, **kw)
        _total_seconds = time.time() - t0
        total_seconds = int(_total_seconds)
        hours = total_seconds // 3600
        total_seconds = total_seconds % 3600
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        out_str = f"call {func.__name__}() uses seconds {round(_total_seconds, 3)}s"
        if total_seconds > 3600:
            out_str = f'{out_str}, i.e. hours:mm:ss {hours}:{minutes}:{seconds}'
        elif total_seconds > 60:
            out_str = f'{out_str}, i.e. mm:ss {minutes}:{seconds}'
        print(out_str)
        return res

    return wrapper


@contextlib.contextmanager
def simple_timing(msg: str = "", logger=None):
    if logger is None:
        logger = get_logger()
    logger.info("Started %s", msg)
    tic = time.time()
    yield
    toc = time.time()
    total_seconds = toc - tic
    hours = total_seconds / 3600
    logging.info(
        "Finished %s in %.3f seconds, i.e. %.3f hours", msg, total_seconds, hours
    )


def time_to_str(timestamp):
    dt_object = datetime.fromtimestamp(timestamp)
    # 格式化输出为包含年月日时分秒毫秒的字符串
    formatted_time = dt_object.strftime("%Y-%m-%d %H:%M:%S.%f")
    # 因为 strftime 的 %f 表示微秒，所以如果有需要的话可以只取前三位作为毫秒
    formatted_time_ms = formatted_time[:-3]
    return formatted_time_ms


# TODO, to print out or save to dict
def timer_wrapper(func_name: str):
    def wrapper(func):
        def inner(*args, **kwargs):
            start_time = time.time()
            res = func(*args, **kwargs)
            end_time = time.time()
            time_diff = round(end_time - start_time, 3)
            timer_info = TimerInfo(
                func_name,
                time_diff,
                start_time=time_to_str(start_time),
                end_time=time_to_str(end_time),
            )

            return res

        return inner

    return wrapper


def timer_wrapper_generator(func_name: str):
    def wrapper(func):
        def inner(*args, **kwargs):
            start_time = time.time()
            res = func(*args, **kwargs)
            if isinstance(res, Generator):
                try:
                    while True:
                        yield next(res)
                except StopIteration as e:
                    res = e.value
            end_time = time.time()
            time_diff = round(end_time - start_time, 3)
            # timer_info = TimerInfo(
            #     func_name,
            #     time_diff,
            #     start_time=time_to_str(start_time),
            #     end_time=time_to_str(end_time),
            # )
            # add_time_func = getattr(g, "add_timer", None)
            # if add_time_func is not None:
            #     add_time_func(timer_info)
            return res

        return inner

    return wrapper


if __name__ == "__main__":
    with simple_timing("test"):
        a = 1
        for i in range(1000):
            a = 1
        time.sleep(1)

    @func_time_print
    def funcname():
        time.sleep(2)

    funcname()