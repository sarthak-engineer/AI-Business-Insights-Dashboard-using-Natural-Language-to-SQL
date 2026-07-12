# AI-Powered Natural Language to SQL Business Insights Dashboard

## 📖 Overview

AI-Powered Natural Language to SQL Business Insights Dashboard is a full-stack Business Intelligence platform that enables users to interact with structured datasets using natural language instead of SQL.

The system converts user questions into SQL queries using Groq Llama 3.3, validates them for security, executes them on PostgreSQL or SQLite databases, and presents the results through interactive dashboards with AI-generated business insights.

Designed for analysts, business users, and non-technical stakeholders, the platform simplifies data exploration while integrating Generative AI, Machine Learning, Data Visualization, and Business Intelligence into a single application.

---

# ✨ Features

## 🧠 Natural Language → SQL

- Convert plain English into SQL
- Schema-aware prompt generation
- Semantic query normalization
- SQL optimization
- Read-only execution
- SQL validation layer

Example

User Query

```text
What is the total revenue by category?
```

Generated SQL

```sql
SELECT category,
SUM(revenue) AS total_revenue
FROM sales
GROUP BY category
ORDER BY total_revenue DESC;
```

---

## 📊 Interactive Dashboard

- Revenue Analysis
- Monthly Sales Trends
- Customer Insights
- Product Category Performance
- Purchase Behaviour Analysis
- Customer Retention
- Spending Analytics
- KPI Cards
- Interactive Charts
- Searchable Tables

---

## 🤖 AI Business Insights

Automatically generates

- Executive summaries
- Revenue observations
- Trend analysis
- Business recommendations
- Statistical summaries
- Confidence indicators

---

## 📁 Dynamic Dataset Upload

- Upload CSV datasets
- Automatic schema detection
- SQLite table generation
- Data preprocessing
- Instant querying

---

## 🤖 Machine Learning

### Customer Churn Prediction

Features

- Purchase Frequency
- Satisfaction Score
- Spending History
- Return Behaviour

Model

- RandomForestClassifier

### Spending Anomaly Detection

- Statistical deviation analysis
- High-risk customer identification
- Spending anomaly detection

---

## 🔒 Security

- Read-only SQL execution
- Keyword filtering
- SQL validation
- DROP blocked
- DELETE blocked
- UPDATE blocked
- ALTER blocked
- SQLite sandbox
- Environment variable protection

---

## ⚡ Performance

- AI response caching
- Optimized prompt engineering
- Efficient dataframe operations
- Async API requests
- Lightweight backend

---

# 🏗 System Architecture

```text
User

↓

React + Vite Frontend

↓

Flask REST API

↓

Semantic Processing Layer

↓

Groq Llama 3.3

↓

SQL Validation Layer

↓

PostgreSQL / SQLite

↓

Pandas + Machine Learning

↓

Business Insights Engine

↓

Interactive Dashboard
```

---

# 🛠 Technology Stack

## Frontend

- React.js
- Vite
- JavaScript
- HTML
- CSS
- Recharts

## Backend

- Python
- Flask
- REST API

## Database

- PostgreSQL (Supabase)
- SQLite

## AI

- Groq API
- Llama 3.3

## Machine Learning

- Pandas
- NumPy
- Scikit-Learn

---

# 📂 Project Structure

```text
AI-Business-Insights/
│
├── backend/
│   ├── app.py
│   ├── routes/
│   ├── services/
│   ├── models/
│   ├── utils/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── datasets/
├── screenshots/
├── README.md
└── .env
```

Update the structure if your repository differs.

---

# 🚀 Installation

## Clone Repository

```bash
git clone https://github.com/sarthak-engineer/AI-Business-Insights-Dashboard-using-Natural-Language-to-SQL.git
cd AI-Business-Insights-Dashboard-using-Natural-Language-to-SQL
```

## Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

---

# 🔑 Environment Variables

Create a `.env` file.

```env
GROQ_API_KEY=YOUR_GROQ_API_KEY

SUPABASE_URL=YOUR_SUPABASE_URL

SUPABASE_KEY=YOUR_SUPABASE_KEY
```

---

# 🔄 Workflow

```text
Natural Language Question

↓

Prompt Engineering

↓

Groq Llama 3.3

↓

SQL Generation

↓

SQL Validation

↓

Database Execution

↓

Data Processing

↓

Machine Learning

↓

Business Insights

↓

Interactive Dashboard
```

---

# 📈 Supported KPIs

- Total Revenue
- Monthly Revenue
- Average Purchase Value
- Revenue Growth
- Customer Retention
- Customer Churn
- Top Categories
- Customer Satisfaction
- Spending Analytics

---

# 💻 Example

Question

```text
Show monthly revenue trend for 2025
```

Generated SQL

```sql
SELECT month,
SUM(revenue)
FROM sales
GROUP BY month
ORDER BY month;
```

Output

- Revenue chart
- KPI cards
- AI insights
- Trend summary

---

# 🧪 Testing

Validated for

- Natural Language conversion
- SQL generation
- Secure execution
- CSV upload
- API integration
- Dashboard responsiveness
- Dynamic schema handling
- AI insight generation

> Include quantitative accuracy metrics only if they were actually measured.

---

# 🔮 Future Improvements

- Role Based Access Control
- Conversational Memory
- Multi-turn Analytics
- Retrieval-Augmented Generation (RAG)
- Fine-tuned NL-to-SQL models
- Multi-database support
- Forecasting models
- PDF/Excel export
- Authentication
- Docker deployment
- Kubernetes deployment

---

# 📸 Screenshots

Create a `screenshots/` folder and add images such as:

```
screenshots/
├── dashboard.png
├── query.png
├── insights.png
├── upload.png
└── architecture.png
```

Example:

```md
![Dashboard](screenshots/dashboard.png)
```

---

# 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push the branch
5. Open a Pull Request

---

# 📄 License

This project is licensed under the MIT License.

---

# 🙏 Acknowledgements

- Groq API
- Llama 3.3
- React
- Flask
- PostgreSQL
- SQLite
- Scikit-Learn
- Pandas
- NumPy
- Recharts

---

# 👨‍💻 Author

**Sarthak B.C.**

Artificial Intelligence & Machine Learning Engineer

### Technologies Used

- Python
- React.js
- Flask
- PostgreSQL
- SQLite
- Groq Llama 3.3
- Pandas
- NumPy
- Scikit-Learn
- Recharts

---

⭐ If you found this project useful, consider giving it a star.
