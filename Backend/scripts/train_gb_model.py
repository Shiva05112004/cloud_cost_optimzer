import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import classification_report, roc_auc_score

print("⚡ Loading processed feature engineering dataset...")
df = pd.read_csv("processed_metric_features.csv")

# Project architecture features matching your schema exactly
features = ['cpu', 'memory', 'connections', 'cpu_velocity', 'memory_velocity', 
            'connections_velocity', 'rolling_cpu', 'rolling_memory', 'rolling_connections']

X = df[features]
y = df['is_failure_imminent']

print("⚡ Splitting dataset for evaluation...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

print("🌲 Initializing Gradient Boosting Classifier (Sequential Learning Phase)...")
# Using shallow depths and slight subsampling for faster training across 365k rows
model = GradientBoostingClassifier(
    n_estimators=100, 
    learning_rate=0.1, 
    max_depth=4, 
    subsample=0.8,
    random_state=42
)

print("🏋️‍♂️ Training model kernel (this may take a minute due to large dataset size)...")
model.fit(X_train, y_train)

print("\n--- 🏁 Verification Model Performance Evaluation ---")
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]
print(classification_report(y_test, y_pred))
print(f"ROC AUC Score: {roc_auc_score(y_test, y_prob):.4f}")

# Save the binary asset right inside your ml/ services core folder
model_path = "app/ml/predictive_model.joblib"
joblib.dump(model, model_path)
print(f"\n🎉 Model compiled and exported successfully to: {model_path}")