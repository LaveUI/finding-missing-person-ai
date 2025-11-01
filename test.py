from deepface import DeepFace
import cv2
import os

print("="*60)
print("FACE RECOGNITION DEBUG TEST")
print("="*60)

# Configuration
upload_folder = 'app/static/uploads'

# List all registered images
print("\n1. Checking registered images...")
if not os.path.exists(upload_folder):
    print(f"❌ Upload folder doesn't exist: {upload_folder}")
    exit()

images = [f for f in os.listdir(upload_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
print(f"✓ Found {len(images)} registered image(s):")
for img in images:
    print(f"  - {img}")

if not images:
    print("❌ No images registered! Register a person first.")
    exit()

# Test first image
test_image = os.path.join(upload_folder, images[0])
print(f"\n2. Testing image: {images[0]}")

# Test face detection
print("\n3. Testing face detection...")
try:
    faces = DeepFace.extract_faces(
        img_path=test_image,
        detector_backend='opencv',
        enforce_detection=False
    )
    print(f"✓ Found {len(faces)} face(s)")
    if len(faces) == 0:
        print("❌ NO FACES DETECTED! This is the problem.")
        print("   Solution: Re-register with a clearer photo")
except Exception as e:
    print(f"❌ Error: {e}")

# Test same image comparison (should always match)
print("\n4. Testing self-comparison (should be 100% match)...")
models = ['VGG-Face', 'Facenet512', 'ArcFace']
for model in models:
    try:
        result = DeepFace.verify(
            img1_path=test_image,
            img2_path=test_image,
            model_name=model,
            distance_metric='cosine',
            enforce_detection=False
        )
        print(f"\n{model}:")
        print(f"  Verified: {result['verified']}")
        print(f"  Distance: {result['distance']:.6f}")
        print(f"  Threshold: {result['threshold']:.6f}")
        
        if result['distance'] > 0.01:
            print(f"  ⚠️ WARNING: Same image has distance > 0.01")
    except Exception as e:
        print(f"  ❌ {model} error: {e}")

# Test camera capture
print("\n5. Testing camera capture...")
try:
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if camera.isOpened():
        ret, frame = camera.read()
        if ret:
            # Mirror the frame (like in your app)
            frame = cv2.flip(frame, 1)
            
            # Save test frame
            test_frame_path = 'test_camera_frame.jpg'
            cv2.imwrite(test_frame_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            print(f"✓ Captured frame saved as: {test_frame_path}")
            
            # Test if frame has faces
            faces = DeepFace.extract_faces(
                img_path=test_frame_path,
                detector_backend='opencv',
                enforce_detection=False
            )
            print(f"✓ Camera frame has {len(faces)} face(s)")
            
            # Compare registered image with camera frame
            print(f"\n6. Comparing registered image with camera frame...")
            for model in ['Facenet512', 'VGG-Face']:
                try:
                    result = DeepFace.verify(
                        img1_path=test_image,
                        img2_path=test_frame_path,
                        model_name=model,
                        distance_metric='cosine',
                        enforce_detection=False
                    )
                    print(f"\n{model}:")
                    print(f"  Verified: {result['verified']}")
                    print(f"  Distance: {result['distance']:.6f}")
                    print(f"  Threshold: {result['threshold']:.6f}")
                    
                    if result['distance'] < 0.50:
                        print(f"  ✓ MATCH! They look similar")
                    else:
                        print(f"  ❌ NO MATCH - distance too high")
                except Exception as e:
                    print(f"  ❌ Error: {e}")
            
            camera.release()
            
            # Display images side by side
            print("\n7. Displaying comparison (press any key to close)...")
            registered_img = cv2.imread(test_image)
            frame_img = cv2.imread(test_frame_path)
            
            # Resize to same height
            h = 400
            registered_resized = cv2.resize(registered_img, (int(registered_img.shape[1] * h / registered_img.shape[0]), h))
            frame_resized = cv2.resize(frame_img, (int(frame_img.shape[1] * h / frame_img.shape[0]), h))
            
            # Combine side by side
            combined = cv2.hconcat([registered_resized, frame_resized])
            cv2.putText(combined, "Registered", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(combined, "Camera", (registered_resized.shape[1] + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            cv2.imshow('Comparison: Registered vs Camera', combined)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            print("❌ Failed to capture frame")
    else:
        print("❌ Camera failed to open")
except Exception as e:
    print(f"❌ Camera error: {e}")

print("\n" + "="*60)
print("Test complete!")
print("="*60)
