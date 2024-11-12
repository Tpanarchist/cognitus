"""Constants for Wikipedia API interaction."""

WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"

# Search parameters
SEARCH_PARAMS = {
    "action": "query",
    "list": "search",
    "format": "json",
    "srprop": "",
    "srwhat": "text"
}

# Lookup parameters
LOOKUP_PARAMS = {
    "action": "query",
    "prop": "extracts",
    "exlimit": "1",
    "explaintext": "1",
    "formatversion": "2",
    "format": "json"
}