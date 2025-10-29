"""
Flask Web Application for Academic Future Predictor
This app serves an existing ML model and front-end interface to predict student academic outcomes.

The model predicts one of three outcomes:
- 0 = "Drop Out" (student will not complete the program)
- 1 = "Remain Enrolled" (student continues but hasn't graduated yet)
- 2 = "Graduate" (student will successfully complete the program)
"""
# Import required libraries
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import numpy as np
import os
import sys

# Import joblib (required)
try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False
    print("❌ ERROR: joblib not installed!")
    print("   Install it with: pip install joblib")
    import sys
    sys.exit(1)

# Create Flask app - no static folder since HTML files are in root
app = Flask(__name__)

# Enable CORS
CORS(app)

# ============================================================================
# LOAD THE TRAINED MODEL
# ============================================================================

model = None

# Use relative path based on the app.py location
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
MODEL_PATH_PKL = os.path.join(MODEL_DIR, "dropout_model_improved.pkl")
MODEL_PATH_JOBLIB = os.path.join(MODEL_DIR, "dropout_model_improved.joblib")

# Get the base directory where HTML files are located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Check common locations for HTML files
POSSIBLE_HTML_DIRS = [
    os.path.join(BASE_DIR, "static"),  # static folder (MOST COMMON)
    BASE_DIR,  # Same directory as app.py
    os.path.join(BASE_DIR, "templates"),  # templates folder
    os.path.join(BASE_DIR, "frontend"),  # frontend folder
    os.path.join(BASE_DIR, "html"),  # html folder
]

# Find where index.html actually is
HTML_DIR = None
for directory in POSSIBLE_HTML_DIRS:
    if os.path.exists(os.path.join(directory, "index.html")):
        HTML_DIR = directory
        break

# Debug: Print the paths being used
print(f"🔍 Looking for model at:")
print(f"   PKL:    {MODEL_PATH_PKL} (exists: {os.path.exists(MODEL_PATH_PKL)})")
print(f"   JOBLIB: {MODEL_PATH_JOBLIB} (exists: {os.path.exists(MODEL_PATH_JOBLIB)})")
print(f"🐍 Python version: {sys.version}")
print(f"📁 Base directory: {BASE_DIR}")
print(f"📁 Static folder: {os.path.join(BASE_DIR, 'static')}")
print(f"📁 HTML directory: {HTML_DIR if HTML_DIR else 'NOT FOUND'}")

if HTML_DIR:
    print(f"✓ Found index.html at: {os.path.join(HTML_DIR, 'index.html')}")
else:
    print(f"✗ Could not find index.html in any of these locations:")
    for d in POSSIBLE_HTML_DIRS:
        print(f"   - {d}")

def load_model_with_compatibility():
    """
    Attempt to load the model with various compatibility options.
    Tries joblib first (most robust), then pickle with multiple methods.
    """
    global model
    
    # METHOD 1: Try joblib first (most reliable for ML models)
    if JOBLIB_AVAILABLE and os.path.exists(MODEL_PATH_JOBLIB):
        try:
            model = joblib.load(MODEL_PATH_JOBLIB)
            print(f"✓ Model loaded successfully using joblib (.joblib file)")
            print(f"  Model expects {model.n_features_in_} features")
            return True
        except Exception as e:
            print(f"  Joblib method failed: {e}")
    
    # METHOD 2: Try pickle with encoding='latin1' (Python 2 to 3 compatibility)
    if os.path.exists(MODEL_PATH_PKL):
        import pickle
        try:
            with open(MODEL_PATH_PKL, "rb") as f:
                model = pickle.load(f, encoding='latin1')
            print(f"✓ Model loaded successfully using pickle with encoding='latin1'")
            return True
        except Exception as e:
            print(f"  Pickle method 1 (latin1) failed: {e}")
    
        # METHOD 3: Try pickle with encoding='bytes'
        try:
            with open(MODEL_PATH_PKL, "rb") as f:
                model = pickle.load(f, encoding='bytes')
            print(f"✓ Model loaded successfully using pickle with encoding='bytes'")
            return True
        except Exception as e:
            print(f"  Pickle method 2 (bytes) failed: {e}")
        
        # METHOD 4: Try standard pickle load
        try:
            with open(MODEL_PATH_PKL, "rb") as f:
                model = pickle.load(f)
            print(f"✓ Model loaded successfully with standard pickle")
            return True
        except Exception as e:
            print(f"  Pickle method 3 (standard) failed: {e}")
        
        # METHOD 5: Try with fix_imports=True
        try:
            with open(MODEL_PATH_PKL, "rb") as f:
                model = pickle.load(f, fix_imports=True, encoding='ASCII')
            print(f"✓ Model loaded successfully with fix_imports=True")
            return True
        except Exception as e:
            print(f"  Pickle method 4 (fix_imports) failed: {e}")
    
    return False

# Try to load the model
try:
    if not os.path.exists(MODEL_PATH_PKL) and not os.path.exists(MODEL_PATH_JOBLIB):
        print(f"✗ ERROR: No model file found in {MODEL_DIR}")
        print(f"  Please ensure model file exists (.pkl or .joblib)")
    else:
        success = load_model_with_compatibility()
        if not success:
            print(f"\n⚠️  SOLUTION: The model file is incompatible with your Python version.")
            print(f"\n   FIX OPTIONS:")
            print(f"   1. RECOMMENDED: Re-save the model using joblib:")
            print(f"      >>> import joblib")
            print(f"      >>> joblib.dump(model, 'models/dropout_model_improved.joblib')")
            print(f"   ")
            print(f"   2. Or retrain the model with your current Python version")
            print(f"   ")
            print(f"   3. Or use the exact Python version that created the .pkl file")
except Exception as e:
    print(f"✗ ERROR loading model: {e}")

# ============================================================================
# ROUTES FOR SERVING HTML AND STATIC FILES
# ============================================================================

@app.route("/")
def home():
    """Serve the main index.html page"""
    if HTML_DIR is None:
        return """
        <h1>❌ HTML Files Not Found</h1>
        <p>Could not locate index.html. Please check the server console for details.</p>
        <p>Make sure your HTML files are in one of these locations:</p>
        <ul>
            <li>Same directory as app.py</li>
            <li>static/ folder</li>
            <li>templates/ folder</li>
            <li>frontend/ folder</li>
            <li>html/ folder</li>
        </ul>
        """, 404
    try:
        response = send_file(os.path.join(HTML_DIR, "index.html"))
        # Disable caching for development
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        return f"Error loading index.html: {e}. HTML directory: {HTML_DIR}", 404

@app.route("/signup.html")
def signup():
    """Serve the signup page"""
    if HTML_DIR is None:
        return "HTML files not found. Check server console.", 404
    try:
        response = send_file(os.path.join(HTML_DIR, "signup.html"))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        return f"Error loading signup.html: {e}", 404

@app.route("/questionnaire.html")
def questionnaire():
    """Serve the questionnaire page"""
    if HTML_DIR is None:
        return "HTML files not found. Check server console.", 404
    try:
        response = send_file(os.path.join(HTML_DIR, "questionnaire.html"))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        return f"Error loading questionnaire.html: {e}", 404

@app.route("/results.html")
def results():
    """Serve the results page"""
    if HTML_DIR is None:
        return "HTML files not found. Check server console.", 404
    try:
        response = send_file(os.path.join(HTML_DIR, "results.html"))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        return f"Error loading results.html: {e}", 404

@app.route("/recommendations.html")
def recommendations():
    """Serve the recommendations page"""
    if HTML_DIR is None:
        return "HTML files not found. Check server console.", 404
    try:
        response = send_file(os.path.join(HTML_DIR, "recommendations.html"))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        return f"Error loading recommendations.html: {e}", 404

@app.route("/css/<path:path>")
def serve_css(path):
    """Serve CSS files from css folder"""
    if HTML_DIR is None:
        return "HTML files not found. Check server console.", 404
    try:
        css_dir = os.path.join(HTML_DIR, "css")
        response = send_from_directory(css_dir, path)
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        return f"CSS file not found: {path}", 404

@app.route("/js/<path:path>")
def serve_js(path):
    """Serve JavaScript files from js folder"""
    if HTML_DIR is None:
        return "HTML files not found. Check server console.", 404
    try:
        js_dir = os.path.join(HTML_DIR, "js")
        return send_from_directory(js_dir, path)
    except Exception as e:
        return f"JavaScript file not found: {path}", 404

@app.route("/images/<path:path>")
def serve_images(path):
    """Serve images from images folder"""
    if HTML_DIR is None:
        return "HTML files not found. Check server console.", 404
    try:
        images_dir = os.path.join(HTML_DIR, "images")
        return send_from_directory(images_dir, path)
    except Exception as e:
        return f"Image file not found: {path}", 404

# ============================================================================
# PREDICTION API ENDPOINT
# ============================================================================

@app.route("/predict", methods=["POST"])
def predict():
    """
    Main prediction endpoint. Expects JSON data with student features.
    Returns prediction outcome and confidence level.
    """
    if model is None:
        return jsonify({
            "error": "Model not loaded. The model file may be incompatible with your Python version. Check server logs for details.",
            "success": False
        }), 500
   
    try:
        # Get JSON data from request
        data = request.get_json()
        if not data:
            return jsonify({
                "error": "No data provided. Please send JSON data in the request body.",
                "success": False
            }), 400

        # Define required features (must match model training order)
        # These map to the actual dataset column names used in training
        required_features = [
            "gender",                      # -> Gender
            "nationality_group",           # -> Nacionality
            "parent_occupation_group",     # -> Mother's occupation
            "marital_status",              # -> Marital status
            "student_type",                # -> International
            "previous_qualification_group", # -> Previous qualification
            "age_at_enrollment",           # -> Age at enrollment
            "tuition_up_to_date",          # -> Tuition fees up to date
            "displaced",                   # -> Displaced
            "special_needs",               # -> Educational special needs
            "first_semester_grade",        # -> Curricular units 1st sem (grade)
            "second_semester_grade",       # -> Curricular units 2nd sem (grade)
            "second_semester_approved",    # -> Curricular units 2nd sem (approved)
            "first_semester_approved",     # -> Curricular units 1st sem (approved)
            "admission_grade"              # -> Admission grade
        ]
       
        # Check for missing features
        missing_features = [f for f in required_features if f not in data]
        if missing_features:
            return jsonify({
                "error": f"Missing required features: {', '.join(missing_features)}",
                "success": False
            }), 400
       
        # Extract and validate features
        features = []
        for feature_name in required_features:
            value = data[feature_name]
            if not isinstance(value, (int, float)):
                return jsonify({
                    "error": f"Feature '{feature_name}' must be a number. Got: {type(value).__name__}",
                    "success": False
                }), 400
            features.append(float(value))
       
        # Convert to numpy array
        features_array = np.array([features])
       
        # Make prediction
        prediction_result = model.predict(features_array)[0]
        
        # Handle both numeric and string predictions
        if isinstance(prediction_result, str):
            # If model returns string, map it to numeric
            string_to_numeric = {
                "Dropout": 0,
                "Drop Out": 0,
                "Enrolled": 1,
                "Remain Enrolled": 1,
                "Graduate": 2
            }
            prediction = string_to_numeric.get(prediction_result, 0)
        else:
            # If model returns numeric, use it directly
            prediction = int(prediction_result)
       
        # Get confidence score if available
        if hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(features_array)[0]
            confidence = float(probabilities[prediction])
        else:
            confidence = 1.0
       
        # Map prediction to outcome
        outcome_map = {
            0: "Drop Out",
            1: "Remain Enrolled",
            2: "Graduate"
        }
        outcome = outcome_map.get(prediction, "Unknown")
       
        # Prepare response
        response = {
            "success": True,
            "outcome": outcome,
            "prediction": prediction,
            "confidence": round(confidence, 4)
        }
       
        print(f"✓ Prediction made: {outcome} (confidence: {confidence:.2%})")
        return jsonify(response), 200
   
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"✗ Prediction error: {e}")
        print(f"Full error:\n{error_details}")
        return jsonify({
            "error": f"An error occurred during prediction: {str(e)}",
            "success": False
        }), 500

# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@app.route("/health", methods=["GET"])
def health_check():
    """Simple health check to verify server and model status"""
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None,
        "model_features": model.n_features_in_ if model else None,
        "joblib_available": JOBLIB_AVAILABLE,
        "python_version": sys.version
    }), 200

# ============================================================================
# RUN THE APPLICATION
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🎓 ACADEMIC FUTURE PREDICTOR - Server Starting")
    print("="*70)
    print(f"📁 Model directory: {MODEL_DIR}")
    print(f"📁 HTML files directory: {HTML_DIR if HTML_DIR else 'NOT FOUND ✗'}")
    if HTML_DIR:
        print(f"✓ HTML files found at: {HTML_DIR}")
    else:
        print(f"✗ HTML files NOT FOUND!")
        print(f"   Please place your HTML files in one of these locations:")
        for d in POSSIBLE_HTML_DIRS:
            print(f"   - {d}")
    print(f"✓ Model status: {'Loaded ✓' if model else 'NOT LOADED ✗'}")
    if model:
        print(f"✓ Model features: {model.n_features_in_}")
    print(f"✓ Joblib available: {'Yes ✓' if JOBLIB_AVAILABLE else 'No ✗'}")
    if not model:
        print(f"\n⚠️  The model couldn't be loaded. Solutions:")
        print(f"   1. Install joblib: pip install joblib")
        print(f"   2. Re-save model as .joblib format (see logs above)")
        print(f"   3. Or retrain the model with your current Python version\n")
    print(f"🌐 Server URL: http://localhost:5000")
    print(f"🔍 Health check: http://localhost:5000/health")
    print(f"🎯 Prediction API: http://localhost:5000/predict (POST)")
    print("="*70 + "\n")
   
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)