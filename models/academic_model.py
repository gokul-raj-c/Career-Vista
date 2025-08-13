import pandas as pd
import joblib

model = joblib.load("models/academic_prediction_model.pkl")

def predict_result_academic(val):
    input_df = pd.DataFrame([val])
    return model.predict(input_df)[0]
