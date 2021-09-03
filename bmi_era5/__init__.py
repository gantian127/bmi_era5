from .utils import Era5Data
from .bmi import BmiEra5
from ._version import get_versions

__all__ = ["Era5Data", "BmiEra5"]

__version__ = get_versions()['version']
del get_versions
