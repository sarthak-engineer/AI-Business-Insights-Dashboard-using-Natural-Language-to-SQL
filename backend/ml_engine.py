# -*- coding: utf-8 -*-
# backend/ml_engine.py
import sys

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import os

class MLEngine:
    def __init__(self):
        self.encoder = LabelEncoder()
        self.model = None
        self.is_trained = False

    def train_churn_model(self, df):
        """
        Trains a simple Churn Prediction model using RandomForest.
        For demo purposes, we'll create a synthetic 'churn' label based on engagement.
        """
        if df.empty or len(df) < 10:
            return False
            
        try:
            # 1. Feature Engineering
            # Use numeric features and encode categorical ones
            ml_df = df.copy()
            
            # Target variable (synthetic): Churn if satisfaction < 4 or return rate > 0.5
            # Or if frequency is 'Rarely'
            if 'customer_satisfaction' in ml_df.columns:
                ml_df['churn'] = ((ml_df['customer_satisfaction'] < 4) | (ml_df['return_rate'] > 0.4)).astype(int)
            else:
                # Fallback synthetic target
                ml_df['churn'] = (ml_df['purchase_amount'] < ml_df['purchase_amount'].mean() * 0.5).astype(int)

            features = ['age', 'purchase_amount', 'product_rating', 'return_rate', 'customer_satisfaction']
            # Filter only existing columns
            features = [f for f in features if f in ml_df.columns]
            
            if not features:
                return False

            X = ml_df[features].fillna(0)
            y = ml_df['churn']

            self.model = RandomForestClassifier(n_estimators=50, random_state=42)
            self.model.fit(X, y)
            self.is_trained = True
            self.features = features
            return True
        except Exception as e:
            print(f"ML Training Error: {e}")
            return False

    def predict_churn(self, df):
        """Returns churn probability and risk level for the dataset with intelligent fallback."""
        if df.empty:
            return {
                "status": "fallback",
                "risk": "Unknown",
                "message": "🔍 No data available for churn analysis. Try a broader query to include more customer records.",
                "reason": "Dataset is empty",
                "suggestion": "Expand filters or remove restrictions to include more data points."
            }
        
        if not self.is_trained:
            # Provide meaningful analysis even without ML model training
            if len(df) >= 3:
                # Basic statistical analysis when ML isn't available
                avg_satisfaction = df['customer_satisfaction'].mean() if 'customer_satisfaction' in df.columns else None
                if avg_satisfaction and avg_satisfaction < 3:
                    return {
                        "status": "fallback",
                        "risk": "High",
                        "message": "⚠️ **Preliminary assessment**: Customer satisfaction is low (avg {:.1f}/5), indicating potential churn risk.".format(avg_satisfaction),
                        "reason": "Insufficient historical data for ML model",
                        "suggestion": "🎯 Action: Improve support/product quality to reduce churn risk."
                    }
                elif avg_satisfaction and avg_satisfaction >= 4:
                    return {
                        "status": "fallback",
                        "risk": "Low",
                        "message": "✅ **Preliminary assessment**: Customer satisfaction is strong (avg {:.1f}/5), suggesting low churn risk.".format(avg_satisfaction),
                        "reason": "Insufficient historical data for ML model",
                        "suggestion": "📈 Action: Maintain current service quality while gathering more historical data."
                    }
            
            return {
                "status": "fallback",
                "risk": "Unknown",
                "message": "📊 **Limited scope analysis**: Need at least 10 historical records to build predictive model.",
                "reason": "Insufficient data ({} records) for ML training".format(len(df)),
                "suggestion": "Try including more customer records or broader date ranges."
            }
        
        if len(df) < 5:
            return {
                "status": "fallback",
                "risk": "Unknown",
                "message": "📈 **Sample-based analysis**: Dataset too small for high-confidence predictions. Here's what we observe...",
                "reason": "Only {} records available".format(len(df)),
                "suggestion": "Expand query to include more data for accurate churn assessment."
            }
        
        try:
            X = df[self.features].fillna(0)
            preds = self.model.predict(X)
            churn_count = sum(preds)
            churn_rate = (churn_count / len(df)) * 100
            
            # Assess confidence based on dataset size
            confidence = "High" if len(df) >= 50 else ("Moderate" if len(df) >= 20 else "Low")
            
            risk = "High" if churn_rate > 30 else ("Medium" if churn_rate > 15 else "Low")
            message = f"🎯 **{risk} Risk** ({confidence} confidence): {churn_rate:.1f}% users likely to churn."
            
            return {
                "status": "success",
                "risk": risk,
                "message": message,
                "confidence": confidence,
                "churn_rate": churn_rate
            }
        except Exception as e:
            return {
                "status": "fallback",
                "risk": "Error",
                "message": "⚠️ Prediction service encountered a processing issue.",
                "reason": str(e)[:50],
                "suggestion": "Try simplifying filters or broadening your data range."
            }

    def get_recommendations(self, df):
        """Enhanced Recommendation logic based on spending behavior with meaningful fallbacks."""
        if df.empty:
            return ["📊 Unable to generate recommendations without data. Refine your query to include customer records."]
        
        recs = []
        
        # Check for purchase_amount column
        if 'purchase_amount' not in df.columns:
            return ["💡 Recommendation unavailable: Dataset doesn't include spending metrics. Try including purchase-related fields."]
        
        avg_spend = df['purchase_amount'].mean()
        max_spend = df['purchase_amount'].max()
        
        # Add data size context
        data_size_note = f"(based on {len(df)} customer records)"
        
        # Tier 1: High Spenders (>$300)
        if avg_spend > 300:
            recs.append(f"💎 **Premium Tier Opportunity** {data_size_note}: Average spending ₹{avg_spend:,.0f}. **Action**: Introduce luxury products and VIP programs to maximize segment value.")
        
        # Tier 2: Moderate Spenders ($150-300)
        elif avg_spend > 150:
            recs.append(f"📦 **Cross-sell & Bundle Strategy** {data_size_note}: Average spending ₹{avg_spend:,.0f}. **Action**: Bundle products to increase basket size and customer lifetime value.")
        
        # Tier 3: Budget Segment (<$150)
        else:
            recs.append(f"🏷️ **Value & Volume Focus** {data_size_note}: Average spending ₹{avg_spend:,.0f}. **Action**: Offer discounts, volume deals, and essential products to drive volume.")
        
        # Additional insight: Spending range
        if max_spend > avg_spend * 3:
            recs.append(f"🔍 **Segmentation Insight**: Significant variation detected (₹{df['purchase_amount'].min():,.0f}→₹{max_spend:,.0f}). Consider tiered strategies for different customer segments.")
        
        return recs

    def detect_anomalies(self, df):
        """Enhanced anomaly detection with statistical methods and meaningful messaging."""
        if df.empty:
            return []
        
        anomalies = []
        
        # Check for purchase_amount column
        if 'purchase_amount' not in df.columns:
            return ["📌 Anomaly detection unavailable: Dataset lacks purchase data. Include spending metrics for analysis."]
        
        amounts = df['purchase_amount'].dropna()
        if len(amounts) < 2:
            return []  # Need at least 2 values for meaningful analysis
        
        avg = amounts.mean()
        std = amounts.std() if len(amounts) > 1 else 0
        
        # Multi-method anomaly detection
        # Method 1: 3x Average (Original)
        limit_3x = avg * 3
        outliers_3x = df[df['purchase_amount'] > limit_3x]
        
        # Method 2: 2-sigma (Statistical)
        if std > 0:
            limit_2sigma = avg + (2 * std)
            outliers_2sigma = df[df['purchase_amount'] > limit_2sigma]
        else:
            outliers_2sigma = pd.DataFrame()
        
        # Report strongest anomaly detection
        if not outliers_3x.empty:
            count = len(outliers_3x)
            pct = (count / len(df)) * 100
            anomalies.append(f"🚩 **Extreme Behavior Alert** ({pct:.1f}% of dataset): {count} purchase(s) exceeded 3x average threshold (Limit: ₹{limit_3x:,.0f}). Suggests premium/bulk/anomalous transactions.")
        
        elif not outliers_2sigma.empty and len(outliers_2sigma) > 0:
            count = len(outliers_2sigma)
            pct = (count / len(df)) * 100
            anomalies.append(f"⚠️ **Unusual Pattern Detected** ({pct:.1f}% of dataset): {count} case(s) show spending 2 standard deviations above average (₹{limit_2sigma:,.0f}). Worth investigating.")
        
        # If few anomalies, provide confirmation
        if not anomalies and len(df) >= 10:
            anomalies.append("✅ **No anomalies detected**: Spending patterns are within normal ranges. Dataset shows consistent behavior.")
        
        return anomalies

# Global engine instance for performance (avoiding re-initialization overhead)
_global_engine = None

def get_ml_insights(df):
    """
    Entry point for generating ML-driven insights.
    Optimized to use a persistent engine instance and avoid redundant training
    on small datasets if the model is already sufficiently trained.
    """
    global _global_engine
    if _global_engine is None:
        _global_engine = MLEngine()
    
    # Only re-train if we have a substantial new dataset (e.g. upload) 
    # or if the current engine is not trained yet.
    # For performance, we avoid re-training on very small query results (< 10 rows)
    # as the statistical fallbacks in predict_churn are faster and more accurate.
    if not _global_engine.is_trained and len(df) >= 15:
        _global_engine.train_churn_model(df)
    
    return {
        "churn_prediction": _global_engine.predict_churn(df),
        "recommendations": _global_engine.get_recommendations(df),
        "anomalies": _global_engine.detect_anomalies(df)
    }
