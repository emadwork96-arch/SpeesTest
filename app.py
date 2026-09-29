from flask import Flask, request, Response, render_template, jsonify
import os, time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ping')
def ping():
    return jsonify(pong=True)

@app.route('/download')
def download():
    size = int(request.args.get('bytes', 25000000))
    size = min(size, 100*1024*1024)
    def gen():
        chunk = 1024*1024
        sent = 0
        while sent < size:
            yield os.urandom(min(chunk, size-sent))
            sent += chunk
    headers = {
        'Content-Type': 'application/octet-stream',
        'Cache-Control': 'no-store, no-cache',
        'Access-Control-Allow-Origin': '*'
    }
    return Response(gen(), headers=headers)

@app.route('/upload', methods=['POST','OPTIONS'])
def upload():
    if request.method == 'OPTIONS':
        r = Response('')
        r.headers['Access-Control-Allow-Origin'] = '*'
        r.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        r.headers['Access-Control-Allow-Headers'] = '*'
        return r
    data = request.get_data()
    r = jsonify(received=len(data))
    r.headers['Access-Control-Allow-Origin'] = '*'
    return r

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
