import requests
import json
from dotenv import dotenv_values

class CaptchaSolver:
    def __init__(self, method="capsolver"):
        self.config = dotenv_values(".env")
        self.method = method.lower()

    def solve_captcha(self, base64_image):
        if self.method == "capsolver":
            try:
                return self.capsolver(base64_image)
            except Exception as e:
                print(f"API error: {e}.")
                print("Falling back to manual mode...")
                return self.solve_captcha_manual()
        elif self.method == "api2":
            # Placeholder for another API method
            pass
        elif self.method == "manual":
            return self.solve_captcha_manual()
        else:
            raise Exception("Invalid CAPTCHA solving method specified")
        
    def solve_captcha_manual(self):
        return "Automated CAPTCHA solving is disabled. Please solve the CAPTCHA manually."

    def capsolver(self, base64_image):
        # API endpoint
        url = "https://api.capsolver.com/createTask"
        headers = {"Content-Type": "application/json"}
        payload = {
            "clientKey": self.config.get("CAPSOLVER_API_KEY"),
            "appId": self.config.get("CAPSOLVER_APP_ID", ""),
            "task": {
                "type": "ImageToTextTask",
                "body": base64_image,
                "case": "true",
            }
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response_data = response.json()

        if response_data['errorId'] == 0 and response_data.get('status') == 'ready':
            # Successful response with immediate solution
            return response_data['solution']['text']
        else:
            # Handle error
            raise Exception("API did not return a solution")

