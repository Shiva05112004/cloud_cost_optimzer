import math
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from pyod.models.iforest import IForest


def build_features(daily_series: Dict[str, float]):
    """Build feature matrix from a date->cost mapping.

    Returns: (X, dates, df)
    - X: numpy array shape (n_samples, n_features)
    - dates: list of date strings in same order
    - df: pandas DataFrame with columns ['date','cost','day_of_week',...]
    """
    # series may be unordered; ensure sorted by date ascending
    s = pd.Series(daily_series)
    s.index = pd.to_datetime(s.index)
    df = s.sort_index().rename_axis('date').reset_index(name='cost')

    df['day_of_week'] = df['date'].dt.weekday  # 0=Mon..6=Sun
    df['rolling_mean_7'] = df['cost'].rolling(7, min_periods=1).mean()
    df['pct_change'] = df['cost'].pct_change().fillna(0.0)

    # Features: raw cost and day_of_week numeric (simple and effective)
    X = df[['cost', 'day_of_week']].to_numpy(dtype=float)
    dates = df['date'].dt.strftime('%Y-%m-%d').tolist()
    return X, dates, df


def magnitude_bucket(cost: float) -> str:
    if cost <= 0:
        return '0'
    # coarse logarithmic bucket
    return str(int(math.floor(math.log10(cost + 1))))


class SeasonalAnomalyDetector:
    """IsolationForest-based detector that is weekday-aware via features

    Fit on a matrix where features include `cost` and `day_of_week`.
    """

    def __init__(self, contamination: float = 0.05):
        self.contamination = float(contamination)
        self.model: Optional[IForest] = None
        self.baselines: Dict[int, Tuple[Optional[float], Optional[float]]] = {}

    def _compute_baselines(self, df: pd.DataFrame):
        baselines: Dict[int, Tuple[Optional[float], Optional[float]]] = {}
        for dow in range(7):
            vals = df.loc[df['day_of_week'] == dow, 'cost'].values
            if len(vals) == 0:
                baselines[dow] = (None, None)
                continue
            q1, q3 = np.percentile(vals, [25, 75])
            iqr = max(q3 - q1, 0.0)
            low = max(0.0, q1 - 1.5 * iqr)
            high = q3 + 1.5 * iqr
            baselines[dow] = (float(low), float(high))
        self.baselines = baselines

    def fit(self, X: np.ndarray, df: pd.DataFrame):
        n = X.shape[0]
        if n < 5:
            self.model = None
            self._compute_baselines(df)
            return

        # Adjust contamination for small samples
        if n < 14:
            cont = max(self.contamination, 0.10)
        elif n < 30:
            cont = max(self.contamination, 0.07)
        else:
            cont = self.contamination

        self.model = IForest(contamination=cont, random_state=42)
        self.model.fit(X)
        self._compute_baselines(df)

    def predict_single(self, x: np.ndarray, day_of_week: int, service: Optional[str] = None) -> Dict:
        """Predict for a single sample `x` (shape (n_features,)).

        Returns a dict with keys: is_anomaly (bool), model_label (0/1 or None), expected_low, expected_high, deviation_pct, reason, magnitude_bucket
        """
        result = {
            'is_anomaly': False,
            'model_label': None,
            'expected_low': None,
            'expected_high': None,
            'deviation_pct': 0.0,
            'reason': 'normal',
            'magnitude_bucket': magnitude_bucket(float(x[0])),
        }

        cost = float(x[0])
        # baseline check
        baseline = self.baselines.get(int(day_of_week))
        if baseline is not None:
            low, high = baseline
            result['expected_low'] = low
            result['expected_high'] = high
            if low is not None and high is not None and (cost < low or cost > high):
                result['deviation_pct'] = ((cost - ((low + high) / 2)) / max((low + high) / 2, 1e-6)) * 100.0
                result['reason'] = 'outside_baseline'

        # model prediction
        if self.model is not None:
            label = int(self.model.predict(x.reshape(1, -1))[0])
            result['model_label'] = label
            # PyOD IForest: predict returns 1 for outlier
            if label == 1:
                result['is_anomaly'] = True
                result['reason'] = 'model_outlier'

        # If baseline flagged and/or model flagged, set overall
        if (result['reason'] != 'normal') and (result['model_label'] == 1 or result['reason'] == 'outside_baseline'):
            result['is_anomaly'] = True

        return result
