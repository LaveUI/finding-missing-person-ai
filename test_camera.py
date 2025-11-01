import cv2

print("Testing available cameras...")

# Test camera indices 0-4
for i in range(5):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print(f"✓ Camera {i}: Working - Resolution: {frame.shape}")
        else:
            print(f"✗ Camera {i}: Opens but can't read frames")
        cap.release()
    else:
        print(f"✗ Camera {i}: Not available")

print("\nTest complete!")
