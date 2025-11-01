from app import create_app

app = create_app()

if __name__ == '__main__':
    print("="*50)
    print("AI-Based Missing Person Detection System")
    print("="*50)
    print("\nStarting server...")
    print("Access the application at: http://127.0.0.1:5000")
    print("\nPress CTRL+C to quit")
    print("="*50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
