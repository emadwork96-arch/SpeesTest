from flask import Flask, request, Response, render_template, jsonify, redirect, abort, url_for
from markupsafe import Markup, escape
from werkzeug.exceptions import ClientDisconnected
from werkzeug.middleware.proxy_fix import ProxyFix
import datetime
import ipaddress
import json
import os
import re
import threading
import time
import urllib.request

import content

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)   # correct https:// URLs behind Render / Cloudflare
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 7 * 24 * 3600               # /static is versioned with ?v=
# Upload chunks from the page are 8 MB; allow some headroom, reject anything huge.
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024

# ---------------------------------------------------------------- settings (environment variables, see README)
SITE_NAME = os.environ.get('SITE_NAME', 'SpeedTest')
SITE_URL = os.environ.get('SITE_URL', '').rstrip('/')                  # e.g. https://yourdomain.com
CONTACT_EMAIL = os.environ.get('CONTACT_EMAIL', 'contact@example.com')
OPERATOR_NAME = os.environ.get('OPERATOR_NAME', SITE_NAME)
SERVER_LOCATION = os.environ.get('SERVER_LOCATION', '')                # e.g. Frankfurt, Germany (shown under the test)
DEFAULT_LANG = os.environ.get('DEFAULT_LANG', 'en')
ADSENSE_CLIENT = os.environ.get('ADSENSE_CLIENT', '').strip()          # ca-pub-XXXXXXXXXXXXXXXX ; empty = no ads at all
ADSENSE_SLOT_TOP = os.environ.get('ADSENSE_SLOT_TOP', '').strip()      # optional manual ad units
ADSENSE_SLOT_BOTTOM = os.environ.get('ADSENSE_SLOT_BOTTOM', '').strip()
MAX_BYTES_PER_HOUR = int(float(os.environ.get('MAX_MB_PER_HOUR', '6000')) * 1024 * 1024)   # per visitor IP
ASSET_VERSION = os.environ.get('ASSET_VERSION', '20')
if DEFAULT_LANG not in content.LANGS:
    DEFAULT_LANG = 'en'

CHUNK = 1024 * 1024
# Generate 1 MB of random bytes once at startup and reuse it for every download.
# os.urandom() on every chunk burns CPU on Render's free tier for no benefit.
PAYLOAD = os.urandom(CHUNK)

NO_CACHE = {
    'Cache-Control': 'no-store, no-cache, no-transform, max-age=0',
    'Pragma': 'no-cache',
    'Access-Control-Allow-Origin': '*',
}


# ---------------------------------------------------------------- bandwidth protection
# Every test moves 100-300 MB. To stop scripts from burning the hosting bandwidth, each public IP gets an
# hourly budget. Normal visitors (a few tests) never reach it. Private/local addresses are exempt.
_usage = {}                      # ip -> [window_start, bytes]
_usage_lock = threading.Lock()


def _exempt(ip):
    try:
        return not ipaddress.ip_address(ip).is_global
    except ValueError:
        return True


def over_quota(ip):
    if not ip or _exempt(ip):
        return False
    with _usage_lock:
        rec = _usage.get(ip)
        return bool(rec and time.time() - rec[0] < 3600 and rec[1] >= MAX_BYTES_PER_HOUR)


def add_usage(ip, n):
    if not ip or _exempt(ip):
        return
    now = time.time()
    with _usage_lock:
        rec = _usage.get(ip)
        if not rec or now - rec[0] >= 3600:
            if len(_usage) > 5000:
                _usage.clear()
            rec = _usage[ip] = [now, 0]
        rec[1] += n


# ---------------------------------------------------------------- pages (server-rendered, one URL per language)
def site_url():
    return SITE_URL or request.url_root.rstrip('/')


def fill(text):
    return text.replace('{site}', SITE_NAME).replace('{email}', CONTACT_EMAIL).replace('{operator}', OPERATOR_NAME)


_url_re = re.compile(r'(https?://[^\s<]+[^\s<.,;:)])|([\w.+-]+@[\w-]+\.[\w.-]+\w)')


@app.template_filter('linkify')
def linkify(text):
    out, last = [], 0
    for m in _url_re.finditer(text):
        out.append(escape(text[last:m.start()]))
        if m.group(1):
            out.append(Markup('<a href="%s" rel="noopener nofollow" target="_blank">%s</a>') % (m.group(1), m.group(1)))
        else:
            out.append(Markup('<a href="mailto:%s">%s</a>') % (m.group(2), m.group(2)))
        last = m.end()
    out.append(escape(text[last:]))
    return Markup('').join(out)


def page_path(lang, page=None):
    return f'/{lang}' + (f'/{page}' if page else '')


def common_ctx(lang, page=None):
    base = site_url()
    c = content.T[lang]
    return dict(
        lang=lang, rtl=lang in content.RTL, site=SITE_NAME, site_url=base, ver=ASSET_VERSION,
        ui=c['ui'], nav=c['nav'], c=c, year=datetime.date.today().year, og_locale=content.OG_LOCALE[lang],
        canonical=base + page_path(lang, page),
        alternates=[(l, base + page_path(l, page)) for l in content.LANGS],
        xdefault=base + page_path(DEFAULT_LANG, page),
        lang_options=[(l, content.NAMES[l], page_path(l, page)) for l in content.LANGS],
        server_loc=SERVER_LOCATION, adsense_client=ADSENSE_CLIENT,
        ads=({'client': ADSENSE_CLIENT, 'slot_top': ADSENSE_SLOT_TOP, 'slot_bottom': ADSENSE_SLOT_BOTTOM}
             if ADSENSE_CLIENT and page is None else None),
    )


def html(template, **ctx):
    resp = Response(render_template(template, **ctx))
    resp.headers['Cache-Control'] = 'public, max-age=300'
    return resp


def detect_lang():
    saved = request.cookies.get('st_lang')
    if saved in content.LANGS:
        return saved
    for tag, _q in request.accept_languages:
        primary = tag.split('-')[0].lower()
        if primary in content.LANGS:
            return primary
    return DEFAULT_LANG


@app.route('/')
def root():
    resp = redirect(page_path(detect_lang()), code=302)        # crawlers send no language and get the default
    resp.headers['Vary'] = 'Accept-Language, Cookie'
    resp.headers['Cache-Control'] = 'private, max-age=0'
    return resp


@app.route('/<any(%s):lang>' % ','.join(content.LANGS))
def home(lang):
    c = content.T[lang]
    base = site_url()
    faq = [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in c['faq']]
    jsonld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'WebApplication', 'name': SITE_NAME, 'url': base + page_path(lang), 'description': c['desc'],
         'applicationCategory': 'UtilitiesApplication', 'operatingSystem': 'Any', 'inLanguage': lang,
         'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'USD'}},
        {'@type': 'FAQPage', 'mainEntity': faq}]}
    return html('index.html', title=c['title'], desc=c['desc'], jsonld=jsonld, **common_ctx(lang))


@app.route('/<any(%s):lang>/<any(%s):page>' % (','.join(content.LANGS), ','.join(content.PAGES)))
def info_page(lang, page):
    d = content.T[lang]['pages'][page]
    body = [(k, fill(v)) for k, v in d['body']]
    return html('page.html', title=fill(d['title']) + ' | ' + SITE_NAME, desc=fill(d['desc']), page_title=fill(d['title']),
                body=body, updated=content.UPDATED if page in ('privacy', 'terms') else '', **common_ctx(lang, page))


@app.errorhandler(404)
def not_found(_e):
    lang = detect_lang()
    c = content.T[lang]
    resp = Response(render_template('page.html', title=c['ui']['notfound'] + ' | ' + SITE_NAME, desc=c['ui']['notfound'],
                                    page_title=c['ui']['notfound'], body=[('p', c['ui']['notfound_p'])], updated='',
                                    **common_ctx(lang, None)), status=404)
    return resp


@app.route('/robots.txt')
def robots():
    txt = ('User-agent: *\nAllow: /\nDisallow: /download\nDisallow: /upload\nDisallow: /ping\nDisallow: /info\n\n'
           f'Sitemap: {site_url()}/sitemap.xml\n')
    return Response(txt, mimetype='text/plain')


@app.route('/sitemap.xml')
def sitemap():
    base = site_url()
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for page in [None] + content.PAGES:
        for lang in content.LANGS:
            out.append(f'<url><loc>{base}{page_path(lang, page)}</loc>')
            for l in content.LANGS:
                out.append(f'<xhtml:link rel="alternate" hreflang="{l}" href="{base}{page_path(l, page)}"/>')
            out.append(f'<xhtml:link rel="alternate" hreflang="x-default" href="{base}{page_path(DEFAULT_LANG, page)}"/>')
            out.append('<changefreq>monthly</changefreq></url>')
    out.append('</urlset>')
    return Response('\n'.join(out), mimetype='application/xml')


@app.route('/ads.txt')
def ads_txt():
    if not ADSENSE_CLIENT.startswith('ca-pub-'):
        abort(404)
    return Response(f'google.com, {ADSENSE_CLIENT.replace("ca-", "", 1)}, DIRECT, f08c47fec0942fa0\n', mimetype='text/plain')


@app.route('/healthz')
def healthz():
    return 'ok'


@app.after_request
def security_headers(resp):
    resp.headers.setdefault('X-Content-Type-Options', 'nosniff')
    resp.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
    return resp


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


_ip_cache = {}          # ip -> (expires_at, info)
IP_CACHE_TTL = 3600


def _get_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'speedtest/1.0'})
    with urllib.request.urlopen(req, timeout=2.5) as r:
        return json.loads(r.read().decode('utf-8', 'replace'))


def lookup_ip(ip):
    """ISP / location / mobile-network flag for a public IP.

    Tries three free HTTPS providers in order and returns {} if all fail.
    'mobile' is True/False when the provider knows, None when it does not.
    'via' names the provider that answered and 'note' says why earlier ones did not,
    so the page can show the real reason instead of a bare "Unknown".
    """
    why = []

    def fail(name, e):
        why.append(f'{name}: {type(e).__name__} {str(e)[:60]}')

    try:
        d = _get_json(f'https://api.ipapi.is/?q={ip}')
        comp, asn, loc = d.get('company') or {}, d.get('asn') or {}, d.get('location') or {}
        isp = comp.get('name') or asn.get('org') or ''
        if isp:
            mob = d.get('is_mobile')
            if not isinstance(mob, bool):
                why.append(f'ipapi.is: no is_mobile flag ({mob!r})')
            return {'isp': isp, 'asn': asn.get('asn') or '',
                    'city': loc.get('city') or '', 'country': loc.get('country') or '',
                    'mobile': mob if isinstance(mob, bool) else None,
                    'via': 'ipapi.is', 'note': '; '.join(why)}
        why.append('ipapi.is: empty answer ' + str(d.get('error') or d.get('message') or '')[:60])
    except Exception as e:
        fail('ipapi.is', e)
    try:
        d = _get_json(f'https://ipwho.is/{ip}')
        if d.get('success'):
            conn = d.get('connection') or {}
            return {'isp': conn.get('isp') or conn.get('org') or '',
                    'asn': conn.get('asn') or '',
                    'city': d.get('city') or '', 'country': d.get('country') or '',
                    'mobile': None, 'via': 'ipwho.is', 'note': '; '.join(why)}
        why.append('ipwho.is: ' + str(d.get('message') or 'not successful')[:60])
    except Exception as e:
        fail('ipwho.is', e)
    try:
        d = _get_json(f'https://ipapi.co/{ip}/json/')
        if not d.get('error'):
            return {'isp': d.get('org') or '', 'asn': d.get('asn') or '',
                    'city': d.get('city') or '', 'country': d.get('country_name') or '',
                    'mobile': None, 'via': 'ipapi.co', 'note': '; '.join(why)}
        why.append('ipapi.co: ' + str(d.get('reason') or d.get('error'))[:60])
    except Exception as e:
        fail('ipapi.co', e)
    return {'note': '; '.join(why)}


@app.route('/info')
def info():
    ip = client_ip()
    out = {'ip': ip, 'isp': '', 'city': '', 'country': '', 'mobile': None, 'via': '', 'note': ''}
    try:
        public = bool(ip) and ipaddress.ip_address(ip).is_global
    except ValueError:
        public = False
    if public:
        hit = _ip_cache.get(ip)
        if hit and hit[0] > time.time():
            found = hit[1]
        else:
            found = lookup_ip(ip)
            if found.get('isp'):                 # never cache total failures
                if len(_ip_cache) > 500:
                    _ip_cache.clear()
                ttl = IP_CACHE_TTL if found.get('mobile') is not None else 60   # incomplete answer: retry soon
                _ip_cache[ip] = (time.time() + ttl, found)
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
    ip = client_ip()
    if over_quota(ip):
        r = jsonify(error='hourly limit reached')
        r.status_code = 429
        r.headers['Retry-After'] = '600'
        r.headers.update(NO_CACHE)
        return r
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
            add_usage(ip, n)                       # counts what is actually sent (aborted requests cost little)
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

    ip = client_ip()
    if over_quota(ip):
        r = jsonify(error='hourly limit reached')
        r.status_code = 429
        r.headers['Retry-After'] = '600'
        r.headers.update(NO_CACHE)
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
            add_usage(ip, len(chunk))
    except (ClientDisconnected, OSError):
        pass  # the browser aborts in-flight uploads when the test ends

    resp = jsonify(ok=True, received=received)
    resp.headers.update(NO_CACHE)
    return resp


if __name__ == '__main__':
    # Local run: python app.py  (threaded so parallel streams don't queue)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), threaded=True)
