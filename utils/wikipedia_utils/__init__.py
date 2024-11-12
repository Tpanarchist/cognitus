"""Wikipedia search utilities for Cognitus."""

from .sync_search import search, lookup, search_and_lookup
from .async_search import search as async_search
from .async_search import lookup as async_lookup
from .async_search import search_and_lookup as async_search_and_lookup

__all__ = [
    'search',
    'lookup',
    'search_and_lookup',
    'async_search',
    'async_lookup', 
    'async_search_and_lookup'
]