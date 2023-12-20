from abc import ABC, abstractmethod
import requests
import json
from time import sleep


class ApiCaller(ABC):
    @abstractmethod
    def call_api(self, *args, **kwargs):
        pass

    def call_with_retry(self, prompt, retries=5, *args, **kwargs):
        for i in range(retries):
            try:
                print("Calling API...")
                result = self.call_api(prompt, *args, **kwargs)
                return result
            except KeyboardInterrupt:
                print("API call interrupted by user.")
                break
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                print("Retrying...")
                sleep(1)
        raise Exception("Max retries reached. API call failed.")
