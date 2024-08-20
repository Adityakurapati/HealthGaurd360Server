import os
import json
import logging
import firebase_admin
from firebase_admin import credentials, db
from flask import Flask, jsonify, request
from flask_cors import CORS

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Starting application...")

# Load Firebase credentials from environment variable
firebase_creds_json = os.environ.get('FIREBASE_CREDENTIALS')
if firebase_creds_json:
    cred = credentials.Certificate(json.loads(firebase_creds_json))
    logger.debug("Firebase credentials loaded successfully")
else:
    logger.error("FIREBASE_CREDENTIALS environment variable not set")
    raise ValueError("FIREBASE_CREDENTIALS environment variable not set")

firebase_admin.initialize_app(cred, {
    "databaseURL": "https://healthgaurd360-426SSf4-default-rtdb.asia-southeast1.firebasedatabase.app/"
})
logger.info("Firebase app initialized")

# Flask app setup
app = Flask(__name__)
CORS(app)  # This enables CORS for all routes
logger.info("Flask app created with CORS enabled")

# Reference the root of the database
ref = db.reference('/')
logger.debug("Database reference created")

# Helper function to add no-cache headers
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/')
def message():
    logger.debug("Root route accessed")
    return jsonify({"message": "Hello from Flask!"})

@app.route('/api/nearby_hospitals', methods=['GET'])
def get_nearby_hospitals():
    logger.debug("/api/nearby_hospitals endpoint triggered")
    try:
        lat = float(request.args.get('lat'))
        lng = float(request.args.get('lng'))
        
        hospitals_ref = ref.child('hospitals')
        hospitals = hospitals_ref.order_by_child('lat').start_at(lat - 0.05).end_at(lat + 0.05).get()
        
        if hospitals:
            logger.info(f"Found {len(hospitals)} nearby hospitals")
            return add_no_cache_headers(jsonify(list(hospitals.values())))
        else:
            logger.info("No nearby hospitals found")
            return add_no_cache_headers(jsonify([]))
    except Exception as e:
        logger.error(f"Error in get_nearby_hospitals: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ... (other routes with similar logging)

@app.route('/api/sensor_data', methods=['GET'])
def store_sensor_data():
    logger.debug("/api/sensor_data endpoint triggered")
    try:
        heartrate = request.args.get('heartrate')
        blood_oxygen = request.args.get('blood_oxygen')

        logger.info(f"Received sensor data - Heartrate: {heartrate}, Blood Oxygen: {blood_oxygen}")

        sensor_data = {
            'heartrate': heartrate,
            'blood_oxygen': blood_oxygen
        }

        ref.child('sensor_data').set(sensor_data)
        logger.debug("Sensor data stored in Firebase")

        return jsonify({"success": True, "sensor_data": sensor_data}), 200
    except Exception as e:
        logger.error(f"Error in store_sensor_data: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port)