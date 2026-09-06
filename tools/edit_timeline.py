#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
edit_timeline.py — Stage 9 review surface: the cutting-room timeline (brain/16).

Renders 09-timeline.json (built by tools/assemble.py) as one page:
  - the VO waveform (fixed spine) with the section bands
  - a block per beat, width ∝ duration, coloured by kind, PROMISE/PAY + EXPLICADOR
    marked, uncovered beats flagged
  - a 720p proxy preview with a scrubbable playhead
  - per-beat inspector: swap asset · trim · nudge · Ken Burns motion · a note for
    a regen · approve
  - a music lane

You drag / trim / nudge / swap / preview in the browser — no tokens.
"Finalizar Stage 9" POSTs the whole timeline back; the server saves it and,
on the final render, Claude applies the KB notes and assemble.py renders the 4K.

Writes  episodes/E0XX-slug/09-edit.html   (gitignored)
Reads   09-timeline.json · 09-wave.b64 · 09-rough.mp4   (from assemble.py)

Usage
  python tools/edit_timeline.py E0XX-slug
"""
import html as _h
import json
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
import theme as T          # noqa: E402
import assemble as A       # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = "09-edit.html"


def build(slug):
    ep = A.EP_DIR / slug
    tj = ep / "09-timeline.json"
    if not tj.exists():
        A.build_timeline(slug)
        A.waveform(slug)
    data = json.loads(tj.read_text(encoding="utf-8"))
    wave = ""
    wf = ep / "09-wave.b64"
    if wf.exists():
        wave = wf.read_text(encoding="utf-8").strip()
    has_rough = (ep / "09-rough.mp4").exists()
    e = _h.escape
    epid = slug[:4]

    n_beats = len(data["beats"])
    n_un = sum(1 for b in data["beats"] if b["state"] == "uncovered")
    n_fix = sum(1 for b in data["beats"] if b.get("fix"))
    aligned = data.get("aligned")

    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")

    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sala de montaje · {e(slug)}</title>
{T.FAVICON}
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700&display=swap">
{T.CSS}
{T.TIMELINE_CSS}
</head><body class="tl">
<header class="topbar">
 <span class="brand" style="font-size:1.15rem">Conquest</span>
 <span class="crumb">Stage 9 · <b>Sala de montaje</b></span>
 <span class="ep">{e(epid)} · {e(slug.split('-',1)[-1])}</span>
 <span class="pill {'on' if not n_fix and not n_un else 'warn'}"><span class="dot"></span>{
   'primer corte '+('alineado a la voz' if aligned else '(tiempos del shotlist)')}</span>
 <span class="spacer"></span>
 <button class="btn" id="prev">Previsualizar región</button>
 <button class="btn primary" id="fin">Finalizar Stage&nbsp;9</button>
 <a class="btn ghost" href="http://localhost:8765/">Volver al panel</a>
</header>

<div class="work">
 <section class="preview">
  <div class="screen" id="screen">
   {'<video id="vid" preload="metadata" src="09-rough.mp4#t=0.01"></video>' if has_rough else ''}
   <div class="frame" id="frame">
    <div class="big" id="scrtc">0:00</div>
    <div id="scrbeat">—</div>
    {'' if has_rough else '<div style="margin-top:.5rem;font-size:.72rem">sin corte proxy todavía — <code>assemble.py '+e(slug)+' --rough</code></div>'}
   </div>
   <span class="tag">corte aproximado · 720p · sin grade</span>
   <span class="lab" id="scrlab" hidden>Ilustración — Conquest</span>
  </div>
  <div class="transport">
   <button class="play" id="play" aria-label="Reproducir">
     <svg viewBox="0 0 16 16" id="playi"><path d="M4 2l10 6-10 6z"/></svg></button>
   <span class="tc"><span id="tccur">0:00</span><span class="sep">/</span><span class="tot" id="tctot">0:00</span></span>
   <span class="phint">rueda = scroll · Ctrl+rueda = zoom · Shift+rueda = scroll rápido · espacio = play · arrastra un clip para reubicarlo</span>
  </div>
 </section>
 <aside class="inspector" id="inspector"><div class="insp-empty">Selecciona un clip para editarlo.</div></aside>
</div>

<section class="timeline">
 <div class="tl-bar">
  <div class="zoom"><span class="lbl" style="margin-right:.2rem">Zoom</span>
   <button id="zout" aria-label="Alejar">−</button><button id="zin" aria-label="Acercar">+</button>
   <button class="fit" id="zfit">ajustar</button></div>
  <span class="range" id="range">0:00 – 0:00</span>
  <div class="legend">
   <span><i style="background:var(--k-archive)"></i>archivo</span>
   <span><i style="background:var(--k-stock)"></i>stock</span>
   <span><i style="background:var(--k-kb)"></i>ken burns</span>
   <span><i style="background:var(--k-ai)"></i>IA</span>
   <span><i style="background:repeating-linear-gradient(-45deg,#0000 0 4px,#d98a5f55 4px 6px);border:1px solid var(--neg)"></i>sin cubrir</span>
  </div>
 </div>
 <div class="minimap" id="minimap">
  <canvas class="mm-canvas" id="mm"></canvas><div class="mm-window" id="mmwin"></div><div class="mm-play" id="mmplay"></div>
 </div>
 <div class="tl-scroll" id="scroll">
  <div class="tl-inner" id="inner">
   <div class="lane ruler" id="ruler"></div>
   <div class="lane bands" id="bands"></div>
   <div class="lane wave">{'<span class="wlbl">voz — pista fija</span><img id="waveimg" alt="">' if wave else '<span class="wlbl">voz — aún sin grabar</span>'}</div>
   <div class="lane vtrack" id="vtrack"></div>
   <div class="lane mtrack" id="mtrack"><div class="mclip" id="music"><span class="mono" id="musicname"></span><span class="wv"></span></div></div>
   <div class="playhead" id="playhead"><span class="grab"></span></div>
   <div class="snapguide" id="snap"></div>
  </div>
 </div>
</section>

<footer class="statusbar">
 <span class="ok">beats cubiertos <b id="stcov">{n_beats-n_un} / {n_beats}</b></span>
 <span class="warn">con corrección <b id="stfix">{n_fix}</b></span>
 {'<span class="bad">sin cubrir <b>'+str(n_un)+'</b></span>' if n_un else ''}
 <span>música · duck {data['music']['duck_db']} dB bajo la voz</span>
 <span>salida <b>{data['w']}×{data['h']}</b> · <b>−14 LUFS</b></span>
 <span style="margin-left:auto;color:var(--faint)">picture-lock: pendiente · firma Usuario 002</span>
</footer>

<div class="toast" id="toast"></div><div class="tltip" id="tltip"></div>

<script>
"use strict";
const TL = {payload};
const WAVE = {json.dumps(wave)};
const EPID = {json.dumps(epid)}, SLUG = {json.dumps(slug)};
const SECN = {{"cold open":"COLD OPEN","bumper":"BUMPER","pivote":"PIVOTE","contexto":"CONTEXTO",
 "explicador":"EXPLICADOR","teorías":"TEORÍAS","teorias":"TEORÍAS","cierre":"CIERRE","cta":"CTA"}};
const KIND = {{archivo:"var(--k-archive)",stock:"var(--k-stock)",kb:"var(--k-kb)",ia:"var(--k-ai)",
 "gráfico":"var(--k-graphic)",grafico:"var(--k-graphic)",negro:"var(--k-none)"}};
const KLAB = {{archivo:"archivo",stock:"stock",kb:"ken burns",ia:"IA","gráfico":"gráfico",grafico:"gráfico",negro:"negro"}};
const KVAR = {{archivo:"--k-archive",stock:"--k-stock",kb:"--k-kb",ia:"--k-ai","gráfico":"--k-graphic",grafico:"--k-graphic",negro:"--k-none"}};
const MOTIONS=[["push","empuje"],["pan-h","paneo H"],["pan-v","paneo V"],["static","estático"],["zoom","zoom a detalle"],["cut","clip (sin move)"]];
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const B = TL.beats;
const TOTAL = TL.total;
const fmt = s=>{{s=Math.max(0,Math.round(s));return Math.floor(s/60)+":"+String(s%60).padStart(2,"0");}};
const secname = s=>SECN[s]|| (s||"").toUpperCase();
let PPS=5, sel=null, playing=false, cur=0, raf=0, lastT=0;
const vid = $("#vid");
const inner=$("#inner"), vtrack=$("#vtrack"), ruler=$("#ruler"), bands=$("#bands"), scroll=$("#scroll");
if(WAVE && $("#waveimg")) $("#waveimg").src = WAVE;
$("#tctot").textContent = fmt(TOTAL);
$("#musicname").textContent = (TL.music.bed||"sin pista").split("/").pop();

function layout(){{
  const W = TOTAL*PPS;
  inner.style.width = (W+40)+"px";
  ruler.innerHTML="";
  const step = PPS>10?15:PPS>5?30:PPS>3?60:120;
  for(let s=0;s<=TOTAL;s+=step){{
    const d=document.createElement("div");d.className="tick";d.style.left=(s*PPS)+"px";d.textContent=fmt(s);ruler.appendChild(d);
  }}
  bands.innerHTML="";
  let a=B[0].section, st=B[0].in;
  const runs=[];
  B.forEach(b=>{{if(b.section!==a){{runs.push([a,st,b.in]);a=b.section;st=b.in;}}}});
  runs.push([a,st,TOTAL]);
  runs.forEach(([sec,x0,x1])=>{{
    const w=(x1-x0)*PPS;
    const d=document.createElement("div");d.className="band";
    d.style.left=(x0*PPS)+"px";d.style.width=(w-2)+"px";
    d.textContent = w>46 ? secname(sec) : "";
    d.title=secname(sec);
    bands.appendChild(d);
  }});
  vtrack.innerHTML="";
  B.forEach(b=>{{
    const w=(b.out-b.in)*PPS;
    const el=document.createElement("div");
    el.className="clip"+(b.state==="uncovered"?" uncov":"")
      +((b.marker||"").startsWith("EXPL")?" expl":"")+(w<64?" narrow":"")+(b===sel?" sel":"");
    el.style.left=(b.in*PPS)+"px";el.style.width=(w-2)+"px";el.dataset.n=b.n;
    const col=KIND[b.kind]||"var(--k-none)";
    el.innerHTML=
      '<div class="kbar" style="background:'+col+'"></div>'+
      '<div class="body"><div class="cn"><span style="color:'+col+'">'+String(b.n).padStart(2,"0")+'</span>'+
      '<span>'+(KLAB[b.kind]||b.kind)+'</span></div>'+
      '<div class="ca">'+(b.state==="uncovered"?"— sin asset —":(b.asset||b.file||"—"))+'</div>'+
      '<div class="cd">'+esc(b.frag||"")+'</div></div>'+
      (b.marker?'<span class="badge">'+esc(b.marker)+'</span>':"")+
      (b.fix?'<span class="fixdot"></span>':"")+
      (b.approved&&!b.fix?'<svg class="okdot" viewBox="0 0 16 16"><path fill="currentColor" d="M6.5 11L3 7.5l1-1 2.5 2.4L12 3l1 1z"/></svg>':"")+
      '<span class="grip l"></span><span class="grip r"></span>';
    el.addEventListener("click",ev=>{{if(!ev.target.classList.contains("grip"))select(b.n);}});
    el.addEventListener("pointerenter",ev=>tip(ev,b));
    el.addEventListener("pointermove",tipmove);
    el.addEventListener("pointerleave",tiphide);
    dragClip(el,b);
    vtrack.appendChild(el);
  }});
  const m=TL.music;
  $("#music").style.left=(m.in*PPS)+"px";
  $("#music").style.width=((m.out-m.in)*PPS)+"px";
  placePlayhead(); drawMinimap(); updRange();
}}
function esc(s){{const d=document.createElement("div");d.textContent=s;return d.innerHTML;}}

function updRange(){{
  const v0=scroll.scrollLeft/PPS, v1=(scroll.scrollLeft+scroll.clientWidth)/PPS;
  $("#range").textContent=fmt(v0)+" – "+fmt(Math.min(v1,TOTAL));
  const mmW=$("#minimap").clientWidth;
  $("#mmwin").style.left=(v0/TOTAL*mmW)+"px";
  $("#mmwin").style.width=Math.max(6,(v1-v0)/TOTAL*mmW)+"px";
}}

function drawMinimap(){{
  const c=$("#mm"),dpr=devicePixelRatio||1,w=$("#minimap").clientWidth,h=34;
  c.width=w*dpr;c.height=h*dpr;const x=c.getContext("2d");x.scale(dpr,dpr);x.clearRect(0,0,w,h);
  const cs=getComputedStyle(document.documentElement);
  B.forEach(b=>{{
    const x0=b.in/TOTAL*w, bw=Math.max(1,(b.out-b.in)/TOTAL*w);
    x.fillStyle = b.state==="uncovered" ? "#d98a5f" : cs.getPropertyValue(KVAR[b.kind]||"--k-none").trim();
    x.globalAlpha = b.fix?1:.72; x.fillRect(x0,7,bw-.4,h-14); x.globalAlpha=1;
    if(b.marker){{x.fillStyle="#c9a24a";x.fillRect(x0,2,Math.max(1,bw-.4),3);}}
  }});
  let a=B[0].section;
  B.forEach(b=>{{if(b.section!==a){{a=b.section;const px=b.in/TOTAL*w;
    x.strokeStyle="#0a0908";x.beginPath();x.moveTo(px,0);x.lineTo(px,h);x.stroke();}}}});
}}

function placePlayhead(){{
  $("#playhead").style.left=(cur*PPS)+"px";
  $("#playhead").style.height=(20+2+20+2+40+6+66+30)+"px";
  $("#tccur").textContent=fmt(cur); $("#scrtc").textContent=fmt(cur);
  const b=B.find(x=>cur>=x.in&&cur<x.out)||B[B.length-1];
  $("#scrbeat").textContent="beat "+String(b.n).padStart(2,"0")+" · "+secname(b.section).toLowerCase();
  $("#scrlab").hidden = b.kind!=="ia";
  const mmW=$("#minimap").clientWidth; $("#mmplay").style.left=(cur/TOTAL*mmW)+"px";
  $$(".clip.playing").forEach(c=>c.classList.remove("playing"));
  if(playing){{const el=vtrack.querySelector('.clip[data-n="'+b.n+'"]');if(el)el.classList.add("playing");}}
  if(vid && Math.abs(vid.currentTime-cur)>0.3) try{{vid.currentTime=cur;}}catch(e){{}}
}}
function loop(ts){{
  if(!playing)return;
  if(vid && !vid.paused){{ cur=vid.currentTime; }}
  else {{ if(!lastT)lastT=ts; cur+=(ts-lastT)/1000; lastT=ts; }}
  if(cur>=TOTAL){{cur=TOTAL;setPlaying(false);}}
  placePlayhead();
  const px=cur*PPS;
  if(px<scroll.scrollLeft||px>scroll.scrollLeft+scroll.clientWidth-80) scroll.scrollLeft=px-scroll.clientWidth*.4;
  raf=requestAnimationFrame(loop);
}}
function setPlaying(p){{
  playing=p; lastT=0;
  $("#playi").innerHTML = p?'<path d="M3 2h4v12H3zM9 2h4v12H9z"/>':'<path d="M4 2l10 6-10 6z"/>';
  if(vid){{ if(p){{vid.currentTime=cur;vid.play().catch(()=>{{}});}} else vid.pause(); }}
  if(p)raf=requestAnimationFrame(loop); else cancelAnimationFrame(raf);
  placePlayhead();
}}
$("#play").onclick=()=>setPlaying(!playing);
addEventListener("keydown",e=>{{if(e.code==="Space"&&e.target.tagName!=="TEXTAREA"&&e.target.tagName!=="SELECT"){{e.preventDefault();setPlaying(!playing);}}}});

scroll.addEventListener("pointerdown",e=>{{
  if(e.target.closest(".clip")||e.target.closest(".mclip")||e.target.closest(".playhead"))return;
  const r=inner.getBoundingClientRect();
  cur=Math.max(0,Math.min(TOTAL,(e.clientX-r.left)/PPS)); setPlaying(false); placePlayhead();
}});
$("#playhead .grab").addEventListener("pointerdown",e=>{{
  e.stopPropagation();
  const mv=ev=>{{const r=inner.getBoundingClientRect();
    cur=Math.max(0,Math.min(TOTAL,(ev.clientX-r.left)/PPS));placePlayhead();}};
  const up=()=>{{removeEventListener("pointermove",mv);removeEventListener("pointerup",up);}};
  addEventListener("pointermove",mv);addEventListener("pointerup",up);
}});
scroll.addEventListener("scroll",updRange);

/* wheel: scroll / zoom-at-cursor / fast-scroll */
scroll.addEventListener("wheel",e=>{{
  if(e.ctrlKey||e.metaKey){{
    e.preventDefault();
    const r=inner.getBoundingClientRect();
    const tAt=(e.clientX-r.left)/PPS;
    setZoom(PPS*(e.deltaY<0?1.18:1/1.18));
    scroll.scrollLeft = tAt*PPS - (e.clientX-scroll.getBoundingClientRect().left);
  }} else {{
    e.preventDefault();
    const d = Math.abs(e.deltaX)>Math.abs(e.deltaY) ? e.deltaX : e.deltaY;
    scroll.scrollLeft += d * (e.shiftKey?3:1) * (e.deltaMode===1?16:1);
  }}
}},{{passive:false}});

/* clip drag: reposition + snap to word boundary */
function dragClip(el,b){{
  el.addEventListener("pointerdown",e=>{{
    if(e.target.classList.contains("grip"))return;
    const sx=e.clientX, x0=b.in*PPS; let moved=false; const snap=$("#snap");
    const gsize = 0.5*PPS;
    const mv=ev=>{{
      const dx=ev.clientX-sx;
      if(!moved && Math.abs(dx)<3)return; moved=true; el.style.transition="none";
      let nx=x0+dx; const sn=Math.round(nx/gsize)*gsize;
      if(Math.abs(nx-sn)<7){{nx=sn;snap.style.display="block";snap.style.left=nx+"px";
        snap.style.height=(20+20+40+66+14)+"px";}} else snap.style.display="none";
      el.style.left=nx+"px";
    }};
    const up=()=>{{
      removeEventListener("pointermove",mv);removeEventListener("pointerup",up);
      snap.style.display="none";el.style.transition="";
      if(moved){{
        const nx=Math.round(parseFloat(el.style.left)/gsize)*gsize;
        const shift=(nx/PPS)-b.in;
        b.in=Math.max(0,b.in+shift); b.out=b.out+shift;
        toast('clip <span class="mono">'+String(b.n).padStart(2,"0")+'</span> reubicado a <span class="mono">'+fmt(b.in)+'</span> · «Previsualizar» para verlo');
        layout(); select(b.n);
      }} else select(b.n);
    }};
    addEventListener("pointermove",mv);addEventListener("pointerup",up);
  }});
}}

/* inspector */
function select(n){{
  sel = B.find(b=>b.n===n);
  $$(".clip.sel").forEach(c=>c.classList.remove("sel"));
  const el=vtrack.querySelector('.clip[data-n="'+n+'"]'); if(el)el.classList.add("sel");
  cur=sel.in; setPlaying(false); placePlayhead();
  const b=sel, ins=$("#inspector");
  const showMotion = b.kind!=="negro";
  ins.innerHTML =
   '<div class="insp-head"><span class="n">'+String(b.n).padStart(2,"0")+'</span>'+
     '<h3>'+esc((b.frag||"").slice(0,50)||"beat "+b.n)+'</h3></div>'+
   '<div class="insp-sec">'+secname(b.section)+' · <span class="k">'+fmt(b.in)+'–'+fmt(b.out)+'</span>'+
     (b.marker?' · <span class="marker">'+esc(b.marker)+'</span>':"")+'</div>'+
   (b.state==="uncovered"?'<div class="field"><div class="notebox" style="border-color:var(--neg);color:var(--neg)">Este beat no tiene visual. Elige un asset en 07-selection.md o marca «regenerar».</div></div>':"")+
   '<div class="field"><span class="lbl">Asset ('+(KLAB[b.kind]||b.kind)+')</span>'+
     '<div class="control"><select id="i-asset">'+
       '<option'+(b.asset?' selected':'')+'>'+esc(b.asset||"— sin elegir —")+'</option>'+
       '<option>· elegir otro en 07-selection.md</option></select></div></div>'+
   '<div class="field" style="display:flex;gap:.7rem">'+
     '<div style="flex:1"><span class="lbl">Duración</span><div class="stepper">'+
       '<button data-d="-0.5">−</button><span class="val" id="i-dur">'+(b.out-b.in).toFixed(1)+'s</span><button data-d="0.5">+</button></div></div>'+
     '<div style="flex:1"><span class="lbl">Nudge ± frames</span><div class="stepper">'+
       '<button data-nf="-1">−</button><span class="val" id="i-nudge">'+(b.nudge||0)+'</span><button data-nf="1">+</button></div></div></div>'+
   (showMotion?'<div class="field"><span class="lbl">Movimiento</span><div class="motionrow" id="i-motion">'+
     MOTIONS.map(m=>'<button class="mchip" data-m="'+m[0]+'" aria-pressed="'+(b.motion===m[0])+'">'+m[1]+'</button>').join("")+'</div></div>':"")+
   '<div class="field"><span class="lbl">Regenerar clip — nota para Claude</span>'+
     '<textarea class="fixnote" id="i-fix" placeholder="«más lento» · «empieza a la izquierda» · «dir arriba» · «déjalo 4 s»">'+esc(b.fix||"")+'</textarea></div>'+
   '<label class="approve'+(b.approved?" on":"")+'"><input type="checkbox" id="i-ok"'+(b.approved?" checked":"")+'> clip aprobado</label>';

  $("#i-ok").onchange=ev=>{{ b.approved=ev.target.checked; if(ev.target.checked)b.fix=""; ev.target.closest(".approve").classList.toggle("on",ev.target.checked); layout(); select(n); status(); }};
  $("#i-fix").oninput=ev=>{{ b.fix=ev.target.value.trim(); if(b.fix)b.approved=false; status(); layout2(n); }};
  $$("#i-motion .mchip").forEach(c=>c.onclick=()=>{{ b.motion=c.dataset.m;
    $$("#i-motion .mchip").forEach(x=>x.setAttribute("aria-pressed","false")); c.setAttribute("aria-pressed","true"); }});
  $$('.stepper [data-d]').forEach(x=>x.onclick=()=>{{ b.out=Math.max(b.in+0.5,+(b.out+ +x.dataset.d).toFixed(2));
    $("#i-dur").textContent=(b.out-b.in).toFixed(1)+"s"; layout(); select(n); }});
  $$('.stepper [data-nf]').forEach(x=>x.onclick=()=>{{ b.nudge=(b.nudge||0)+ +x.dataset.nf; $("#i-nudge").textContent=b.nudge; }});
}}
function layout2(n){{ /* light re-style of one clip without full relayout */
  const el=vtrack.querySelector('.clip[data-n="'+n+'"]'); if(!el)return;
  const b=B.find(x=>x.n===n);
  el.querySelector(".fixdot")?.remove();
  if(b.fix){{const s=document.createElement("span");s.className="fixdot";el.appendChild(s);}}
}}

/* tooltip */
const tt=$("#tltip");
function tip(e,b){{
  tt.innerHTML='<b>beat '+String(b.n).padStart(2,"0")+'</b> · <span class="k">'+(KLAB[b.kind]||b.kind)+
    '</span> · <span class="k">'+fmt(b.in)+'–'+fmt(b.out)+'</span>'+
    (b.frag?'<br>'+esc(b.frag):"")+(b.marker?'<br><span class="k">'+esc(b.marker)+'</span>':"")+
    (b.fix?'<br><span style="color:var(--gold)">corrección: '+esc(b.fix)+'</span>':"")+
    (b.state==="uncovered"?'<br><span style="color:var(--neg)">sin visual asignado</span>':"");
  tt.classList.add("show"); tipmove(e);
}}
function tipmove(e){{
  let x=e.clientX+14,y=e.clientY+14;
  if(x+tt.offsetWidth>innerWidth-8)x=e.clientX-tt.offsetWidth-14;
  if(y+tt.offsetHeight>innerHeight-8)y=e.clientY-tt.offsetHeight-14;
  tt.style.left=x+"px";tt.style.top=y+"px";
}}
function tiphide(){{tt.classList.remove("show");}}

/* minimap nav */
const mm=$("#minimap");
function mmSeek(e){{const r=mm.getBoundingClientRect();
  scroll.scrollLeft=((e.clientX-r.left)/r.width)*TOTAL*PPS - scroll.clientWidth/2;}}
mm.addEventListener("pointerdown",e=>{{mmSeek(e);
  const mv=ev=>mmSeek(ev), up=()=>{{removeEventListener("pointermove",mv);removeEventListener("pointerup",up);}};
  addEventListener("pointermove",mv);addEventListener("pointerup",up);}});

/* zoom */
function setZoom(p){{ const mid=(scroll.scrollLeft+scroll.clientWidth/2)/PPS;
  PPS=Math.max(1.2,Math.min(30,p)); layout(); scroll.scrollLeft=mid*PPS-scroll.clientWidth/2; }}
$("#zin").onclick=()=>setZoom(PPS*1.5);
$("#zout").onclick=()=>setZoom(PPS/1.5);
$("#zfit").onclick=()=>{{PPS=Math.max(.85,(scroll.clientWidth-24)/TOTAL);layout();scroll.scrollLeft=0;}};

/* toast */
let toT; function toast(html,ms=2800){{const el=$("#toast");el.innerHTML=html;el.classList.add("show");
  clearTimeout(toT);toT=setTimeout(()=>el.classList.remove("show"),ms);}}

/* status */
function status(){{
  const un=B.filter(b=>b.state==="uncovered").length, fx=B.filter(b=>b.fix).length;
  $("#stcov").textContent=(B.length-un)+" / "+B.length; $("#stfix").textContent=fx;
}}

/* preview + finalize */
async function post(path,body){{
  const r=await fetch("http://localhost:8765"+path,{{method:"POST",
    headers:{{"content-type":"application/json"}},body:JSON.stringify(body)}});
  if(!r.ok)throw new Error("server "+r.status);
  return r.json();
}}
$("#prev").onclick=async()=>{{
  const a=sel?Math.max(0,sel.in-1):Math.max(0,cur-15), b=sel?sel.out+1:cur+15;
  toast('renderizando <span class="mono">'+fmt(a)+'–'+fmt(b)+'</span> a 720p…',60000);
  try{{ const j=await post("/tl-preview",{{ep:EPID,slug:SLUG,t0:a,t1:b}});
    toast('previsualización lista · recarga el reproductor',2600);
    if(vid){{vid.load();vid.currentTime=a;}} }}
  catch(e){{ toast('server no disponible — corre <span class="mono">python tools/assemble.py '+SLUG+' --preview '+Math.floor(a)+' '+Math.ceil(b)+'</span>',5000); }}
}};
$("#fin").onclick=async()=>{{
  const un=B.filter(b=>b.state==="uncovered").length, fx=B.filter(b=>b.fix).length;
  TL.beats=B; TL.finalized=new Date().toISOString().slice(0,10);
  try{{
    const j=await post("/timeline",{{ep:EPID,slug:SLUG,timeline:TL}});
    alert("Stage 9 cerrado.\\n"+(j.msg||"")+
      (fx?("\\n\\n"+fx+" clip(s) con corrección → Claude los regenera."):"")+
      (un?("\\n"+un+" beat(s) sin cubrir → elige asset antes del render final."):""));
  }}catch(e){{
    const blob=new Blob([JSON.stringify(TL,null,1)],{{type:"application/json"}});
    const url=URL.createObjectURL(blob), link=document.createElement("a");
    link.href=url;link.download="09-timeline.json";link.click();
    alert("Server no detectado — descargado 09-timeline.json. Ponlo en la carpeta del episodio y corre:\\npython tools/advance.py fold "+EPID);
  }}
}};

/* init */
status(); layout();
addEventListener("resize",()=>{{drawMinimap();updRange();placePlayhead();}});
if(B.length)select(B[0].n);
scroll.scrollLeft=0;
</script></body></html>
"""


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        sys.exit(2)
    slug = a[0]
    ep = A.EP_DIR / slug
    if not ep.is_dir():
        sys.exit(f"no existe {ep}")
    (ep / OUT).write_text(build(slug), encoding="utf-8")
    print(f"escrito  episodes/{slug}/{OUT}")
    print("siguiente: ábrelo desde el dashboard, ajusta la timeline, «Finalizar Stage 9»")
