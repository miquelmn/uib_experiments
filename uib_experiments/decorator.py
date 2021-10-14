import os
import subprocess
import logging
from logging.handlers import TimedRotatingFileHandler
import sys

from . import experiment as exps


def experiment(out_path="./out", explanation: str = exps.experiment.DONT_WRITE_TK):
    def decorator(func):
        """ Decorator, make a sound after the function is finished

        Args:
            func:

        Returns:

        """

        def wrapper(*args, **kwargs):
            logger = __get_logger(path=os.path.join(out_path, "logging.log"))
            exp = exps.experiment.Experiment(out_path, logger=logger, explanation=explanation,
                                             arguments=(args, kwargs))
            exp.init()

            kwargs["exp"] = exp
            res = func(*args, **kwargs)

            duration = 1  # seconds
            freq = 440  # Hz
            if sys.platform.startswith("linux"):
                os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq))
                if explanation != exps.experiment.DONT_WRITE_TK:
                    subprocess.Popen(
                        ['notify-send',
                         f"Experiment {exp.get_num_exp()} finished \n{exp.explanation}"])
            else: # Windows
                import winsound
                from win10toast import ToastNotifier

                winsound.Beep(freq, duration * 1000)

                toaster = ToastNotifier()
                toaster.show_toast("Sample Notification", "Python is awesome!!!")


            exp.finish()

            return res

        return wrapper

    return decorator


__FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
__LOGGER = None


def __get_logger(logger_name="Experiment", logger_level=logging.INFO, path="logging.log",
                 rebuild=False):
    global __LOGGER

    def __build_logger():
        """ Function to build the logger.

        This function generates a logger with the indication passed as parameter.

        Returns:

        """

        def get_console_handler():
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(__FORMATTER)
            return console_handler

        def get_file_handler():
            file_handler = TimedRotatingFileHandler(path, when='midnight')
            file_handler.setFormatter(__FORMATTER)
            return file_handler

        logger = logging.getLogger(logger_name)
        logger.addHandler(get_console_handler())

        logger.addHandler(get_file_handler())
        logger.setLevel(logger_level)  # better to have too much log than not enough

        # with this pattern, it's rarely necessary to propagate the error up to parent
        logger.propagate = False
        return logger

    if __LOGGER is None or rebuild:
        __LOGGER = __build_logger()

    return __LOGGER
