// theme toggle
(function(){
  const k='pref-theme', r=document.documentElement, b=document.getElementById('themeToggle');
  const s=localStorage.getItem(k);
  r.setAttribute('data-theme',(s==='dark'||s==='light')?s:'light');
  function x(){ if(b) b.setAttribute('aria-pressed',r.getAttribute('data-theme')==='dark'); }
  x();
  if(b) b.addEventListener('click',()=>{
    const c=r.getAttribute('data-theme')==='dark'?'light':'dark';
    r.setAttribute('data-theme',c); localStorage.setItem(k,c); x();
  });
})();

// search (header) – show clear button & basic filtering if list exists
(function(){
  const q=document.getElementById('q'), go=document.getElementById('qIcon'), cl=document.getElementById('qClear'), L=document.getElementById('list');
  if(!q) return;
  function apply(){
    const t=q.value.trim().toLowerCase(); q.parentElement.classList.toggle('has-text',t.length>0);
    if(!L) return;
    L.querySelectorAll('.post').forEach(p=>{
      const h=p.dataset.title?.toLowerCase().includes(t); p.style.display=h?'':'none';
    });
  }
  q.addEventListener('input',apply);
  if(go) go.addEventListener('click',()=>{ apply(); const f=[...L?.querySelectorAll('.post')||[]].find(p=>p.style.display!=='none'); if(f) f.scrollIntoView({behavior:'smooth',block:'center'}); });
  if(cl) cl.addEventListener('click',()=>{ q.value=''; apply(); q.focus(); });
  apply();
})();

// ===== Compact search for small screens =====
(function(){
  const shell = document.querySelector('.search');
  const icon = document.getElementById('qIcon');
  if(!shell || !icon) return;

  function isSmall(){ return window.innerWidth <= 600; }
  function close(){ shell.classList.remove('compact-open'); }
  function toggle(){
    if(!isSmall()) return;
    shell.classList.toggle('compact-open');
    if(shell.classList.contains('compact-open')){
      const input = shell.querySelector('input'); input && input.focus();
    }
  }

  icon.addEventListener('click', toggle);
  window.addEventListener('resize', ()=>{ if(!isSmall()) close(); });
  document.addEventListener('click', (e)=>{
    if(!isSmall()) return;
    if(!shell.contains(e.target)) close();
  });
})();

// Mark active category pill when on /category/<slug>.html
(function(){
  const pills = document.querySelectorAll('.pills .pill');
  if(!pills.length) return;
  const path = location.pathname.replace(/\/+$/,''); // bỏ dấu / cuối
  pills.forEach(a => {
    try{
      if(a.pathname.replace(/\/+$/,'') === path){ a.classList.add('is-active'); }
    }catch(e){}
  });
})();

// Stick header with shadow when scrolling
(function(){
  var head = document.querySelector('.site-head');
  if(!head) return;
  var stuck = false;
  function onScroll(){
    var s = (window.pageYOffset || document.documentElement.scrollTop || 0) > 4;
    if(s !== stuck){
      stuck = s;
      head.classList.toggle('is-stuck', s);
    }
  }
  onScroll();
  window.addEventListener('scroll', onScroll, {passive:true});
})();

// Set --head-h = actual header height, and keep it updated
(function(){
  var head = document.querySelector('.site-head');
  if(!head) return;

  function setVar(){
    var h = head.offsetHeight || 60;
    document.documentElement.style.setProperty('--head-h', h + 'px');
  }
  setVar();
  window.addEventListener('load', setVar);
  window.addEventListener('resize', setVar);

  // shadow when scrolled a bit
  function onScroll(){
    var s = (window.pageYOffset || document.documentElement.scrollTop || 0) > 4;
    head.classList.toggle('is-stuck', s);
  }
  onScroll();
  window.addEventListener('scroll', onScroll, {passive:true});
})();


// Compact search: icon -> expand on mobile
(function(){
  var box   = document.querySelector('.search');
  var input = document.getElementById('q');
  var icon  = document.getElementById('qIcon');
  var clear = document.getElementById('qClear');
  if(!box || !icon) return;

  var mql = window.matchMedia('(max-width: 720px)');

  function openSearch(){
    box.classList.add('is-open');
    setTimeout(function(){ input && input.focus(); }, 0);
  }
  function closeSearch(){
    box.classList.remove('is-open');
  }
  function isOpen(){ return box.classList.contains('is-open'); }

  // bấm icon: nếu mobile & đang đóng -> mở; nếu đang mở -> trigger tìm
  icon.addEventListener('click', function(e){
    if(mql.matches && !isOpen()){
      e.preventDefault();
      openSearch();
    }else{
      // giữ hành vi cũ của nút (scroll tới kết quả đầu, nếu có script index)
    }
  });

  // bấm ra ngoài để đóng (chỉ trên mobile)
  document.addEventListener('click', function(e){
    if(!mql.matches) return;
    if(isOpen() && !box.contains(e.target)) closeSearch();
  }, {capture:true});

  // ESC để đóng
  document.addEventListener('keydown', function(e){
    if(mql.matches && e.key === 'Escape') closeSearch();
  });

  // khi clear hết nội dung mà đang ở mobile -> vẫn giữ trạng thái mở
  if(clear){
    clear.addEventListener('click', function(){
      if(input) input.value = '';
    });
  }
})();

