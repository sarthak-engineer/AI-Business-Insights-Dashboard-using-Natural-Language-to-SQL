from supabase import create_client

# Supabase connection
url = "https://qalwstleimbxrjeqyyqh.supabase.co"
key = "sb_publishable_0RRLIyHLDrXgLP39jqPKyg_Z-6eeX_5"

supabase = create_client(url, key)

# Example query
response = supabase.table("ecommerce_behavior").select("*").execute()

print("Ecommerce Behavior Data:")
print(response.data)
