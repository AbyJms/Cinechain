import pandas as pd
from flask import Flask, request, jsonify
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from flask_cors import CORS # Required for cross-origin requests from the HTML file
import numpy as np

# --- 1. SETUP THE FLASK APPLICATION ---
app = Flask(__name__)
CORS(app) # Enable CORS for frontend communication

# --- 2. MOCK DATASET FOR TRAINING THE AI MODEL ---
# Features: [Purchase Count (Tickets/VOD), Genre Match (0.0-1.0), Social Engagement Score (0-10)]
# Target: [Loyalty Status (0=Low Value, 1=High Value)]
# This mock data is crucial for the hackathon demo.

data = {
    'Purchase_Count': [1, 5, 2, 8, 3, 10, 1, 6, 2, 9, 4, 7],
    'Genre_Match':    [0.2, 0.9, 0.4, 0.95, 0.6, 0.85, 0.1, 0.75, 0.3, 0.9, 0.5, 0.8],
    'Engagement_Score': [3, 9, 4, 10, 6, 9, 2, 7, 5, 10, 8, 8],
    'Loyalty_Status': [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1]
}

df = pd.DataFrame(data)

# Separate features (X) and target (y)
X = df[['Purchase_Count', 'Genre_Match', 'Engagement_Score']]
y = df['Loyalty_Status']

# Train the Decision Tree Classifier (The AI Model)
model = DecisionTreeClassifier(random_state=42)
model.fit(X, y)

print("AI Loyalty Model Trained Successfully. Ready for prediction.")

# --- 3. API ENDPOINT FOR PREDICTION ---

@app.route('/predict_loyalty', methods=['POST'])
def predict_loyalty():
    """
    Receives user data from the frontend and returns a loyalty prediction.
    """
    try:
        # Get JSON data sent from the JavaScript frontend
        user_data = request.json
        
        # Extract features in the order the model expects
        input_data = [
            user_data.get('purchaseCount'),
            user_data.get('genreMatch'),
            user_data.get('engagementScore')
        ]

        # Convert to numpy array and reshape for the model
        input_array = np.array(input_data).reshape(1, -1)
        
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
        print(f"Error during prediction: {e}")
        return jsonify({"error": str(e), "message": "Invalid input data."}), 400

# --- 4. RUN THE SERVER ---
if __name__ == '__main__':
    # Run on port 5000, accessible by the frontend
    app.run(debug=True, port=5000)
