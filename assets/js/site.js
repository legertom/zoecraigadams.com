/* Scroll reveal — lights come up as each plate enters the house. */
(function () {
  var els = document.querySelectorAll('.reveal');
  if (!els.length) return;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce || !('IntersectionObserver' in window)) {
    els.forEach(function (el) { el.classList.add('is-in'); });
    return;
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
    });
  }, { rootMargin: '0px 0px -12% 0px', threshold: 0.08 });
  els.forEach(function (el) { io.observe(el); });
})();

/* A "Now Playing" band retires itself after closing night, so the site can
   never advertise a closed run just because nobody rebuilt it. */
(function () {
  var today = new Date().toISOString().slice(0, 10);
  Array.prototype.forEach.call(document.querySelectorAll('.now[data-until]'), function (el) {
    if (el.getAttribute('data-until') < today) el.remove();
  });
})();
