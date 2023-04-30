"""

"""

from .experiment import Experiment
from importlib import resources

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


_cfg = tomllib.loads(resources.read_text("reader", "experiment/config.toml"))
DONT_WRITE_TK = _cfg["experiments"]["DONT_WRITE_TK"]
