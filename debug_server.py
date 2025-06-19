#!/usr/bin/env python3
"""Debug what's happening with Flask."""

try:
    print("1. Importing Flask...")
    from flask import Flask
    print("   ✅ Flask imported successfully")
    
    print("2. Creating Flask app...")
    app = Flask(__name__)
    print("   ✅ Flask app created")
    
    @app.route('/')
    def hello():
        return "<h1>IT WORKS!</h1>"
    
    print("3. Starting server...")
    print("   🌐 Go to: http://127.0.0.1:7777")
    print("   🔥 If you see 'IT WORKS!' then Flask is fine")
    
    # Use threaded mode and different host
    app.run(host='0.0.0.0', port=7777, debug=False, threaded=True)
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()