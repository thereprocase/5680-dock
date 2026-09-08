/* The page works without JavaScript. Keep enhancement small and local. */
(() => {
  const links = [...document.querySelectorAll('.site-header nav a[href^="#"]')];
  if (!('IntersectionObserver' in window)) return;
  const targets = links.map(link => document.querySelector(link.getAttribute('href'))).filter(Boolean);
  const visible = new Map();
  const observer = new IntersectionObserver(entries => {
    for (const entry of entries) visible.set(entry.target.id, entry);
    const current = [...visible.values()].filter(entry => entry.isIntersecting)
      .sort((a, b) => Math.abs(a.target.getBoundingClientRect().top) - Math.abs(b.target.getBoundingClientRect().top))[0];
    for (const link of links) {
      if (current && link.hash === '#' + current.target.id) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    }
  }, { rootMargin: '-12% 0px -60% 0px', threshold: 0 });
  targets.forEach(target => observer.observe(target));
})();
