from google import genai
import sys

try:
    client = genai.Client(api_key='AIzaSyACexuc68eIcp2TEFYVeGLGAaDaeLAHlVY')
    for m in client.models.list():
        print(m.name)
except Exception as e:
    print(f"Error: {e}")
