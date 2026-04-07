import warnings
from datetime import datetime

import joblib
import numpy as np
import sklearn

MODEL_TRAINING_VERSION = "1.6.1"
MODEL_PATH = "random_forest_addiction_model.pkl"

model = joblib.load(MODEL_PATH)

if sklearn.__version__ != MODEL_TRAINING_VERSION:
    warnings.warn(
        f"Model was trained against scikit-learn {MODEL_TRAINING_VERSION}, but runtime is using {sklearn.__version__}.",
        RuntimeWarning,
    )


def predict_addiction(payload: dict):
    input_data = np.array(
        [
            float(payload["daily_screen_time"]),
            float(payload["gaming_time"]),
            float(payload["social_media_usage"]),
            float(payload["app_sessions"]),
            float(payload["notifications"]),
            float(payload["night_usage"]),
        ]
    ).reshape(1, -1)

    prediction = model.predict(input_data)[0]
    probability = model.predict_proba(input_data)[0][prediction]
    confidence = round(float(probability) * 100, 2)

    if prediction == 1:
        result = "User is Digitally Addicted"
    else:
        result = "User is Not Digitally Addicted"

    if confidence < 40:
        risk = "Low"
    elif confidence < 70:
        risk = "Medium"
    else:
        risk = "High"

    return {
        "prediction": int(prediction),
        "prediction_text": result,
        "confidence": confidence,
        "risk": risk,
        "timestamp": datetime.now(),
    }
