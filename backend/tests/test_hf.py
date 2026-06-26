import os
import requests
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)
api_key = os.environ.get("GEMINI_API", "").strip('"')
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
r = requests.get(url)
print(r.status_code, r.text)
