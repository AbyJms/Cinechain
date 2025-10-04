import pandas as pd
from flask import Flask, request, jsonify
from sklearn.tree import DecisionTreeClassifier
from flask_cors import CORS 
import numpy as np

# --- 1. SETUP THE FLASK APPLICATION ---
app = Flask(__name__)
CORS(app) # Enable CORS for frontend communication

# --- 2. MOCK DATASET FOR TRAINING THE AI MODEL (3 FEATURES) ---
# Features: [Purchase Count (1-10), Genre Match (0.0-1.0), Social Engagement Score (0-10)]
# Target: [Loyalty Status (0=Low Value, 1=High Value)]

# Training Rule enforced by this data:
# 1. Eligibility (AND): Must have PC>=1 AND GM>=0.2 AND ES>=4
# 2. High Value (OR): Must be Eligible AND (PC>=5 OR GM>=0.8 OR ES>=8)

data = {
    # Test Data points are designed to test the eligibility AND OR rules:
    'Purchase_Count':   [8, 6, 2, 4, 5, 1, 4, 3, 0, 3, 1, 10, 5, 1, 4, 7, 2, 3, 9, 1],
    'Genre_Match':      [0.9, 0.7, 0.9, 0.8, 0.4, 0.2, 0.7, 0.5, 0.9, 0.1, 0.9, 1.0, 0.3, 0.1, 0.9, 0.2, 0.9, 0.7, 0.1, 0.2],
    'Engagement_Score': [10, 9, 5, 8, 4, 4, 7, 6, 10, 8, 3, 10, 3, 5, 3, 4, 8, 7, 4, 1],
    
    # Target Status based on the specific rules:
    # 1 (HV): Meets all minimums AND hits one of the high thresholds.
    # 0 (LV): Fails a minimum OR meets minimums but fails all high thresholds.
    'Loyalty_Status': [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0] 
}

df = pd.DataFrame(data)

# Separate features (X) and target (y)
X = df[['Purchase_Count', 'Genre_Match', 'Engagement_Score']]
y = df['Loyalty_Status']

# Train the Decision Tree Classifier (The AI Model)
model = DecisionTreeClassifier(random_state=42)
model.fit(X, y)

print("AI Loyalty Model Trained Successfully with custom two-stage rule logic. Ready for prediction.")

# --- 3. API ENDPOINT FOR PREDICTION ---

@app.route('/predict_loyalty', methods=['POST'])
def predict_loyalty():
    """
    Receives user data (3 features) from the frontend and returns a loyalty prediction.
    """
    try:
        # Get JSON data sent from the JavaScript frontend
        user_data = request.json
        
        # Extract the 3 features in the exact order the model expects
        input_data = [
            user_data.get('purchaseCount'),
            user_data.get('genreMatch'),
            user_data.get('engagementScore'),
        ]
        
        # CRITICAL: Convert inputs to float, raising an error if data is missing or invalid
        input_data_converted = []
        for x in input_data:
            if x is None:
                raise ValueError("Missing input data received from frontend.")
            input_data_converted.append(float(x))

        # Convert to numpy array and reshape for the model (size 1x3)
        input_array = np.array(input_data_converted).reshape(1, -1)
        
        # Make the prediction
        prediction = model.predict(input_array)[0]
        
        # Get probability to give a "confidence" score (XAI - Explainable AI)
        probabilities = model.predict_proba(input_array)
        confidence = round(np.max(probabilities) * 100, 2)
        
        # Determine LTV (Lifetime Value) prediction based on the status
        if prediction == 1:
            status = "HIGH VALUE"
            ltv_prediction = "$500+ (Eligible for NFT Reward)"
        else:
            status = "LOW VALUE"
            ltv_prediction = "$50 (Requires Engagement Push)"

        return jsonify({
            "status": status,
            "prediction_value": int(prediction),
            "ltv_prediction": ltv_prediction,
            "confidence": f"{confidence}%"
        })

    except Exception as e:
        # Log the error in the server console for debugging
        print(f"Error during prediction: {e}")
        # Return a 400 error response so the JavaScript can display a clean error message
        return jsonify({"error": str(e), "message": "Invalid input data or server prediction error."}), 400

# --- 4. RUN THE SERVER ---
if __name__ == '__main__':
    # Setting use_reloader=False prevents certain double-start issues in some environments
    app.run(debug=True, port=5000, use_reloader=False)
