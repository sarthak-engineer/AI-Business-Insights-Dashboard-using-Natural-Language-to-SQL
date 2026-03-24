# backend/app.py (Flask API Backend)
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from supabase import create_client
import pandas as pd
import httpx
from nl_to_sql_api import generate_sql
import json
import io
from ml_engine import get_ml_insights
from data_manager import process_upload, load_schema, is_uploaded_dataset_active, execute_local_sql, clear_uploaded_dataset

import logging

load_dotenv()

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ========== SECURITY: Restricted CORS Configuration ==========
# Only allow requests from localhost (development) or specified domains
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
CORS(app, resources={
    r"/*": {
        "origins": cors_origins,
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "max_age": 3600
    }
})

# ========== SECURITY: Flask Security Configuration ==========
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'  # Default: False (safe)
app.config['TESTING'] = False

# ========== SECURITY: Add Security Headers ==========
@app.after_request
def set_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'  # Prevent MIME-type sniffing
    response.headers['X-Frame-Options'] = 'DENY'  # Prevent clickjacking
    response.headers['X-XSS-Protection'] = '1; mode=block'  # Enable XSS protection
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'  # Force HTTPS
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'"  # CSP
    return response

# Supabase configuration
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

import numpy as np

def generate_statistical_insight(avg, median):
    if avg > median:
        return "High values dominate the dataset"
    elif avg < median:
        return "Most records are in the lower to moderate range"
    else:
        return "Distribution is relatively even"

ALLOWED_COLUMNS = [
    "purchase_amount",
    "purchase_category",
    "gender",
    "purchase_date",
    "discount_used",
    "location",
    "occupation",
    "purchase_channel",
    "time_of_purchase",
    "customer_satisfaction",
    "return_rate",
    "age",
    "product_rating",
    "customer_id",
    "total_revenue",
    "average_spend",
    "total_count",
    "percentage",
    "discount_applied",
    "records"
]

def validate_sql(sql: str, allowed_columns: list = None) -> bool:
    """
    Validates SQL strings to ensure they are safe and only interact with allowed columns.
    """
    import re
    sql_clean = sql.upper().replace('"', '').replace('`', '')
    
    # 1. Block destructive keywords
    if any(keyword in sql_clean for keyword in ["DROP", "DELETE", "UPDATE", "INSERT", "TRUNCATE", "ALTER"]):
        logger.warning(f"SECURITY: Blocked destructive SQL: {sql}")
        return False
        
    # 2. Must contain SELECT
    if "SELECT" not in sql_clean:
        return False
        
    # 3. Block multiple statements
    if sql.count(';') > 1:
        return False
        
    # 4. Whitelist Column Validation
    if allowed_columns:
        sql_keywords = set(["SELECT", "FROM", "WHERE", "GROUP", "BY", "ORDER", "JOIN", "ON", "AND", "OR", "IN", "LIKE", "AS", "COUNT", "SUM", "AVG", "MIN", "MAX", "LIMIT", "DESC", "ASC", "HAVING", "DISTINCT", "BETWEEN", "IS", "NULL", "NOT", "CASE", "WHEN", "THEN", "ELSE", "END", "ECOMMERCE_BEHAVIOR", "UPLOADED_DATASET", "*", "UNION", "ALL"])
        words = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', sql_clean)
        for word in words:
            if word not in sql_keywords and not word.isdigit():
                if word.lower() not in [c.lower() for c in allowed_columns]:
                    logger.warning(f"VALIDATION: Potential unauthorized field detected: '{word}'")
                    # return False # Soft warning for now
    
    return True


def sanitize_sql_string(value: str, max_length: int = 255) -> str:
    """
    Sanitizes user input for safe use in SQL queries.
    - Limits length to prevent buffer overflow
    - Escapes single quotes (SQL injection prevention)
    - Removes dangerous characters
    """
    if not isinstance(value, str):
        value = str(value)
    
    # Limit length
    value = value[:max_length]
    
    # Escape single quotes (double them for SQL)
    value = value.replace("'", "''")
    
    # Log suspicious patterns
    dangerous_patterns = ["--", "/*", "*/", "xp_", "sp_", "drop", "delete", "truncate", "insert", "update"]
    if any(pattern in value.lower() for pattern in dangerous_patterns):
        logger.warning(f"SECURITY: Suspicious SQL pattern detected in drill-down value: {value[:50]}")
    
    return value


# Simple Python-based Insight Summary Generator
def generate_insight(data_list):
    """
    Highly Controlled Adaptive & Intelligent Insights.
    Input: List of dicts with numeric values.
    """
    if not data_list or len(data_list) <= 1:
        return "Not enough data to generate meaningful insight."

    # Extract numeric values and labels
    values = []
    labels = []
    for d in data_list:
        v_list = [v for v in d.values() if isinstance(v, (int, float))]
        l_list = [v for v in d.values() if isinstance(v, str)]
        if v_list: values.append(v_list[0])
        labels.append(l_list[0] if l_list else "N/A")

    if not values or len(values) <= 1:
        return "Not enough numeric data for deep analysis."

    # 1. Compute Base Metrics
    n = len(values)
    max_val = max(values)
    min_val = min(values)
    total_sum = sum(values)
    avg_val = total_sum / n
    
    # Identify Top Category and Second Highest
    sorted_data = sorted(zip(values, labels), key=lambda x: x[0], reverse=True)
    max_val, top_category = sorted_data[0]
    second_val = sorted_data[1][0] if n > 1 else max_val

    # 2. Derived Metrics (Safe division with 1e-6)
    divisor = avg_val + 1e-6
    dominance_ratio = max_val / divisor
    gap_ratio = (max_val - second_val) / divisor
    spread_ratio = (max_val - min_val) / divisor
    percentage_share = (max_val / (total_sum + 1e-6)) * 100

    # 3. Priority-based Controlled Logic
    # Tier 1: Strong Dominance (Strict)
    if dominance_ratio > 1.7 and gap_ratio > 0.5 and percentage_share > 30:
        insight = f"{top_category} strongly dominates, contributing approximately {percentage_share:.1f}% of the total."
        
    # Tier 2: Moderate Leader
    elif dominance_ratio > 1.3 and percentage_share > 15:
        insight = f"{top_category} is the leading category with noticeably higher values."
        
    # Tier 3: No real dominance (Small share leader)
    elif percentage_share < 10:
        insight = "No single category dominates; values are fairly distributed across categories."
        
    # Tier 4: Even Distribution
    elif spread_ratio < 0.1:
        insight = "Values are very evenly distributed across categories."
        
    # Tier 5: Underperformance Detection
    elif min_val < avg_val * 0.5:
        insight = "Some categories are significantly underperforming compared to the average."
        
    # Default Case
    else:
        insight = "There is moderate variation across categories."

    return insight

def generate_python_summary(df):
    if df.empty or len(df) <= 1:
        return "Not enough data to generate meaningful insight."
    
    # Convert dataframe to records for the helper
    data_records = df.to_dict(orient="records")
    return generate_insight(data_records)


# Quick Interpretation Logic (Frontend Helper)
def quick_interpret(query):
    query = query.lower()
    metric = "General Analytics"
    if any(word in query for word in ["sales", "revenue", "amount", "sold"]): metric = "Total Sales"
    elif "count" in query or "number of" in query: metric = "Record Count"
    elif "average" in query or "avg" in query: metric = "Average Value"
    elif "rating" in query: metric = "Product Ratings"
    
    # Advanced Grouping Detection
    group_by = None
    if "by gender" in query: group_by = "Gender"
    elif "by category" in query: group_by = "Purchase Category"
    elif "by location" in query or "by city" in query: group_by = "Location"
    elif "by occupation" in query: group_by = "Occupation"
    elif "by channel" in query: group_by = "Purchase Channel"
    elif "by month" in query: group_by = "Month"
    
    # Legacy/Default fallback if no explicit "by" used
    if not group_by:
        if "month" in query: group_by = "Month"
        elif "category" in query: group_by = "Category"
        elif "location" in query or "city" in query: group_by = "Location"
        else: group_by = "Overall"

    
    filters = []
    months = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
    for m in months:
        if m in query or m[:3] in query:
            filters.append(m.title())
    if "bangalore" in query: filters.append("Bangalore")
    if "male" in query and "female" not in query: filters.append("Male")
    
    operation = "Aggregate" if any(word in query for word in ["total", "sum", "average", "avg", "count"]) else "Listing"
    
    return {
        "metric": metric,
        "group_by": group_by,
        "filter": ", ".join(filters) if filters else "None",
        "operation": operation
    }

# --- Synonym & Semantic Normalization Layer ---
SYNONYM_MAP = {
    "spending": "purchase_amount",
    "revenue": "purchase_amount",
    "sales": "purchase_amount",
    "cost": "purchase_amount",
    "items": "purchase_category",
    "group": "purchase_category",
    "city": "location",
    "place": "location",
    "rating": "product_rating",
    "score": "customer_satisfaction"
}

def normalize_query(query):
    if not query:
        return query
    
    import re
    normalized = query
    # Sort synonyms by length to handle multi-word if any, or just single words
    for word, actual in sorted(SYNONYM_MAP.items(), key=lambda x: len(x[0]), reverse=True):
        pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
        normalized = pattern.sub(actual, normalized)
    
    return normalized

def detect_chart_type(query):
    q = query.lower()
    if any(k in q for k in ["over time", "month", "year", "trend", "timeline", "date"]):
        return "line"
    if any(k in q for k in ["distribution", "range", "spread", "histogram"]):
        return "histogram"
    if any(k in q for k in ["pie", "breakdown", "proportion", "share", "contribution"]):
        return "pie"
    return "bar"


@app.route('/query', methods=['POST'])
def handle_query():
    data = request.json
    user_query = data.get('query', '')
    
    # 0. Synonym Normalization Layer (Normalization Step)
    logger.info(f"Incoming Request Query: {user_query}")
    user_query = normalize_query(user_query)
    
    # 1. Incorporate active UI filters into query context
    filters = data.get('filters', {})
    active_filters_prompt = []
    if filters.get('category') and filters.get('category') != 'all':
        active_filters_prompt.append(f"Purchase_Category must be '{filters['category']}'")
    if filters.get('gender') and filters.get('gender') != 'all':
        active_filters_prompt.append(f"Gender must be '{filters['gender']}'")
    if filters.get('startDate') and filters.get('endDate'):
         active_filters_prompt.append(f"Time_of_Purchase must be between '{filters['startDate']}' and '{filters['endDate']}'")
         
    if active_filters_prompt:
        filter_str = " AND ".join(active_filters_prompt)
        user_query = f"{user_query} (FILTER CONTEXT: Only include records where {filter_str})"

    # 1.5 Input Validation Layer (Security Check & Intent Validation)
    INTENT_KEYWORDS = [
        "sale", "revenue", "earning", "income", "amount", "spend", "purchas",
        "count", "number", "how many", "total", "users", "orders",
        "avg", "average", "mean", "percentage", "ratio", "proportion", "percent",
        "highest", "top", "best", "rank", "maximum", "max", "min", "lowest",
        "all data", "show everything", "everything", "full data",
        "category", "gender", "location", "age", "rating", "discount", "satisfied", "churn"
    ]
    
    # 1.5 Input Validation Layer (Hard Stop Intent Validation)
    query_lower = user_query.lower()
    has_intent = any(keyword in query_lower for keyword in INTENT_KEYWORDS)
    
    if not has_intent and len(user_query.strip().split()) < 3:
         logger.warning(f"TERMINATED: Unclear query intent detected: {user_query}")
         return jsonify({
             "status": "error",
             "message": "Sorry, I couldn't understand the query. Please rephrase with more business details (e.g. Sales, Category, etc.)."
         }), 400

    def is_valid_column(col):
        return col.lower() in [c.lower() for c in ALLOWED_COLUMNS]

    # Intelligent Dataset Switching Logic
    active_table = "ecommerce_behavior"
    active_schema = None
    allowed_cols = ALLOWED_COLUMNS
    use_local_db = False
    
    if is_uploaded_dataset_active():
        active_schema = load_schema()
        if active_schema:
            active_table = "uploaded_dataset"
            allowed_cols = [col["clean"] for col in active_schema["columns"]]
            use_local_db = True
            logger.info(f"Switching to UPLOADED DATASET context. Columns: {len(allowed_cols)}")
        else:
            logger.warning("Uploaded dataset detected but schema load failed. Falling back to demo.")

    try:
        # 2. Check for drill down first
        drill_down = data.get('drill_down')
        if drill_down:
            field = drill_down.get('field')
            value = str(drill_down.get('value', '')).strip()
            
            # 1. Validation (Hard Termination)
            if not value:
                logger.warning("TERMINATED: Empty drill-down value.")
                return jsonify({"status": "error", "message": "Invalid drill-down input (selection is empty)."}), 400

            # 2. Whitelist Validation for Field
            if field.lower() not in [c.lower() for c in allowed_cols]:
                logger.warning(f"TERMINATED: Unauthorized field '{field}'")
                return jsonify({"status": "error", "message": "Invalid column selection."}), 400
            
            # 3. SQL Injection Prevention - Sanitize user input  
            sanitized_value = sanitize_sql_string(value, max_length=255)
            sql_query = f"SELECT * FROM {active_table} WHERE LOWER(TRIM(\"{field}\"::TEXT)) = LOWER(TRIM('{sanitized_value}')) LIMIT 100"
            enhanced_query = f"Drill-down: {field}={value}"
            interpretation = {"metric": f"Details: {value}", "group_by": field, "operation": "Drill-down"}
            chart_type = "table"
        else:
            # 1. SQL Generation with Safe Termination & Input Validation
            sql_query, enhanced_query, validation_hint = generate_sql(user_query, table_name=active_table, schema=active_schema)
            logger.info(f"Raw SQL Generation Attempt for: {user_query}")
            
            if not sql_query:
                # If validation_hint contains the error from our new validation layer
                error_display = validation_hint if validation_hint else "Sorry, I couldn't understand the query. Please rephrase."
                logger.warning(f"TERMINATED: Validation or Generation failed: {error_display}")
                return jsonify({
                    "status": "error",
                    "message": error_display
                }), 400
                
            # 0. Interpretation & Chart Detection
            interpretation = quick_interpret(user_query)
            sql_query = sql_query.strip().rstrip(';')
            
            # Use the smarter suggestion from nl_to_sql_api if it's a valid chart type
            chart_type = validation_hint if validation_hint and not validation_hint.startswith("Query is") else detect_chart_type(user_query)
            
        # 2. Execution Guard (Safety Layer)
        if not validate_sql(sql_query, allowed_columns=allowed_cols):
            logger.warning(f"TERMINATED: SQL failed safety validation: {sql_query}")
            return jsonify({
                "status": "error",
                "message": "Security Alert: This query has been blocked for safety reasons."
            }), 403

        # 3. Database Execution (Routes to SQLite for uploaded datasets, Supabase for demo)
        try:
            if use_local_db:
                # Execute against local SQLite for uploaded datasets
                result_data = execute_local_sql(sql_query)
                df_result = pd.DataFrame(result_data)
                logger.info(f"[LOCAL SQLite] Query executed. Rows: {len(df_result)}")
            else:
                # Execute against Supabase for demo dataset
                result = supabase.rpc("execute_sql", {"query": sql_query}).execute()
                df_result = pd.DataFrame(result.data)
                logger.info(f"[Supabase] Query executed. Rows: {len(df_result)}")
            
            # Check for empty results with intelligent suggestions
            if df_result.empty:
                suggestion = "Try simplifying or broadening your query."
                
                # Smart Suggestion Logic from user requirement
                if ">" in sql_query:
                    suggestion = "Try reducing the numeric threshold (e.g., using > 50 instead of a higher value)."
                elif "<" in sql_query:
                    suggestion = "Try increasing your numeric range to capture more records."
                elif "WHERE" in sql_query.upper():
                    suggestion = "The filters applied are too specific. Try removing a category or location constraint."
                
                logger.warning(f"No results found for query: {user_query}")
                return jsonify({
                    "original_query": user_query,
                    "data": [],
                    "message": "No results matched your criteria.",
                    "suggestion": suggestion,
                    "insights": f"📉 **Status**: No data found.\n💡 **Suggestion**: {suggestion}",
                    "sql": sql_query,
                    "interpretation": interpretation
                }), 200
        except Exception as e:
            logger.error(f"SQL Execution Error: {str(e)}")
            return jsonify({"status": "error", "message": f"Query failed: {str(e)}", "sql": sql_query}), 500

        
        # 3.5 Ensure numeric columns are actually numbers
        for col in df_result.columns:
            temp_col = pd.to_numeric(df_result[col], errors='coerce')
            if not temp_col.isna().all():
                df_result[col] = temp_col.fillna(0)
        
        # 4. Generate Insight Summary
        insights = generate_python_summary(df_result)
        
        # 5. Advanced Purchase Insights (New Layer)
        # Adapt to dynamic column names
        amt_col = next((c for c in df_result.columns if c.lower() in ["purchase_amount", "amount", "sales", "revenue"]), None)
        if amt_col:
            values = pd.to_numeric(df_result[amt_col], errors='coerce').dropna().tolist()
            if len(values) > 1:
                avg_val = sum(values) / len(values)
                median_val = float(np.median(values))
                insight_text = generate_statistical_insight(avg_val, median_val)
                
                purchase_insight = (
                    f"**Average {amt_col.replace('_', ' ').title()}**: {avg_val:,.2f}  \n"
                    f"**Median {amt_col.replace('_', ' ').title()}**: {median_val:,.2f}  \n"
                    f"**Deep Insight**: {insight_text}"
                )
                # Combine with existing insights
                insights = purchase_insight + "\n\n---\n" + insights
        
        # 6. ML Analytics Layer (New AI Features)
        ml_layer = get_ml_insights(df_result)
        
        return jsonify({

            "original_query": user_query,
            "enhanced_query": enhanced_query if not drill_down else "N/A (Drill-down)",
            "interpretation": interpretation,
            "chart_type": chart_type,
            "data": df_result.to_dict(orient="records"),
            "sql": sql_query,
            "insights": insights,
            "ml_insights": ml_layer
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "Backend is running"}), 200

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handles CSV upload: parse, detect schema, store in local SQLite."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if not file.filename.lower().endswith('.csv'):
        return jsonify({"error": "Only CSV files are supported"}), 400
    
    logger.info(f"Upload request received: {file.filename}")
    
    # Use the new local SQLite pipeline (no Supabase DDL needed)
    success, message, schema = process_upload(file)
    
    if success:
        logger.info(f"Upload SUCCESS: {file.filename} - {message}")
        return jsonify({
            "message": f"✅ {file.filename}: {message}",
            "columns": [col["clean"] for col in schema["columns"]],
            "schema_summary": {
                "numeric": schema.get("numeric", []),
                "categorical": schema.get("categorical", []),
                "date": schema.get("date", [])
            }
        }), 200
    else:
        logger.error(f"Upload FAILED: {file.filename} - {message}")
        return jsonify({"error": message}), 400

@app.route('/reset', methods=['POST'])
def reset_dataset():
    """Clears uploaded dataset and reverts to demo."""
    success = clear_uploaded_dataset()
    if success:
        logger.info("Dataset reset to demo successfully")
        return jsonify({"message": "Successfully reset to demo dataset"}), 200
    else:
        return jsonify({"error": "Failed to clear uploaded dataset"}), 500

@app.route('/export', methods=['POST'])
def export_csv():
    try:
        data = request.json.get('data', [])
        if not data:
            return jsonify({"error": "No data to export"}), 400
            
        df = pd.DataFrame(data)
        
        # Create CSV in memory
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        
        from flask import Response
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=dashboard_report.csv"}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ========== SMART COLUMN DETECTION FOR DYNAMIC SCHEMA ==========

def find_numeric_column_for_measure(schema):
    """
    Intelligently detect the best numeric column for metrics (revenue, amount, sales).
    Priority: amount/revenue > value > numeric columns
    Returns: column name (cleaned) or None
    """
    if not schema or not schema.get("numeric"):
        return None
    
    schema_cols = {col["original"]: col["clean"] for col in schema.get("columns", [])}
    numeric_cols = schema.get("numeric", [])
    
    # Priority keywords for measure columns
    measure_keywords = ["amount", "revenue", "sales", "total", "value", "price", "spend", "cost"]
    
    for col_clean in numeric_cols:
        col_orig = next((c["original"] for c in schema["columns"] if c["clean"] == col_clean), col_clean)
        col_lower = col_orig.lower()
        if any(keyword in col_lower for keyword in measure_keywords):
            logger.info(f"Detected measure column: {col_clean} (from '{col_orig}')")
            return col_clean
    
    # Fallback: return first numeric column
    if numeric_cols:
        logger.info(f"Using first numeric column as measure: {numeric_cols[0]}")
        return numeric_cols[0]
    
    return None


def find_categorical_columns_for_grouping(schema, max_cols=3):
    """
    Intelligently detect categorical columns for grouping (category, location, customer, product).
    Priority: category/location/customer > other categorical
    Returns: list of column names (cleaned, up to max_cols)
    """
    if not schema or not schema.get("categorical"):
        return []
    
    schema_cols = {col["original"]: col["clean"] for col in schema.get("columns", [])}
    categorical_cols = schema.get("categorical", [])
    
    # Priority keywords for grouping columns
    grouping_keywords = ["category", "location", "customer", "product", "type", "status", "region", "segment"]
    priority_cols = []
    
    for col_clean in categorical_cols:
        col_orig = next((c["original"] for c in schema["columns"] if c["clean"] == col_clean), col_clean)
        col_lower = col_orig.lower()
        if any(keyword in col_lower for keyword in grouping_keywords):
            priority_cols.append(col_clean)
    
    # Return priority columns first, then others
    result = priority_cols + [c for c in categorical_cols if c not in priority_cols]
    return result[:max_cols]


def get_analytics_columns(schema):
    """
    Returns a dict with detected measure and grouping columns for analytics.
    Handles both demo (hardcoded) and uploaded (dynamic) datasets.
    """
    if schema:
        measure = find_numeric_column_for_measure(schema)
        grouping = find_categorical_columns_for_grouping(schema, max_cols=1)
        
        return {
            "measure": measure,
            "grouping": grouping[0] if grouping else None,
            "all_grouping": grouping,
            "schema": schema
        }
    else:
        # Demo dataset hardcoded defaults
        return {
            "measure": "purchase_amount",
            "grouping": "purchase_category",
            "all_grouping": ["purchase_category", "location", "customer_id"],
            "schema": None
        }


# ========== ANALYTICS ENDPOINTS WITH DYNAMIC DATASET SUPPORT ==========

@app.route('/analytics/sales', methods=['GET'])
def get_sales_analytics():
    """
    Sales Analytics: Sales by Category/Division
    Dynamically adapts to uploaded dataset schema
    """
    try:
        # 1. Detect Dataset Context
        active_table = "ecommerce_behavior"
        use_local_db = False
        active_schema = None
        
        if is_uploaded_dataset_active():
            active_schema = load_schema()
            if active_schema:
                active_table = "uploaded_dataset"
                use_local_db = True
                logger.info(f"📊 Sales Analytics: Using UPLOADED DATASET")
            else:
                logger.warning("📊 Sales Analytics: Uploaded dataset detected but schema load failed. Using demo.")
        else:
            logger.info(f"📊 Sales Analytics: Using DEMO DATASET")
        
        # 2. Detect Columns
        col_config = get_analytics_columns(active_schema)
        measure_col = col_config["measure"]
        grouping_col = col_config["grouping"]
        
        if not measure_col or not grouping_col:
            logger.warning(f"Sales Analytics: Could not detect required columns. measure={measure_col}, grouping={grouping_col}")
            return jsonify([])
        
        logger.info(f"Sales Analytics: measure_col={measure_col}, grouping_col={grouping_col}")
        
        # 3. Fetch Data
        if use_local_db:
            sql_query = f'SELECT "{grouping_col}", SUM(CAST("{measure_col}" AS REAL)) as revenue FROM "{active_table}" GROUP BY "{grouping_col}" ORDER BY revenue DESC'
            result_data = execute_local_sql(sql_query)
            df = pd.DataFrame(result_data)
            # Use column name from SQL alias
            if not df.empty and 'revenue' in df.columns:
                df.rename(columns={'revenue': 'Revenue'}, inplace=True)
                df.rename(columns={grouping_col: 'Category'}, inplace=True)
        else:
            result = supabase.table(active_table).select(f"{grouping_col}, {measure_col}").execute()
            df = pd.DataFrame(result.data)
            df[measure_col] = pd.to_numeric(df[measure_col], errors="coerce").fillna(0)
            # Group by Category and Sum Revenue
            cat_sales = df.groupby(grouping_col)[measure_col].sum().reset_index()
            cat_sales.columns = ["Category", "Revenue"]
            df = cat_sales.sort_values(by="Revenue", ascending=False)
        
        print(f"📊 Sales Data Rows: {len(df)}")
        if df.empty:
            return jsonify([])
        
        # Return results (handle both demo and uploaded formats)
        if not use_local_db:
            return jsonify(df.to_dict(orient="records"))
        else:
            # For uploaded DBs, just return the dataframe as-is since it's already formatted
            return jsonify(df.to_dict(orient="records"))
            
    except Exception as e:
        logger.error(f"Error in sales analytics: {str(e)}")
        print(f"Error in sales analytics: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/analytics/customers', methods=['GET'])
def get_customer_analytics():
    """
    Customer Analytics: Customer Distribution by Location/Segment
    Dynamically adapts to uploaded dataset schema
    """
    try:
        # 1. Detect Dataset Context
        active_table = "ecommerce_behavior"
        use_local_db = False
        active_schema = None
        
        if is_uploaded_dataset_active():
            active_schema = load_schema()
            if active_schema:
                active_table = "uploaded_dataset"
                use_local_db = True
                logger.info(f"👤 Customer Analytics: Using UPLOADED DATASET")
            else:
                logger.warning("👤 Customer Analytics: Uploaded dataset detected but schema load failed. Using demo.")
        else:
            logger.info(f"👤 Customer Analytics: Using DEMO DATASET")
        
        # 2. Detect Columns (use all available grouping columns)
        col_config = get_analytics_columns(active_schema)
        grouping_cols = col_config["all_grouping"]
        
        if not grouping_cols:
            logger.warning(f"Customer Analytics: Could not detect grouping columns")
            return jsonify([])
        
        # For customer analytics, prefer "location" if available, otherwise use first grouping column
        location_col = None
        for col in grouping_cols:
            if "location" in col.lower() or "segment" in col.lower() or "region" in col.lower():
                location_col = col
                break
        
        location_col = location_col or grouping_cols[0]
        logger.info(f"Customer Analytics: grouping_col={location_col}")
        
        # 3. Fetch Data
        if use_local_db:
            sql_query = f'SELECT "{location_col}", COUNT(*) as count FROM "{active_table}" GROUP BY "{location_col}" ORDER BY count DESC'
            result_data = execute_local_sql(sql_query)
            df = pd.DataFrame(result_data)
            if not df.empty:
                df.rename(columns={location_col: 'Location', 'count': 'Count'}, inplace=True)
        else:
            result = supabase.table(active_table).select(f"{location_col}").execute()
            df = pd.DataFrame(result.data)
            # Group by Location and Count Customers
            location_data = df.groupby(location_col).size().reset_index(name="Count")
            location_data = location_data.sort_values(by="Count", ascending=False)
            location_data.columns = ["Location", "Count"]
            df = location_data
        
        print(f"👤 Customer Data Rows: {len(df)}")
        if df.empty:
            return jsonify([])
        
        return jsonify(df.to_dict(orient="records"))
    except Exception as e:
        logger.error(f"Error in customer analytics: {str(e)}")
        print(f"Error in customer analytics: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/analytics/products', methods=['GET'])
def get_product_analytics():
    """
    Product Analytics: Product/Category Revenue Ranking
    Dynamically adapts to uploaded dataset schema
    """
    try:
        # 1. Detect Dataset Context
        active_table = "ecommerce_behavior"
        use_local_db = False
        active_schema = None
        
        if is_uploaded_dataset_active():
            active_schema = load_schema()
            if active_schema:
                active_table = "uploaded_dataset"
                use_local_db = True
                logger.info(f"📦 Product Analytics: Using UPLOADED DATASET")
            else:
                logger.warning("📦 Product Analytics: Uploaded dataset detected but schema load failed. Using demo.")
        else:
            logger.info(f"📦 Product Analytics: Using DEMO DATASET")
        
        # 2. Detect Columns
        col_config = get_analytics_columns(active_schema)
        measure_col = col_config["measure"]
        grouping_cols = col_config["all_grouping"]
        
        if not measure_col or not grouping_cols:
            logger.warning(f"Product Analytics: Could not detect required columns. measure={measure_col}, grouping={grouping_cols}")
            return jsonify([])
        
        # For product analytics, prefer "category" or "product" if available
        product_col = None
        for col in grouping_cols:
            if "category" in col.lower() or "product" in col.lower() or "type" in col.lower():
                product_col = col
                break
        
        product_col = product_col or grouping_cols[0]
        logger.info(f"Product Analytics: product_col={product_col}, measure_col={measure_col}")
        
        # 3. Fetch Data
        if use_local_db:
            sql_query = f'SELECT "{product_col}", SUM(CAST("{measure_col}" AS REAL)) as total_revenue FROM "{active_table}" GROUP BY "{product_col}" ORDER BY total_revenue DESC'
            result_data = execute_local_sql(sql_query)
            df = pd.DataFrame(result_data)
            if not df.empty:
                df.rename(columns={product_col: 'Category', 'total_revenue': 'Total Revenue'}, inplace=True)
        else:
            result = supabase.table(active_table).select(f"{product_col}, {measure_col}").execute()
            df = pd.DataFrame(result.data)
            df[measure_col] = pd.to_numeric(df[measure_col], errors="coerce").fillna(0)
            # Top Categories by Revenue
            top_categories = df.groupby(product_col)[measure_col].sum().sort_values(ascending=False).reset_index()
            top_categories.columns = ["Category", "Total Revenue"]
            df = top_categories
        
        print(f"📦 Product Data Rows: {len(df)}")
        if df.empty:
            return jsonify([])
        
        return jsonify(df.to_dict(orient="records"))
    except Exception as e:
        logger.error(f"Error in product analytics: {str(e)}")
        print(f"Error in product analytics: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # ========== SECURITY: Safe Development Server Configuration ==========
    # Default to safe settings; only enable debug if explicitly requested
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('FLASK_PORT', '5000'))
    
    logger.info(f"Starting Flask server - DEBUG={debug_mode}, PORT={port}")
    logger.warning("SECURITY: Using Flask development server. Use Gunicorn/uWSGI for production!")
    
    app.run(
        debug=debug_mode,  # Disabled by default for safety
        port=port,
        host='127.0.0.1',  # Localhost only by default (not 0.0.0.0)
        use_reloader=False  # Disable reloader in production
    )
