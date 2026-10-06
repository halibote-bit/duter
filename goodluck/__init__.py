"""goodluck — cast a spell, bloom fireworks, feel the luck.

Quickstart
----------
>>> import goodluck
>>> goodluck.cast()                     # random-colour fireworks
>>> goodluck.cast(spell="gryffindor")   # themed colours
>>> goodluck.cast(duration=12)          # a longer show

While the window is open: click anywhere to fire an extra firework,
press Esc (or close the window) to end early.
"""

from .core import THEMES, cast

__version__ = "0.1.0"
__all__ = ["cast", "THEMES", "__version__"]
