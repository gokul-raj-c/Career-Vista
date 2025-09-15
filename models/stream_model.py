import pandas as pd
import joblib

model = joblib.load("models/stream_selection_model.pkl")

def predict_result_stream(val):
    input_df = pd.DataFrame([val])
    return model.predict(input_df)[0]

