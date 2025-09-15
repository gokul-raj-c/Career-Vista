import pandas as pd
import joblib

# Load model
model = joblib.load("models/careerpath_prediction_model.pkl")

# Exact column order from training
feature_names = [
    "stream", "learning_style", "certification", "internship_domain",
    "Math", "Physics", "Chemistry", "Computer_Science", "Biology", "English",
    "Accountancy", "Economics", "Business_Studies",
    "History", "Political_Science", "Psychology"
]

def predict_result_career(val_dict):
    # Convert to DataFrame
    input_df = pd.DataFrame([val_dict])
    # Ensure correct column order
    input_df = input_df.reindex(columns=feature_names)
    # Fill missing with 0
    input_df = input_df.fillna(0)
    # Predict
    return model.predict(input_df)[0]
