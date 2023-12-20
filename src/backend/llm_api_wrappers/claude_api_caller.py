import json
import requests
from .api_caller import ApiCaller
from .APIKEYS import claude_API_KEY


class ClaudeApiCaller(ApiCaller):
    def call_api(self, prompt, model="claude-2.0", max_tokens=2048):

        assert prompt[:len("\n\nHuman:")] == "\n\nHuman:", "Prompt must start with '\n\nHuman:'"
        
        #assert prompt[-len("\n\nAssistant:"):] == "\n\nAssistant:", "Prompt must end with '\n\nAssitant:'"

        #assert model != 'claude-2'

        headers = {
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
            "x-api-key": claude_API_KEY,
        }

        payload = {"model": model, "prompt": prompt, "max_tokens_to_sample": max_tokens}

        response = requests.post(
            "https://api.anthropic.com/v1/complete", headers=headers, json=payload
        )

        if response.status_code == 200:
            completion =  json.loads(response.text)
            # extract the text from the json response
            return completion["completion"].strip()
        else:
            print("Error, Response: ", response.text)
            raise Exception(f"API call failed with status code {response.status_code}.")
