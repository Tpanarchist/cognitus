"""Whitespace removal components"""

from .extra_space_trimmer import ExtraSpaceTrimmer, SpaceTrimConfig
from .line_break_cleaner import LineBreakCleaner, LineBreakConfig

__all__ = [
    "ExtraSpaceTrimmer",
    "SpaceTrimConfig",
    "LineBreakCleaner",
    "LineBreakConfig",
]