#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
edit_timeline.py — Stage 9 review surface: the cutting-room timeline (brain/16).

Renders 09-timeline.json (built by tools/assemble.py) as one page:
  - the VO waveform (fixed spine) with the section bands
  - a block per beat, width ∝ duration, coloured by kind, PROMISE/PAY + EXPLICADOR
    marked, uncovered beats flagged
  - a 720p proxy preview with a scrubbable playhead
  - per-beat inspector: swap asset (real picker + paste a path/URL) · lock a
    duration · nudge · reorder (drag the block past a neighbour) · Ken Burns
    motion · a note for a regen · approve
  - a music lane

You drag / resize / reorder / swap / preview in the browser — no tokens.
**Guardar** autosaves (debounced): dur-lock / slot / nudge / approve / fix are
POSTed to `/tl-save`, the server re-runs `build_timeline` (align() then
`_apply_edits`) and hands the recomputed timeline back. The overrides survive
every later rebuild. "Finalizar Stage 9" flushes the save then folds the gate.

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
    rf = ep / "09-rough.mp4"
    has_rough = rf.exists() and rf.stat().st_size > 0
    has_vo = (ep / "09-vo.m4a").exists()
    e = _h.escape
    epid = slug[:4]
    # the live compositor plays the narrator take continuously (muted) as #face —
    # the 720p proxy if it exists, else the ~800 MB master (still better than a
    # cold seek on every acamara beat).
    _af = next((b["file"] for b in data["beats"]
                if b["kind"] in ("acamara", "a-cámara", "a-camara") and b.get("file")), "")
    take_src = "09-take.mp4" if (ep / "09-take.mp4").exists() else _af
    _rev = next(iter(sorted(ep.glob("assets/*.review.html"))), None)
    review_href = f"http://localhost:8765/episodes/{slug}/assets/{_rev.name}" if _rev else ""

    n_beats = len(data["beats"])
    n_un = sum(1 for b in data["beats"] if b["state"] == "uncovered")
    n_fix = sum(1 for b in data["beats"] if b.get("fix"))
    aligned = data.get("aligned")

    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    try:
        import beat_asset as _BA
        assets_js = json.dumps(_BA.asset_library(slug), ensure_ascii=False).replace("</", "<\\/")
    except Exception:
        assets_js = "[]"

    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sala de montaje · {e(slug)}</title>
{T.FAVICON}
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700&display=swap">
{T.CSS}
{T.TIMELINE_CSS}
<style>
 .screen img#still{{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;background:#000;z-index:1}}
 .screen video#clip{{z-index:1}}
 .screen #vid{{z-index:1}}
 #modeg{{display:inline-flex;border:1px solid var(--line-2);border-radius:6px;overflow:hidden}}
 #modeg button{{border:0;border-radius:0;background:var(--surface-2);color:var(--muted);
   font:inherit;font-size:.72rem;padding:.3rem .7rem;cursor:pointer}}
 #modeg button.on{{background:var(--gold);color:#161109;font-weight:700}}
 #modeg button:disabled{{opacity:.4;cursor:not-allowed}}
 .clip.pace{{box-shadow:inset 0 0 0 2px #a35}}
 .clip.edited{{outline:1px dashed var(--gold);outline-offset:-3px}}
 #save.dirty{{border-color:var(--gold);color:var(--gold)}}
 .btn.sm{{font-size:.68rem;padding:.2rem .5rem}}
 .mixrow{{display:flex;align-items:center;gap:.7rem;padding:.4rem .1rem 0;flex-wrap:wrap}}
 .mixlbl{{font-size:.66rem;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}}
 .mixctl{{display:flex;align-items:center;gap:.35rem;font-size:.7rem;color:var(--muted)}}
 .mixctl input[type=range]{{width:92px;accent-color:var(--gold)}}
 .mixv{{font-family:var(--mono);font-size:.64rem;color:var(--bone);min-width:42px;text-align:right}}
 #scrrot{{position:absolute;inset:0;display:flex;flex-direction:column;gap:.4em;
   align-items:center;justify-content:center;text-align:center;z-index:3;
   font-family:Georgia,"Times New Roman",serif;font-size:clamp(1.4rem,4vw,2.6rem);
   color:#d6cbb5;letter-spacing:.01em;pointer-events:none}}
 #screen:fullscreen{{width:100vw;height:100vh;border:0;border-radius:0;background:#000}}
 #screen:fullscreen::before{{display:none}}
 #screen:fullscreen .tag,#screen:fullscreen .lab{{display:none}}
 #screen:fullscreen #still{{width:100%;height:100%;object-fit:contain}}
 #screen:fullscreen #scrrot{{font-size:clamp(2rem,6vw,4rem)}}
 #fs{{font-size:.68rem;padding:.2rem .5rem;white-space:nowrap}}
</style>
</head><body class="tl">
<header class="topbar">
 <span class="brand" style="font-size:1rem">Conquest</span>
 <span class="crumb"><b>Sala de montaje</b></span>
 <span class="ep">{e(epid)}</span>
 <span class="pill {'on' if not n_fix and not n_un else 'warn'}" style="font-size:.68rem"><span class="dot"></span>{
   'alineado a la voz' if aligned else 'tiempos del shotlist'}</span>
 <span class="spacer"></span>
 <button class="btn" id="rrough" data-tip="Renderiza el vídeo entero a un borrador 720p (con voz, música, Ken Burns y cortes reales — sin grade) en segundo plano. Tarda unos minutos; cuando termine, míralo en «corte renderizado». Guarda antes.">{'Re-renderizar' if has_rough else 'Renderizar'}</button>
 <a class="btn ghost" target="_blank" href="http://localhost:8765/episodes/{e(slug)}/assets/graphic/_index.html" data-tip="Abre en otra pestaña el índice de gráficos del episodio (G1, G3, G4…) para comprobar cómo quedaron antes de montarlos. No modifica nada.">Gráficos</a>
 {f'<a class="btn ghost" target="_blank" href="{e(review_href)}" data-tip="Abre la sala de transcripción/recorte de la toma en otra pestaña — para revisar el texto de la voz, marcar retomas y ajustar los cortes. Al aplicar cambios allí, re-corre el Stage 8 y esta línea se recalcula.">Transcripción</a>' if review_href else ''}
 <button class="btn" id="save" data-tip="Fija en 09-timeline.json tus cambios de duración (dur_lock), orden (slot) y mezcla, y recalcula la línea contra la voz. Hay autoguardado cada pocos segundos; el botón se pone en dorado con «•» si queda algo sin guardar.">Guardar</button>
 <button class="btn primary" id="fin" data-tip="Cierra el Stage 9: guarda, avisa de los beats sin visual o con corrección pendiente, y marca el corte como listo para el render final. Los clips marcados «corrección» se los pasa a Claude para regenerar.">Finalizar</button>
 <a class="btn ghost" href="http://localhost:8765/" data-tip="Vuelve al dashboard de Conquest. El autoguardado ya conserva tus cambios; no se renderiza nada.">← Panel</a>
</header>

<div class="work">
 <section class="preview">
  <div class="screen" id="screen">
   {'<video id="vid" preload="metadata" src="09-rough.mp4#t=0.01"></video>' if has_rough else ''}
   <img id="still" alt="" hidden>
   <video id="clip" playsinline preload="auto" hidden></video>
   <video id="face" playsinline muted preload="auto" hidden {f'src="{e(take_src)}"' if take_src else ''}></video>
   <audio id="vo" preload="auto" {'src="09-vo.m4a"' if has_vo else ''}></audio>
   <audio id="bed" preload="auto" loop></audio>
   <div class="frame" id="frame" hidden>
    <div class="big" id="scrtc">0:00</div>
    <div id="scrbeat">—</div>
    <div id="scrrot" hidden></div>
   </div>
   <span class="tag" id="scrtag">en vivo · voz + toma / clip · sin Ken Burns · sin grade</span>
   <span class="lab" id="scrlab" hidden>Ilustración — Conquest</span>
  </div>
  <div class="transport">
   <button class="play" id="play" aria-label="Reproducir">
     <svg viewBox="0 0 16 16" id="playi"><path d="M4 2l10 6-10 6z"/></svg></button>
   <span class="tc"><span id="tccur">0:00</span><span class="sep">/</span><span class="tot" id="tctot">0:00</span></span>
   <span class="modeg" id="modeg">
     <button class="on" data-mode="live">en vivo</button>
     <button data-mode="rough" {'disabled' if not has_rough else ''}>corte renderizado</button>
   </span>
   <button class="btn ghost sm" id="fs" style="margin-left:.2rem" data-tip="Expande el reproductor a pantalla completa. En «corte renderizado» salen los controles del vídeo; en «en vivo» usa espacio para play/pausa y Esc para salir.">⛶ pantalla completa</button>
   <span class="phint">rueda = scroll · Ctrl+rueda = zoom · espacio = play · arrastra un clip para reubicarlo</span>
  </div>
  <div class="mixrow" id="mixrow">
   <span class="mixlbl">Mezcla</span>
   <label class="mixctl">Voz <input type="range" id="mx-vo" min="-6" max="6" step="0.5"><span id="mx-vo-v" class="mixv"></span></label>
   <label class="mixctl">Música <input type="range" id="mx-bed" min="-44" max="-10" step="1"><span id="mx-bed-v" class="mixv"></span></label>
   <label class="mixctl">Ducking <input type="range" id="mx-duck" min="0" max="18" step="1"><span id="mx-duck-v" class="mixv"></span></label>
   <button class="btn ghost sm" id="mx-reset">↺</button>
  </div>
 </section>
 <aside class="inspector" id="inspector">
   <div class="insp-cap">Inspector del beat
     <span class="qm" data-tip="Aquí editas el beat seleccionado: su visual (cambiar / traer / quitar), su duración y encuadre, la nota de regeneración, y la estructura (fusionar con un vecino, eliminar, partir, añadir uno nuevo). Los cambios de asset y estructura son retroactivos al shotlist y a las fases anteriores.">?</span>
   </div>
   <div id="inspbody"><div class="insp-empty">Selecciona un clip para editarlo.</div></div>
 </aside>
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
const ASSETS = {assets_js};
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
let B = TL.beats;
let TOTAL = TL.total;
const fmt = s=>{{s=Math.max(0,Math.round(s));return Math.floor(s/60)+":"+String(s%60).padStart(2,"0");}};
const secname = s=>SECN[s]|| (s||"").toUpperCase();
let PPS=5, sel=null, playing=false, cur=0, raf=0, lastT=0;
let _mmW=0, _playEl=null, _lastTc="";      // per-frame caches (see placePlayhead)
const vid = $("#vid"), still=$("#still"), clip=$("#clip"), face=$("#face"), vo=$("#vo"), bed=$("#bed");
const inner=$("#inner"), vtrack=$("#vtrack"), ruler=$("#ruler"), bands=$("#bands"), scroll=$("#scroll");
if(WAVE && $("#waveimg")) $("#waveimg").src = WAVE;
$("#tctot").textContent = fmt(TOTAL);
$("#musicname").textContent = (TL.music.bed||"sin pista").split("/").pop();

// ---- live compositor: VO m4a as master clock, one still/clip on screen ----
let MODE = vo.getAttribute("src") ? "live" : "rough";
const IMG=/\\.(png|jpe?g|webp|gif|tiff?)$/i, VIDF=/\\.(mp4|webm|mov)$/i;
const db2g = d=>Math.min(1,Math.pow(10,d/20));
TL.music = TL.music || {{}};
if(TL.music.bed_db==null)TL.music.bed_db=-30;
if(TL.music.vo_gain_db==null)TL.music.vo_gain_db=0;
if(TL.music.duck_db==null)TL.music.duck_db=8;
function applyMix(){{
  const m=TL.music;
  // live can't sidechain-duck or boost past 1.0 — approximate the balance:
  // bed ≈ bed_db − most of the duck − (any voice boost); voice only shows cuts
  if(bed) bed.volume = db2g((+m.bed_db) - (+m.duck_db)*0.6 - Math.max(0,+m.vo_gain_db));
  vo.volume = db2g(Math.min(0,+m.vo_gain_db));
  const set=(id,v,suf)=>{{const s=$(id);if(s)s.value=v;const o=$(id+"-v");if(o)o.textContent=(v>0?"+":"")+v+suf;}};
  set("#mx-vo",m.vo_gain_db," dB"); set("#mx-bed",m.bed_db," dB"); set("#mx-duck",m.duck_db," dB");
}}
if(bed && TL.music.bed){{ bed.src="/"+TL.music.bed; }}
["mx-vo","mx-bed","mx-duck"].forEach(id=>{{
  const key={{"mx-vo":"vo_gain_db","mx-bed":"bed_db","mx-duck":"duck_db"}}[id];
  $("#"+id)?.addEventListener("input",e=>{{ TL.music[key]=+e.target.value; applyMix(); markDirty(); }});
}});
$("#mx-reset")?.addEventListener("click",()=>{{
  Object.assign(TL.music,{{bed_db:-30,vo_gain_db:0,duck_db:8}}); applyMix(); markDirty(); }});
applyMix();
let shownBeat=-1, clipSrc="", lastFaceSync=0;
const AC=new Set(["acamara","a-cámara","a-camara"]);
function assetURL(f){{ return f ? (f.startsWith("assets/")? f : "assets/"+f) : ""; }}
function syncFace(hard){{
  // #face plays the narrator take start→end alongside #vo (muted); keep it near
  // the master clock without a cold seek on every beat.
  if(!face.getAttribute("src")) return;
  const d=Math.abs(face.currentTime-cur);
  if(hard || d>1.2){{ try{{face.currentTime=cur;}}catch(e){{}} lastFaceSync=cur; }}
  if(playing && face.paused) face.play().catch(()=>{{}});
}}
function updateScreen(force){{
  const b=B.find(x=>cur>=x.in&&cur<x.out)||B[B.length-1];
  $("#scrlab").hidden = !(b.kind==="ia"||/recre/i.test(b.label||""));
  if(MODE==="rough"){{ if(vid) vid.hidden=false; still.hidden=true; clip.hidden=true; face.hidden=true;
    clip.pause(); face.pause(); $("#frame").hidden=true; return; }}
  if(vid) vid.hidden=true;
  vo.muted=false;                              // #vo (m4a) always carries the voice
  const isAC=AC.has(b.kind);
  if(isAC) syncFace(false);                    // cheap drift-correct every frame
  // same beat, not a video b-roll → nothing on screen changes; skip the DOM work.
  // (acamara included now: the hard re-seek only needs to happen on the beat switch.)
  if(!force && b.n===shownBeat && !VIDF.test(b.file||"")){{ return; }}
  shownBeat=b.n;
  const f=b.file||"";
  $("#frame").hidden = !(b.kind==="negro"||(!f&&!isAC));
  if(b.kind==="negro"||(!f&&!isAC)){{ still.hidden=true; clip.hidden=true; face.hidden=true; clip.pause();
    const rot = (b.kind==="negro" && (b.label||"").trim()) ? b.label.trim() : "";
    $("#scrrot").hidden = !rot;
    $("#scrrot").innerHTML = rot ? rot.split(/\\s*\\/\\s*/).map(s=>"<div>"+s+"</div>").join("") : "";
    $("#scrbeat").textContent = rot ? "" : (b.kind==="negro" ? "— negro —"
      : "beat "+String(b.n).padStart(2,"0")+" · sin asset");
    return; }}
  $("#scrrot").hidden = true;
  if(isAC){{                                   // narrator on camera → the continuous take
    if(!face.getAttribute("src")){{           // no take / no proxy → labelled frame
      face.hidden=true; still.hidden=true; clip.hidden=true; clip.pause();
      $("#frame").hidden=false; $("#scrrot").hidden=true;
      $("#scrbeat").textContent="beat "+String(b.n).padStart(2,"0")+" · a cámara (sin toma)";
      return;
    }}
    syncFace(true); face.hidden=false; still.hidden=true; clip.hidden=true; clip.pause();
    return;
  }}
  face.hidden=true;                            // (face keeps playing behind the b-roll)
  if(IMG.test(f)){{
    const u=assetURL(f); if(still.getAttribute("src")!==u) still.src=u;
    still.hidden=false; clip.hidden=true; clip.pause(); return;
  }}
  if(VIDF.test(f)){{
    const u=assetURL(f);
    if(clipSrc!==u){{ clipSrc=u; clip.src=u; }}
    const localT=Math.max(0, cur-b.in);
    if(Math.abs(clip.currentTime-localT)>0.5){{ try{{clip.currentTime=localT;}}catch(e){{}} }}
    clip.volume=0;                             // b-roll video is always silent (voice is #vo)
    if(playing && clip.paused) clip.play().catch(()=>{{}});
    still.hidden=true; clip.hidden=false; return;
  }}
  // unknown ext → treat as still
  const u=assetURL(f); if(still.getAttribute("src")!==u) still.src=u;
  still.hidden=false; clip.hidden=true;
}}
function setMode(m){{
  if(m==="rough"&&!vid) return;
  setPlaying(false);
  MODE=m; shownBeat=-1; clipSrc="";
  $$("#modeg button").forEach(x=>x.classList.toggle("on",x.dataset.mode===m));
  $("#scrtag").textContent = m==="rough" ? "corte renderizado · 720p · sin grade"
    : "en vivo · voz + toma / clip · sin Ken Burns · sin grade";
  still.hidden=true; clip.hidden=true; face.hidden=true; face.pause();
  updateScreen(true);
}}
$$("#modeg button").forEach(x=>x.onclick=()=>setMode(x.dataset.mode));

function layout(){{
  _mmW=0; _playEl=null;                       // clips get rebuilt below — drop stale refs
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
      +((b.marker||"").startsWith("EXPL")?" expl":"")+(w<64?" narrow":"")+(b===sel?" sel":"")
      +(b.pace?" pace":"")+((b.dur_lock||typeof b.slot==="number")?" edited":"");
    el.style.left=(b.in*PPS)+"px";el.style.width=(w-2)+"px";el.dataset.n=b.n;
    const col=KIND[b.kind]||"var(--k-none)";
    el.innerHTML=
      '<div class="kbar" style="background:'+col+'"></div>'+
      '<div class="body"><div class="cn"><span style="color:'+col+'">'+String(b.n).padStart(2,"0")+'</span>'+
      '<span>'+(KLAB[b.kind]||b.kind)+'</span></div>'+
      '<div class="ca">'+(b.state==="uncovered"?"— sin asset —":(b.asset||b.file||"—"))+'</div>'+
      '<div class="cd">'+esc(b.frag||"")+'</div></div>'+
      (b.marker?'<span class="badge">'+esc(b.marker)+'</span>':"")+
      (b.pace?'<span class="badge" style="background:#5a2f2f;color:#e0a89c" title="'+b.pace+'s en un visual — parte el beat o corta a cámara">⚠ '+Math.round(b.pace)+'s</span>':"")+
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
function fileB64(f){{return new Promise((res,rej)=>{{const r=new FileReader();
  r.onload=()=>res(String(r.result).split(",")[1]); r.onerror=rej; r.readAsDataURL(f);}});}}

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
  const ph=$("#playhead");
  ph.style.left=(cur*PPS)+"px";
  if(!ph.style.height) ph.style.height=(20+2+20+2+40+6+66+30)+"px";
  const tc=fmt(cur);
  if(tc!==_lastTc){{ $("#tccur").textContent=tc; $("#scrtc").textContent=tc; _lastTc=tc; }}
  const b=B.find(x=>cur>=x.in&&cur<x.out)||B[B.length-1];
  if(!_mmW) _mmW=$("#minimap").clientWidth || 1;   // clientWidth forces reflow — read once
  $("#mmplay").style.left=(cur/TOTAL*_mmW)+"px";
  const want = playing ? vtrack.querySelector('.clip[data-n="'+b.n+'"]') : null;
  if(want!==_playEl){{ if(_playEl)_playEl.classList.remove("playing"); if(want)want.classList.add("playing"); _playEl=want; }}
}}
function loop(ts){{
  if(!playing)return;
  if(MODE==="rough" && vid && !vid.paused){{ cur=vid.currentTime; }}
  else if(MODE==="live" && !vo.paused){{ cur=vo.currentTime; }}
  else {{ if(!lastT)lastT=ts; cur+=(ts-lastT)/1000; lastT=ts; }}
  if(cur>=TOTAL){{cur=TOTAL;setPlaying(false);}}
  // music bed: only between music.in and music.out (nothing over the CTA coda)
  if(bed && bed.src && MODE==="live"){{
    const on = cur>(TL.music.in||0) && cur<(TL.music.out||1e9);
    if(on && bed.paused && playing) bed.play().catch(()=>{{}});
    else if(!on && !bed.paused) bed.pause();
  }}
  updateScreen();
  placePlayhead();
  const px=cur*PPS;
  if(px<scroll.scrollLeft||px>scroll.scrollLeft+scroll.clientWidth-80) scroll.scrollLeft=px-scroll.clientWidth*.4;
  raf=requestAnimationFrame(loop);
}}
function setPlaying(p){{
  playing=p; lastT=0;
  $("#playi").innerHTML = p?'<path d="M3 2h4v12H3zM9 2h4v12H9z"/>':'<path d="M4 2l10 6-10 6z"/>';
  if(!p){{ try{{vid&&vid.pause();}}catch(e){{}} vo.pause(); bed&&bed.pause(); clip.pause(); face.pause(); }}
  else if(MODE==="rough" && vid){{ vid.currentTime=cur; vid.play().catch(()=>{{}}); }}
  else {{
    vo.currentTime=cur; vo.play().catch(()=>{{}});
    if(face.getAttribute("src")){{ try{{face.currentTime=cur;}}catch(e){{}} face.play().catch(()=>{{}}); }}
    if(bed && bed.src && cur>(TL.music.in||0) && cur<(TL.music.out||1e9)) bed.play().catch(()=>{{}});
  }}
  updateScreen(true);
  if(p)raf=requestAnimationFrame(loop); else cancelAnimationFrame(raf);
  placePlayhead();
}}
// a hidden tab throttles rAF and pauses the muted #face — catch up on return
document.addEventListener("visibilitychange",()=>{{
  if(document.visibilityState!=="visible"||!playing||MODE!=="live")return;
  cur=vo.currentTime; syncFace(true); updateScreen(true);
}});
function seekTo(t){{
  cur=Math.max(0,Math.min(TOTAL,t));
  if(MODE==="rough" && vid){{ try{{vid.currentTime=cur;}}catch(e){{}} }}
  else {{ try{{vo.currentTime=cur;}}catch(e){{}} if(face.getAttribute("src")){{try{{face.currentTime=cur;}}catch(e){{}}}} }}
  updateScreen(true); placePlayhead();
}}
$("#play").onclick=()=>setPlaying(!playing);
addEventListener("keydown",e=>{{if(e.code==="Space"&&e.target.tagName!=="TEXTAREA"&&e.target.tagName!=="SELECT"){{e.preventDefault();setPlaying(!playing);}}}});

scroll.addEventListener("pointerdown",e=>{{
  if(e.target.closest(".clip")||e.target.closest(".mclip")||e.target.closest(".playhead"))return;
  const r=inner.getBoundingClientRect();
  setPlaying(false); seekTo((e.clientX-r.left)/PPS);
}});
$("#playhead .grab").addEventListener("pointerdown",e=>{{
  e.stopPropagation();
  const mv=ev=>{{const r=inner.getBoundingClientRect();
    seekTo((ev.clientX-r.left)/PPS);}};
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

/* drag the clip body = reorder (the VO stays; which picture shows when changes).
   drag the right grip = lock this beat's duration (steals from the next beat). */
function slotKey(x){{ return typeof x.slot==="number" ? x.slot : B.indexOf(x); }}
function dragClip(el,b){{
  el.addEventListener("pointerdown",e=>{{
    if(e.target.classList.contains("grip")) return;
    const sx=e.clientX, x0=b.in*PPS; let moved=false;
    const mv=ev=>{{
      const dx=ev.clientX-sx;
      if(!moved && Math.abs(dx)<4) return;
      moved=true; el.style.transition="none"; el.style.zIndex=9; el.style.opacity=.85;
      el.style.left=(x0+dx)+"px";
    }};
    const up=()=>{{
      removeEventListener("pointermove",mv); removeEventListener("pointerup",up);
      el.style.transition=""; el.style.zIndex=""; el.style.opacity="";
      if(!moved){{ select(b.n); return; }}
      const cx=(parseFloat(el.style.left)+el.offsetWidth/2)/PPS;         // drop centre, s
      const others=B.filter(x=>x!==b);
      let i=others.findIndex(x=>((x.in+x.out)/2)>cx); if(i<0) i=others.length;
      const before = i>0 ? slotKey(others[i-1]) : slotKey(others[0])-1;
      const after  = i<others.length ? slotKey(others[i]) : slotKey(others[others.length-1])+1;
      b.slot = (before+after)/2;
      toast('beat <span class="mono">'+String(b.n).padStart(2,"0")+'</span> → nueva posición · guardando…',2500);
      markDirty(); layout(); select(b.n);
    }};
    addEventListener("pointermove",mv); addEventListener("pointerup",up);
  }});
  const gr=el.querySelector(".grip.r");
  if(gr) gr.addEventListener("pointerdown",e=>{{
    e.stopPropagation();
    const sx=e.clientX, w0=el.offsetWidth;
    const mv=ev=>{{ el.style.width=Math.max(16,w0+(ev.clientX-sx))+"px"; }};
    const up=()=>{{
      removeEventListener("pointermove",mv); removeEventListener("pointerup",up);
      b.dur_lock=Math.max(1,+(el.offsetWidth/PPS).toFixed(1));
      b.out=+(b.in+b.dur_lock).toFixed(2);
      toast('beat <span class="mono">'+String(b.n).padStart(2,"0")+'</span> → '+b.dur_lock+'s (fija) · guardando…',2500);
      markDirty(); layout(); select(b.n);
    }};
    addEventListener("pointermove",mv); addEventListener("pointerup",up);
  }});
  /* left grip = move the boundary with the previous beat: drag left ⇒ this beat
     grows backwards and the previous one shrinks (we lock the previous beat). */
  const gl=el.querySelector(".grip.l");
  if(gl) gl.addEventListener("pointerdown",e=>{{
    e.stopPropagation();
    const idx=B.indexOf(b); if(idx<=0){{ toast("el primer beat no se puede alargar hacia atrás",2200); return; }}
    const prev=B[idx-1];
    const pel=vtrack.querySelector('.clip[data-n="'+prev.n+'"]');
    const sx=e.clientX, L0=b.in*PPS, W0=el.offsetWidth;
    const pL0=prev.in*PPS, pW0=pel?pel.offsetWidth:(prev.out-prev.in)*PPS;
    const mv=ev=>{{
      let d=ev.clientX-sx;
      d=Math.max(-(pW0-14), Math.min(W0-14, d));   // keep both clips on screen
      el.style.left=(L0+d)+"px"; el.style.width=(W0-d)+"px";
      if(pel) pel.style.width=(pW0+d)+"px";
    }};
    const up=()=>{{
      removeEventListener("pointermove",mv); removeEventListener("pointerup",up);
      const newBound=+((parseFloat(el.style.left)/PPS)).toFixed(2);
      prev.dur_lock=Math.max(1,+((newBound-prev.in)).toFixed(1));
      prev.out=+(prev.in+prev.dur_lock).toFixed(2);
      b.in=prev.out;
      toast('beat <span class="mono">'+String(prev.n).padStart(2,"0")+'</span> → '+prev.dur_lock+'s (fija) · guardando…',2500);
      markDirty(); layout(); select(b.n);
    }};
    addEventListener("pointermove",mv); addEventListener("pointerup",up);
  }});
}}

/* inspector — asset swap */
const SWAPPABLE=new Set(["archivo","stock","kb","ia","gráfico","grafico"]);
function assetOpts(b){{
  const g={{}}; ASSETS.forEach(a=>{{ (g[a.sub]=g[a.sub]||[]).push(a); }});
  let h="";
  ["graphic","archive","video","stock","kb","ai","intro"].forEach(sub=>{{
    if(!g[sub])return;
    h+='<optgroup label="'+sub+'">';
    g[sub].forEach(a=>{{ h+='<option value="'+esc(a.id)+'"'+(a.id===b.asset?' selected':'')+'>'+esc(a.id)+(a.video?'  ▸ vídeo':'')+'</option>'; }});
    h+='</optgroup>';
  }});
  return h;
}}
async function beatEdit(body, msgSel){{
  const msg = msgSel && $(msgSel); if(msg){{msg.hidden=false;msg.textContent='aplicando… (puede tardar)';}}
  try{{
    const r=await fetch("/beat-asset",{{method:"POST",headers:{{"content-type":"application/json"}},
      body:JSON.stringify(Object.assign({{ep:EPID,slug:SLUG,timeline:TL}},body))}});
    const j=await r.json().catch(()=>({{error:"respuesta ilegible del server"}}));
    if(!r.ok||j.error){{ if(msg)msg.textContent='⚠ '+(j.error||('server '+r.status)); toast('⚠ '+(j.error||r.status),5000); return null; }}
    if(j.timeline && j.timeline.beats){{         // structural edit → reload the whole timeline
      const keep = j.n || (sel && sel.n);
      Object.assign(TL,j.timeline); B=TL.beats; TOTAL=TL.total||TOTAL; if(typeof applyMix==="function")applyMix();
      $("#tctot").textContent=fmt(TOTAL); shownBeat=-1; clipSrc="";
      status(); layout();
      if(keep!=null && B.find(x=>x.n===keep)) select(keep);
      else $("#inspbody").innerHTML='<div class="insp-empty">Selecciona un clip.</div>';
    }}
    if(msg)msg.textContent='✓ '+(j.note||j.asset||'hecho');
    toast('✓ '+(j.note||('beat '+(j.n||'')+' → '+j.asset)),4000);
    return j;
  }}catch(e){{ if(msg)msg.textContent='⚠ server no disponible ('+e+')'; return null; }}
}}
async function applyAsset(n,body){{
  const j=await beatEdit(Object.assign({{n:n}},body),"#i-amsg");
  if(!j || (j.timeline))return;               // structural already reloaded
  const bt=B.find(x=>x.n===n); if(!bt)return;
  bt.asset=j.asset; bt.file=j.file; bt.state=j.state||bt.state;
  if(j.tipo)bt.kind=j.tipo; if(j.motion)bt.motion=j.motion;
  shownBeat=-1; clipSrc=""; layout(); select(n); updateScreen(true); status();
}}

/* inspector */
function select(n){{
  sel = B.find(b=>b.n===n);
  $$(".clip.sel").forEach(c=>c.classList.remove("sel"));
  const el=vtrack.querySelector('.clip[data-n="'+n+'"]'); if(el)el.classList.add("sel");
  setPlaying(false); seekTo(sel.in);
  const b=sel, ins=$("#inspbody");
  const showMotion = b.kind!=="negro";
  ins.innerHTML =
   '<div class="insp-head"><span class="n">'+String(b.n).padStart(2,"0")+'</span>'+
     '<h3>'+esc((b.frag||"").slice(0,50)||"beat "+b.n)+'</h3></div>'+
   '<div class="insp-sec">'+secname(b.section)+' · <span class="k">'+fmt(b.in)+'–'+fmt(b.out)+'</span>'+
     (b.marker?' · <span class="marker">'+esc(b.marker)+'</span>':"")+'</div>'+
   (b.state==="uncovered"?'<div class="field"><div class="notebox" style="border-color:var(--neg);color:var(--neg)">Este beat aún no tiene visual — elige uno abajo o pega una ruta/URL.</div></div>':"")+
   (SWAPPABLE.has(b.kind)
    ? ('<div class="field"><span class="lbl">Asset ('+(KLAB[b.kind]||b.kind)+')</span>'+
       '<div class="control"><select id="i-asset" data-tip="Reemplaza el visual del beat por otro recurso que ya está en assets/. El cambio se escribe en el shotlist (06) y es retroactivo: picks, timeline y 07-assets se actualizan solos.">'+
         '<option value="">'+(b.asset?esc(b.asset):"— sin elegir —")+'</option>'+assetOpts(b)+
       '</select></div>'+
       '<div class="control" style="margin-top:.4rem;display:flex;gap:.4rem;flex-wrap:wrap">'+
         '<button class="btn" id="i-abrowse" data-tip="Abre el explorador de archivos de tu equipo para traer una imagen o vídeo como visual de este beat. Se copia a assets/, se fija en _index.json y se cablea al beat.">Examinar…</button>'+
         '<input id="i-asrc" placeholder="o pega una URL directa" style="flex:1;min-width:120px" data-tip="Pega una URL directa a una imagen/vídeo (o un id de asset ya en la biblioteca). Pexels y Pixabay se resuelven a la descarga real.">'+
         '<button class="btn ghost" id="i-ago" data-tip="Descarga lo que haya en el campo de la izquierda y lo asigna a este beat.">traer URL</button>'+
         '<input type="file" id="i-afile" accept="image/*,video/*" hidden></div>'+
       '<div class="notebox" id="i-amsg" hidden></div></div>')
    : '<div class="field"><span class="lbl">Asset</span><div class="notebox muted">este beat es «'+(KLAB[b.kind]||b.kind)+'» — no lleva asset que cambiar</div></div>')+
   '<div class="field" style="display:flex;gap:.7rem">'+
     '<div style="flex:1" data-tip="Fija la duración del beat en segundos (dur_lock). El tiempo se le quita o se le da al beat siguiente; ningún vecino baja de su mínimo (2,8 s b-roll · 2,5 s a-cámara · 5 s gráfico). Para más, usa fusionar o partir.">'+
       '<span class="lbl">Duración</span><div class="stepper">'+
       '<button data-d="-0.5">−</button><span class="val" id="i-dur">'+
         (b.dur_lock?b.dur_lock.toFixed(1)+'s (fija)':(b.out-b.in).toFixed(1)+'s')+
       '</span><button data-d="0.5">+</button></div></div>'+
     '<div style="flex:1" data-tip="Adelanta o atrasa el punto de entrada del clip ± fotogramas, sin mover la frontera del beat. Para cuadrar un gesto, un pico de la música o un corte de cámara.">'+
       '<span class="lbl">Nudge ± frames</span><div class="stepper">'+
       '<button data-nf="-1">−</button><span class="val" id="i-nudge">'+(b.nudge||0)+'</span><button data-nf="1">+</button></div></div></div>'+
   ((b.dur_lock||typeof b.slot==="number")
     ? '<div class="field"><div class="notebox" style="border-color:var(--gold)">'+
       (b.dur_lock?'duración fija · ':'')+(typeof b.slot==="number"?'reordenado · ':'')+
       '<a href="#" id="i-reset" style="color:var(--gold)">↺ restablecer este beat</a></div></div>' : "")+
   (showMotion?'<div class="field" data-tip="Movimiento de cámara sobre el plano en el render final. Los gráficos siempre se mueven (nunca estáticos); el vídeo B-roll nunca lleva Ken Burns. «corte» = plano fijo.">'+
     '<span class="lbl">Movimiento</span><div class="motionrow" id="i-motion">'+
     MOTIONS.map(m=>'<button class="mchip" data-m="'+m[0]+'" aria-pressed="'+(b.motion===m[0])+'">'+m[1]+'</button>').join("")+'</div></div>':"")+
   '<div class="field" data-tip="Instrucción para que Claude regenere este clip al cerrar el Stage 9: «más lento», «empieza a la izquierda», «dir. arriba», «déjalo 4 s»… Al escribir aquí, el clip deja de estar aprobado.">'+
     '<span class="lbl">Regenerar clip — nota para Claude</span>'+
     '<textarea class="fixnote" id="i-fix" placeholder="«más lento» · «empieza a la izquierda» · «dir arriba» · «déjalo 4 s»">'+esc(b.fix||"")+'</textarea></div>'+
   '<label class="approve'+(b.approved?" on":"")+'" data-tip="Marca el clip como bueno para el render final. Borra cualquier nota de regeneración de arriba.">'+
     '<input type="checkbox" id="i-ok"'+(b.approved?" checked":"")+'> clip aprobado</label>'+
   '<div class="field" style="margin-top:.5rem;border-top:1px solid var(--line-2);padding-top:.5rem">'+
     '<span class="lbl">Estructura</span>'+
     '<div style="display:flex;flex-wrap:wrap;gap:.35rem">'+
       (SWAPPABLE.has(b.kind)?'<button class="btn ghost sm" id="i-clear" data-tip="Deja el beat sin visual (sin cubrir). El tramo de voz sigue igual; le asignas un recurso después. No cambia la duración.">✕ quitar visual</button>':"")+
       '<button class="btn ghost sm" id="i-mprev" data-tip="Funde este beat en el anterior: el plano del anterior pasa a cubrir también este tramo de voz. Se renumera la espina y se reescriben picks / timeline / prosa / 07-assets.">⤺ fusionar anterior</button>'+
       '<button class="btn ghost sm" id="i-mnext" data-tip="Funde este beat en el siguiente: el plano del siguiente cubre también este tramo. Renumera y reescribe las fases anteriores.">fusionar siguiente ⤻</button>'+
       '<button class="btn ghost sm" id="i-del" style="color:var(--neg)" data-tip="Elimina el beat entero. El tramo de voz lo reparten los vecinos al realinear. Renumera la espina y reescribe picks / timeline / prosa / 07-assets / source-log.">🗑 eliminar beat</button>'+
       '<button class="btn ghost sm" id="i-split" data-tip="Parte el beat en dos por donde esté el cabezal (llévalo dentro del beat primero). Las dos mitades conservan el mismo plano; reasignas el visual de la 2ª. El corte se ajusta a la palabra más cercana de la voz.">✂ partir aquí</button>'+
       '<button class="btn ghost sm" id="i-addb" data-tip="Inserta un beat nuevo justo después de este. Necesita un fragmento de la voz escrito verbatim para colocarlo en el tiempo; roba duración a los vecinos.">＋ beat después</button></div>'+
     '<div class="notebox" id="i-smsg" hidden></div>'+
     '<div id="i-addform" hidden style="margin-top:.4rem;display:flex;flex-direction:column;gap:.3rem">'+
       '<textarea id="i-af-frag" rows="2" placeholder="fragmento de la voz para el beat nuevo (verbatim de la VO)" data-tip="Copia aquí, palabra por palabra, la frase de la voz que suena durante el beat nuevo. align() la busca en la transcripción real para colocar el beat; si no es idéntica, el beat cae mal y puede fusionarse solo."></textarea>'+
       '<div style="display:flex;gap:.3rem;flex-wrap:wrap"><select id="i-af-kind" data-tip="Tipo del beat nuevo. «acamara» sale de la toma sola y «negro» no llevan asset; los demás necesitan un visual (ahora o después).">'+
         ["archivo","stock","acamara","gráfico","ia","negro"].map(k=>'<option>'+k+'</option>').join("")+'</select>'+
         '<button class="btn" id="i-af-browse" data-tip="Trae el visual del beat nuevo desde un archivo de tu equipo.">Examinar…</button>'+
         '<input id="i-af-src" placeholder="o URL / id de asset (opcional)" style="flex:1;min-width:110px" data-tip="Alternativa a Examinar: URL directa o id de un asset ya en la biblioteca. Opcional — puedes crear el beat sin visual.">'+
         '<button class="btn" id="i-af-go" data-tip="Crea el beat: inserta la fila en el shotlist, renumera la espina y reconstruye la línea.">añadir</button>'+
         '<input type="file" id="i-af-file" accept="image/*,video/*" hidden></div>'+
       '<div id="i-af-fname" class="mono" style="font-size:.62rem;color:var(--gold)"></div></div></div>';

  $("#i-asset")?.addEventListener("change",ev=>{{ const v=ev.target.value; if(v)applyAsset(n,{{asset:v}}); }});
  $("#i-ago")?.addEventListener("click",()=>{{ const v=($("#i-asrc").value||"").trim(); if(v)applyAsset(n,{{src:v}}); }});
  $("#i-abrowse")?.addEventListener("click",()=>$("#i-afile").click());
  $("#i-afile")?.addEventListener("change",async ev=>{{
    const f=ev.target.files&&ev.target.files[0]; if(!f)return;
    if(f.size>200*1024*1024){{alert("El archivo pasa de 200 MB.");return;}}
    const msg=$("#i-amsg"); if(msg){{msg.hidden=false;msg.textContent='subiendo '+f.name+' ('+(f.size/1048576).toFixed(1)+' MB)…';}}
    try{{ const data=await fileB64(f); applyAsset(n,{{upload:{{name:f.name,data:data}}}}); }}
    catch(e){{ if(msg)msg.textContent='⚠ no se pudo leer el archivo'; }}
    ev.target.value="";
  }});
  $("#i-clear")?.addEventListener("click",()=>{{ if(confirm("¿Quitar el visual del beat "+n+"? Quedará sin cubrir."))beatEdit({{action:"clear",n:n}},"#i-smsg"); }});
  $("#i-mprev")?.addEventListener("click",()=>{{ if(confirm("Fusionar el beat "+n+" en el anterior (su plano cubre el tramo)?"))beatEdit({{action:"merge",n:n,into:"prev"}},"#i-smsg"); }});
  $("#i-mnext")?.addEventListener("click",()=>{{ if(confirm("Fusionar el beat "+n+" en el siguiente?"))beatEdit({{action:"merge",n:n,into:"next"}},"#i-smsg"); }});
  $("#i-del")?.addEventListener("click",()=>{{ if(confirm("¿Eliminar el beat "+n+"? La voz la reparten los vecinos."))beatEdit({{action:"del",n:n}},"#i-smsg"); }});
  $("#i-split")?.addEventListener("click",()=>{{
    const t=cur, flo=AC.has(b.kind)?2.5:(b.kind==="gráfico"||b.kind==="grafico")?5:2.8;
    if(!(t>b.in+0.2 && t<b.out-0.2)){{
      alert("Lleva el cabezal DENTRO del beat "+n+" (haz clic en la regla o reproduce y pausa) y vuelve a pulsar «partir».");
      return;
    }}
    if(t-b.in<flo || b.out-t<flo){{
      alert("Cada mitad debe durar ≥ "+flo+"s. Acerca el cabezal al centro del beat.");
      return;
    }}
    if(confirm("Partir el beat "+n+" en "+fmt(t)+"\\n· 1ª mitad ≈ "+(t-b.in).toFixed(1)+"s\\n· 2ª mitad ≈ "+(b.out-t).toFixed(1)+"s — mismo plano, reasignas el visual de la 2ª\\n\\nSe renumera la espina."))
      beatEdit({{action:"split",n:n,at:t}},"#i-smsg");
  }});
  $("#i-addb")?.addEventListener("click",()=>{{ const f=$("#i-addform"); f.hidden=!f.hidden; }});
  let afUpload=null;
  $("#i-af-browse")?.addEventListener("click",()=>$("#i-af-file").click());
  $("#i-af-file")?.addEventListener("change",async ev=>{{
    const f=ev.target.files&&ev.target.files[0]; if(!f)return;
    if(f.size>200*1024*1024){{alert("El archivo pasa de 200 MB.");return;}}
    try{{ afUpload={{name:f.name,data:await fileB64(f)}}; $("#i-af-fname").textContent="▸ "+f.name; }}
    catch(e){{ $("#i-af-fname").textContent="⚠ no se pudo leer"; }}
  }});
  $("#i-af-go")?.addEventListener("click",()=>{{
    const frag=($("#i-af-frag").value||"").trim(); if(!frag){{alert("El beat nuevo necesita un fragmento de la voz.");return;}}
    const src=($("#i-af-src").value||"").trim(); const kind=$("#i-af-kind").value;
    const body={{action:"add",after:n,frag:frag,kind:kind,section:b.section}};
    if(afUpload) body.upload=afUpload;
    else if(src && /[\\/.:]/.test(src)) body.src=src;
    else if(src) body.asset=src;
    beatEdit(body,"#i-smsg");
  }});
  $("#i-ok").onchange=ev=>{{ b.approved=ev.target.checked; if(ev.target.checked)b.fix=""; ev.target.closest(".approve").classList.toggle("on",ev.target.checked); markDirty(); layout(); select(n); status(); }};
  $("#i-fix").oninput=ev=>{{ b.fix=ev.target.value.trim(); if(b.fix)b.approved=false; status(); layout2(n); markDirty(); }};
  $$("#i-motion .mchip").forEach(c=>c.onclick=()=>{{ b.motion=c.dataset.m;
    $$("#i-motion .mchip").forEach(x=>x.setAttribute("aria-pressed","false")); c.setAttribute("aria-pressed","true"); }});
  $$('.stepper [data-d]').forEach(x=>x.onclick=()=>{{
    b.dur_lock=Math.max(1,+(((b.dur_lock|| (b.out-b.in))+ +x.dataset.d)).toFixed(1));
    b.out=+(b.in+b.dur_lock).toFixed(2);
    $("#i-dur").textContent=b.dur_lock.toFixed(1)+"s (fija)"; markDirty(); layout(); select(n); }});
  $$('.stepper [data-nf]').forEach(x=>x.onclick=()=>{{ b.nudge=(b.nudge||0)+ +x.dataset.nf;
    $("#i-nudge").textContent=b.nudge; markDirty(); }});
  $("#i-reset")?.addEventListener("click",()=>{{
    delete b.dur_lock; delete b.slot; markDirty(); layout(); select(n); }});
}}
/* ---- save: dur_lock / slot / nudge persist via /tl-save (recomputes align) ---- */
let saveT=0, saving=false;
function markDirty(){{ const s=$("#save"); s.textContent="Guardar •"; s.classList.add("dirty");
  clearTimeout(saveT); saveT=setTimeout(saveTL,900); }}
async function saveTL(){{
  clearTimeout(saveT); if(saving)return; saving=true;
  const s=$("#save"); s.textContent="Guardando…";
  try{{
    TL.beats=B;
    const j=await post("/tl-save",{{ep:EPID,slug:SLUG,timeline:TL}});
    if(j && j.timeline && j.timeline.beats){{
      const selN = sel && sel.n;
      Object.assign(TL,j.timeline); B=TL.beats; TOTAL=TL.total||TOTAL; if(typeof applyMix==="function")applyMix();
      $("#tctot").textContent=fmt(TOTAL); status(); layout();
      if(selN!=null) select(selN);
    }}
    s.textContent="Guardado ✓"; s.classList.remove("dirty");
  }}catch(e){{ s.textContent="⚠ sin guardar"; }}
  saving=false;
}}
$("#save").onclick=saveTL;
addEventListener("beforeunload",e=>{{ if($("#save").classList.contains("dirty")){{ e.preventDefault(); e.returnValue=""; }} }});
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
/* [data-tip] bubbles: the topbar draws them in pure CSS ([data-tip]:hover::after).
   the inspector is a scroll box that would clip a CSS bubble, so there we reuse
   the mouse-following #tltip (position:fixed). one mechanism per element — never
   both — so no double bubble. */
let tipEl=null;
const _ib=$("#inspbody");
_ib.addEventListener("pointerover",e=>{{
  const t=e.target.closest("[data-tip]");
  if(t===tipEl) return;
  tipEl=t;
  if(!t){{ tiphide(); return; }}
  tt.textContent=t.getAttribute("data-tip"); tt.classList.add("show"); tipmove(e);
}});
_ib.addEventListener("pointermove",e=>{{ if(tipEl) tipmove(e); }});
_ib.addEventListener("pointerleave",()=>{{ tipEl=null; tiphide(); }});
// safety: pointer left the inspector for anything else (fast move / topbar) → drop it
document.addEventListener("pointerover",e=>{{
  if(tipEl && !(e.target.closest && e.target.closest("#inspbody"))){{ tipEl=null; tiphide(); }}
}});
// entering the topbar (CSS bubbles there) always clears any JS bubble
$(".topbar")?.addEventListener("pointerover",()=>{{ tipEl=null; tiphide(); }});

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
  const r=await fetch(path,{{method:"POST",
    headers:{{"content-type":"application/json"}},body:JSON.stringify(body)}});
  if(!r.ok)throw new Error("server "+r.status);
  return r.json();
}}
$("#rrough").onclick=async()=>{{
  if($("#save").classList.contains("dirty")) await saveTL();
  toast('renderizando el vídeo entero a 720p en segundo plano — unos minutos. Recarga y mira en «corte renderizado» cuando termine.',6500);
  try{{ await post("/tl-rough",{{ep:EPID,slug:SLUG,timeline:TL}}); }}
  catch(e){{ toast('server no disponible — corre <span class="mono">python tools/assemble.py '+SLUG+' --rough</span>',6000); }}
}};
$("#fs")?.addEventListener("click",()=>{{
  const s=$("#screen");
  if(document.fullscreenElement){{ document.exitFullscreen(); return; }}
  const req=s.requestFullscreen||s.webkitRequestFullscreen;
  if(req) req.call(s).then(()=>{{ if(MODE==="rough"&&vid) vid.controls=true; }}).catch(()=>{{}});
}});
document.addEventListener("fullscreenchange",()=>{{
  if(!document.fullscreenElement && vid) vid.controls=false;
}});
$("#fin").onclick=async()=>{{
  if($("#save").classList.contains("dirty")) await saveTL();
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
addEventListener("resize",()=>{{_mmW=0;drawMinimap();updRange();placePlayhead();}});
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
