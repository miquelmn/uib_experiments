import os
import subprocess

from . import experiment as exps


def experiment(out_path="./out", explanation: str = exps.experiment.DONT_WRITE_TK):
    def decorator(func):
        """ Decorator, make a sound after the function is finished

        Args:
            func:

        Returns:

        """

        def wrapper(*args, **kwargs):
            exp = exps.experiment.Experiment(out_path, explanation=explanation)
            exp.init()

            kwargs["exp"] = exp
            res = func(*args, **kwargs)

            duration = 2  # seconds
            freq = 440  # Hz
            os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq))
            if explanation != exps.experiment.DONT_WRITE_TK:
                subprocess.Popen(['notify-send', "Experiment finished"])
            exp.finish()

            return res

        return wrapper

    return decorator
