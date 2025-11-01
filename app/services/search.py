import cv2
import numpy as np
from deepface import DeepFace
from datetime import datetime
import os
import tempfile


class FaceSearchService:
    """Face detection and recognition service using DeepFace"""
    
    def __init__(self, model_name='Facenet512', distance_metric='cosine', detector_backend='opencv'):
        self.model_name = model_name
        self.distance_metric = distance_metric
        self.detector_backend = detector_backend
        self.last_detection = {}
        
        # Default threshold - will be overridden by config
        self.threshold = 0.50
        
        print(f"✓ Face service initialized:")
        print(f"  Model: {model_name}")
        print(f"  Metric: {distance_metric}")
        print(f"  Detector: {detector_backend}")
    
    def verify_face_in_image(self, image_path):
        """Verify that image contains a face"""
        try:
            faces = DeepFace.extract_faces(
                img_path=image_path,
                detector_backend=self.detector_backend,
                enforce_detection=False
            )
            
            if len(faces) > 0:
                print(f"✓ Registration: Found {len(faces)} face(s) in image")
                return True
            else:
                print(f"✗ Registration: No faces found in image")
                return False
                
        except Exception as e:
            print(f"✗ Face detection error: {e}")
            return False
    
    def find_person_in_frame(self, frame, database_path, threshold=None):
        """Find registered persons in video frame"""
        if threshold is None:
            threshold = self.threshold
        
        detected_persons = []
        temp_frame_path = None
        
        try:
            # Save frame temporarily
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                temp_frame_path = tmp.name
                cv2.imwrite(temp_frame_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            
            # Get registered images
            if not os.path.exists(database_path):
                print(f"Database path not found: {database_path}")
                return detected_persons
            
            registered_images = [f for f in os.listdir(database_path) 
                                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
            
            if not registered_images:
                print("No registered images found")
                return detected_persons
            
            print(f"Checking against {len(registered_images)} registered image(s)...")
            
            # Compare against each registered person
            for img_file in registered_images:
                try:
                    img_path = os.path.join(database_path, img_file)
                    
                    # Verify faces match
                    result = DeepFace.verify(
                        img1_path=temp_frame_path,
                        img2_path=img_path,
                        model_name=self.model_name,
                        distance_metric=self.distance_metric,
                        detector_backend=self.detector_backend,
                        enforce_detection=False
                    )
                    
                    distance = result['distance']
                    
                    print(f"  {img_file}: distance = {distance:.4f} (threshold = {threshold:.4f})")
                    
                    # Check if match
                    if distance < threshold:
                        confidence = 1 - (distance / threshold)
                        confidence = max(0, min(1, confidence))
                        
                        detected_persons.append({
                            'photo_filename': img_file,
                            'confidence': float(confidence),
                            'distance': float(distance),
                            'verified': True
                        })
                        print(f"  ✓✓✓ MATCH! {img_file}")
                
                except Exception as e:
                    print(f"  Error comparing {img_file}: {e}")
                    continue
        
        except Exception as e:
            print(f"Frame detection error: {e}")
        
        finally:
            if temp_frame_path and os.path.exists(temp_frame_path):
                try:
                    os.remove(temp_frame_path)
                except:
                    pass
        
        return detected_persons
    
    def compare_faces(self, img1_path, img2_path):
        """Compare two face images"""
        try:
            result = DeepFace.verify(
                img1_path=img1_path,
                img2_path=img2_path,
                model_name=self.model_name,
                distance_metric=self.distance_metric,
                detector_backend=self.detector_backend,
                enforce_detection=False
            )
            return result['verified'], result['distance']
        except Exception as e:
            print(f"Comparison error: {e}")
            return False, 1.0
    
    def should_log_detection(self, person_id, cooldown_seconds=10):
        """Check if enough time passed since last detection"""
        current_time = datetime.now()
        
        if person_id not in self.last_detection:
            self.last_detection[person_id] = current_time
            return True
        
        time_diff = (current_time - self.last_detection[person_id]).seconds
        
        if time_diff >= cooldown_seconds:
            self.last_detection[person_id] = current_time
            return True
        
        return False
