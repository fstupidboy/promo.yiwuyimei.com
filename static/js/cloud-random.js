document.addEventListener('DOMContentLoaded', () => {
  const cloud = document.querySelector('.word-cloud');
  if (!cloud) return;
  const words = Array.from(cloud.children);
  // Shuffle words
  for (let i = words.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [words[i], words[j]] = [words[j], words[i]];
  }
  // Apply shuffled order
  words.forEach((el, idx) => {
    el.style.order = idx;
    // Random subtle rotation / translation for more organic layout
    const rot = (Math.random() * 6) - 3; // -3deg to 3deg
    const ty = (Math.random() * 12) - 6; // -6px to 6px
    el.style.transform = `translateY(${ty}px) rotate(${rot}deg)`;
  });
});
