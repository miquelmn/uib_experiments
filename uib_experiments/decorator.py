# -*- coding: utf-8 -*-
""" Module containing the decorators.

Written by: Miquel Miró Nicolau (UIB)
"""

import os
import subprocess
import sys

from . import experiment as exps


def experiment(logger, out_path="./out", explanation: str = exps.experiment.DONT_WRITE_TK,
               notification: bool = False, db_path=None):
    def decorator(func):
        """ Decorator, make a sound after the function is finished

        Args:
            func:

        Returns:

        """

        def wrapper(*args, **kwargs):
            exp = exps.experiment.Experiment(out_path, logger=logger, explanation=explanation,
                                             database_name=db_path)
            exp.init()

            kwargs["exp"] = exp
            res = func(*args, **kwargs)

            exp.finish()

            if notification:
                duration = 1  # seconds
                freq = 440  # Hz
                if sys.platform.startswith("linux"):
                    os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq))
                    if explanation != exps.experiment.DONT_WRITE_TK:
                        subprocess.Popen(
                            ['notify-send',
                             f"Experiment {exp.get_num_exp()} finished \n{exp.description}"])
                elif sys.platform.startswith("win"):  # Windows
                    import winsound
                    from win10toast import ToastNotifier

                    winsound.Beep(freq, duration * 1000)

                    toaster = ToastNotifier()
                    toaster.show_toast(f"Experiment {exp.get_num_exp()}",
                                       f"Experiment {exp.get_num_exp()} finished, "
                                       f"last {exp.time} \n"
                                       f"Results: {exp.results} ")

            return res

        return wrapper

    return decorator
