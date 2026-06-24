import pandas as pd
from sqlalchemy import create_engine
import joblib

# 1. Connect to PostgreSQL
engine = create_engine("postgresql+psycopg2://postgres:4321@localhost:5432/cloudcost")

print("⚡ Loading processed feature engineering dataset...")
df = pd.read_csv("processed_metric_features.csv")

# 🔧 THE CRITICAL FIX: Cast 0/1 integers to True/False for strict PostgreSQL Boolean types
df['is_failure_imminent'] = df['is_failure_imminent'].astype(bool)

# 2. Standardize columns to lower-case to match PostgreSQL design patterns
if 'timestamp' in df.columns:
    df = df.rename(columns={'timestamp': 'ts'})

# 3. Seed raw metric data features directly to PostgreSQL
print("💾 Seeding metric features table to PostgreSQL...")
df.to_sql("metric_features", engine, if_exists="append", index=False)
print("✅ Successfully injected historical records into 'metric_features'.")

# 4. Load your pre-compiled Gradient Boosting model
print("🌲 Loading pre-trained Gradient Boosting binary asset...")
model = joblib.load("app/ml/predictive_model.joblib")

# 5. Define the EXACT 9 feature columns the model was trained on
features = [
    'cpu', 'memory', 'connections', 
    'cpu_velocity', 'memory_velocity', 'connections_velocity', 
    'rolling_cpu', 'rolling_memory', 'rolling_connections'
]

# Extract only the required feature array for inference
X_inference = df[features]

print("🧠 Running runtime inference classification across the telemetry dataset...")
# Run the predictions safely on the pure feature matrix
df['predicted'] = model.predict(X_inference)

# Convert the predictions column to boolean as well if your predictions table uses a Boolean type
df['predicted'] = df['predicted'].astype(bool)

# 6. Extract only the tracking parameters to write to the predictions index
predictions_df = df[['ts', 'predicted']]

print("💾 Seeding generated predictions index to PostgreSQL...")
predictions_df.to_sql("predictions", engine, if_exists="append", index=False)
print("🎉 Step complete! Database completely seeded and synced.")