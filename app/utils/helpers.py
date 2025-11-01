import os
from werkzeug.utils import secure_filename
from datetime import datetime

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, upload_folder):
    """Save uploaded file and return filename"""
    if file and allowed_file(file.filename):
        # Create unique filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        original_filename = secure_filename(file.filename)
        filename = f"{timestamp}_{original_filename}"
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        return filename, filepath
    return None, None

def format_detection_time(timestamp):
    """Format timestamp for display"""
    if isinstance(timestamp, datetime):
        return timestamp.strftime('%Y-%m-%d %H:%M:%S')
    return str(timestamp)

def calculate_age_from_year(birth_year):
    """Calculate age from birth year"""
    current_year = datetime.now().year
    return current_year - birth_year

def get_file_size_mb(filepath):
    """Get file size in MB"""
    size_bytes = os.path.getsize(filepath)
    return round(size_bytes / (1024 * 1024), 2)
