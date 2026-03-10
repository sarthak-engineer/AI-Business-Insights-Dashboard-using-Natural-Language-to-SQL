from supabase import create_client

url = "https://qalwstleimbxrjeqyyqh.supabase.co"

key = "sb_publishable_0RRLIyHLDrXgLP39jqPKyg_Z-6eeX_5"

supabase = create_client(url, key)

response = supabase.table("ecommerce_behavior").select("*").execute()

print(response)
