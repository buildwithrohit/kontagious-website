(function () {
  // Mobile menu
  var btn = document.querySelector('.menu-btn');
  var nav = document.getElementById('nav');
  if (btn && nav) {
    btn.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    nav.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') {
        nav.classList.remove('open');
        btn.setAttribute('aria-expanded', 'false');
      }
    });
  }

  // Footer year
  var y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();

  // Hide events whose end date (data-end="YYYY-MM-DD") has passed
  var today = new Date();
  today.setHours(0, 0, 0, 0);
  var events = document.querySelectorAll('#event-list .event');
  var visible = 0;
  events.forEach(function (el) {
    var end = el.getAttribute('data-end');
    if (end) {
      var d = new Date(end + 'T23:59:59');
      if (d < today) {
        el.hidden = true;
        return;
      }
    }
    visible++;
  });
  var none = document.getElementById('no-events');
  if (none) none.hidden = visible > 0;

  // Fade-in on scroll
  var targets = document.querySelectorAll('.card, .stat, .gallery a, .ticks');
  if ('IntersectionObserver' in window) {
    targets.forEach(function (t) { t.classList.add('reveal'); });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          en.target.classList.add('in');
          io.unobserve(en.target);
        }
      });
    }, { threshold: 0.12 });
    targets.forEach(function (t) { io.observe(t); });
  }
})();
