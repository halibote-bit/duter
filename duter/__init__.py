"""duter — summon a sprite, bloom sparks of joy, feel the happiness.

Quickstart
----------
>>> import duter
>>> duter.summon()                     # random-colour sparks
>>> duter.summon(mood="sunrise")       # themed colours
>>> duter.summon(duration=12)          # a longer show

While the window is open: click anywhere to create extra sparks of joy,
press Esc (or close the window) to end early.
"""

from .core import MOODS, summon

__version__ = "0.1.1"
__all__ = ["summon", "MOODS", "__version__"]