#!/usr/bin/env python3
"""Super simple test server to verify Flask is working."""

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '''
    <html>
    <head><title>Test Server</title></head>
    <body>
        <h1>🎉 IT WORKS!</h1>
        <p>Flask server is running properly!</p>
        <p>Time to build the earthquake dashboard!</p>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print('🔥 Starting test server...')
    print('📡 Go to: http://127.0.0.1:8000')
    print('🚀 This should definitely work!')
    
    app.run(host='127.0.0.1', port=8000, debug=True)

