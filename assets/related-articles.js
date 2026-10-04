(function(){
var STOP='about after also and are but can does for from have how into just more not our out that the their them then they this what when where which why will with you your'.split(' ');
function norm(u){u=String(u||'').split('#')[0].split('?')[0].replace(/^https?:\/\/[^\/]+/,'').replace(/index\.html$/,'');if(u.charAt(0)!=='/')u='/'+u;if(u.slice(-1)!=='/')u+='/';return u.toLowerCase()}
function set(a){var o={};(a||[]).forEach(function(x){x=String(x).toLowerCase().trim();if(x)o[x]=1});return o}
function ov(a,b){var A=set(a),n=0;Object.keys(set(b)).forEach(function(k){if(A[k])n++});return n}
function words(p){return(((p.title||'')+' '+(p.excerpt||'')).toLowerCase().match(/[a-z0-9]{4,}/g)||[]).filter(function(w){return STOP.indexOf(w)<0})}
function score(a,b){var s=0;
if(a.category&&String(a.category).toLowerCase()===String(b.category||'').toLowerCase())s+=5;
s+=2*ov(a.tags,b.tags);s+=2*Math.min(ov(a.audience,b.audience),2);s+=3*Math.min(ov(a.services,b.services),1);
s+=.5*Math.min(ov(words(a),words(b)),3);return s}
function pick(posts,cur,max){cur=norm(cur);max=max||5;var seen={},me={};
var list=(posts||[]).filter(function(p){if(!p||!p.url||!p.title)return false;var u=norm(p.url);if(u===cur){me=p;return false}if(seen[u])return false;seen[u]=1;return true});
list.forEach(function(p){p._s=score(me,p);p._d=Date.parse(p.date||'')||0});
list.sort(function(x,y){return y._s-x._s||y._d-x._d||(x.title<y.title?-1:1)});return list.slice(0,max)}
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function cut(s){s=String(s||'').trim();if(s.length<=150)return s;return s.slice(0,150).replace(/\s+\S*$/,'')+'...'}
function fb(){return(typeof window!=='undefined'&&window.RA_FALLBACK_IMAGE)||'/assets/og-image.png'}
function card(p){return'<article class="ra-card"><img src="'+esc(p.image||fb())+'" alt="'+esc(p.imageAlt||p.title)+'" width="640" height="360" loading="lazy" decoding="async"><div class="ra-b">'+(p.category?'<p class="ra-c">'+esc(p.category)+'</p>':'')+'<h3><a href="'+esc(p.url)+'">'+esc(p.title)+'</a></h3><p class="ra-e">'+esc(cut(p.excerpt))+'</p><span class="ra-more" aria-hidden="true">Read article</span></div></article>'}
var CSS='.ra{background:#F3F6F2;padding:72px 0}.ra-in{max-width:1080px;margin:0 auto;padding:0 24px}.ra-h{font-family:"Source Serif 4",Georgia,serif;font-weight:600;color:#1B3A2D;font-size:clamp(1.6rem,3.2vw,2.2rem);margin:0 0 28px}.ra-grid{display:grid;gap:24px;grid-template-columns:repeat(3,1fr)}.ra-n4{grid-template-columns:repeat(4,1fr)}.ra-card{position:relative;background:#fff;border:1px solid #d3dfd7;border-radius:8px;overflow:hidden;display:flex;flex-direction:column}.ra-card:hover{border-color:#C9A24B}.ra-card img{display:block;width:100%;height:auto;aspect-ratio:16/9;object-fit:cover;background:#1B3A2D}.ra-b{padding:18px;display:flex;flex-direction:column;gap:8px;flex:1}.ra-c{margin:0;font-size:.78rem;letter-spacing:.08em;text-transform:uppercase;color:#4F5E57;font-weight:700}.ra-card h3{margin:0;font-family:"Source Serif 4",Georgia,serif;font-size:1.15rem;line-height:1.3}.ra-card h3 a{color:#1B3A2D;text-decoration:none}.ra-card h3 a:after{content:"";position:absolute;inset:0}.ra-card h3 a:focus-visible{outline:3px solid #C9A24B;outline-offset:-3px}.ra-e{margin:0;color:#4F5E57;font-size:.95rem;line-height:1.55}.ra-more{margin-top:auto;font-weight:700;color:#1B4332;font-size:.95rem}.ra-card:hover .ra-more{text-decoration:underline}@media(max-width:1000px){.ra-grid,.ra-n4{grid-template-columns:repeat(2,1fr)}}@media(max-width:620px){.ra{padding:52px 0}.ra-grid,.ra-n4{grid-template-columns:1fr}}';
function mount(posts){var g=document.getElementById('ra-grid');if(!g)return;var sec=document.getElementById('related-articles');
if(!document.getElementById('ra-css')){var st=document.createElement('style');st.id='ra-css';st.textContent=CSS;document.head.appendChild(st)}
if(g.children.length)return;var cur=g.getAttribute('data-current')||location.pathname;var r=pick(posts,cur,5);
if(!r.length){if(sec)sec.hidden=true;return}g.className='ra-grid ra-n'+r.length;g.innerHTML=r.map(card).join('')}
if(typeof module!=='undefined')module.exports={pick:pick,score:score,norm:norm};
if(typeof document==='undefined')return;
function run(){if(window.RA_POSTS){mount(window.RA_POSTS);return}
fetch('/assets/posts.json').then(function(r){return r.json()}).then(function(d){mount(d.posts||d)}).catch(function(){var s=document.getElementById('related-articles');if(s)s.hidden=true})}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',run);else run();
})();