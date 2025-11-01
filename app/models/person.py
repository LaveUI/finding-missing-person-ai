from datetime import datetime
from bson.objectid import ObjectId

class Person:
    """Model for missing persons"""
    
    @staticmethod
    def get_collection():
        """Get the victims collection"""
        from app import db
        return db['victims'] if db is not None else None
    
    @staticmethod
    def create(name, age, contact, photo_path, description=None):
        """Create a new missing person record"""
        collection = Person.get_collection()
        person_data = {
            'name': name,
            'age': age,
            'contact': contact,
            'photo_path': photo_path,
            'description': description,
            'registered_date': datetime.now(),
            'status': 'missing',
            'last_seen_location': None,
            'last_seen_time': None
        }
        result = collection.insert_one(person_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_all():
        """Get all missing persons"""
        collection = Person.get_collection()
        return list(collection.find())
    
    @staticmethod
    def get_by_id(person_id):
        """Get person by ID"""
        try:
            collection = Person.get_collection()
            return collection.find_one({'_id': ObjectId(person_id)})
        except:
            return None
    
    @staticmethod
    def update_last_seen(person_id, location, timestamp):
        """Update last seen information"""
        collection = Person.get_collection()
        collection.update_one(
            {'_id': ObjectId(person_id)},
            {
                '$set': {
                    'last_seen_location': location,
                    'last_seen_time': timestamp
                }
            }
        )
    
    @staticmethod
    def update_status(person_id, status):
        """Update person status (missing/found)"""
        collection = Person.get_collection()
        collection.update_one(
            {'_id': ObjectId(person_id)},
            {'$set': {'status': status}}
        )
    
    @staticmethod
    def delete(person_id):
        """Delete a person record"""
        collection = Person.get_collection()
        result = collection.delete_one({'_id': ObjectId(person_id)})
        return result.deleted_count > 0


class Detection:
    """Model for detection events"""
    
    @staticmethod
    def get_collection():
        """Get the detections collection"""
        from app import db
        return db['detections'] if db is not None else None
    
    @staticmethod
    def log(person_id, camera_id, location, confidence, timestamp):
        """Log a detection event"""
        collection = Detection.get_collection()
        detection_data = {
            'person_id': person_id,
            'camera_id': camera_id,
            'location': location,
            'confidence': confidence,
            'timestamp': timestamp
        }
        result = collection.insert_one(detection_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_recent(limit=50):
        """Get recent detections"""
        collection = Detection.get_collection()
        return list(collection.find().sort('timestamp', -1).limit(limit))
    
    @staticmethod
    def get_by_person(person_id, limit=20):
        """Get detections for specific person"""
        collection = Detection.get_collection()
        return list(collection.find({'person_id': person_id}).sort('timestamp', -1).limit(limit))
    
    @staticmethod
    def get_by_location(location, limit=20):
        """Get detections at specific location"""
        collection = Detection.get_collection()
        return list(collection.find({'location': location}).sort('timestamp', -1).limit(limit))
