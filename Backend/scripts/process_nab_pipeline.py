import os
import glob
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

# Your Windows path
NAB_DIR = "D:/Downloads/NAB-master"  

def load_and_compile_nab_recursive():
    print("⚡ Step 1: Running deep recursive scan for CSV files inside NAB-master...")
    
    # This matches any .csv file anywhere inside the directory tree
    search_path = os.path.join(NAB_DIR, "**", "*.csv")
    csv_files = glob.glob(search_path, recursive=True)
    
    if not csv_files:
        raise ValueError(f"Zero CSV files found anywhere inside '{NAB_DIR}'. Please check if the archive unzipped fully.")
        
    print(f"🎯 Found a total of {len(csv_files)} CSV data streams across all subdirectories.")
    
    master_frames = []
    
    # Defined categories to keep your dataset focused on system monitoring telemetry
    valid_categories = {
        "realawscloudwatch", "realknowncause", "realtraffic", 
        "realadexchange", "realtweets", "artificialwithanomaly", "artificialnoanomaly"
    }
    
    print("⚡ Step 2: Extracting streams and executing full feature engineering pipeline...")
    for file_full_path in csv_files:
        # Extract folder context to categorize the stream correctly
        parent_folder = os.path.basename(os.path.dirname(file_full_path))
        
        if parent_folder.lower() not in valid_categories:
            continue
            
        try:
            # Read individual time-series metrics
            df = pd.read_csv(file_full_path)
            
            # Skip empty files or non-standard tables
            if df.empty or 'timestamp' not in df.columns or 'value' not in df.columns:
                continue
                
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.rename(columns={'value': 'cpu'}) 
            
            # --- SYNTHESIZE MULTI-VARIATE FEATURE DEPENDECIES ---
            np.random.seed(42)
            df['memory'] = (1024 + df['cpu'] * 25 + np.random.normal(0, 100, len(df))).astype(int)
            df['connections'] = (10 + df['cpu'] * 4 + np.random.normal(0, 15, len(df))).astype(int)
            
            # --- CALCULATE PROJECT VELOCITIES (Formula: X_t - X_t-1) ---
            df['cpu_velocity'] = df['cpu'].diff().fillna(0)
            df['memory_velocity'] = df['memory'].diff().fillna(0)
            df['connections_velocity'] = df['connections'].diff().fillna(0)
            
            # --- CALCULATE ROLLING AVERAGES ---
            df['rolling_cpu'] = df['cpu'].rolling(window=5, min_periods=1).mean()
            df['rolling_memory'] = df['memory'].rolling(window=5, min_periods=1).mean()
            df['rolling_connections'] = df['connections'].rolling(window=5, min_periods=1).mean()
            
            # --- AUTOMATED STATISTICAL ANOMALY TARGET LABELING ---
            df['is_failure_imminent'] = ((df['rolling_cpu'] > 85) | 
                                          (df['connections'] > 420) | 
                                          (df['cpu_velocity'].abs() > 25)).astype(int)
            
            master_frames.append(df)
            
        except Exception as e:
            # Silently pass corrupted or locked system file lines to ensure processing completion
            continue
            
    if not master_frames:
        raise ValueError("Could not parse data points from found CSV structures. Check file formats.")
        
    df_master = pd.concat(master_frames, ignore_index=True)
    print(f"✅ Step 3: Master compilation complete. Total integrated rows: {df_master.shape[0]}")
    return df_master

if __name__ == "__main__":
    try:
        df_dataset = load_and_compile_nab_recursive()
        
        features = ['cpu', 'memory', 'connections', 'cpu_velocity', 'memory_velocity', 
                    'connections_velocity', 'rolling_cpu', 'rolling_memory', 'rolling_connections']
        
        X = df_dataset[features]
        y = df_dataset['is_failure_imminent']
        
        print("⚡ Step 4: Stratifying dataset into Training (80%) and Test (20%) partitions...")
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
        
        print(f"📊 Final Dataset Distribution Class balance:\n{y_train.value_counts()}")
        
        # Write processed dataset out into your current active backend directory context
        df_dataset.to_csv("processed_metric_features.csv", index=False)
        print("🎉 Step 5: Engineering data file written cleanly to 'processed_metric_features.csv'!")
        
    except Exception as e:
        print(f"\n❌ Execution pipeline failed: {e}")