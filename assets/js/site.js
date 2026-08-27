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

/* Gallery lightbox. The markup ships as plain links to the full-size files,
   so this is an upgrade, not a dependency - with JS off, a click still opens
   the photograph. Uses a native <dialog> so focus trapping, Esc and the
   inert background come from the platform rather than from here. */
(function () {
  var shots = [].slice.call(document.querySelectorAll('.gallery a.shot'));
  if (!shots.length || !window.HTMLDialogElement) return;

  var i = 0, opener = null;
  var dlg = document.createElement('dialog');
  dlg.className = 'lb';
  dlg.setAttribute('aria-label', 'Production photographs');
  dlg.innerHTML =
    '<div class="lb__stage"><img class="lb__img" alt=""></div>' +
    '<button class="lb__btn lb__close" aria-label="Close">×</button>' +
    '<button class="lb__btn lb__nav lb__prev" aria-label="Previous photograph">‹</button>' +
    '<button class="lb__btn lb__nav lb__next" aria-label="Next photograph">›</button>' +
    '<p class="lb__count"><b class="lb__i">1</b> / <span class="lb__n"></span></p>';
  document.body.appendChild(dlg);

  var img   = dlg.querySelector('.lb__img'),
      idxEl = dlg.querySelector('.lb__i'),
      numEl = dlg.querySelector('.lb__n');
  numEl.textContent = shots.length;
  if (shots.length < 2) {
    dlg.querySelector('.lb__prev').hidden = true;
    dlg.querySelector('.lb__next').hidden = true;
    dlg.querySelector('.lb__count').hidden = true;
  }

  function preload(n) {
    var a = shots[(n + shots.length) % shots.length];
    if (a) { var p = new Image(); p.src = a.href; }
  }

  function show(n) {
    i = (n + shots.length) % shots.length;
    var a = shots[i], thumb = a.querySelector('img');
    dlg.classList.add('is-loading');
    img.src = a.href;
    img.alt = thumb ? thumb.alt : '';
    idxEl.textContent = i + 1;
    if (img.complete) dlg.classList.remove('is-loading');
    preload(i + 1); preload(i - 1);
  }
  img.addEventListener('load', function () { dlg.classList.remove('is-loading'); });

  shots.forEach(function (a, n) {
    a.addEventListener('click', function (e) {
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return;  // let people open in a tab
      e.preventDefault();
      opener = a;
      show(n);
      dlg.showModal();
      document.documentElement.style.overflow = 'hidden';
    });
  });

  // Not all engines dispatch dialog's 'close' event, so teardown is explicit
  // and idempotent rather than relying on it firing.
  function teardown() {
    document.documentElement.style.overflow = '';
    img.removeAttribute('src');
    if (opener) { opener.focus(); opener = null; }
  }
  function close() {
    if (dlg.open) dlg.close();
    teardown();
  }

  dlg.querySelector('.lb__next').addEventListener('click', function () { show(i + 1); });
  dlg.querySelector('.lb__prev').addEventListener('click', function () { show(i - 1); });
  dlg.querySelector('.lb__close').addEventListener('click', close);

  // a click on the backdrop lands on the dialog itself, not on its contents
  dlg.addEventListener('click', function (e) {
    if (e.target === dlg || e.target.classList.contains('lb__stage')) close();
  });

  dlg.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowRight') { e.preventDefault(); show(i + 1); }
    else if (e.key === 'ArrowLeft') { e.preventDefault(); show(i - 1); }
  });

  dlg.addEventListener('cancel', teardown);   // Esc
  dlg.addEventListener('close', teardown);    // engines that do fire it

  // swipe on touch
  var x0 = null;
  dlg.addEventListener('touchstart', function (e) { x0 = e.changedTouches[0].clientX; }, {passive: true});
  dlg.addEventListener('touchend', function (e) {
    if (x0 === null) return;
    var dx = e.changedTouches[0].clientX - x0;
    if (Math.abs(dx) > 45) show(dx < 0 ? i + 1 : i - 1);
    x0 = null;
  }, {passive: true});
})();
