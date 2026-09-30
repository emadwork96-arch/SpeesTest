from flask import Flask, request, Response, render_template, jsonify
from werkzeug.exceptions import ClientDisconnected
import ipaddress
import json
import os
import time
import urllib.request

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


def client_ip():
    """Best guess of the visitor's public IP behind Render's proxy/Cloudflare."""
    candidates = [
        request.headers.get('CF-Connecting-IP'),
        request.headers.get('True-Client-IP'),
        (request.headers.get('X-Forwarded-For') or '').split(',')[0].strip(),
        request.remote_addr,
    ]
    for c in candidates:
        if not c:
            continue
        try:
            return str(ipaddress.ip_address(c.strip()))   # validates: no junk reaches the lookup URL
        except ValueError:
            continue
    return ''


_ip_cache = {}          # ip -> (timestamp, info)
IP_CACHE_TTL = 3600


def _get_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'speedtest/1.0'})
    with urllib.request.urlopen(req, timeout=3) as r:
        return json.loads(r.read().decode('utf-8', 'replace'))


def lookup_ip(ip):
    """ISP / location for a public IP. Tries two free HTTPS providers; returns {} if both fail."""
    try:
        d = _get_json(f'https://ipwho.is/{ip}')
        if d.get('success'):
            conn = d.get('connection') or {}
            return {'isp': conn.get('isp') or conn.get('org') or '',
                    'asn': conn.get('asn') or '',
                    'city': d.get('city') or '', 'country': d.get('country') or ''}
    except Exception:
        pass
    try:
        d = _get_json(f'https://ipapi.co/{ip}/json/')
        if not d.get('error'):
            return {'isp': d.get('org') or '', 'asn': d.get('asn') or '',
                    'city': d.get('city') or '', 'country': d.get('country_name') or ''}
    except Exception:
        pass
    return {}


@app.route('/info')
def info():
    ip = client_ip()
    out = {'ip': ip, 'isp': '', 'city': '', 'country': ''}
    try:
        public = bool(ip) and ipaddress.ip_address(ip).is_global
    except ValueError:
        public = False
    if public:
        hit = _ip_cache.get(ip)
        if hit and time.time() - hit[0] < IP_CACHE_TTL:
            found = hit[1]
        else:
            found = lookup_ip(ip)
            if found:                       # don't cache failures
                if len(_ip_cache) > 500:
                    _ip_cache.clear()
                _ip_cache[ip] = (time.time(), found)
        out.update(found)
    resp = jsonify(out)
    resp.headers['Cache-Control'] = 'no-store'
    return resp


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
