import requests
import time


class RateLimitedRequest:
    def __init__(self, requests_per_minute=250):
        self.requests_per_minute = requests_per_minute
        self.request_history = None

    def get(self, url, params=None, headers=None):
        min_delay = 60 / self.requests_per_minute

        current_time = time.time()
        time_since_last_request = current_time - self.request_history if self.request_history else min_delay

        if time_since_last_request < min_delay:
            time_to_sleep = min_delay - time_since_last_request
            time.sleep(time_to_sleep)

        response = requests.get(url, params=params, headers=headers)

        self.request_history = time.time()
        return response
