"""Application composition entry point.

The UI is implemented in :mod:`blindtyping.ui`; this module remains as a
small compatibility import so older launch commands continue to work.
"""

from .ui import BlindTypingUI, main

BlindTypingApp = BlindTypingUI

__all__ = ["BlindTypingApp", "BlindTypingUI", "main"]
