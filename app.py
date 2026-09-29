from flask import Flask, request, Response, render_template, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ping')
def ping():
    return jsonify(pong=True)

@app.route('/download')
def download():
    size = int(request.args.get('bytes', 30000000))
    size = min(size, 100*1024*1024)
    def gen():
        sent = 0
        while sent < size:
            yield os.urandom(min(1024*1024, size-sent))
            sent += 1024*1024
    return Response(gen(), headers={
        'Content-Type': 'application/octet-stream',
        'Cache-Control': 'no-store',
        'Content-Length': str(size),
        'Access-Control-Allow-Origin': '*'
    })

@app.route('/upload', methods=['POST', 'OPTIONS'])
def upload():
    if request.method == 'OPTIONS':
        r = Response('')
        r.headers['Access-Control-Allow-Origin'] = '*'
        r.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        r.headers['Access-Control-Allow-Headers'] = '*'
        return r
    # لا نقرأ البيانات - نرجع فوراً، القياس من وقت إرسال العميل
    # هذا يمنع التعليق على Render Free
    resp = jsonify(ok=True, received=request.content_length or 0)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Cache-Control'] = 'no-store'
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)), threaded=True)
