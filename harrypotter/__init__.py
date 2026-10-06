"""harrypotter — cast a spell, bloom fireworks. One line of magic.

Quickstart
----------
>>> import harrypotter
>>> harrypotter.cast()                     # random-colour fireworks
>>> harrypotter.cast(spell="gryffindor")   # themed colours
>>> harrypotter.cast(duration=12)          # a longer show

While the window is open: click anywhere to fire an extra firework,
press Esc (or close the window) to end early.
"""

from .core import THEMES, cast

__version__ = "0.1.0"
__all__ = ["cast", "THEMES", "__version__"]
