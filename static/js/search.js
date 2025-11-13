document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('search-input');
  const results = document.getElementById('search-results');
  let index = [];

  function render(items) {
    results.innerHTML = '';
    if (!items.length) {
      results.innerHTML = '<p>No results.</p>';
      return;
    }
    const frag = document.createDocumentFragment();
    items.slice(0, 100).forEach(it => {
      const a = document.createElement('a');
      a.href = it.url;
      a.className = 'search-item';
      a.innerHTML = `
        <img src="${it.image}" alt="${it.title}">
        <div>
          <h3>${it.title}</h3>
          <p class="muted">${it.category || ''}</p>
          <p>${(it.description || '').slice(0, 160)}</p>
        </div>`;
      frag.appendChild(a);
    });
    results.appendChild(frag);
  }

  function qmatch(str, q) {
    return (str || '').toLowerCase().includes(q);
  }

  function search(q) {
    q = q.trim().toLowerCase();
    if (!q) { render(index); return; }
    const words = q.split(/\s+/).filter(Boolean);
    const out = index.filter(it => words.every(w => qmatch(it.title, w) || qmatch(it.category, w) || qmatch(it.description, w)));
    render(out);
  }

  fetch('/index.json')
    .then(r => r.json())
    .then(data => { index = data; render(index); })
    .catch(() => { results.innerHTML = '<p>Unable to load search index.</p>'; });

  input?.addEventListener('input', () => search(input.value));
});
