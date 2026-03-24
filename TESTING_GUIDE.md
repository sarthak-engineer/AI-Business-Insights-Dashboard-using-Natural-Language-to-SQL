# 🚀 Testing the Analytics Fix in the React Dashboard

## Prerequisites

Both development servers must be running:

✅ **Backend**: http://localhost:5000 (Flask)
✅ **Frontend**: http://localhost:5173 (React with Vite)

### Starting the Servers

**Terminal 1 - Backend**:
```bash
cd backend
python -m flask run --no-reload
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm run dev
```

---

## Test Procedure

### Scenario 1: View Analytics with Demo Dataset (DEFAULT)

1. **Open Browser**: Navigate to `http://localhost:5173`
2. **Scroll Down**: See three analytics sections:
   - 📊 **Sales Analytics** chart (top-left) - Shows ~24 product categories
   - 👤 **Customer Analytics** chart (top-right) - Shows customer distribution
   - 📦 **Product Analytics** chart (bottom) - Shows top products by revenue
3. **Verify**: All charts show demo data (original hardcoded values)
4. **Note**: Export feature works, charts are interactive

**Expected Demo Data**:
- Sales: 24 categories like "Jewelry & Accessories", "Sports & Outdoors", etc.
- Customer: 969 location groups scattered worldwide
- Product: 24 categories ranked by total revenue

---

### Scenario 2: Upload a CSV and See Analytics Change

#### Step 1: Prepare Test CSV
Create a file `sales_test.csv` with content:
```csv
Region,Sales_Amount,Product_Type,Manager,Quarter
North,5000,Electronics,Alice,Q1
South,3000,Furniture,Bob,Q1
East,4500,Electronics,Charlie,Q2
West,6000,Furniture,Diana,Q2
East,7000,Clothing,Ernest,Q3
South,2500,Clothing,Fiona,Q3
```

#### Step 2: Upload File
1. **Look for "Upload Dataset" button** (usually near top of dashboard)
2. **Click Upload** and select `sales_test.csv`
3. **Wait** for confirmation message: `✅ sales_test.csv: Successfully processed...`
4. **Note the schema**:
   - Columns detected: `region`, `sales_amount`, `product_type`, `manager`, `quarter`
   - Numeric: `sales_amount`
   - Categorical: `region`, `product_type`, `manager`, `quarter`

#### Step 3: Observe Analytics Change
Immediately after upload, all three analytics should change to show **uploaded data**:

**Sales Analytics Now Shows**:
- Only 3 regions (North, South, East, West)
- Total sales by region (sum of sales_amount)
- Example values: North=5000, South=5500, East=11500, West=6000

**Customer Analytics Now Shows**:
- Only 3-4 groups (regions or product types)
- Count of records per group
- Example: South=2, North=1, etc.

**Product Analytics Now Shows**:
- Only 3 categories (Electronics, Furniture, Clothing)
- Total sales by product type
- Example: Electronics=11500, Furniture=8500, Clothing=9500

| Data | Demo | After Upload |
|------|------|--------------|
| Sales Categories | 24 | 3-4 (from uploaded file) |
| Customer Groups | 969 | 3-4 (from uploaded file) |
| Product Categories | 24 | 3-4 (from uploaded file) |

**⚠️ KEY VERIFICATION**: 
- Sales values should match your CSV totals
- Categories/groups should be from your CSV columns
- Data must be completely different from demo

---

### Scenario 3: Query the Uploaded Data

1. **Try NL→SQL Query**: Type `show sales by region` in the query box
2. **Expected**: 
   - Results should show YOUR regions (North, South, East, West) NOT demo regions
   - Values should match your uploaded data
   - SQL should use `uploaded_dataset` table instead of `ecommerce_behavior`

---

### Scenario 4: Reset to Demo

1. **Look for "Reset Dataset" button** (usually near upload button)
2. **Click Reset**
3. **Confirm**: System confirms "Successfully reset to demo dataset"
4. **Verify**:
   - Analytics go back to 24 categories
   - Charts show original demo data
   - NL→SQL queries return demo results

| Stage | Sales | Customers | Products |
|-------|-------|-----------|----------|
| Initial (Demo) | 24 | 969 | 24 |
| After Upload | 3-4 | 3-4 | 3-4 |
| After Reset | 24 | 969 | 24 |

---

## Detailed Visual Verification Checklist

### Sales Analytics Chart
```
[DEMO STATE]
✓ Shows 24 colored bars (one per category)
✓ Highest: "Jewelry & Accessories" (~$15,139)
✓ Sorted descending by revenue
✓ Total across all categories: ~$300,000+

[UPLOADED STATE]
✓ Shows only 3-4 colored bars (your categories)
✓ Heights should match YOUR CSV total_sales_by_category
✓ Category names come from YOUR CSV
✓ Totally different from demo layout
```

### Customer Analytics Chart
```
[DEMO STATE]
✓ Pie/bar chart with ~969 individual entries
✓ Shows "Oslo", "London", "New York", etc.
✓ Very fragmented data

[UPLOADED STATE]
✓ Shows only 3-4 entries (from YOUR columns)
✓ Names from YOUR CSV (regions or managers)
✓ Clean, consolidated view
✓ Count matches YOUR file row counts grouped appropriately
```

### Product Analytics Column
```
[DEMO STATE]
✓ Ranking table with 24 products
✓ "Jewelry & Accessories" at top
✓ Clear tier hierarchy

[UPLOADED STATE]
✓ Ranking table with 3-4 products/categories
✓ Names from YOUR CSV product column
✓ Values match YOUR CSV sales amounts
✓ Completely different layout and numbers
```

---

## Troubleshooting

### Issue: Analytics not changing after upload
**Solution**:
- Check browser console (F12) for errors
- Verify backend is running: `curl http://localhost:5000/health`
- Try refreshing browser (Ctrl+R)
- Check backend logs for error messages

### Issue: Numbers don't match your CSV
**Solution**:
- Some numeric columns might have been converted to text
- Check the schema summary from upload confirmation
- Try with simpler numeric values (no currency symbols, commas)
- Ensure your "measure" column contains numbers

### Issue: Categories/groups missing  
**Solution**:
- Verify your CSV has categorical (text) columns
- Schema detection prefers columns with <50 unique values as categorical
- Check the schema summary from upload confirmation

### Issue: Reset doesn't work
**Solution**:
- Backend must be running with no-reload mode
- Check backend logs: `tail -f backend/app.log`
- Try restarting backend server

---

## What to Report if Issues Occur

If something doesn't work as expected, provide:

1. **CSV content**: Share the test file you uploaded
2. **Expected behavior**: What you thought would happen
3. **Actual behavior**: What actually happened
4. **Backend logs**: Last 20 lines of `backend/app.log`
5. **Browser console**: Any console errors (F12)
6. **API response**: Try `curl http://localhost:5000/analytics/sales`

---

## Success Indicators

✅ **You'll know it's working when**:

1. **Demo analytics show** default Supabase data (24 categories, lots of regions)
2. **After upload, same analytics show** your CSV data (different numbers and categories)
3. **Reset brings back** original demo data
4. **All three endpoints** switch correctly:
   - `/analytics/sales`
   - `/analytics/customers`
   - `/analytics/products`
5. **NL→SQL queries adapt** to use uploaded data after upload
6. **Charts update in realtime** without page refresh

---

## Performance Notes

- **Initial load**: Takes ~2-3 seconds (Supabase query for demo data)
- **After upload**: Takes ~1 second (SQLite query for uploaded data)
- **Reset**: Instant (no data fetch needed initially)

---

## Architecture Reminder

```
User Action
    ↓
[React Dashboard]
    ↓
POST /upload → Parse CSV → Detect Schema → Store in SQLite
GET /analytics/{sales|customers|products}
    ↓
[Backend Decision]
    ├─ is_uploaded_dataset_active()?
    │  ├─ YES → Load schema.json → Detect columns → Query SQLite
    │  └─ NO → Use hardcoded demo columns → Query Supabase
    ↓
[DataFrame Processing]
    ├─ Group by detected column
    ├─ Aggregate measure column
    └─ Return formatted JSON
    ↓
[React Charts] ← Display results
```

---

**Ready to test? Start your servers and begin with Scenario 1! 🚀**
