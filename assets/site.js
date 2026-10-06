var b=document.querySelector('.menu'),n=document.getElementById('nav');
if(b&&n){b.addEventListener('click',function(){var o=n.classList.toggle('open');b.setAttribute('aria-expanded',o)})}

(function(){var t=document.querySelector('.toc-d');if(!t)return;var mq=window.matchMedia('(min-width:1100px)');function sync(){if(mq.matches)t.setAttribute('open','');else t.removeAttribute('open')}sync();if(mq.addEventListener)mq.addEventListener('change',sync);
var links=[].slice.call(t.querySelectorAll('a[href^="#"]')),hs=links.map(function(a){return document.getElementById(a.getAttribute('href').slice(1))}).filter(Boolean);if(!('IntersectionObserver' in window))return;
var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){links.forEach(function(a){a.classList.toggle('on',a.getAttribute('href')==='#'+e.target.id)})}})},{rootMargin:'0px 0px -70% 0px'});hs.forEach(function(h){io.observe(h)})})();
