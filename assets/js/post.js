// Build TOC from headings in post body
(function(){
  const body=document.getElementById('postBody'); if(!body) return;
  function slugify(s){return String(s).toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[^a-z0-9\s-]/g,'').trim().replace(/\s+/g,'-').replace(/-+/g,'-');}
  const hs=body.querySelectorAll('h1,h2,h3');
  const toc=document.getElementById('toc'), list=document.getElementById('tocList');
  if(!hs.length){ if(toc) toc.style.display='none'; return; }
  const ul=document.createElement('ul');
  hs.forEach(h=>{
    const lvl=+h.tagName.substring(1); if(!h.id) h.id=slugify(h.textContent);
    const li=document.createElement('li'); li.className='lvl-'+lvl;
    const a=document.createElement('a'); a.href='#'+h.id; a.textContent=h.textContent;
    li.appendChild(a); ul.appendChild(li);
  });
  list.appendChild(ul);
  const btn=document.getElementById('tocToggle');
  function setLabel(){ if(btn && toc) btn.textContent = toc.classList.contains('collapsed')?'Expand all':'Collapse all'; }
  setLabel();
  if(btn) btn.addEventListener('click',e=>{ e.preventDefault(); toc.classList.toggle('collapsed'); setLabel(); });
  const t=document.getElementById('tocTop'), b=document.getElementById('tocBottom');
  if(t) t.addEventListener('click',e=>{ e.preventDefault(); window.scrollTo({top:0,behavior:'smooth'}); });
  if(b) b.addEventListener('click',e=>{ e.preventDefault(); window.scrollTo({top:document.body.scrollHeight,behavior:'smooth'}); });
})();
