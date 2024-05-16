import requests
from functools import wraps
from time import time

# Cache dictionary with expiration times
cache = {}

def get_page(url):
    """Fetches the HTML content of a URL with caching and access tracking.

    Args:
        url (str): The URL to fetch.

    Returns:
        str: The HTML content of the URL.
    """

    current_time = time()

    # Check if URL is in cache and hasn't expired
    if url in cache and current_time - cache[url]["time"] < 10:
        print(f"Using cached content for {url}")
        return cache[url]["content"]

    # Fetch content from URL if not cached or expired
    response = requests.get(url)
    response.raise_for_status()  # Raise exception for non-200 status codes
    content = response.text

    # Update cache with new content and timestamp
    cache[url] = {"content": content, "time": current_time}
    print(f"Fetched content from {url}")

    # Track access count for URL in a separate dictionary (not cached)
    access_counts = getattr(get_page, "_access_counts", {})  # Initialize on first call
    access_counts[url] = access_counts.get(url, 0) + 1
    setattr(get_page, "_access_counts", access_counts)  # Update access counts

    return content

def access_count(func):
    """Decorator to track access count for a function.

    Args:
        func: The function to decorate.

    Returns:
        function: The decorated function with access count tracking.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print(f"Access count for '{func.__name__}' ({args[0]}): {get_page._access_counts.get(args[0], 0)}")
        return result

    return wrapper

# Usage with and without decorator
print(get_page("http://slowwly.robertomurray.co.uk/delay/3000/url/https://www.example.com"))
print(get_page("http://slowwly.robertomurray.co.uk/delay/3000/url/https://www.example.com"))  # Should be cached
print(get_page("https://www.another-example.com"))  # Access count without decorator

@access_count
def decorated_get_page(url):
    return get_page(url)

print(decorated_get_page("http://slowwly.robermuray.co.uk/delay/3000/url/https://www.example.com"))

