from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Global instances
mongo_client = None
db = None

def create_app(config_name='development'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    app.config['DATABASE_NAME'] = os.getenv('DATABASE_NAME', 'missing_persons_db')
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))
    app.config['DETECTION_COOLDOWN'] = int(os.getenv('DETECTION_COOLDOWN', 10))
    
    # Face Recognition Configuration (NEW)
    app.config['DEEPFACE_MODEL'] = os.getenv('DEEPFACE_MODEL', 'VGG-Face')
    app.config['DETECTOR_BACKEND'] = os.getenv('DETECTOR_BACKEND', 'opencv')
    app.config['RECOGNITION_THRESHOLD'] = float(os.getenv('RECOGNITION_THRESHOLD', '0.50'))
    app.config['DISTANCE_METRIC'] = os.getenv('DISTANCE_METRIC', 'cosine')
    
    # Camera Configuration (NEW)
    app.config['CAMERA_INDEX'] = int(os.getenv('CAMERA_INDEX', '0'))
    app.config['MIRROR_CAMERA'] = os.getenv('MIRROR_CAMERA', 'true').lower() == 'true'
    app.config['SKIP_DETECTION_FRAMES'] = int(os.getenv('SKIP_DETECTION_FRAMES', '5'))
    
    # Enable CORS
    CORS(app)
    
    # Initialize MongoDB
    global mongo_client, db
    try:
        mongo_client = MongoClient(app.config['MONGO_URI'])
        db = mongo_client[app.config['DATABASE_NAME']]
        
        # Test database connection
        mongo_client.server_info()
        print("✓ MongoDB connected successfully!")
        
        # Create indexes for better performance
        db['victims'].create_index('name')
        db['detections'].create_index([('person_id', 1), ('timestamp', -1)])
        
    except Exception as e:
        print(f"✗ MongoDB connection failed: {e}")
        db = None
    
    # Create upload folder
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Print configuration for debugging
    print("\n" + "="*50)
    print("Face Recognition Configuration:")
    print(f"  Model: {app.config['DEEPFACE_MODEL']}")
    print(f"  Detector: {app.config['DETECTOR_BACKEND']}")
    print(f"  Threshold: {app.config['RECOGNITION_THRESHOLD']}")
    print(f"  Distance Metric: {app.config['DISTANCE_METRIC']}")
    print(f"  Camera Index: {app.config['CAMERA_INDEX']}")
    print(f"  Mirror Camera: {app.config['MIRROR_CAMERA']}")
    print("="*50 + "\n")
    
    # Register blueprints
    from app.routes import main_bp
    from app.api.v1 import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    return app
