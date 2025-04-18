import joblib

SLEEP_QUALITY_MODEL = joblib.load("./models/sleep_quality_model.pkl")

SLEEP_STAGE_MODEL = joblib.load("./models/sleep_stage_model.pkl")
