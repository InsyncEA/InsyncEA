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
