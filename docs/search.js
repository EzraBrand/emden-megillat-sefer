(function () {
  var data = null, idx = null;
  var qEl = document.getElementById('q'), langEl = document.getElementById('lang');
  var out = document.getElementById('results'), status = document.getElementById('status');
  var HEB_SKIP = /[֑-ׇ"'׳״‘’“”]/;

  // normalise a string and keep a map from each normalised character back to the original index
  function norm(s, he) {
    var n = '', map = [];
    for (var i = 0; i < s.length; i++) {
      var c = s[i];
      if (he) {
        if (HEB_SKIP.test(c)) continue;
      } else {
        c = c.normalize('NFD').replace(/[̀-̣̱ͯ]/g, '').toLowerCase();
        if (c === '’' || c === '‘') c = "'";
        if (!c) continue;
      }
      for (var j = 0; j < c.length; j++) { n += c[j]; map.push(i); }
    }
    return { n: n, map: map };
  }
  function esc(s) { return s.replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  function snippet(orig, nm, pos, len, he) {
    var a = nm.map[pos], b = nm.map[pos + len - 1] + 1;
    var s = Math.max(0, a - 90), e = Math.min(orig.length, b + 90);
    return '<div class="snip' + (he ? ' he' : '') + '">' + (s > 0 ? '… ' : '') + esc(orig.slice(s, a)) + '<mark>' +
      esc(orig.slice(a, b)) + '</mark>' + esc(orig.slice(b, e)) + (e < orig.length ? ' …' : '') + '</div>';
  }

  function run() {
    var q = qEl.value.trim(), lang = langEl.value;
    var u = new URL(location.href);
    if (q) u.searchParams.set('q', q); else u.searchParams.delete('q');
    history.replaceState(null, '', u);
    out.innerHTML = '';
    if (!q) { status.textContent = ''; return; }
    var isHe = /[א-ת]/.test(q);
    var nq = norm(q, isHe).n;
    if (nq.length < 2) { status.textContent = 'Type at least two letters.'; return; }
    var html = [], pages = 0, total = 0;
    data.forEach(function (d, k) {
      var fields = [];
      if (isHe && lang !== 'en') fields.push(['h', true]);
      if (!isHe && lang !== 'he') fields.push(['e', false]);
      fields.forEach(function (f) {
        var nm = idx[k][f[0]], hits = [], p = nm.n.indexOf(nq);
        while (p !== -1) { hits.push(p); p = nm.n.indexOf(nq, p + nq.length); }
        if (!hits.length) return;
        pages++; total += hits.length;
        if (pages > 300) return;
        html.push('<li><a href="' + d.f + '#' + d.a + '">Chapter ' + d.c + ', ' + d.l + '</a> <span class="sub">(' + hits.length +
          (hits.length > 1 ? ' hits' : ' hit') + ', ' + (f[1] ? 'Hebrew' : 'English') + ')</span>' +
          hits.slice(0, 3).map(function (h) { return snippet(d[f[0]], nm, h, nq.length, f[1]); }).join('') + '</li>');
      });
    });
    out.innerHTML = html.join('');
    status.textContent = total ? total + ' hits on ' + pages + ' pages' + (pages > 300 ? ' (first 300 shown)' : '') + '.' :
      'No hits.' + (isHe && lang === 'en' ? ' (Hebrew query, English only selected.)' : '');
  }

  var t;
  function later() { clearTimeout(t); t = setTimeout(run, 200); }
  status.textContent = 'Loading the text…';
  fetch('search.json').then(function (r) { return r.json(); }).then(function (d) {
    data = d;
    idx = d.map(function (x) { return { h: norm(x.h, true), e: norm(x.e, false) }; });
    status.textContent = '';
    var q = new URLSearchParams(location.search).get('q');
    if (q) qEl.value = q;
    run();
    qEl.addEventListener('input', later);
    langEl.addEventListener('change', run);
    document.getElementById('sf').addEventListener('submit', function (e) { e.preventDefault(); run(); });
  }).catch(function () { status.textContent = 'Could not load search.json.'; });
})();
