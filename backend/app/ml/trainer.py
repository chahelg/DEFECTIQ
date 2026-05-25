import os
from typing import Tuple
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score
from app.ml.model_registry import register_model

MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models'))
os.makedirs(MODEL_DIR, exist_ok=True)


def _feature_engineer(df: pd.DataFrame) -> pd.DataFrame:
    # Basic features: age_days, reopen_count, priority mapped, text_length
    now = pd.Timestamp.utcnow()
    df['opened_at'] = pd.to_datetime(df.get('opened_at'), utc=True)
    df['closed_at'] = pd.to_datetime(df.get('closed_at'), utc=True)
    df['age_days'] = (now - df['opened_at']).dt.days.fillna(0).astype(int)
    df['is_open'] = df['closed_at'].isna().astype(int)
    df['reopen_count'] = pd.to_numeric(df.get('reopen_count')).fillna(0).astype(int)
    df['priority_score'] = df.get('priority').map({'1 - Critical': 4, '2 - High':3, '3 - Moderate':2, '4 - Low':1}).fillna(0)
    df['text'] = (df.get('short_description', '') + ' ' + df.get('description', '')).fillna('')
    df['text_len'] = df['text'].str.len()
    return df


def train_sla_breach_model(df: pd.DataFrame, model_name: str = 'sla_breach', version: str = 'v1') -> dict:
    df = _feature_engineer(df.copy())

    # target: sla_breached = SLA due passed and still open
    df['sla_due'] = pd.to_datetime(df.get('sla_due'))
    df['sla_breached'] = ((df['sla_due'].notna()) & (df['sla_due'] < pd.Timestamp.utcnow()) & (df['is_open'] == 1)).astype(int)

    features = ['age_days', 'is_open', 'reopen_count', 'priority_score', 'text_len']
    X = df[features]
    y = df['sla_breached']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    clf = XGBClassifier(use_label_encoder=False, eval_metric='logloss', n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    preds = clf.predict(X_test)
    probs = clf.predict_proba(X_test)[:,1]

    metrics = {
        'accuracy': float(accuracy_score(y_test, preds)),
        'precision': float(precision_score(y_test, preds, zero_division=0)),
        'recall': float(recall_score(y_test, preds, zero_division=0)),
    }

    model_path = os.path.join(MODEL_DIR, f"{model_name}_{version}.joblib")
    joblib.dump({'model': clf, 'features': features}, model_path)

    register_model(model_name, version, model_path, metrics)

    return {'model_path': model_path, 'metrics': metrics}


def train_assignment_model(df: pd.DataFrame, model_name: str = 'assignment_recommend', version: str = 'v1') -> dict:
    df = _feature_engineer(df.copy())
    df['assignment_group'] = df.get('assignment_group').fillna('UNASSIGNED')

    features = ['age_days', 'is_open', 'reopen_count', 'priority_score', 'text_len']
    X = df[features]
    y = df['assignment_group']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    clf = XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    preds = clf.predict(X_test)

    # simplistic metric: accuracy
    metrics = {'accuracy': float(accuracy_score(y_test, preds))}

    model_path = os.path.join(MODEL_DIR, f"{model_name}_{version}.joblib")
    joblib.dump({'model': clf, 'features': features}, model_path)
    register_model(model_name, version, model_path, metrics)
    return {'model_path': model_path, 'metrics': metrics}


def train_resolution_model(df: pd.DataFrame, model_name: str = 'resolution_time', version: str = 'v1') -> dict:
    df = _feature_engineer(df.copy())
    # target: resolution time in days
    df['closed_at'] = pd.to_datetime(df.get('closed_at'))
    df['resolution_days'] = (df['closed_at'] - df['opened_at']).dt.days.fillna(0)

    features = ['age_days', 'reopen_count', 'priority_score', 'text_len']
    X = df[features]
    y = df['resolution_days']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    from sklearn.ensemble import RandomForestRegressor

    reg = RandomForestRegressor(n_estimators=100, random_state=42)
    reg.fit(X_train, y_train)

    preds = reg.predict(X_test)

    metrics = {'rmse': float(np.sqrt(np.mean((preds - y_test) ** 2)))}

    model_path = os.path.join(MODEL_DIR, f"{model_name}_{version}.joblib")
    joblib.dump({'model': reg, 'features': features}, model_path)
    register_model(model_name, version, model_path, metrics)
    return {'model_path': model_path, 'metrics': metrics}


def load_model_entry(model_name: str):
    from app.ml.model_registry import get_model_entry
    entry = get_model_entry(model_name)
    if not entry:
        return None
    model_obj = joblib.load(entry['path'])
    return model_obj, entry


def predict_from_features(model_obj: dict, features: dict) -> dict:
    model = model_obj['model']
    feat_names = model_obj['features']
    X = np.array([[features.get(f, 0) for f in feat_names]])
    prob = float(model.predict_proba(X)[0,1])
    pred = int(model.predict(X)[0])
    return {'prediction': pred, 'probability': prob}
