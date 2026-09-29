from flask import Flask, request, Response, render_template, jsonify
import os, time

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ping')
def ping():
    resp = jsonify(pong=True)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route('/download')
def download():
    size = int(request.args.get('bytes', 25000000))
    size = min(size, 100*1024*1024)
    def gen():
        chunk_size = 1024*1024
        sent = 0
        while sent < size:
            yield os.urandom(min(chunk_size, size-sent))
            sent += chunk_size
    headers = {
        'Content-Type': 'application/octet-stream',
        'Cache-Control': 'no-store, no-cache, must-revalidate',
        'Access-Control-Allow-Origin': '*',
        'Content-Length': str(size)
    }
    return Response(gen(), headers=headers)

@app.route('/upload', methods=['POST', 'OPTIONS'])
def upload():
    if request.method == 'OPTIONS':
        r = Response('')
        r.headers['Access-Control-Allow-Origin'] = '*'
        r.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        r.headers['Access-Control-Allow-Headers'] = '*'
        return r
    try:
        total = 0
        while True:
            chunk = request.stream.read(64*1024)
            if not chunk:
                break
            total += len(chunk)
        if total == 0:
            total = request.content_length or 0
        resp = jsonify(received=total, ok=True)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    except Exception as e:
        resp = jsonify(error=str(e), ok=False)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp, 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, threaded=True)
