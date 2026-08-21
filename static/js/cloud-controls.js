document.addEventListener('DOMContentLoaded', () => {
  const cloud = document.querySelector('.word-cloud');
  if (!cloud) return;
  const sortButtons = document.querySelectorAll('.btn-sort');
  const filterInput = document.querySelector('.cloud-filter');

  const readItems = () => Array.from(cloud.querySelectorAll('.cloud-word'));
  const nameOf = el => el.textContent.trim().toLowerCase();
  const countOf = el => parseInt(el.getAttribute('data-weight') || '0', 10);

  function render(items) {
    items.forEach((el, i) => { el.style.order = i; });
  }

  function sortByPopular() {
    const items = readItems().sort((a, b) => countOf(b) - countOf(a));
    render(items);
  }

  function sortByAZ() {
    const items = readItems().sort((a, b) => nameOf(a).localeCompare(nameOf(b)));
    render(items);
  }

  function applyFilter() {
    const q = (filterInput?.value || '').trim().toLowerCase();
    readItems().forEach(el => {
      const show = !q || nameOf(el).includes(q);
      el.style.display = show ? '' : 'none';
    });
  }

  sortButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      sortButtons.forEach(b => b.setAttribute('aria-pressed', 'false'));
      btn.setAttribute('aria-pressed', 'true');
      const mode = btn.getAttribute('data-sort');
      if (mode === 'popular') sortByPopular();
      if (mode === 'az') sortByAZ();
    });
  });

  filterInput?.addEventListener('input', () => applyFilter());
});
