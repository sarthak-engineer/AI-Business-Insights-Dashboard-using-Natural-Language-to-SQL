import pandas as pd
from supabase import create_client
from nl_to_sql import generate_sql

url = "https://qalwstleimbxrjeqyyqh.supabase.co"
key = "sb_publishable_0RRLIyHLDrXgLP39jqPKyg_Z-6eeX_5"
supabase = create_client(url, key)

question = "Total sales amount by product"
print(f"Question: {question}")

sql_query = generate_sql(question)
print(f"Original SQL: {sql_query}")

sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
sql_query = sql_query.rstrip(";")
print(f"Cleaned SQL: {sql_query}")

try:
    result = supabase.rpc("execute_sql", {"query": sql_query}).execute()
    data = result.data
    df = pd.DataFrame(data)
    print("DataFrame:")
    print(df)
    
    if "sales_amount" in df.columns:
        print("Total Sales", f"₹{df['sales_amount'].sum():,.0f}")
except Exception as e:
    print("Error executing query")
    print(e)
