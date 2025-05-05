import pickle
import numpy as np

with open("models/scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

model_names = ["Random_Forest", "SVM", "Gradient_Boosting", "Logistic_Regression"]
models = {name: pickle.load(open(f"models/{name}.pkl", "rb")) for name in model_names}

with open("models/validation_scores.pkl", "rb") as f:
    validation_scores = pickle.load(f)

def predict_jaundice_ml(user_input):
    user_input_scaled = scaler.transform([user_input])
    tb, alt, itching, urine, stool = user_input[2], user_input[4], user_input[10], user_input[11], user_input[9]

    if tb > 3.0 and alt > 120:
        selected_model = "Random_Forest"
    elif tb > 3.0:
        selected_model = "SVM"
    elif itching == 1 and urine == 1:
        selected_model = "Gradient_Boosting"
    elif urine == 1 and stool == 1:
        selected_model = "Logistic_Regression"
    else:
        selected_model = max(validation_scores, key=validation_scores.get)

    model = models[selected_model]
    prediction = model.predict(user_input_scaled)[0]
    return "Jaundice Detected" if prediction == 1 else "No Jaundice"
