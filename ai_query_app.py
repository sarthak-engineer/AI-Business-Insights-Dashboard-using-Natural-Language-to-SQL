import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# Supabase connection
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)

# Example query
response = supabase.table("ecommerce_behavior").select("*").execute()

print("Ecommerce Behavior Data:")
print(response.data)
