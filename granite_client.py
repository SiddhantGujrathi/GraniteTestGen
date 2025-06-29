import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

class GraniteClient:
    def __init__(self):
        self.api_key = os.environ.get("IBM_API_KEY")
        self.project_id = os.environ.get("IBM_PROJECT_ID")
        self.base_url = os.environ.get("IBM_WATSONX_URL")  # <-- Make sure this is set
        self.model_id = os.environ.get("GRANITE_MODEL")
        self.access_token = None
        self.token_expires_at = 0

        if not self.api_key or not self.project_id or not self.base_url:
            raise ValueError("Missing IBM_API_KEY, IBM_PROJECT_ID, or IBM_WATSONX_URL in environment variables.")
        if not self.model_id:
            raise ValueError("Missing GRANITE_MODEL in environment variables.")
    
    def get_access_token(self):
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token
        
        url = "https://iam.cloud.ibm.com/identity/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": self.api_key
        }
        
        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data["access_token"]
            self.token_expires_at = time.time() + token_data.get("expires_in", 3600) - 300
            
            return self.access_token
        except Exception as e:
            raise Exception(f"Failed to get access token: {str(e)}")
    
    def generate_test_cases(self, prompt):
        url = f"{self.base_url}/ml/v1/text/generation?version=2023-05-29"
        
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model_id": self.model_id,
            "project_id": self.project_id,
            "input": prompt,
            "parameters": {
                "decoding_method": "greedy",
                "max_new_tokens": 1000,
                "min_new_tokens": 1,
                "stop_sequences": ["<end of code>"],
                "repetition_penalty": 1
            },
            "moderations": {
                "hap": {
                    "input": {
                        "enabled": True,
                        "threshold": 0.5,
                        "mask": {
                            "remove_entity_value": True
                        }
                    },
                    "output": {
                        "enabled": True,
                        "threshold": 0.5,
                        "mask": {
                            "remove_entity_value": True
                        }
                    }
                }
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result["results"][0]["generated_text"]
        except Exception as e:
            print(response.status_code, response.text)
            raise Exception(f"Failed to generate test cases: {str(e)}")
