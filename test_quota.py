import time
import os
from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

available_models = []
try:
    for m in client.models.list():
        available_models.append(m.name)
except Exception as e:
    print(f"Error fetching models: {e}")

print("Testing models for quota...")
working_models = []
for model_name in available_models:
    if "flash" in model_name or "pro" in model_name:
        try:
            print(f"Testing {model_name}...")
            # We strip 'models/' prefix since the generate_content expects just the name or models/name
            name_to_test = model_name.replace("models/", "")
            response = client.models.generate_content(
                model=name_to_test,
                contents="Hello"
            )
            print(f"✅ {model_name} works!")
            working_models.append(name_to_test)
        except errors.ClientError as e:
            print(f"❌ {model_name} failed: {e.message[:100]}...")
        except Exception as e:
            print(f"❌ {model_name} failed with other error: {str(e)[:100]}...")
        time.sleep(1)

print("\n--- WORKING MODELS ---")
for wm in working_models:
    print(wm)
