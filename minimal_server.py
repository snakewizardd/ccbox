#!/usr/bin/env python3
"""Absolute minimal test to see what's happening."""

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return """
    <html>
    <body>
        <h1 style="color: red; font-size: 50px;">HELLO WORLD TEST</h1>
        <p>If you can see this, Flask is working!</p>
    </body>
    </html>
    """

if __name__ == '__main__':
    print("="*50)
    print("STARTING MINIMAL TEST SERVER")
    print("Go to: http://127.0.0.1:9999")
    print("="*50)
    app.run(host='127.0.0.1', port=9999, debug=False)
