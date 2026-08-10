// Mobile menu
function openMobileMenu(){
  document.getElementById('mobileMenu').classList.add('is-open');
  document.getElementById('mobileBackdrop').classList.add('is-open');
  document.body.classList.add('menu-open');
}
function closeMobileMenu(){
  document.getElementById('mobileMenu').classList.remove('is-open');
  document.getElementById('mobileBackdrop').classList.remove('is-open');
  document.body.classList.remove('menu-open');
}
document.addEventListener('keydown', function(e){
  if (e.key === 'Escape') closeMobileMenu();
});

// Homepage visual carousel (safe no-op on pages without #vizTrack)
(function(){
  var track = document.getElementById('vizTrack');
  if (!track) return;
  var current = 0;
  var total = 4;
  function vizGo(n){
    current = ((n % total) + total) % total;
    track.style.transform = 'translateX(-' + (current * 100) + '%)';
    document.querySelectorAll('.viz-dot').forEach(function(d,i){
      d.classList.toggle('viz-dot--active', i === current);
    });
  }
  window.vizMove = function(dir){ vizGo(current + dir); };
  window.vizGo = vizGo;
  setInterval(function(){ vizGo(current + 1); }, 5000);
})();

// Scroll-reveal animation (progressive enhancement — tags existing elements at runtime)
(function(){
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  if (!('IntersectionObserver' in window)) return;

  var selectors = [
    '.hp-card', '.svc-card', '.tg-card', '.bg-card', '.bside-card',
    '.av-item', '.pst-item', '.ws-item', '.hs-card', '.port-case',
    '.viz-carousel', '.faq-item', '.img-card', '.gm-main', '.gm-cell',
    '.pc-doc', '.vs-card', '.video-feat', '.ab-card', '.ha-right',
    '.hq-inner', '.sec-h', '.hs-header'
  ];
  var nodes = document.querySelectorAll(selectors.join(','));
  if (!nodes.length) return;

  nodes.forEach(function(el, i){
    el.classList.add('reveal-init');
    el.style.transitionDelay = (Math.min(i % 6, 5) * 70) + 'ms';
  });

  var io = new IntersectionObserver(function(entries){
    entries.forEach(function(entry){
      if (entry.isIntersecting){
        entry.target.classList.add('is-visible');
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

  nodes.forEach(function(el){ io.observe(el); });
})();
