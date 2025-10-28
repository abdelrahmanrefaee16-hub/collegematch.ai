"""
Flask Web Application for Academic Future Predictor
This app serves an existing ML model and front-end interface to predict student academic outcomes.

The model predicts one of three outcomes:
- 0 = "Drop Out" (student will not complete the program)
- 1 = "Remain Enrolled" (student continues but hasn't graduated yet)
- 2 = "Graduate" (student will successfully complete the program)
"""
import os
print("Current working directory:", os.getcwd())
print("Files in current folder:", os.listdir())
print("Files in models folder:", os.listdir("dropout_model_improved.pkl"))

# Import required libraries
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pickle
import numpy as np
import os

# Create Flask app with static folder configuration
# The static_folder points to where our HTML, CSS, and JS files are located
# The static_url_path="" makes files accessible at root URL (e.g., /index.html instead of /static/index.html)
app = Flask(__name__, static_folder="static", static_url_path="")

# Enable CORS (Cross-Origin Resource Sharing) so JavaScript can call our API
# This is important for the front-end to communicate with the back-end
CORS(app)

# ============================================================================
# LOAD THE TRAINED MODEL
# ============================================================================
# The model is loaded when the server starts (not on every request)
# This makes predictions faster since we only load the model once

model = None
MODEL_PATH = "models/dropout_model_improved.pkl"

try:
    # Try to load the model using pickle
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    print(f"✓ Model loaded successfully from {MODEL_PATH}")
except FileNotFoundError:
    print(f"✗ ERROR: Model file not found at {MODEL_PATH}")
    print("  Make sure the model file exists in the models/ folder")
except Exception as e:
    print(f"✗ ERROR loading model: {e}")

# ============================================================================
# ROUTES FOR SERVING HTML AND STATIC FILES
# ============================================================================

@app.route("/")
def home():
    """
    Serve the home page (index.html)
    When users visit http://localhost:5000/, they'll see index.html
    """
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def static_files(path):
    """
    Serve all other static files (HTML, CSS, JS, images)
    Examples:
    - /signup.html
    - /css/style.css
    - /js/script.js
    """
    return send_from_directory(app.static_folder, path)

# ============================================================================
# PREDICTION API ENDPOINT
# ============================================================================

@app.route("/predict", methods=["POST"])
def predict():
    """
    Main prediction endpoint - accepts JSON data and returns prediction
    
    EXPECTED INPUT FORMAT (JSON):
    {
      "gender": 1,                      # Male=1, Female=0
      "nationality_group": 0,           # 0-4 (Portuguese=0, European=1, etc.)
      "parent_occupation_group": 2,     # 0-9 (occupation category)
      "marital_status": 0,              # Single=0, Married=1, etc.
      "student_type": 0,                # National=0, International=1
      "previous_qualification_group": 1, # 0-4 (education level)
      "age_at_enrollment": 19,          # 17-60
      "tuition_up_to_date": 1,          # Yes=1, No=0
      "displaced": 0,                   # Yes=1, No=0
      "special_needs": 0,               # Yes=1, No=0
      "first_semester_grade": 13.5,     # 0-20
      "second_semester_grade": 14.0,    # 0-20
      "second_semester_approved": 7,    # 0-10 (number of units passed)
      "first_semester_approved": 6,     # 0-10 (number of units passed)
      "admission_grade": 15.0           # 0-20
    }
    
    RESPONSE FORMAT (JSON):
    {
      "outcome": "Graduate",
      "prediction": 2,
      "confidence": 0.85
    }
    """
    
    # Check if model is loaded
    if model is None:
        return jsonify({
            "error": "Model not loaded. Please check server logs.",
            "success": False
        }), 500
    
    try:
        # Get JSON data from the request
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No data provided. Please send JSON data in the request body.",
                "success": False
            }), 400
        
        # ====================================================================
        # EXTRACT AND VALIDATE INPUT FEATURES
        # ====================================================================
        # The model expects exactly 15 features in this specific order:
        required_features = [
            "gender",                      # 1
            "nationality_group",           # 2
            "parent_occupation_group",     # 3
            "marital_status",              # 4
            "student_type",                # 5
            "previous_qualification_group", # 6
            "age_at_enrollment",           # 7
            "tuition_up_to_date",          # 8
            "displaced",                   # 9
            "special_needs",               # 10
            "first_semester_grade",        # 11
            "second_semester_grade",       # 12
            "second_semester_approved",    # 13
            "first_semester_approved",     # 14
            "admission_grade"              # 15
        ]
        
        # Check if all required features are present
        missing_features = [f for f in required_features if f not in data]
        if missing_features:
            return jsonify({
                "error": f"Missing required features: {', '.join(missing_features)}",
                "success": False
            }), 400
        
        # Extract features in the correct order
        features = []
        for feature_name in required_features:
            value = data[feature_name]
            
            # Validate that the value is a number
            if not isinstance(value, (int, float)):
                return jsonify({
                    "error": f"Feature '{feature_name}' must be a number. Got: {type(value).__name__}",
                    "success": False
                }), 400
            
            features.append(float(value))
        
        # Convert to numpy array with shape (1, 15) - one sample with 15 features
        features_array = np.array([features])
        
        # ====================================================================
        # MAKE PREDICTION
        # ====================================================================
        
        # Get the predicted class (0, 1, or 2)
        prediction = int(model.predict(features_array)[0])
        
        # Get prediction probabilities for all classes
        # This gives us confidence scores for each outcome
        if hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(features_array)[0]
            # The confidence is the probability of the predicted class
            confidence = float(probabilities[prediction])
        else:
            # If the model doesn't support probabilities, use a default value
            confidence = 1.0
        
        # ====================================================================
        # MAP PREDICTION TO TEXT LABEL
        # ====================================================================
        outcome_map = {
            0: "Drop Out",
            1: "Remain Enrolled",
            2: "Graduate"
        }
        
        outcome = outcome_map.get(prediction, "Unknown")
        
        # ====================================================================
        # RETURN RESPONSE
        # ====================================================================
        response = {
            "success": True,
            "outcome": outcome,
            "prediction": prediction,
            "confidence": round(confidence, 4)
        }
        
        print(f"✓ Prediction made: {outcome} (confidence: {confidence:.2%})")
        
        return jsonify(response), 200
    
    except KeyError as e:
        # This happens if a required field is missing from the JSON
        return jsonify({
            "error": f"Missing field in request: {str(e)}",
            "success": False
        }), 400
    
    except ValueError as e:
        # This happens if data types are wrong (e.g., text instead of number)
        return jsonify({
            "error": f"Invalid data format: {str(e)}",
            "success": False
        }), 400
    
    except Exception as e:
        # Catch any other unexpected errors
        print(f"✗ Prediction error: {e}")
        return jsonify({
            "error": f"An error occurred during prediction: {str(e)}",
            "success": False
        }), 500

# ============================================================================
# HEALTH CHECK ENDPOINT (OPTIONAL BUT USEFUL)
# ============================================================================

@app.route("/health", methods=["GET"])
def health_check():
    """
    Simple endpoint to check if the server is running
    Visit http://localhost:5000/health to test
    """
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None
    }), 200

# ============================================================================
# RUN THE APPLICATION
# ============================================================================

if __name__ == "__main__":
    """
    Start the Flask development server
    
    To run this app:
    1. Open terminal/command prompt
    2. Navigate to the folder containing app.py
    3. Run: python app.py
    4. Open browser to: http://localhost:5000
    
    Options:
    - debug=True: Enables auto-reload when code changes (helpful for development)
    - host='0.0.0.0': Makes server accessible from other devices on the network
    - port=5000: The port number (you can change this if needed)
    """
    
    # Print startup information
    print("\n" + "="*70)
    print("🎓 ACADEMIC FUTURE PREDICTOR - Server Starting")
    print("="*70)
    print(f"📁 Model path: {MODEL_PATH}")
    print(f"✓ Model status: {'Loaded' if model else 'NOT LOADED - Check file path!'}")
    print(f"🌐 Server URL: http://localhost:5000")
    print(f"🔍 Health check: http://localhost:5000/health")
    print(f"🎯 Prediction API: http://localhost:5000/predict (POST)")
    print("="*70 + "\n")
    
    # Start the server
    app.run(debug=True, host='0.0.0.0', port=5000)