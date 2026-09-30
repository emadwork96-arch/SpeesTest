<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Speed Test</title>
<meta name="theme-color" content="#0a0a0a">
<script>
/* apply the saved (or system) theme before the first paint, so there is no flash */
(function(){ var t = null;
  try { t = localStorage.getItem('st_theme'); } catch(e) {}
  if (t !== 'light' && t !== 'dark') t = (window.matchMedia && matchMedia('(prefers-color-scheme: light)').matches) ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', t);
})();
</script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@500;700&family=Noto+Sans+Arabic:wght@500;700&display=swap" rel="stylesheet">
<style>
:root{
  color-scheme:dark;
  --bg:#0a0a0a; --card:#121212; --line:#1e1e1e; --line2:#1a1a1a; --panel:#0e0e0e; --shadow:none;
  --text:#ffffff; --muted:#666666; --dim:#555555;
  --btn:#181818; --btnline:#2a2a2a;
  --tick:#262626; --tickmajor:#3d3d3d;
  --ink:#ffffff;                       /* needle, hub, dial numbers, peak marker */
  --dlc:#22d3ee; --ulc:#f472b6;        /* phase label colours */
  --g1:#3b82f6;  --g2:#22d3ee;         /* download gradient */
  --u1:#8b5cf6;  --u2:#ec4899;         /* upload gradient */
  --tip:#67e8f9; --tipu:#f9a8d4;
  --ulnum1:#a78bfa; --ulnum2:#f472b6;
  --err:#f87171; --focus:#a78bfa;
}
:root[data-theme="light"]{
  color-scheme:light;
  --bg:#f3f4f7; --card:#ffffff; --line:#e4e7ec; --line2:#eef0f3; --panel:#f7f8fa;
  --shadow:0 1px 2px rgba(16,24,40,.05),0 8px 24px rgba(16,24,40,.06);
  --text:#0f1115; --muted:#667085; --dim:#8b93a1;
  --btn:#f2f4f7; --btnline:#d5d9e0;
  --tick:#e3e6eb; --tickmajor:#c3c9d2;
  --ink:#111827;
  --dlc:#0e7490; --ulc:#be185d;
  --g1:#2563eb;  --g2:#0891b2;
  --u1:#7c3aed;  --u2:#db2777;
  --tip:#0891b2; --tipu:#db2777;
  --ulnum1:#7c3aed; --ulnum2:#db2777;
  --err:#dc2626; --focus:#7c3aed;
}
*{margin:0;padding:0;box-sizing:border-box;font-family:Inter,"Noto Sans Arabic",system-ui,sans-serif}
html{background:var(--bg)}
body{background:var(--bg);color:var(--text);min-height:100vh;display:flex;flex-direction:column;transition:background-color .25s,color .25s}
html[dir="rtl"] *{letter-spacing:normal!important}      /* letter-spacing breaks Arabic/Persian letter joining */
.ltr{direction:ltr;unicode-bidi:isolate}                /* numbers + units always read left-to-right */
header{max-width:720px;width:100%;margin:0 auto;display:flex;justify-content:space-between;align-items:center;padding:18px 20px}
.brand{font-weight:800}
.ctl{display:flex;align-items:center;gap:8px}
.sel{background:var(--card);color:var(--text);border:1px solid var(--line);border-radius:10px;padding:8px 10px;font-size:12px;cursor:pointer;transition:background-color .25s,border-color .25s}
.ib{width:36px;height:36px;display:grid;place-items:center;background:var(--card);color:var(--text);border:1px solid var(--line);border-radius:10px;cursor:pointer;transition:background-color .25s,border-color .25s}
.sel:focus-visible,.ib:focus-visible,.go:focus-visible,.copy:focus-visible{outline:2px solid var(--focus);outline-offset:2px}
.i-moon{display:none}
:root[data-theme="light"] .i-sun{display:none}
:root[data-theme="light"] .i-moon{display:block}
.card{max-width:720px;width:92%;margin:10px auto;background:var(--card);border:1px solid var(--line);border-radius:24px;overflow:hidden;box-shadow:var(--shadow);transition:background-color .25s,border-color .25s}
.inner{padding:26px 28px}
.stats{display:flex;justify-content:space-between;gap:16px}
.stat small{display:block;font-size:10px;color:var(--muted);letter-spacing:.14em;font-weight:700;margin-bottom:6px;text-transform:uppercase}
.stat b{font-size:42px;font-weight:700;font-variant-numeric:tabular-nums;direction:ltr;unicode-bidi:isolate}
.stat b span{font-size:14px;color:var(--muted);margin-left:4px}
.stat.ulbox{text-align:end}
.stat.err b{font-size:20px;color:var(--err)}
.mid{display:flex;justify-content:center;flex-wrap:wrap;gap:28px;padding:14px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line);margin:16px 0;font-size:12px;color:var(--muted)}
.mid b{color:var(--text)}
#phase{color:var(--dlc);text-transform:uppercase}
.gauge{position:relative;width:min(400px,100%);aspect-ratio:1;margin:0 auto;direction:ltr}   /* the dial never mirrors */
.gauge svg{width:100%;height:100%;overflow:visible}
/* dial: ticks that light up, numbers that swell as the pointer passes, a peak marker */
.tb{stroke:var(--tick);stroke-width:3;stroke-linecap:round}
.tbm{stroke:var(--tickmajor);stroke-width:3.4;stroke-linecap:round}
.tl{stroke:url(#g);stroke-width:3.6;stroke-linecap:round}   /* opacity is set per frame from JS (a CSS value here would override it) */
.gauge.up .tl{stroke:url(#g2)}
.lab{font-size:14px;font-weight:700;fill:var(--ink);text-anchor:middle;font-variant-numeric:tabular-nums}
@keyframes labin{from{opacity:0}to{opacity:1}}
#labels.fade{animation:labin .35s ease}
.tip{fill:var(--tip)}
.gauge.up .tip{fill:var(--tipu)}
.ink{fill:var(--ink)}
.btnW{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%)}
.go{width:128px;height:128px;border-radius:50%;background:var(--btn);border:1.5px solid var(--btnline);color:var(--text);font-weight:700;font-size:20px;cursor:pointer;display:grid;place-items:center;text-transform:uppercase;transition:background-color .25s,border-color .25s}
.go:hover{border-color:var(--dlc)}
.status{position:absolute;left:50%;top:61%;transform:translateX(-50%);text-align:center;display:none;white-space:nowrap}
.status small{display:block;font-size:10px;color:var(--muted);letter-spacing:.14em;font-weight:700;text-transform:uppercase}
.status b{font-size:24px;font-variant-numeric:tabular-nums;direction:ltr;unicode-bidi:isolate}
.ul-num{background:linear-gradient(90deg,var(--ulnum1),var(--ulnum2));-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;color:transparent}
.stat.err .ul-num{-webkit-text-fill-color:var(--err);color:var(--err)}
.info{margin-top:14px;border:1px solid var(--line);border-radius:14px;overflow:hidden;font-size:12px}
.info .row{display:flex;justify-content:space-between;align-items:center;gap:14px;padding:10px 14px;border-bottom:1px solid var(--line2)}
.info .row:last-child{border-bottom:0}
.info .row span{color:var(--muted);flex:none}
.info .row b{font-weight:500;text-align:end;word-break:break-word;min-width:0}
.hint{font-size:10px;color:var(--dim);margin-top:6px;text-align:center}
.copy{display:block;width:100%;margin-top:14px;padding:13px;border-radius:14px;border:0;font-size:14px;font-weight:700;color:#fff;cursor:pointer;background:linear-gradient(90deg,var(--u1),var(--u2))}
.copy:disabled{opacity:.3;cursor:default}
.note{min-height:18px;text-align:center;font-size:12px;color:var(--err);margin-top:6px}
#diag summary{cursor:pointer;font-size:12px;color:var(--muted)}
.diagpre{margin-top:10px;padding:12px;background:var(--panel);border:1px solid var(--line);border-radius:12px;font-size:11px;line-height:1.6;color:var(--muted);white-space:pre-wrap;word-break:break-word;direction:ltr;text-align:left;unicode-bidi:isolate}
.dbtn{margin-top:8px;padding:6px 12px;font-size:11px;background:var(--btn);color:var(--text);border:1px solid var(--btnline);border-radius:8px;cursor:pointer}
.foot{padding:16px 28px;background:var(--panel);border-top:1px solid var(--line);display:flex;justify-content:space-between;font-size:11px;color:var(--muted);transition:background-color .25s,border-color .25s}
</style>
</head>
<body>
<header>
  <div class="brand">SPEEDTEST</div>
  <div class="ctl">
    <select id="langSel" class="sel" aria-label="Language">
      <option value="ar">العربية</option>
      <option value="en">English</option>
      <option value="tr">Türkçe</option>
      <option value="fr">Français</option>
      <option value="fa">فارسی</option>
    </select>
    <button id="themeBtn" class="ib" type="button" aria-label="Theme">
      <svg class="i-sun" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
      <svg class="i-moon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>
    </button>
  </div>
</header>
<div class="card">
  <div class="inner">
    <div class="stats">
      <div class="stat" id="dlBox"><small data-i18n="lbl.download">Download</small><b id="dl">—</b></div>
      <div class="stat ulbox" id="ulBox"><small data-i18n="lbl.upload">Upload</small><b id="ul" class="ul-num">—</b></div>
    </div>
    <div class="mid">
      <div><span data-i18n="lbl.ping">Ping</span> <span class="ltr"><b id="ping">—</b> ms</span></div>
      <div><span data-i18n="lbl.jitter">Jitter</span> <span class="ltr"><b id="jit">—</b> ms</span></div>
      <div><span id="phase">Idle</span></div>
    </div>
    <div class="gauge" id="gauge">
      <svg viewBox="0 0 400 400" aria-hidden="true">
        <defs>
          <linearGradient id="g"  gradientUnits="userSpaceOnUse" x1="60" y1="0" x2="340" y2="0"><stop offset="0%" style="stop-color:var(--g1)"/><stop offset="100%" style="stop-color:var(--g2)"/></linearGradient>
          <linearGradient id="g2" gradientUnits="userSpaceOnUse" x1="60" y1="0" x2="340" y2="0"><stop offset="0%" style="stop-color:var(--u1)"/><stop offset="100%" style="stop-color:var(--u2)"/></linearGradient>
          <filter id="glow" x="-150%" y="-150%" width="400%" height="400%"><feGaussianBlur stdDeviation="3.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
        </defs>
        <g id="ticksBase"></g>
        <g id="ticksLit"></g>
        <g id="labels"></g>
        <g id="peak" style="opacity:0;transition:opacity .3s"><path class="ink" d="M200 57 l-4.5 -8 h9 z"/></g>
        <g id="needle" transform="rotate(-135 200 200)">
          <path class="ink" d="M196 200 L204 200 L201.2 94 L198.8 94 Z"/>
          <circle class="tip" cx="200" cy="91" r="5" filter="url(#glow)"/>
        </g>
        <circle class="ink" cx="200" cy="200" r="9"/>
      </svg>
      <div class="btnW" id="btnW"><button id="go" class="go">Go</button></div>
      <div class="status" id="status"><small id="st">Ping</small><b id="sd">…</b></div>
    </div>
    <div class="note" id="note"></div>
    <div class="info">
      <div class="row"><span data-i18n="info.ip">IP address</span><b id="ipV" dir="ltr">…</b></div>
      <div class="row"><span data-i18n="info.isp">Provider (ISP)</span><b id="ispV" dir="ltr">…</b></div>
      <div class="row"><span data-i18n="info.loc">Location</span><b id="locV" dir="ltr">…</b></div>
      <div class="row"><span data-i18n="info.conn">Connection</span><b id="connV">…</b></div>
    </div>
    <div class="hint" id="connHint"></div>
    <button class="copy" id="copyBtn" disabled data-i18n="btn.copy">Copy result</button>
    <details id="diag" style="display:none;margin-top:14px">
      <summary data-i18n="diag.title">Test details</summary>
      <pre id="diagTxt" class="diagpre"></pre>
      <button id="diagCopy" class="dbtn" data-i18n="diag.copy">Copy details</button>
    </details>
  </div>
  <div class="foot"><div data-i18n="foot.left">Istanbul • 6 streams</div><div data-i18n="foot.right">Own server</div></div>
</div>
<script>
// ---------- settings ----------
const CFG = {
  streams: 6,            // parallel streams for download and upload
  dlBytes: 50e6,         // bytes per download request (stream restarts when done)
  ulMB: 8,               // MB per upload request
  minDur: 8000,          // ms: earliest a phase may stop (if speed is stable)
  maxDur: 15000,         // ms: hard stop per phase
  grace: 2500            // ms ignored at start (TCP slow-start + mobile radio ramp-up)
};

// ---------- languages ----------
// Every visible string lives here. Add a language = add one block + one <option> in the header.
const I18N = {
  en: {
    title:'Internet Speed Test', 'lbl.download':'Download', 'lbl.upload':'Upload', 'lbl.ping':'Ping', 'lbl.jitter':'Jitter',
    'btn.go':'Go', 'btn.again':'Again', 'btn.copy':'Copy result', 'btn.copied':'Copied ✓', 'btn.copyfail':'Copy failed',
    'info.ip':'IP address', 'info.isp':'Provider (ISP)', 'info.loc':'Location', 'info.conn':'Connection',
    'info.unavailable':'unavailable', 'info.unknown':'unknown',
    'diag.title':'Test details', 'diag.copy':'Copy details', 'diag.copied':'Copied', 'diag.manual':'Select the text and copy manually',
    'foot.left':'Istanbul • 6 streams', 'foot.right':'Own server',
    'aria.lang':'Language', 'aria.toLight':'Switch to light mode', 'aria.toDark':'Switch to dark mode',
    'phase.IDLE':'Idle', 'phase.PING':'Ping', 'phase.DOWNLOAD':'Download', 'phase.UPLOAD':'Upload', 'phase.DONE':'Done',
    'err.label':'Error', 'err.nodata':'no data transferred', 'err.network':'network error',
    'note.dlfail':'Download failed: {msg}', 'note.ulfail':'Upload failed: {msg}', 'note.test':'Test error: {msg}',
    'res.title':'Speedtest', 'res.failed':'failed',
    'conn.cell':'Mobile data', 'conn.wifi':'Wi-Fi', 'conn.eth':'Cable (Ethernet)', 'conn.wifiOrCable':'Wi-Fi or Cable',
    'conn.cellProb':'Mobile data (probably)', 'conn.unknown':'Unknown',
    'how.device':'Detected from your device', 'how.adapter':"Detected from your device's network adapter",
    'how.prov':'Your provider runs a mobile network',
    'how.phoneWifi':'Your provider is not a mobile network, so this phone or tablet is on Wi-Fi',
    'how.noTell':'This browser cannot tell Wi-Fi from cable on a computer',
    'how.name':'Guessed from the provider name', 'how.unknown':'Could not be detected', 'how.unknownWhy':'Could not be detected ({why})',
    'dg.proto':'Protocol', 'dg.streams':'Streams', 'dg.grace':'warm-up', 'dg.persec':'per second', 'dg.net':'Network',
    'dg.adapters':'Adapters', 'dg.browser':'Browser', 'dg.na':'n/a (no request finished)'
  },
  ar: {
    title:'فحص سرعة الإنترنت', 'lbl.download':'التنزيل', 'lbl.upload':'الرفع', 'lbl.ping':'البنق', 'lbl.jitter':'التذبذب',
    'btn.go':'ابدأ', 'btn.again':'إعادة', 'btn.copy':'نسخ النتيجة', 'btn.copied':'تم النسخ ✓', 'btn.copyfail':'تعذّر النسخ',
    'info.ip':'عنوان IP', 'info.isp':'مزوّد الخدمة', 'info.loc':'الموقع', 'info.conn':'نوع الاتصال',
    'info.unavailable':'غير متاح', 'info.unknown':'غير معروف',
    'diag.title':'تفاصيل الاختبار', 'diag.copy':'نسخ التفاصيل', 'diag.copied':'تم النسخ', 'diag.manual':'حدّد النص وانسخه يدوياً',
    'foot.left':'إسطنبول • 6 مسارات', 'foot.right':'خادم خاص',
    'aria.lang':'اللغة', 'aria.toLight':'التبديل إلى الوضع الفاتح', 'aria.toDark':'التبديل إلى الوضع الداكن',
    'phase.IDLE':'جاهز', 'phase.PING':'قياس البنق', 'phase.DOWNLOAD':'التنزيل', 'phase.UPLOAD':'الرفع', 'phase.DONE':'اكتمل',
    'err.label':'خطأ', 'err.nodata':'لم تُنقل أي بيانات', 'err.network':'خطأ في الشبكة',
    'note.dlfail':'فشل التنزيل: {msg}', 'note.ulfail':'فشل الرفع: {msg}', 'note.test':'خطأ في الاختبار: {msg}',
    'res.title':'فحص السرعة', 'res.failed':'فشل',
    'conn.cell':'بيانات الهاتف', 'conn.wifi':'واي فاي (Wi-Fi)', 'conn.eth':'كيبل (Ethernet)', 'conn.wifiOrCable':'واي فاي أو كيبل',
    'conn.cellProb':'بيانات الهاتف (غالباً)', 'conn.unknown':'غير معروف',
    'how.device':'تم اكتشافه من جهازك', 'how.adapter':'تم اكتشافه من كرت الشبكة في جهازك',
    'how.prov':'مزوّد الخدمة لديك شبكة هاتف محمول',
    'how.phoneWifi':'مزوّد الخدمة ليس شبكة هاتف محمول، لذلك هذا الهاتف أو الجهاز اللوحي على واي فاي',
    'how.noTell':'هذا المتصفح لا يميّز بين الواي فاي والكيبل على الكمبيوتر',
    'how.name':'تخمين من اسم مزوّد الخدمة', 'how.unknown':'تعذّر الاكتشاف', 'how.unknownWhy':'تعذّر الاكتشاف ({why})',
    'dg.proto':'البروتوكول', 'dg.streams':'المسارات', 'dg.grace':'فترة التهيئة', 'dg.persec':'لكل ثانية', 'dg.net':'الشبكة',
    'dg.adapters':'المحوّلات', 'dg.browser':'المتصفح', 'dg.na':'غير متاح (لم يكتمل أي طلب)'
  },
  tr: {
    title:'İnternet Hız Testi', 'lbl.download':'İndirme', 'lbl.upload':'Yükleme', 'lbl.ping':'Ping', 'lbl.jitter':'Titreşim',
    'btn.go':'Başla', 'btn.again':'Tekrar', 'btn.copy':'Sonucu kopyala', 'btn.copied':'Kopyalandı ✓', 'btn.copyfail':'Kopyalanamadı',
    'info.ip':'IP adresi', 'info.isp':'Servis sağlayıcı', 'info.loc':'Konum', 'info.conn':'Bağlantı',
    'info.unavailable':'kullanılamıyor', 'info.unknown':'bilinmiyor',
    'diag.title':'Test ayrıntıları', 'diag.copy':'Ayrıntıları kopyala', 'diag.copied':'Kopyalandı', 'diag.manual':'Metni seçip elle kopyalayın',
    'foot.left':'İstanbul • 6 akış', 'foot.right':'Özel sunucu',
    'aria.lang':'Dil', 'aria.toLight':'Açık moda geç', 'aria.toDark':'Koyu moda geç',
    'phase.IDLE':'Hazır', 'phase.PING':'Ping ölçülüyor', 'phase.DOWNLOAD':'İndirme', 'phase.UPLOAD':'Yükleme', 'phase.DONE':'Tamamlandı',
    'err.label':'Hata', 'err.nodata':'veri aktarılmadı', 'err.network':'ağ hatası',
    'note.dlfail':'İndirme başarısız: {msg}', 'note.ulfail':'Yükleme başarısız: {msg}', 'note.test':'Test hatası: {msg}',
    'res.title':'Hız testi', 'res.failed':'başarısız',
    'conn.cell':'Mobil veri', 'conn.wifi':'Wi-Fi', 'conn.eth':'Kablo (Ethernet)', 'conn.wifiOrCable':'Wi-Fi veya kablo',
    'conn.cellProb':'Mobil veri (muhtemelen)', 'conn.unknown':'Bilinmiyor',
    'how.device':'Cihazınızdan algılandı', 'how.adapter':'Cihazınızın ağ bağdaştırıcısından algılandı',
    'how.prov':'Servis sağlayıcınız bir mobil ağ işletiyor',
    'how.phoneWifi':'Servis sağlayıcınız mobil ağ değil, bu yüzden bu telefon veya tablet Wi-Fi üzerinde',
    'how.noTell':'Bu tarayıcı bilgisayarda Wi-Fi ile kabloyu ayırt edemez',
    'how.name':'Servis sağlayıcı adından tahmin edildi', 'how.unknown':'Algılanamadı', 'how.unknownWhy':'Algılanamadı ({why})',
    'dg.proto':'Protokol', 'dg.streams':'Akış', 'dg.grace':'ısınma', 'dg.persec':'saniyede', 'dg.net':'Ağ',
    'dg.adapters':'Bağdaştırıcılar', 'dg.browser':'Tarayıcı', 'dg.na':'yok (hiçbir istek tamamlanmadı)'
  },
  fr: {
    title:'Test de débit Internet', 'lbl.download':'Téléchargement', 'lbl.upload':'Envoi', 'lbl.ping':'Ping', 'lbl.jitter':'Gigue',
    'btn.go':'Démarrer', 'btn.again':'Relancer', 'btn.copy':'Copier le résultat', 'btn.copied':'Copié ✓', 'btn.copyfail':'Échec de la copie',
    'info.ip':'Adresse IP', 'info.isp':'Fournisseur (FAI)', 'info.loc':'Localisation', 'info.conn':'Connexion',
    'info.unavailable':'indisponible', 'info.unknown':'inconnu',
    'diag.title':'Détails du test', 'diag.copy':'Copier les détails', 'diag.copied':'Copié', 'diag.manual':'Sélectionnez le texte et copiez-le à la main',
    'foot.left':'Istanbul • 6 flux', 'foot.right':'Serveur dédié',
    'aria.lang':'Langue', 'aria.toLight':'Passer en mode clair', 'aria.toDark':'Passer en mode sombre',
    'phase.IDLE':'Prêt', 'phase.PING':'Mesure du ping', 'phase.DOWNLOAD':'Téléchargement', 'phase.UPLOAD':'Envoi', 'phase.DONE':'Terminé',
    'err.label':'Erreur', 'err.nodata':'aucune donnée transférée', 'err.network':'erreur réseau',
    'note.dlfail':'Échec du téléchargement : {msg}', 'note.ulfail':"Échec de l'envoi : {msg}", 'note.test':'Erreur du test : {msg}',
    'res.title':'Test de débit', 'res.failed':'échec',
    'conn.cell':'Données mobiles', 'conn.wifi':'Wi-Fi', 'conn.eth':'Câble (Ethernet)', 'conn.wifiOrCable':'Wi-Fi ou câble',
    'conn.cellProb':'Données mobiles (probablement)', 'conn.unknown':'Inconnu',
    'how.device':'Détecté depuis votre appareil', 'how.adapter':"Détecté depuis la carte réseau de votre appareil",
    'how.prov':'Votre fournisseur exploite un réseau mobile',
    'how.phoneWifi':"Votre fournisseur n'est pas un réseau mobile : ce téléphone ou cette tablette est donc en Wi-Fi",
    'how.noTell':'Ce navigateur ne distingue pas le Wi-Fi du câble sur un ordinateur',
    'how.name':'Déduit du nom du fournisseur', 'how.unknown':'Détection impossible', 'how.unknownWhy':'Détection impossible ({why})',
    'dg.proto':'Protocole', 'dg.streams':'Flux', 'dg.grace':'préchauffage', 'dg.persec':'par seconde', 'dg.net':'Réseau',
    'dg.adapters':'Adaptateurs', 'dg.browser':'Navigateur', 'dg.na':'n/d (aucune requête terminée)'
  },
  fa: {
    title:'تست سرعت اینترنت', 'lbl.download':'دانلود', 'lbl.upload':'آپلود', 'lbl.ping':'پینگ', 'lbl.jitter':'جیتر',
    'btn.go':'شروع', 'btn.again':'دوباره', 'btn.copy':'کپی نتیجه', 'btn.copied':'کپی شد ✓', 'btn.copyfail':'کپی ناموفق بود',
    'info.ip':'آدرس IP', 'info.isp':'ارائه‌دهنده (ISP)', 'info.loc':'موقعیت', 'info.conn':'نوع اتصال',
    'info.unavailable':'در دسترس نیست', 'info.unknown':'نامشخص',
    'diag.title':'جزئیات تست', 'diag.copy':'کپی جزئیات', 'diag.copied':'کپی شد', 'diag.manual':'متن را انتخاب و دستی کپی کنید',
    'foot.left':'استانبول • 6 جریان', 'foot.right':'سرور اختصاصی',
    'aria.lang':'زبان', 'aria.toLight':'تغییر به حالت روشن', 'aria.toDark':'تغییر به حالت تیره',
    'phase.IDLE':'آماده', 'phase.PING':'اندازه‌گیری پینگ', 'phase.DOWNLOAD':'دانلود', 'phase.UPLOAD':'آپلود', 'phase.DONE':'پایان',
    'err.label':'خطا', 'err.nodata':'داده‌ای منتقل نشد', 'err.network':'خطای شبکه',
    'note.dlfail':'دانلود ناموفق بود: {msg}', 'note.ulfail':'آپلود ناموفق بود: {msg}', 'note.test':'خطای تست: {msg}',
    'res.title':'تست سرعت', 'res.failed':'ناموفق',
    'conn.cell':'داده همراه', 'conn.wifi':'وای‌فای (Wi-Fi)', 'conn.eth':'کابل (Ethernet)', 'conn.wifiOrCable':'وای‌فای یا کابل',
    'conn.cellProb':'داده همراه (احتمالاً)', 'conn.unknown':'نامشخص',
    'how.device':'از روی دستگاه شما تشخیص داده شد', 'how.adapter':'از روی کارت شبکه دستگاه شما تشخیص داده شد',
    'how.prov':'ارائه‌دهنده شما یک شبکه تلفن همراه است',
    'how.phoneWifi':'ارائه‌دهنده شما شبکه تلفن همراه نیست، بنابراین این گوشی یا تبلت روی وای‌فای است',
    'how.noTell':'این مرورگر در کامپیوتر نمی‌تواند وای‌فای را از کابل تشخیص دهد',
    'how.name':'حدس از روی نام ارائه‌دهنده', 'how.unknown':'تشخیص ممکن نبود', 'how.unknownWhy':'تشخیص ممکن نبود ({why})',
    'dg.proto':'پروتکل', 'dg.streams':'جریان‌ها', 'dg.grace':'گرم‌کردن', 'dg.persec':'در هر ثانیه', 'dg.net':'شبکه',
    'dg.adapters':'آداپتورها', 'dg.browser':'مرورگر', 'dg.na':'موجود نیست (هیچ درخواستی کامل نشد)'
  }
};
const RTL = {ar:true, fa:true};
const LOCALE = {en:'en-GB', ar:'ar-u-nu-latn', tr:'tr-TR', fr:'fr-FR', fa:'fa-IR-u-nu-latn'};   // Latin digits everywhere, like the dial
let lang = 'en';
const t = (k, v) => {
  let s = (I18N[lang] && I18N[lang][k]) || I18N.en[k] || k;
  if (v) for (const n in v) s = s.split('{' + n + '}').join(v[n]);
  return s;
};
function pickLang(){
  let l = null;
  try { l = new URLSearchParams(location.search).get('lang'); } catch(e) {}
  if (!I18N[l]) { l = null; try { l = localStorage.getItem('st_lang'); } catch(e) {} }
  if (!I18N[l]) { l = null; for (const n of (navigator.languages || [navigator.language || 'en'])) { const c = String(n).slice(0, 2).toLowerCase(); if (I18N[c]) { l = c; break; } } }
  return I18N[l] ? l : 'en';
}

// ---------- theme ----------
const root = document.documentElement;
function applyTheme(th, save){
  root.setAttribute('data-theme', th);
  const m = document.querySelector('meta[name="theme-color"]'); if (m) m.setAttribute('content', th === 'light' ? '#f3f4f7' : '#0a0a0a');
  if (save){ try { localStorage.setItem('st_theme', th); } catch(e) {} }
  const b = $('themeBtn'); if (b){ const s = t(th === 'light' ? 'aria.toDark' : 'aria.toLight'); b.setAttribute('aria-label', s); b.title = s; }
}

// ---------- UI ----------
const $ = id => document.getElementById(id);
const E = {dl:$('dl'), ul:$('ul'), ping:$('ping'), jit:$('jit'), phase:$('phase'),
  go:$('go'), btnW:$('btnW'), status:$('status'), st:$('st'), sd:$('sd'), note:$('note'),
  dlBox:$('dlBox'), ulBox:$('ulBox')};
let cur=-135, tar=-135, shown={dl:0, ul:0}, target={dl:0, ul:0}, testing=false;
let phaseCode = 'IDLE', goKey = 'btn.go', noteState = null, errs = {dl:null, ul:null};

// ---------- the dial ----------
// Numbers sit on the outer ring at the SAME angles the pointer uses, so the pointer always aims at the
// number of the real speed. The scale is a square-root curve (low speeds get room) and it re-ranges
// by itself: when the speed nears the top of the dial, the whole dial grows to the next range.
const NS = 'http://www.w3.org/2000/svg', CX = 200;
const A0 = -135, SPAN = 270, STEP = 5, NT = SPAN / STEP + 1;       // 55 ticks, one every 5 degrees
const R_IN = 112, R_OUT = 128, R_LAB = 162;
const RANGES = [
  {max: 50,   labels: [0, 2, 5, 10, 20, 30, 40, 50]},
  {max: 100,  labels: [0, 5, 10, 20, 30, 50, 75, 100]},
  {max: 250,  labels: [0, 5, 10, 25, 50, 100, 150, 200, 250]},
  {max: 500,  labels: [0, 10, 25, 50, 100, 200, 300, 400, 500]},
  {max: 1000, labels: [0, 25, 100, 200, 400, 600, 800, 1000]}
];
let rangeIdx = 1, peakVal = 0, peakTar = A0, peakCur = A0, needsDraw = true;
const pol = (r, deg) => [CX + r * Math.sin(deg * Math.PI / 180), CX - r * Math.cos(deg * Math.PI / 180)];
const angleOf = v => A0 + SPAN * Math.sqrt(Math.min(1, Math.max(0, v / RANGES[rangeIdx].max)));
const needleG = $('needle'), peakG = $('peak'), labelsG = $('labels');

const ticks = [];
for (let i = 0; i < NT; i++){
  const a = A0 + i * STEP, major = i % 9 === 0;
  const [x1, y1] = pol(major ? R_IN - 3 : R_IN, a), [x2, y2] = pol(major ? R_OUT + 2 : R_OUT, a);
  const base = document.createElementNS(NS, 'line');
  base.setAttribute('class', major ? 'tbm' : 'tb');
  for (const [k, v] of [['x1', x1], ['y1', y1], ['x2', x2], ['y2', y2]]) base.setAttribute(k, v.toFixed(2));
  $('ticksBase').appendChild(base);
  const [lx1, ly1] = pol(R_IN, a), [lx2, ly2] = pol(R_OUT, a);
  const lit = document.createElementNS(NS, 'line');
  lit.setAttribute('class', 'tl'); lit.setAttribute('stroke-opacity', '0');
  for (const [k, v] of [['x1', lx1], ['y1', ly1], ['x2', lx2], ['y2', ly2]]) lit.setAttribute(k, v.toFixed(2));
  $('ticksLit').appendChild(lit);
  ticks.push({a, l: lit, op: 0, len: R_OUT});
}

let labs = [];
function buildLabels(){
  labelsG.textContent = ''; labs = [];
  for (const v of RANGES[rangeIdx].labels){
    const a = angleOf(v), [x, y] = pol(R_LAB, a);
    const t = document.createElementNS(NS, 'text');
    t.setAttribute('class', 'lab'); t.setAttribute('dy', '.35em'); t.textContent = v;
    labelsG.appendChild(t); labs.push({a, x, y, t});
  }
  labelsG.classList.remove('fade'); void labelsG.getBoundingClientRect(); labelsG.classList.add('fade');
  needsDraw = true;
}

function setGauge(mbps){
  const v = Math.max(0, mbps);
  while (rangeIdx < RANGES.length - 1 && v > RANGES[rangeIdx].max * 0.92){ rangeIdx++; buildLabels(); }
  if (v > peakVal) peakVal = v;
  tar = angleOf(v);                                     // only TARGETS are set here; render() eases toward them
  peakTar = peakVal > 0 ? angleOf(peakVal) : A0;
}
// new phase: forget the peak and pick the smallest range that fits what we expect
function gaugeReset(expected){
  peakVal = 0;
  let i = 1;
  while (i < RANGES.length - 1 && RANGES[i].max * 0.92 < expected) i++;
  if (i !== rangeIdx){ rangeIdx = i; buildLabels(); }
  setGauge(0);
}

function draw(){
  needleG.setAttribute('transform', `rotate(${cur.toFixed(2)} ${CX} ${CX})`);
  for (const t of ticks){
    const op = Math.min(1, Math.max(0, (cur - t.a) / STEP));          // lit up to exactly where the pointer is
    const d = Math.abs(t.a - cur);
    const len = R_OUT + (op > 0 ? 10 * Math.exp(-(d / 11) * (d / 11)) : 0);   // ticks swell just behind the pointer
    if (op !== t.op){ t.l.setAttribute('stroke-opacity', op.toFixed(3)); t.op = op; }
    if (Math.abs(len - t.len) > 0.05){
      const [x2, y2] = pol(len, t.a);
      t.l.setAttribute('x2', x2.toFixed(2)); t.l.setAttribute('y2', y2.toFixed(2)); t.len = len;
    }
  }
  for (const L of labs){                                              // the number under the pointer swells and glows
    const d = Math.abs(L.a - cur);
    const s = 1 + 0.6 * Math.exp(-(d / 16) * (d / 16));
    const o = 0.3 + 0.7 * Math.exp(-(d / 22) * (d / 22));
    L.t.setAttribute('transform', `translate(${L.x.toFixed(1)} ${L.y.toFixed(1)}) scale(${s.toFixed(3)})`);
    L.t.setAttribute('opacity', o.toFixed(2));
  }
  peakG.setAttribute('transform', `rotate(${peakCur.toFixed(2)} ${CX} ${CX})`);
  peakG.style.opacity = peakVal > 0 ? '1' : '0';
}

function fmt(v){ return v >= 100 ? v.toFixed(0) : v.toFixed(1); }
let lastFrame = performance.now(), drawnCur = NaN, drawnPeak = NaN;
function render(now){
  // Time-based easing: same feel at 30, 60 or 120 fps (phones differ), no frame-rate dependent lag.
  const dt = Math.min(0.1, Math.max(0, ((now || performance.now()) - lastFrame) / 1000));
  lastFrame = now || performance.now();
  cur     += (tar     - cur)     * (1 - Math.exp(-dt * 7));
  peakCur += (peakTar - peakCur) * (1 - Math.exp(-dt * 5));
  // Pointer, lit ticks and numbers are all drawn from the same animated value in the same frame,
  // so they can never drift apart. Nothing is redrawn while the dial is at rest.
  if (needsDraw || Math.abs(cur - drawnCur) > 0.004 || Math.abs(peakCur - drawnPeak) > 0.004){
    draw(); drawnCur = cur; drawnPeak = peakCur; needsDraw = false;
  }
  for (const k of ['dl','ul']){
    if (target[k] > 0){
      shown[k] += (target[k] - shown[k]) * (1 - Math.exp(-dt * 8));
      E[k].innerHTML = fmt(shown[k]) + '<span>Mbps</span>';
    }
  }
  requestAnimationFrame(render);
}
buildLabels();
requestAnimationFrame(render);
const sleep = ms => new Promise(r => setTimeout(r, ms));
function setPhase(code){
  phaseCode = code;
  E.phase.dataset.code = code;                       // internal code (stays English) - handy for tests and styling
  E.phase.textContent = t('phase.' + code); E.st.textContent = t('phase.' + code);
  const up = code === 'UPLOAD';
  E.phase.style.color = up ? 'var(--ulc)' : 'var(--dlc)';
  $('gauge').classList.toggle('up', up);
}
const errText = m => m === 'no data transferred' ? t('err.nodata') : m === 'network error' ? t('err.network') : m;
function paintNote(){
  if (!noteState){ E.note.textContent = ''; return; }
  if (noteState.kind === 'test') E.note.textContent = t('note.test', {msg: noteState.msg});
  else E.note.textContent = t(noteState.kind === 'dl' ? 'note.dlfail' : 'note.ulfail', {msg: errText(noteState.msg)});
}
function paintErrors(){
  for (const k of ['dl','ul']) if (errs[k]) E[k].textContent = t('err.label');
}
function showError(k, msg){
  target[k] = 0;
  errs[k] = msg;
  E[k+'Box'].classList.add('err');
  noteState = {kind: k, msg};
  paintErrors(); paintNote();
}

// ---------- ping ----------
async function pingTest(){
  setPhase('PING'); E.sd.textContent = '…';
  const times = [];
  for (let i=0; i<10; i++){
    const s = performance.now();
    try {
      const r = await fetch('/ping?r=' + Math.random(), {cache:'no-store'});
      await r.text();
      if (r.ok) times.push(performance.now() - s);
    } catch(e) {}
    if (times.length) E.ping.textContent = Math.round(Math.min(...times));
    await sleep(60);
  }
  if (!times.length){ E.ping.textContent = '—'; return; }
  const valid = times.slice(1);                         // first request pays the TLS/connection setup
  const use = valid.length ? valid : times;
  let j = 0; for (let i=1; i<use.length; i++) j += Math.abs(use[i]-use[i-1]);   // jitter in the order measured
  E.ping.textContent = Math.round(Math.min(...use));
  E.jit.textContent = use.length > 1 ? Math.round(j/(use.length-1)) : 0;
}

// ---------- shared measuring loop ----------
// startStream(ctx) runs one connection that keeps re-requesting until ctx.done.
function measure(kind, startStream){
  return new Promise(resolve => {
    const ctx = {
      bytes: 0, done: false, errors: 0, lastError: '', live: new Set(),
      add(n){ this.bytes += n; },
      fail(msg){ this.errors++; this.lastError = msg; }
    };
    const t0 = performance.now();
    let gT = 0, gB = 0, mbps = 0, sT = 0, sB = 0;
    const hist = [];                    // [time, bytes] over the last ~1.5 s -> smooth live speed for the gauge
    let liveS = 0;                      // extra smoothing on top of the window (removes bursty-progress wobble)
    const samples = [];                 // Mbps per ~1 s window, after the grace period
    for (let i=0; i<CFG.streams; i++) setTimeout(() => { if (!ctx.done) startStream(ctx); }, i*120);

    const iv = setInterval(() => {
      const now = performance.now(), el = now - t0;
      if (!gT && el >= CFG.grace){ gT = now; gB = ctx.bytes; sT = now; sB = ctx.bytes; }
      if (gT && now - sT >= 1000){
        samples.push((ctx.bytes - sB) * 8 / ((now - sT) / 1000) / 1e6);
        sT = now; sB = ctx.bytes;
      }
      if (gT && now - gT > 250) mbps = (ctx.bytes - gB) * 8 / ((now - gT) / 1000) / 1e6;
      else if (el > 250)        mbps = ctx.bytes * 8 / (el / 1000) / 1e6;
      // Gauge shows a short sliding-window rate (smooth, no jump when the grace period ends);
      // the final number is still the grace-to-end average computed above in `mbps`.
      hist.push([now, ctx.bytes]);
      while (hist.length > 2 && now - hist[0][0] > 3000) hist.shift();
      const span = now - hist[0][0];
      const live = span >= 400 ? (ctx.bytes - hist[0][1]) * 8 / (span / 1000) / 1e6 : 0;
      if (live > 0){
        liveS = liveS ? liveS + (live - liveS) * 0.12 : live;
        target[kind] = liveS; setGauge(liveS); E.sd.textContent = fmt(liveS) + ' Mbps';
      }

      // stop early once the last 3 one-second samples agree within 8%
      let stable = false;
      if (el >= CFG.minDur && samples.length >= 3){
        const l = samples.slice(-3), mx = Math.max(...l), mn = Math.min(...l);
        stable = mx > 0 && (mx - mn) / mx < 0.08;
      }
      const hopeless = ctx.bytes === 0 && ctx.errors >= CFG.streams * 3;
      if (el >= CFG.maxDur || stable || hopeless){
        ctx.done = true; clearInterval(iv);
        ctx.live.forEach(h => { try { h.abort(); } catch(e){} });
        resolve({mbps: ctx.bytes > 0 ? mbps : 0, bytes: ctx.bytes, samples, secs: el/1000,
                 error: ctx.bytes > 0 ? '' : (ctx.lastError || 'no data transferred')});
      }
    }, 100);
  });
}

// ---------- download: fetch + streamed reader ----------
function dlStream(ctx){
  (async () => {
    while (!ctx.done){
      const ac = new AbortController(); ctx.live.add(ac);
      try {
        const r = await fetch(`/download?bytes=${CFG.dlBytes}&r=${Math.random()}`, {cache:'no-store', signal: ac.signal});
        if (!r.ok){ ctx.fail('HTTP ' + r.status); await sleep(300); continue; }
        const rd = r.body.getReader();
        for (;;){ const {done, value} = await rd.read(); if (done) break; ctx.add(value.length); }
      } catch(e){
        if (!ctx.done){ ctx.fail(e.message || 'network error'); await sleep(300); }
      } finally { ctx.live.delete(ac); }
    }
  })();
}

// ---------- upload: XHR so we can count bytes as they leave the browser ----------
let ulBlob = null;
function makeUploadBlob(){
  // crypto.getRandomValues() accepts at most 65,536 bytes per call -> fill 1 MB in 64 KB slices.
  // (Passing 1 MB in one call throws QuotaExceededError — that was the old upload bug.)
  const mb = new Uint8Array(1024*1024);
  for (let o=0; o<mb.length; o+=65536) crypto.getRandomValues(mb.subarray(o, o+65536));
  return new Blob(Array(CFG.ulMB).fill(mb), {type:'application/octet-stream'});
}
function ulStream(ctx){
  const once = () => {
    if (ctx.done) return;
    const x = new XMLHttpRequest();
    let sent = 0;
    ctx.live.add(x);
    x.upload.onprogress = e => { if (e.loaded > sent){ ctx.add(e.loaded - sent); sent = e.loaded; } };
    x.onload = () => {
      ctx.live.delete(x);
      if (x.status >= 200 && x.status < 300){
        if (ulBlob.size > sent) ctx.add(ulBlob.size - sent);
        once();
      } else {
        ctx.fail('HTTP ' + x.status);
        setTimeout(once, 300);
      }
    };
    x.onerror = () => { ctx.live.delete(x); if (!ctx.done){ ctx.fail('network error'); setTimeout(once, 300); } };
    x.open('POST', '/upload?r=' + Math.random(), true);
    x.send(ulBlob);
  };
  once();
}

// ---------- visitor info (IP / ISP / location / connection type) + copy ----------
const copyBtn = $('copyBtn');
let visitor = {ip:'', isp:'', city:'', country:'', mobile:null, via:'', note:''};
let lastResult = null;
let conn = {key:'conn.unknown', how:'how.unknown', vars:null};

// Connection type is worked out automatically; the visitor never has to choose. Sources, best first:
//  1. navigator.connection.type      (Android Chrome)
//  2. WebRTC adapter type            (Chrome / Edge on desktop and Android: "wifi", "ethernet", "cellular")
//  3. provider's "mobile network" flag from /info + kind of device   (works in Safari too)
//  4. guess from the provider name
// A web page can never read the Wi-Fi NAME (SSID). Safari and Firefox do not expose the adapter type, so
// on a computer there they can only say "Wi-Fi or Cable".
async function rtcNetworkTypes(){
  if (!window.RTCPeerConnection) return null;
  let pc;
  try {
    pc = new RTCPeerConnection({iceServers: []});           // no STUN server: nothing leaves the browser
    pc.createDataChannel('x');
    const gathered = new Promise(res => {
      const t = setTimeout(res, 2000);
      pc.addEventListener('icegatheringstatechange', () => { if (pc.iceGatheringState === 'complete'){ clearTimeout(t); res(); } });
    });
    await pc.setLocalDescription(await pc.createOffer());
    await gathered;
    const types = [];
    (await pc.getStats()).forEach(s => { if (s.type === 'local-candidate' && s.networkType) types.push(s.networkType); });
    window.__rtc = types;                                     // shown in "Test details" to help verify on real devices
    return types;                                             // only the adapter TYPE is read, never an address
  } catch(e) { return null; }
  finally { try { pc && pc.close(); } catch(e) {} }
}
const RTC_LABEL = {wifi:'conn.wifi', ethernet:'conn.eth', cellular:'conn.cell'};

async function detectConn(){
  // returns translation KEYS (not text) so the answer can be re-shown in another language without re-detecting
  const c = navigator.connection;
  if (c && c.type === 'cellular') return {key:'conn.cell', how:'how.device'};
  if (c && c.type === 'wifi')     return {key:'conn.wifi', how:'how.device'};
  if (c && c.type === 'ethernet') return {key:'conn.eth',  how:'how.device'};
  // "vpn", "unknown", "bluetooth" adapters are ignored; if exactly one real adapter type is left, that is the answer
  const types = [...new Set((await rtcNetworkTypes()) || [])].filter(x => RTC_LABEL[x]);
  if (types.length === 1) return {key: RTC_LABEL[types[0]], how:'how.adapter'};
  const ua = navigator.userAgent || '';
  const phone = /iPhone|iPad|iPod|Android|Mobile/i.test(ua) || (/Macintosh/.test(ua) && navigator.maxTouchPoints > 1);
  if (visitor.mobile === true)  return {key:'conn.cell', how:'how.prov'};
  if (visitor.mobile === false) return phone
    ? {key:'conn.wifi',        how:'how.phoneWifi'}
    : {key:'conn.wifiOrCable', how:'how.noTell'};
  if (/mobile|mobil|cellular|wireless|gsm|lte/i.test(visitor.isp || ''))
    return {key:'conn.cellProb', how:'how.name'};
  const why = visitor.note || (visitor.via ? 'data from ' + visitor.via + ' has no mobile flag' : '');   // technical reason, kept as-is
  return {key:'conn.unknown', how: why ? 'how.unknownWhy' : 'how.unknown', vars: why ? {why} : null};
}
function paintConn(){
  $('connV').textContent = t(conn.key);
  $('connHint').textContent = t(conn.how, conn.vars) + '.';
}
let detecting = false, rerun = false, infoReady = false;
async function renderConn(){
  if (detecting){ rerun = true; return; }                     // a newer trigger (e.g. /info arrived) re-runs afterwards
  detecting = true;
  try {
    do {
      rerun = false;
      conn = await detectConn();
      if (!infoReady && conn.key === 'conn.unknown') continue;   // don't flash "Unknown" while /info is still loading
      paintConn();
    } while (rerun);
  } finally { detecting = false; }
}
if (navigator.connection && navigator.connection.addEventListener) navigator.connection.addEventListener('change', renderConn);
renderConn();                                                  // start adapter detection right away, in parallel with /info

let infoLoaded = false;
function paintInfo(){
  if (!infoLoaded) return;                                   // keep the "…" placeholders until /info answered
  const loc = [visitor.city, visitor.country].filter(Boolean).join(', ');
  $('ipV').textContent  = visitor.ip  || t('info.unavailable');
  $('ispV').textContent = visitor.isp || t(visitor.ip ? 'info.unknown' : 'info.unavailable');
  $('locV').textContent = loc || t(visitor.ip ? 'info.unknown' : 'info.unavailable');
}
(async function loadInfo(){
  try {
    const r = await fetch('/info', {cache:'no-store'});
    visitor = await r.json();
  } catch(e) {}
  infoReady = true; infoLoaded = true;
  paintInfo();
  renderConn();
})();

function resultText(){
  const r = lastResult;
  const loc = [visitor.city, visitor.country].filter(Boolean).join(', ');
  const when = new Date(r.ts).toLocaleString(LOCALE[lang] || undefined);
  return [
    `${t('res.title')} - ${when}`,
    `${t('lbl.download')}: ${r.dl ? fmt(r.dl) + ' Mbps' : t('res.failed')}`,
    `${t('lbl.upload')}: ${r.ul ? fmt(r.ul) + ' Mbps' : t('res.failed')}`,
    `${t('lbl.ping')}: ${r.ping} ms | ${t('lbl.jitter')}: ${r.jit} ms`,
    `${t('info.ip')}: ${visitor.ip || '-'}`,
    `${t('info.isp')}: ${visitor.isp || '-'}`,
    `${t('info.loc')}: ${loc || '-'}`,
    `${t('info.conn')}: ${t(conn.key)}`
  ].join('\n');
}
async function copyText(txt){
  try { await navigator.clipboard.writeText(txt); return true; } catch(e) {}
  try {                                                    // fallback for older Safari / non-secure pages
    const ta = document.createElement('textarea');
    ta.value = txt; ta.setAttribute('readonly', ''); ta.style.cssText = 'position:fixed;top:0;left:0;opacity:0';
    document.body.appendChild(ta); ta.select(); ta.setSelectionRange(0, txt.length);
    const ok = document.execCommand('copy'); document.body.removeChild(ta); return ok;
  } catch(e) { return false; }
}
copyBtn.onclick = async () => {
  if (!lastResult) return;
  const ok = await copyText(resultText());
  copyBtn.textContent = t(ok ? 'btn.copied' : 'btn.copyfail');
  setTimeout(() => { copyBtn.textContent = t('btn.copy'); }, 2000);
};

// ---------- diagnostics ----------
let lastDiag = null;
function showDiag(dl, ul){
  lastDiag = [dl, ul];
  const res = performance.getEntriesByType('resource');
  const protoOf = re => [...new Set(res.filter(e => re.test(e.name)).map(e => e.nextHopProtocol || '?'))].join(', ') || t('dg.na');
  const fmtS = s => (s && s.length) ? s.map(v => v.toFixed(0)).join(' ') : '-';
  const net = navigator.connection ? `${navigator.connection.effectiveType || '?'}` : 'n/a';
  const lines = [
    `${t('dg.proto')}: ${t('lbl.download')} ${protoOf(/\/download/)} | ${t('lbl.upload')} ${protoOf(/\/upload/)}`,
    `${t('dg.streams')}: ${CFG.streams} (${t('dg.grace')} ${CFG.grace/1000}s)`,
    `${t('lbl.ping')}: ${E.ping.textContent} ms | ${t('lbl.jitter')}: ${E.jit.textContent} ms`,
    `${t('lbl.download')}: ${dl.mbps ? dl.mbps.toFixed(1) : '-'} Mbps / ${dl.secs ? dl.secs.toFixed(1) : '-'}s (${t('dg.persec')}: ${fmtS(dl.samples)})`,
    `${t('lbl.upload')}: ${ul.mbps ? ul.mbps.toFixed(1) : '-'} Mbps / ${ul.secs ? ul.secs.toFixed(1) : '-'}s (${t('dg.persec')}: ${fmtS(ul.samples)})`,
    `${t('dg.net')}: ${net} | ${t('dg.adapters')}: ${(window.__rtc || []).join(', ') || 'n/a'}`,
    `${t('dg.browser')}: ${navigator.userAgent}`
  ];
  $('diagTxt').textContent = lines.join('\n');
  $('diag').style.display = 'block';
}
$('diagCopy').onclick = async () => {
  try { await navigator.clipboard.writeText($('diagTxt').textContent); $('diagCopy').textContent = t('diag.copied'); }
  catch(e) { $('diagCopy').textContent = t('diag.manual'); }
  setTimeout(() => { $('diagCopy').textContent = t('diag.copy'); }, 2000);
};

// ---------- run ----------
E.go.onclick = async () => {
  if (testing) return;
  testing = true;
  E.btnW.style.display = 'none'; E.status.style.display = 'block'; noteState = null; errs = {dl:null, ul:null}; paintNote();
  for (const k of ['dl','ul']){ target[k] = 0; shown[k] = 0; E[k].textContent = '—'; E[k+'Box'].classList.remove('err'); }
  E.ping.textContent = '—'; E.jit.textContent = '—'; gaugeReset(0);
  let dl = {mbps:0}, ul = {mbps:0};
  $('diag').style.display = 'none';
  copyBtn.disabled = true; lastResult = null;
  try { performance.clearResourceTimings(); } catch(e) {}
  try {
    await pingTest();

    setPhase('DOWNLOAD'); E.sd.textContent = '…'; gaugeReset(0);
    dl = await measure('dl', dlStream);
    if (dl.error) showError('dl', dl.error); else target.dl = dl.mbps;

    setPhase('UPLOAD'); E.sd.textContent = '…'; gaugeReset((dl.mbps || 0) * 0.9);
    await sleep(300);
    if (!ulBlob) ulBlob = makeUploadBlob();
    ul = await measure('ul', ulStream);
    if (ul.error) showError('ul', ul.error); else target.ul = ul.mbps;
  } catch(e){
    noteState = {kind:'test', msg: String(e.message || e)}; paintNote();
  } finally {
    try { showDiag(dl, ul); } catch(e) {}
    if (dl.mbps || ul.mbps){
      lastResult = {dl: dl.mbps || 0, ul: ul.mbps || 0, ping: E.ping.textContent, jit: E.jit.textContent,
                    ts: Date.now()};
      copyBtn.disabled = false;
    }
    setPhase('DONE');
    E.sd.textContent = `${dl.mbps ? fmt(dl.mbps) : '—'} / ${ul.mbps ? fmt(ul.mbps) : '—'}`;
    gaugeReset(0);
    setTimeout(() => {
      E.status.style.display = 'none'; E.btnW.style.display = 'block';
      goKey = 'btn.again'; E.go.textContent = t(goKey); testing = false;
    }, 1200);
  }
};
function applyLang(l, save){
  lang = I18N[l] ? l : 'en';
  root.lang = lang; root.dir = RTL[lang] ? 'rtl' : 'ltr';
  document.title = t('title');
  document.querySelectorAll('[data-i18n]').forEach(el => { el.textContent = t(el.dataset.i18n); });
  E.go.textContent = t(goKey);
  E.phase.textContent = t('phase.' + phaseCode); E.st.textContent = t('phase.' + phaseCode);
  $('langSel').value = lang; $('langSel').setAttribute('aria-label', t('aria.lang'));
  applyTheme(root.getAttribute('data-theme') || 'dark', false);      // refreshes the theme button's label
  paintNote(); paintErrors(); paintInfo(); if (infoReady) paintConn();
  if (lastDiag) try { showDiag(lastDiag[0], lastDiag[1]); } catch(e) {}
  if (lastResult) copyBtn.textContent = t('btn.copy');
  if (save){ try { localStorage.setItem('st_lang', lang); } catch(e) {} }
}
$('langSel').onchange = e => applyLang(e.target.value, true);
$('themeBtn').onclick = () => applyTheme(root.getAttribute('data-theme') === 'light' ? 'dark' : 'light', true);
try {                                                              // follow the system theme until the visitor picks one
  const mq = window.matchMedia('(prefers-color-scheme: light)');
  const follow = e => { let saved = null; try { saved = localStorage.getItem('st_theme'); } catch(x) {} if (!saved) applyTheme(e.matches ? 'light' : 'dark', false); };
  if (mq.addEventListener) mq.addEventListener('change', follow);
} catch(e) {}
applyLang(pickLang(), false);
gaugeReset(0);
</script>
</body>
</html>
