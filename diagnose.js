/* Connection diagnosis: pure function, no DOM. Input = what the test really measured, output = rating + findings.
   Every threshold is written down here so the verdict can be audited and tuned in one place.
     input : {dl:{mbps,samples[],errors}, ul:{mbps,samples[],errors}, ping:{min,jit,fails,count}}
     output: {rating, issues:[{id,sev,vars}], uses:[...], stats}
   severity: 0 = information only, 1 = minor, 2 = major, 3 = severe */
(function (root) {
  var r0 = function (x) { return Math.round(x); };
  var r1 = function (x) { return Math.round(x * 10) / 10; };

  // spread of the per-second speeds (samples are taken after the warm-up period, so slow-start is not counted)
  function spread(samples) {
    if (!samples || samples.length < 4) return null;
    var n = samples.length, sum = 0, i;
    for (i = 0; i < n; i++) sum += samples[i];
    var mean = sum / n; if (!(mean > 0)) return null;
    var v = 0; for (i = 0; i < n; i++) v += (samples[i] - mean) * (samples[i] - mean);
    var cv = Math.sqrt(v / n) / mean;
    var s = samples.slice().sort(function (a, b) { return a - b; });
    var median = n % 2 ? s[(n - 1) / 2] : (s[n / 2 - 1] + s[n / 2]) / 2;
    return {n: n, mean: mean, cv: cv, low: median > 0 ? s[0] / median : 1};     // low = slowest second / typical second
  }

  function diagnose(m) {
    var issues = [], uses = [];
    function add(id, sev, vars) { issues.push({id: id, sev: sev, vars: vars || {}}); }
    var dl = m.dl && m.dl.mbps > 0 ? m.dl.mbps : 0;
    var ul = m.ul && m.ul.mbps > 0 ? m.ul.mbps : 0;
    var p = m.ping || {};
    var hasPing = typeof p.min === 'number';
    if (!dl && !ul) return null;           // nothing to judge when both speed phases failed (the page already shows the errors)

    // 1. latency to the test server (it also contains the distance to the server, so the limits are generous)
    if (hasPing) {
      if (p.min > 150) add('lat', 2, {ms: r0(p.min)});
      else if (p.min > 100) add('lat', 1, {ms: r0(p.min)});
    }
    // 2. jitter: how much the delay changes from one request to the next (calls/games need < 30 ms)
    if (typeof p.jit === 'number') {
      if (p.jit > 50) add('jit', 2, {ms: r0(p.jit)});
      else if (p.jit > 30) add('jit', 1, {ms: r0(p.jit)});
    }
    // 3. lost requests during the ping phase
    if (p.count && p.fails > 0) add('loss', p.fails >= 2 ? 2 : 1, {n: p.fails, total: p.count});
    // 4. stability of download / upload speed
    var sd = spread(m.dl && m.dl.samples), su = spread(m.ul && m.ul.samples);
    function stab(id, st) {
      if (!st) return;
      var vars = {cv: r0(st.cv * 100), low: r0(st.low * 100)};
      if (st.cv > 0.35 || st.low < 0.35) add(id, 2, vars);
      else if (st.cv > 0.20 || st.low < 0.55) add(id, 1, vars);
    }
    stab('stab_dl', sd); stab('stab_ul', su);
    // 5. connection dropped while transferring (a request failed after it had started)
    var errs = ((m.dl && m.dl.errors) || 0) + ((m.ul && m.ul.errors) || 0);
    if (errs >= 1) add('drops', errs >= 3 ? 2 : 1, {n: errs});
    // 6. raw speed
    if (dl) { if (dl < 2) add('dl_low', 3, {v: r1(dl)}); else if (dl < 5) add('dl_low', 2, {v: r1(dl)}); else if (dl < 10) add('dl_low', 1, {v: r1(dl)}); }
    if (ul) { if (ul < 0.5) add('ul_low', 3, {v: r1(ul)}); else if (ul < 1) add('ul_low', 2, {v: r1(ul)}); else if (ul < 3) add('ul_low', 1, {v: r1(ul)}); }
    // 7. download slower than upload is unusual (most lines are the other way round)
    if (dl && ul && ul > dl * 1.5 && dl < 100) add('dl_vs_ul', 1, {dl: r1(dl), ul: r1(ul)});
    // 8. information only: very asymmetric line
    if (dl >= 50 && ul && ul < 10 && ul / dl < 0.1) add('ul_ratio', 0, {p: r0(ul / dl * 100)});

    var bad = function (s) { return issues.filter(function (i) { return i.sev === s; }).length; };
    var unstable = issues.some(function (i) { return i.sev >= 2 && (i.id.indexOf('stab') === 0 || i.id === 'loss' || i.id === 'drops'); });
    var rating = unstable ? 'unstable'
      : (bad(3) > 0 || bad(2) >= 2) ? 'poor'
      : bad(2) === 1 ? 'fair'
      : bad(1) >= 1 ? 'good' : 'excellent';

    // what the connection is good for (a stable line is required for calls and games)
    var steady = rating !== 'unstable' && rating !== 'poor';
    if (dl >= 5) uses.push('hd');
    if (dl >= 25) uses.push('4k');
    if (steady && ul >= 3 && dl >= 3 && hasPing && p.min <= 150 && (p.jit || 0) <= 30) uses.push('calls');
    if (steady && hasPing && p.min <= 80 && (p.jit || 0) <= 20 && !(p.fails > 0)) uses.push('gaming');
    if (steady && ul >= 10) uses.push('cloud');

    var order = {stab_dl: 1, stab_ul: 2, loss: 3, drops: 4, jit: 5, lat: 6, dl_low: 7, ul_low: 8, dl_vs_ul: 9, ul_ratio: 10};
    issues.sort(function (a, b) { return (b.sev - a.sev) || (order[a.id] - order[b.id]); });
    return {rating: rating, issues: issues, uses: uses,
            stats: {dlCv: sd ? r0(sd.cv * 100) : null, ulCv: su ? r0(su.cv * 100) : null, fails: p.fails || 0, errors: errs}};
  }
  root.diagnose = diagnose;
  if (typeof module !== 'undefined' && module.exports) module.exports = diagnose;
})(typeof window !== 'undefined' ? window : this);
