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

# Data is structured so high scores across the board predict HIGH VALUE (1).
# We include edge cases (e.g., high engagement but low purchases) to make the model
# consider all three features, rather than just one.
data = {
    'Purchase_Count':   [1, 5, 2, 8, 3, 10, 1, 6, 2, 9, 4, 7, 5, 1, 9, 3, 10, 1],
    'Genre_Match':      [0.2, 0.9, 0.4, 0.95, 0.6, 0.85, 0.1, 0.75, 0.3, 0.9, 0.5, 0.8, 0.35, 0.98, 0.7, 0.15, 0.9, 0.95],
    'Engagement_Score': [3, 9, 4, 10, 6, 9, 2, 7, 5, 10, 8, 8, 9, 2, 5, 10, 1, 1],
    # Statuses: High scores = 1 (High Value); Low scores = 0 (Low Value)
    'Loyalty_Status': [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 0] 
}

df = pd.DataFrame(data)

# Separate features (X) and target (y). Time_Since_Last is removed.
X = df[['Purchase_Count', 'Genre_Match', 'Engagement_Score']]
y = df['Loyalty_Status']

# Train the Decision Tree Classifier (The AI Model)
model = DecisionTreeClassifier(random_state=42)
model.fit(X, y)

print("AI Loyalty Model Trained Successfully with 3 Core Features (Purchase, Genre Match, Engagement). Ready for prediction.")

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
            # NOTE: timeSinceLast is deliberately NOT extracted here
        ]
        
        # CRITICAL FIX: Ensure all inputs are valid numbers and convert them
        # We only expect the first 3 elements (Purchase, Genre, Engagement).
        input_data_converted = []
        
        # We only iterate over the first three expected inputs
        for i in range(3):
            x = input_data[i] 
            if x is None:
                raise ValueError(f"Missing or invalid data received for feature index {i}.")
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
