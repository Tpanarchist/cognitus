"""Synchronous Wikipedia search functionality."""

from typing import List, Union
import httpx
from .constants import WIKIPEDIA_API_URL, SEARCH_PARAMS, LOOKUP_PARAMS

def search(query: str, n: int = 1) -> Union[str, List[str]]:
    """
    Search Wikipedia for articles matching the query.
    
    Args:
        query: The search query
        n: Number of results to return (default: 1)
    
    Returns:
        Single title string if n=1, otherwise list of title strings
        
    Raises:
        httpx.HTTPError: If the Wikipedia API request fails
        ValueError: If n < 1
    """
    if n < 1:
        raise ValueError("Number of results must be at least 1")
        
    params = SEARCH_PARAMS.copy()
    params.update({
        "srsearch": query,
        "srlimit": n
    })
    
    response = httpx.get(WIKIPEDIA_API_URL, params=params)
    response.raise_for_status()
    
    try:
        results = [x["title"] for x in response.json()["query"]["search"]]
    except KeyError as e:
        raise ValueError(f"Unexpected Wikipedia API response format: {e}")
        
    return results[0] if n == 1 else results

def lookup(query: str, sentences: int = 1) -> str:
    """
    Lookup Wikipedia article content by title.
    
    Args:
        query: The article title to look up
        sentences: Number of sentences to return from start of article
    
    Returns:
        String containing the first N sentences of the article
        
    Raises:
        httpx.HTTPError: If the Wikipedia API request fails
        ValueError: If sentences < 1
    """
    if sentences < 1:
        raise ValueError("Number of sentences must be at least 1")
        
    params = LOOKUP_PARAMS.copy()
    params.update({
        "titles": query,
        "exsentences": sentences
    })
    
    response = httpx.get(WIKIPEDIA_API_URL, params=params)
    response.raise_for_status()
    
    try:
        return response.json()["query"]["pages"][0]["extract"]
    except (KeyError, IndexError) as e:
        raise ValueError(f"Unexpected Wikipedia API response format: {e}")

def search_and_lookup(query: str, sentences: int = 1) -> str:
    """
    Search Wikipedia and return content from the best matching article.
    
    Args:
        query: Search query
        sentences: Number of sentences to return from matched article
    
    Returns:
        String containing the first N sentences of the best matching article
        
    Raises:
        httpx.HTTPError: If any Wikipedia API request fails
        ValueError: If no results found or if sentences < 1
    """
    title = search(query)
    return lookup(title, sentences)