from pathlib import Path
import joblib
import pandas as pd

MODEL_PATH = Path(__file__).resolve().parent / "model.pkl"

def predict_price(data):
    if not MODEL_PATH.exists():
        raise FileNotFoundError("model.pkl not found. Run setup.py first.")
    model = joblib.load(MODEL_PATH)
    return float(model.predict(pd.DataFrame([data]))[0])
