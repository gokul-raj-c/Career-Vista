import pandas as pd
import joblib

model = joblib.load("models/job_role_model.pkl")

def predict_job_role(val):
    input_df = pd.DataFrame([val])
    return model.predict(input_df)[0]

