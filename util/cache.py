import requests
import datetime

from util.utils import is_night_time


class RequestCache:
    def __init__(self):
        self.cache = {}

    def get_from_cache(self, key):
        """Retrieve value from cache if present."""
        data = self.cache.get(key)
        if data is not None:
            today_str = (datetime.datetime.now().date() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            # 如果是晚上9点到12点，今日日期不减1，否则日期减1
            if is_night_time():
                today_str = datetime.datetime.now().strftime("%Y-%m-%d")
            if data[len(data) - 1][0] == today_str:
                return data
            else:
                return None
        return data

    def add_to_cache(self, key, value):
        """Add key-value pair to cache."""
        self.cache[key] = value

    def clear_cache(self):
        """Clear the cache."""
        self.cache.clear()


cache = RequestCache()


# Function to simulate a costly request
def fetch_data_from_api(url):
    return requests.get(url).json()


# Example function that checks cache before making a request
def request(url):
    cached_result = cache.get_from_cache(url)
    if cached_result:
        return cached_result

    # If not in cache, fetch data
    result = fetch_data_from_api(url)
    cache.add_to_cache(url, result)
    return result
