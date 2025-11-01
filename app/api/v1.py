from flask import Blueprint, jsonify, request, current_app
from app.models.person import Person, Detection
from app.services.search import FaceSearchService
from app.utils.helpers import save_uploaded_file
import os

api_bp = Blueprint('api', __name__)

@api_bp.route('/persons', methods=['GET'])
def get_persons():
    """API: Get all registered persons"""
    persons = Person.get_all()
    # Convert ObjectId to string
    for person in persons:
        person['_id'] = str(person['_id'])
    return jsonify(persons)

@api_bp.route('/persons/<person_id>', methods=['GET'])
def get_person(person_id):
    """API: Get specific person"""
    person = Person.get_by_id(person_id)
    if person:
        person['_id'] = str(person['_id'])
        return jsonify(person)
    return jsonify({'error': 'Person not found'}), 404

@api_bp.route('/detections', methods=['GET'])
def get_detections():
    """API: Get recent detections"""
    limit = request.args.get('limit', 50, type=int)
    detections = Detection.get_recent(limit=limit)
    
    for detection in detections:
        detection['_id'] = str(detection['_id'])
        person = Person.get_by_id(detection['person_id'])
        detection['person_name'] = person['name'] if person else 'Unknown'
    
    return jsonify(detections)

@api_bp.route('/detections/person/<person_id>', methods=['GET'])
def get_person_detections(person_id):
    """API: Get detections for specific person"""
    detections = Detection.get_by_person(person_id)
    
    for detection in detections:
        detection['_id'] = str(detection['_id'])
    
    return jsonify(detections)

@api_bp.route('/verify_face', methods=['POST'])
def verify_face():
    """API: Verify if uploaded image contains a face"""
    if 'photo' not in request.files:
        return jsonify({'error': 'No photo provided'}), 400
    
    photo = request.files['photo']
    filename, filepath = save_uploaded_file(photo, current_app.config['UPLOAD_FOLDER'])
    
    if not filename:
        return jsonify({'error': 'Invalid file type'}), 400
    
    service = FaceSearchService()
    has_face = service.verify_face_in_image(filepath)
    
    # Clean up
    os.remove(filepath)
    
    return jsonify({'has_face': has_face})

@api_bp.route('/health', methods=['GET'])
def health_check():
    """API: Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Missing Person Detection API',
        'version': '1.0.0'
    })
