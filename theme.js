/* theme toggle + language menu, shared by every page */
(function () {
  var root = document.documentElement;
  function label(th) {
    var b = document.getElementById('themeBtn'); if (!b) return;
    var s = th === 'light' ? b.getAttribute('data-to-dark') : b.getAttribute('data-to-light');
    b.setAttribute('aria-label', s); b.title = s;
  }
  window.applyTheme = function (th, save) {
    root.setAttribute('data-theme', th);
    var m = document.querySelector('meta[name="theme-color"]');
    if (m) m.setAttribute('content', th === 'light' ? '#f3f4f7' : '#0a0a0a');
    if (save) { try { localStorage.setItem('st_theme', th); } catch (e) {} }
    label(th);
  };
  var btn = document.getElementById('themeBtn');
  if (btn) btn.onclick = function () { window.applyTheme(root.getAttribute('data-theme') === 'light' ? 'dark' : 'light', true); };
  window.applyTheme(root.getAttribute('data-theme') || 'dark', false);
  try {                                      /* follow the system theme until the visitor picks one */
    var mq = window.matchMedia('(prefers-color-scheme: light)');
    var follow = function (e) { var saved = null; try { saved = localStorage.getItem('st_theme'); } catch (x) {} if (!saved) window.applyTheme(e.matches ? 'light' : 'dark', false); };
    if (mq.addEventListener) mq.addEventListener('change', follow);
  } catch (e) {}
  var sel = document.getElementById('langSel');
  if (sel) sel.onchange = function () {      /* each language is its own URL (good for search engines) */
    var o = sel.options[sel.selectedIndex];
    try { document.cookie = 'st_lang=' + o.getAttribute('data-code') + ';path=/;max-age=31536000;SameSite=Lax'; } catch (e) {}
    try { localStorage.setItem('st_lang', o.getAttribute('data-code')); } catch (e) {}
    location.href = o.value;
  };
})();
