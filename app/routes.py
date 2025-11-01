from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, Response, jsonify
from werkzeug.utils import secure_filename
from app.models.person import Person, Detection
from app.services.search import FaceSearchService
from app.utils.helpers import save_uploaded_file, format_detection_time
import cv2
from datetime import datetime, timedelta
import os

main_bp = Blueprint('main', __name__)

# Initialize face search service
face_service = None

def get_face_service():
    """Get or create face service instance"""
    global face_service
    if face_service is None:
        print("\nInitializing Face Service...")
        
        model = current_app.config.get('DEEPFACE_MODEL', 'VGG-Face')
        detector = current_app.config.get('DETECTOR_BACKEND', 'opencv')
        metric = current_app.config.get('DISTANCE_METRIC', 'cosine')
        
        print(f"  Model: {model}")
        print(f"  Detector: {detector}")
        print(f"  Metric: {metric}")
        
        face_service = FaceSearchService(
            model_name=model,
            detector_backend=detector,
            distance_metric=metric
        )
        
        threshold = current_app.config.get('RECOGNITION_THRESHOLD', 0.70)
        face_service.threshold = threshold
        
        print(f"  Threshold: {threshold}")
        print("✓ Face service ready\n")
    
    return face_service

@main_bp.route('/')
def index():
    """Home page with live feed"""
    try:
        all_persons = Person.get_all()
        all_detections = Detection.get_recent(limit=1000)
        recent_detections = [
            d for d in all_detections 
            if d['timestamp'] > datetime.now() - timedelta(hours=24)
        ]
        
        stats = {
            'total_persons': len(all_persons),
            'total_detections': len(all_detections),
            'recent_detections': len(recent_detections)
        }
    except Exception as e:
        print(f"Error calculating stats: {e}")
        stats = {
            'total_persons': 0,
            'total_detections': 0,
            'recent_detections': 0
        }
    
    return render_template('index.html', stats=stats)

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register a missing person"""
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            age = request.form.get('age')
            contact = request.form.get('contact')
            description = request.form.get('description', '')
            photo = request.files.get('photo')
            
            if not all([name, age, contact, photo]):
                flash('All required fields must be filled', 'error')
                return redirect(url_for('main.register'))
            
            filename, filepath = save_uploaded_file(photo, current_app.config['UPLOAD_FOLDER'])
            
            if not filename:
                flash('Invalid file type. Please upload an image (PNG, JPG, JPEG, GIF)', 'error')
                return redirect(url_for('main.register'))
            
            service = get_face_service()
            if service.verify_face_in_image(filepath):
                person_id = Person.create(name, age, contact, filename, description)
                flash(f'Successfully registered {name}', 'success')
                return redirect(url_for('main.dashboard'))
            else:
                os.remove(filepath)
                flash('No face detected in image. Please upload a clear photo showing the face.', 'error')
        
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    return render_template('register.html')

@main_bp.route('/dashboard')
def dashboard():
    """View all registered persons and recent detections"""
    try:
        persons = Person.get_all()
        detections = Detection.get_recent(limit=50)
        
        recent_count = 0
        current_time = datetime.now()
        
        for detection in detections:
            try:
                person = Person.get_by_id(detection['person_id'])
                detection['person_name'] = person['name'] if person else 'Unknown'
                detection['formatted_time'] = format_detection_time(detection['timestamp'])
                
                if isinstance(detection['timestamp'], datetime):
                    time_diff = current_time - detection['timestamp']
                    if time_diff < timedelta(hours=24):
                        recent_count += 1
            except Exception as e:
                print(f"Error processing detection: {e}")
                detection['person_name'] = 'Unknown'
                detection['formatted_time'] = 'N/A'
        
        return render_template('dashboard.html', 
                             persons=persons, 
                             detections=detections,
                             recent_count=recent_count)
    
    except Exception as e:
        print(f"Dashboard error: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return render_template('dashboard.html', persons=[], detections=[], recent_count=0)

@main_bp.route('/person/<person_id>')
def person_detail(person_id):
    """View details of a specific person"""
    try:
        person = Person.get_by_id(person_id)
        
        if not person:
            flash('Person not found', 'error')
            return redirect(url_for('main.dashboard'))
        
        detections = Detection.get_by_person(person_id)
        
        for detection in detections:
            detection['formatted_time'] = format_detection_time(detection['timestamp'])
        
        return render_template('person_detail.html', person=person, detections=detections)
    
    except Exception as e:
        print(f"Person detail error: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error loading person details: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))

@main_bp.route('/video_feed')
def video_feed():
    """Video streaming route"""
    # Get app instance before creating response
    app = current_app._get_current_object()
    return Response(generate_frames(app),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

def generate_frames(app):
    """Generate video frames with face detection - SMOOTH 30 FPS"""
    import cv2
    from datetime import datetime
    import threading
    import queue
    import time
    
    with app.app_context():
        print("\n" + "="*60)
        print("VIDEO STREAM STARTING (MULTI-THREADED)")
        print("="*60)
        
        # Camera setup
        camera = None
        for idx in [0, 1, 2]:
            try:
                cam = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
                if cam.isOpened():
                    cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    cam.set(cv2.CAP_PROP_FPS, 30)
                    
                    ret, frame = cam.read()
                    if ret:
                        camera = cam
                        print(f"✓ Camera {idx} working (640x480 @ 30fps)")
                        break
                    cam.release()
            except:
                pass
        
        if not camera:
            print("❌ NO CAMERA!")
            return
        
        upload_folder = app.config.get('UPLOAD_FOLDER')
        persons = Person.get_all()
        person_map = {p['photo_path']: p for p in persons}
        
        registered_images = []
        if os.path.exists(upload_folder):
            registered_images = [f for f in os.listdir(upload_folder) 
                                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
        
        print(f"✓ Loaded {len(persons)} persons, {len(registered_images)} images")
        
        # Create face service
        face_service = None
        try:
            face_service = FaceSearchService(
                model_name='VGG-Face',
                detector_backend='opencv',
                distance_metric='cosine'
            )
            face_service.threshold = 0.70
            print(f"✓ Face service ready")
        except Exception as e:
            print(f"❌ Service failed: {e}")
        
        print("="*60)
        print("SMOOTH VIDEO MODE STARTED")
        print("="*60 + "\n")
        
        # Shared variables for thread communication
        detection_queue = queue.Queue(maxsize=1)
        latest_detection = []
        stop_detection = threading.Event()
        frame_for_detection = None
        frame_lock = threading.Lock()
        detection_count = 0
        
        # Background detection thread
        def detection_worker():
            nonlocal detection_count, latest_detection
            
            while not stop_detection.is_set():
                try:
                    # Get frame to process
                    with frame_lock:
                        if frame_for_detection is None:
                            time.sleep(0.1)
                            continue
                        frame_to_process = frame_for_detection.copy()
                    
                    # Run detection (slow operation, doesn't block video)
                    small_frame = cv2.resize(frame_to_process, (320, 240))
                    detected = face_service.find_person_in_frame(small_frame, upload_folder, 0.70)
                    
                    if detected:
                        detection_count += 1
                        print(f"🎯 DETECTION #{detection_count} 🎯")
                        
                        for det in detected:
                            filename = det['photo_filename']
                            if filename in person_map:
                                person = person_map[filename]
                                person_id = str(person['_id'])
                                confidence = det['confidence']
                                
                                print(f"  MATCH: {person['name']} ({confidence:.1%})")
                                
                                # Log to database
                                if face_service.should_log_detection(person_id, 10):
                                    try:
                                        Detection.log(
                                            person_id=person_id,
                                            camera_id='CAM_001',
                                            location='Main Entrance',
                                            confidence=confidence,
                                            timestamp=datetime.now()
                                        )
                                        Person.update_last_seen(person_id, 'Main Entrance', datetime.now())
                                        print(f"  ✓ Logged to DB")
                                    except Exception as e:
                                        print(f"  DB error: {e}")
                    
                    latest_detection = detected
                    time.sleep(1.0)  # Run detection every 1 second
                    
                except Exception as e:
                    print(f"Detection worker error: {e}")
                    time.sleep(1.0)
        
        # Start detection thread
        if face_service and registered_images:
            detection_thread = threading.Thread(target=detection_worker, daemon=True)
            detection_thread.start()
            print("✓ Detection thread started")
        
        frame_count = 0
        
        try:
            while True:
                success, frame = camera.read()
                if not success:
                    break
                
                frame = cv2.flip(frame, 1)
                frame_count += 1
                
                # Send frame to detection thread every 30 frames (~1 second)
                if face_service and registered_images and frame_count % 30 == 0:
                    with frame_lock:
                        frame_for_detection = frame.copy()
                
                # Draw detection results (from background thread)
                if latest_detection:
                    for det in latest_detection:
                        filename = det['photo_filename']
                        if filename in person_map:
                            person = person_map[filename]
                            confidence = det['confidence']
                            
                            # Draw BIG alert box
                            cv2.rectangle(frame, (10, 10), (600, 120), (0, 0, 255), -1)
                            cv2.putText(frame, f"ALERT: {person['name']}", (20, 50),
                                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
                            cv2.putText(frame, f"Confidence: {confidence*100:.0f}%", (20, 90),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                
                # Minimal status overlay
                status_color = (0, 255, 0) if face_service else (255, 255, 0)
                cv2.putText(frame, "LIVE", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
                
                # Timestamp
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cv2.putText(frame, timestamp, (10, frame.shape[0] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Encode with good quality for smooth display
                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
                if ret:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        
        except GeneratorExit:
            print("\nClient disconnected")
        except Exception as e:
            print(f"Stream error: {e}")
        finally:
            # Stop detection thread
            stop_detection.set()
            if camera:
                camera.release()
            print(f"\nStream ended. Total frames: {frame_count}\n")


@main_bp.route('/simple_video_feed')
def simple_video_feed():
    """Simple video feed without face detection for testing"""
    return Response(simple_camera_stream(), 
                   mimetype='multipart/x-mixed-replace; boundary=frame')

def simple_camera_stream():
    """Simple camera stream without AI processing"""
    import cv2
    
    camera = None
    for idx in [0, 1, 2]:
        try:
            cam = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
            if cam.isOpened():
                ret, frame = cam.read()
                if ret:
                    camera = cam
                    print(f"✓ Simple camera {idx} opened")
                    break
                cam.release()
        except:
            pass
    
    if not camera:
        return
    
    try:
        frame_count = 0
        while True:
            success, frame = camera.read()
            if not success:
                break
            
            frame = cv2.flip(frame, 1)
            frame_count += 1
            
            cv2.putText(frame, f"Frame: {frame_count}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, datetime.now().strftime('%H:%M:%S'), (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    finally:
        camera.release()

@main_bp.route('/debug_info')
def debug_info():
    """Debug information"""
    upload_folder = current_app.config['UPLOAD_FOLDER']
    threshold = current_app.config.get('RECOGNITION_THRESHOLD', 0.50)
    model = current_app.config.get('DEEPFACE_MODEL', 'VGG-Face')
    
    images = []
    if os.path.exists(upload_folder):
        images = [f for f in os.listdir(upload_folder) 
                 if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
    
    persons = Person.get_all()
    
    return jsonify({
        'upload_folder': upload_folder,
        'upload_folder_exists': os.path.exists(upload_folder),
        'images_in_folder': images,
        'persons_in_db': [{'name': p['name'], 'photo': p['photo_path']} for p in persons],
        'threshold': threshold,
        'model': model
    })

@main_bp.route('/test_hello')
def test_hello():
    print("TEST ROUTE CALLED!")
    return "Hello! Routes are working."
