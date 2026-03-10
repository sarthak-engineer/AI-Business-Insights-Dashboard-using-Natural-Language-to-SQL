import streamlit as st
import pandas as pd
from supabase import create_client
from nl_to_sql import generate_sql, generate_insight

st.set_page_config(page_title="AI Business Dashboard", layout="wide")

url = "https://qalwstleimbxrjeqyyqh.supabase.co"
key = "sb_publishable_0RRLIyHLDrXgLP39jqPKyg_Z-6eeX_5"
supabase = create_client(url, key)

st.title("📊 AI Business Insights Dashboard")

# Initialize session state variables to handle re-runs properly with filters
if "df" not in st.session_state:
    st.session_state.df = None
if "sql_query" not in st.session_state:
    st.session_state.sql_query = None
if "question" not in st.session_state:
    st.session_state.question = ""

question = st.text_input("Ask your business question", value=st.session_state.question)

if st.button("Run Query") and question:
    st.session_state.question = question
    
    with st.spinner("Analyzing your question..."):
        # Generate SQL from AI
        sql_query = generate_sql(question)
        
        # Remove markdown formatting if present
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        
        # Extract strictly the SQL part starting with SELECT
        select_idx = sql_query.upper().find("SELECT")
        if select_idx != -1:
            sql_query = sql_query[select_idx:]

        # Remove trailing semicolon for Supabase RPC execution
        sql_query = sql_query.replace(";", "")
        
        st.session_state.sql_query = sql_query

        try:
            # Execute SQL in Supabase
            result = supabase.rpc("execute_sql", {"query": sql_query}).execute()
            
            # Convert JSON result to DataFrame
            st.session_state.df = pd.DataFrame(result.data)
        except Exception as e:
            st.error("Query execution failed")
            st.write(e)
            st.session_state.df = None

# Display Results if they exist in session state
if st.session_state.sql_query:
    with st.expander("View Generated SQL"):
        st.code(st.session_state.sql_query)

if st.session_state.df is not None:
    df = st.session_state.df.copy()
    
    if df.empty:
        st.warning("No results found for your query. Try rephrasing or asking something else.")
    else:
        st.markdown("---")
        st.subheader("🔍 Filter Results")
        
        # Dynamic Filters Layout
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            date_col = "sale_date" if "sale_date" in df.columns else ("time_of_purchase" if "time_of_purchase" in df.columns else None)
            if date_col:
                df[date_col] = pd.to_datetime(df[date_col])
                min_date = df[date_col].min().date()
                max_date = df[date_col].max().date()
                
                # Handling single date edge case
                if min_date == max_date:
                    selected_dates = st.date_input("📅 Select Date Range", value=(min_date, max_date))
                else:
                    selected_dates = st.date_input(
                        "📅 Select Date Range", 
                        value=(min_date, max_date), 
                        min_value=min_date, 
                        max_value=max_date
                    )
                    
                if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
                    start_date, end_date = selected_dates
                    df = df[(df[date_col].dt.date >= start_date) & (df[date_col].dt.date <= end_date)]
                    
        with filter_col2:
            loc_col = "city" if "city" in df.columns else ("location" if "location" in df.columns else None)
            if loc_col:
                locations = df[loc_col].dropna().unique().tolist()
                selected_loc = st.multiselect("🏙️ Filter by Location", options=locations, default=locations)
                if selected_loc:
                    df = df[df[loc_col].isin(selected_loc)]
                    
        with filter_col3:
            prod_col = "product_name" if "product_name" in df.columns else ("purchase_category" if "purchase_category" in df.columns else None)
            if prod_col:
                products = df[prod_col].dropna().unique().tolist()
                selected_product = st.multiselect("📦 Filter by Product", options=products, default=products)
                if selected_product:
                    df = df[df[prod_col].isin(selected_product)]

        # Check if df is empty after applying filters
        if df.empty:
            st.warning("No results found flexibly matching your filters. Please adjust them.")
        else:
            # Dashboard KPIs
            st.markdown("---")
            st.subheader("📈 Dashboard KPIs")
            col1, col2, col3 = st.columns(3)
            
            # Safely compute metrics if columns exist or are aliased as total_sales
            sales_col = "sales_amount" if "sales_amount" in df.columns else ("total_sales" if "total_sales" in df.columns else ("purchase_amount" if "purchase_amount" in df.columns else None))
            product_col = "product_name" if "product_name" in df.columns else ("purchase_category" if "purchase_category" in df.columns else None)

            if sales_col:
                df[sales_col] = pd.to_numeric(df[sales_col], errors="coerce")

            total_sales_val = df[sales_col].sum() if sales_col else 0
            total_products_val = df[product_col].nunique() if product_col else 0
            avg_sales_val = df[sales_col].mean() if sales_col else 0

            with col1:
                st.metric("💰 Total Sales", f"₹{total_sales_val:,.0f}" if total_sales_val else "₹0")
            with col2:
                st.metric("📦 Total Products", f"{total_products_val:,}" if total_products_val else "0")
            with col3:
                st.metric("📊 Average Sales", f"₹{avg_sales_val:,.2f}" if avg_sales_val else "₹0.00")

            st.markdown("---")
            
            # Step 16: Improve UI Design (Side-by-side columns)
            col_table, col_chart = st.columns(2)

            with col_table:
                st.subheader("📋 Result Table")
                st.dataframe(df, use_container_width=True)

            with col_chart:
                question_lower = st.session_state.question.lower()
                if "by" in question_lower or "distribution" in question_lower or "trend" in question_lower:
                    st.subheader("📊 Chart Visualization")
                    if len(df.columns) >= 2:
                        # Use the first column as the X-axis index for better labeled charts
                        st.bar_chart(df.set_index(df.columns[0]))
                    else:
                        st.bar_chart(df)

            # Step 15: Add AI Explanation
            st.markdown("---")
            st.subheader("💡 AI Generated Insight")
            with st.spinner("Generating context-aware insight..."):
                try:
                    # Send top 10 rows to AI for summarization
                    insight_text = generate_insight(st.session_state.question, df.head(10).to_csv(index=False))
                    st.success(insight_text)
                except Exception as e:
                    st.warning("Could not generate AI insight at this time.")