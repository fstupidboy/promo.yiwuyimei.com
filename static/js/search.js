document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('search-input');
  const results = document.getElementById('search-results');
  let index = [];
  let lastQuery = '';
  let timer = null;

  function escapeHTML(str) {
    return (str || '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[c]));
  }

  function highlight(text, words) {
    if (!text) return '';
    const escaped = escapeHTML(text);
    return words.reduce((acc, w) => {
      const re = new RegExp(`(${w.replace(/[-/\\^$*+?.()|[\]{}]/g, '\\$&')})`, 'ig');
      return acc.replace(re, '<mark>$1</mark>');
    }, escaped);
  }

  function scoreItem(it, words) {
    const t = (it.title || '').toLowerCase();
    const d = (it.description || '').toLowerCase();
    const c = (it.category || '').toLowerCase();
    let s = 0;
    words.forEach(w => {
      const wt = (t.match(new RegExp(w, 'g')) || []).length;
      const wd = (d.match(new RegExp(w, 'g')) || []).length;
      const wc = (c.match(new RegExp(w, 'g')) || []).length;
      s += wt * 5 + wd * 2 + wc * 3; // weight title highest, then category, then description
    });
    return s;
  }

  function render(items, words) {
    results.innerHTML = '';
    if (!items.length) { results.innerHTML = '<p>No results.</p>'; return; }
    const frag = document.createDocumentFragment();
    items.slice(0, 100).forEach(it => {
      const a = document.createElement('a');
      a.href = it.url;
      a.className = 'search-item';
      const descSnippet = (it.description || '').slice(0, 180);
      a.innerHTML = `
        <img src="${it.image}" alt="${escapeHTML(it.title)}">
        <div>
          <h3>${highlight(it.title, words)}</h3>
          <p class="muted">${highlight(it.category || '', words)}</p>
          <p>${highlight(descSnippet, words)}</p>
        </div>`;
      frag.appendChild(a);
    });
    results.appendChild(frag);
  }

  function search(q) {
    q = q.trim();
    if (!q) { render(index, []); return; }
    const words = q.toLowerCase().split(/\s+/).filter(Boolean);
    const filtered = index
      .map(it => ({ it, score: scoreItem(it, words) }))
      .filter(obj => obj.score > 0)
      .sort((a,b) => b.score - a.score)
      .map(obj => obj.it);
    render(filtered, words);
  }

  function scheduleSearch(value) {
    lastQuery = value;
    clearTimeout(timer);
    timer = setTimeout(() => search(lastQuery), 120); // debounce
  }

  fetch('/index.json')
    .then(r => r.json())
    .then(data => { index = data; render(index, []); })
    .catch(() => { results.innerHTML = '<p>Unable to load search index.</p>'; });

  input?.addEventListener('input', e => scheduleSearch(e.target.value));
});
