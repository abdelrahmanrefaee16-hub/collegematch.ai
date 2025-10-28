"""
Flask Web Application for Academic Future Predictor
This app serves an existing ML model and front-end interface to predict student academic outcomes.

The model predicts one of three outcomes:
- 0 = "Drop Out" (student will not complete the program)
- 1 = "Remain Enrolled" (student continues but hasn't graduated yet)
- 2 = "Graduate" (student will successfully complete the program)
"""
# Import required libraries
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pickle
import numpy as np
import os

# Create Flask app with static folder configuration
app = Flask(__name__, static_folder="static", static_url_path="")

# Enable CORS
CORS(app)

# ============================================================================
# LOAD THE TRAINED MODEL
# ============================================================================
# The model is loaded when the server starts (not on every request)
# This makes predictions faster since we only load the model once

model = None

# ✅ FIXED: Use the full absolute path to your model
MODEL_PATH = r"C:\Users\Azka\OneDrive\Documents\GitHub\collegematch.ai\models\dropout_model_improved.pkl"

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
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(app.static_folder, path)

# ============================================================================
# PREDICTION API ENDPOINT
# ============================================================================

@app.route("/predict", methods=["POST"])
def predict():
    if model is None:
        return jsonify({
            "error": "Model not loaded. Please check server logs.",
            "success": False
        }), 500
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "error": "No data provided. Please send JSON data in the request body.",
                "success": False
            }), 400

        required_features = [
            "gender",
            "nationality_group",
            "parent_occupation_group",
            "marital_status",
            "student_type",
            "previous_qualification_group",
            "age_at_enrollment",
            "tuition_up_to_date",
            "displaced",
            "special_needs",
            "first_semester_grade",
            "second_semester_grade",
            "second_semester_approved",
            "first_semester_approved",
            "admission_grade"
        ]
        
        missing_features = [f for f in required_features if f not in data]
        if missing_features:
            return jsonify({
                "error": f"Missing required features: {', '.join(missing_features)}",
                "success": False
            }), 400
        
        features = []
        for feature_name in required_features:
            value = data[feature_name]
            if not isinstance(value, (int, float)):
                return jsonify({
                    "error": f"Feature '{feature_name}' must be a number. Got: {type(value).__name__}",
                    "success": False
                }), 400
            features.append(float(value))
        
        features_array = np.array([features])
        
        prediction = int(model.predict(features_array)[0])
        
        if hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(features_array)[0]
            confidence = float(probabilities[prediction])
        else:
            confidence = 1.0
        
        outcome_map = {
            0: "Drop Out",
            1: "Remain Enrolled",
            2: "Graduate"
        }
        outcome = outcome_map.get(prediction, "Unknown")
        
        response = {
            "success": True,
            "outcome": outcome,
            "prediction": prediction,
            "confidence": round(confidence, 4)
        }
        
        print(f"✓ Prediction made: {outcome} (confidence: {confidence:.2%})")
        return jsonify(response), 200
    
    except Exception as e:
        print(f"✗ Prediction error: {e}")
        return jsonify({
            "error": f"An error occurred during prediction: {str(e)}",
            "success": False
        }), 500

# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None
    }), 200

# ============================================================================
# RUN THE APPLICATION
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🎓 ACADEMIC FUTURE PREDICTOR - Server Starting")
    print("="*70)
    print(f"📁 Model path: {MODEL_PATH}")
    print(model)
    print(f"✓ Model status: {'Loaded' if model else 'NOT LOADED - Check file path!'}")
    print(f"🌐 Server URL: http://localhost:5000")
    print(f"🔍 Health check: http://localhost:5000/health")
    print(f"🎯 Prediction API: http://localhost:5000/predict (POST)")
    print("="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
