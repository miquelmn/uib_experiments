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
            logger = get_logger(path=os.path.join(out_path, "logging.log"))
            exp = exps.experiment.Experiment(out_path, logger=logger, explanation=explanation,
                                             arguments=(args, kwargs))
            exp.init()

            kwargs["exp"] = exp
            res = func(*args, **kwargs)

            duration = 2  # seconds
            freq = 440  # Hz
            os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq))
            if explanation != exps.experiment.DONT_WRITE_TK:
                subprocess.Popen(
                    ['notify-send', f"Experiment {exp.get_num_exp()} finished \n{exp.explanation}"])
            exp.finish()

            return res

        return wrapper

    return decorator


FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")


def get_logger(logger_name="Experiment", logger_level=logging.INFO, path="logging.log"):
    def get_console_handler():
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(FORMATTER)
        return console_handler

    def get_file_handler():
        file_handler = TimedRotatingFileHandler(path, when='midnight')
        file_handler.setFormatter(FORMATTER)
        return file_handler

    logger = logging.getLogger(logger_name)
    logger.addHandler(get_console_handler())

    logger.addHandler(get_file_handler())
    logger.setLevel(logger_level)  # better to have too much log than not enough

    # with this pattern, it's rarely necessary to propagate the error up to parent
    logger.propagate = False
    return logger
