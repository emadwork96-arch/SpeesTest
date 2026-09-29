from flask import Flask, request, Response, render_template, jsonify
from werkzeug.exceptions import ClientDisconnected
import os

app = Flask(__name__)
# Upload chunks from the page are 8 MB; allow some headroom, reject anything huge.
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024

CHUNK = 1024 * 1024
# Generate 1 MB of random bytes once at startup and reuse it for every download.
# os.urandom() on every chunk burns CPU on Render's free tier for no benefit.
PAYLOAD = os.urandom(CHUNK)

NO_CACHE = {
    'Cache-Control': 'no-store, no-cache, no-transform, max-age=0',
    'Pragma': 'no-cache',
    'Access-Control-Allow-Origin': '*',
}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/ping')
def ping():
    resp = jsonify(pong=True)
    resp.headers.update(NO_CACHE)
    return resp


@app.route('/download')
def download():
    try:
        size = int(request.args.get('bytes', 25_000_000))
    except ValueError:
        size = 25_000_000
    size = max(1, min(size, 100 * 1024 * 1024))
    view = memoryview(PAYLOAD)

    def gen():
        left = size
        while left > 0:
            n = min(CHUNK, left)
            yield view[:n].tobytes() if n < CHUNK else PAYLOAD
            left -= n

    headers = dict(NO_CACHE)
    headers.update({
        'Content-Type': 'application/octet-stream',
        'Content-Length': str(size),
        'X-Accel-Buffering': 'no',
    })
    return Response(gen(), headers=headers, direct_passthrough=True)


@app.route('/upload', methods=['POST', 'OPTIONS'])
def upload():
    if request.method == 'OPTIONS':
        r = Response('')
        r.headers.update(NO_CACHE)
        r.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        r.headers['Access-Control-Allow-Headers'] = '*'
        return r

    # Read and discard the body in pieces instead of request.get_data(),
    # which would hold the whole upload in memory.
    received = 0
    try:
        stream = request.stream
        while True:
            chunk = stream.read(64 * 1024)
            if not chunk:
                break
            received += len(chunk)
    except (ClientDisconnected, OSError):
        pass  # the browser aborts in-flight uploads when the test ends

    resp = jsonify(ok=True, received=received)
    resp.headers.update(NO_CACHE)
    return resp


if __name__ == '__main__':
    # Local run: python app.py  (threaded so parallel streams don't queue)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), threaded=True)
