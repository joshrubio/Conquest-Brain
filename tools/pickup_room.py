#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pickup_room.py — build the pickup UI for a take's flagged re-record sentences.

Reads <take>.pickups.json (written by trim_talk.py --script — full sentence
text, match confidence, an original-take-second anchor) plus the take's own
waveform (<take>.peaks.json) and word list (<take>.words.raw.json, for
snapping a region to a word boundary), and writes <take>.pickup-room.html:
one shared waveform, a list of pickup cards below it. Selecting a card loads
a draggable region (default: a couple seconds either side of its anchor,
snapped to nearby words) into the waveform — "> original" samples that exact
span from <take>.review.m4a as many times as needed while the operator
records or uploads a new take and dials in a gain slider (live preview via
Web Audio, before it ever touches a file). "Aceptar" posts the region + audio
+ gain to serve.py's /pickup-accept, which matches loudness (match_audio.py)
and splices it into <take>.trimmed.mp4 next time the take is (re)applied.

Usage:
    python tools/pickup_room.py TAKE.mp4
        (re)builds <take>.pickup-room.html from the files above. Safe to
        re-run any time — e.g. after a pickup is accepted, to refresh which
        cards still say "pendiente".
"""
import html as _h
import json as _j
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def _load(p, default):
    return _j.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def build(take: Path):
    pickups_f = take.with_suffix(".pickups.json")
    if not pickups_f.exists():
        sys.exit(f"falta {pickups_f.name} — corre antes  python tools/trim_talk.py {take.name} --script 05-script.md")
    pickups = _j.loads(pickups_f.read_text(encoding="utf-8"))
    raw = _load(take.with_suffix(".words.raw.json"), [])
    peaks_f = take.with_suffix(".peaks.json")
    peaks = peaks_f.read_text(encoding="utf-8") if peaks_f.exists() else None
    if peaks is None:
        sys.exit(f"falta {peaks_f.name} — corre antes  python tools/trim_talk.py {take.name} --script 05-script.md")
    total = _j.loads(peaks)[0]
    accepted = _load(take.with_suffix(".pickups.accepted.json"), {"pickups": []})["pickups"]
    # keyed by sentence TEXT, not `idx` — `idx` is only this sentence's position
    # the last time this page was built; a --script/--rebuild-page re-run can
    # reorder or renumber the flagged list, which would otherwise badge the
    # wrong card. serve.py's /pickup-accept dedups on text for the same reason.
    accepted_texts = {a["text"].strip() for a in accepted}

    e = _h.escape
    slug = take.parent.parent.name
    ep = slug.split("-")[0]
    m4a = e(take.with_suffix(".review.m4a").name)
    PK = _j.dumps(pickups, ensure_ascii=False)
    WB = _j.dumps([round(w["s"], 3) for w in raw] + [round(w["e"], 3) for w in raw])

    cards = []
    for i, pk in enumerate(pickups):
        is_accepted = pk["text"].strip() in accepted_texts
        st = "aceptado ✓" if is_accepted else "pendiente"
        cards.append(f"""<div class="card" data-i="{i}" data-anchor="{pk['anchor_t'] if pk['anchor_t'] is not None else 0}">
  <div class="ctop"><span class="badge {'ok' if is_accepted else ''}">{st}</span>
    <span class="score">match {pk['score']:.0%}</span>
    <span class="anchor">~{_fmt(pk['anchor_t'])}</span></div>
  <div class="ctext">{e(pk['text'])}</div>
  <button class="sel" data-tip="Carga esta línea en la onda de arriba: aparece una región editable centrada en el punto donde probablemente falló, y se abren los controles para escuchar el original, grabar o subir el pickup.">Seleccionar y trabajar esta línea</button>
</div>""")

    html = f"""<!doctype html><meta charset="utf-8"><title>Pickups · {e(take.name)}</title>
<style>
 :root{{--bg:#100d09;--fg:#ece3ce;--gold:#c9a15a;--mut:#96876f;--line:#2e2820;--cut:#5a78be;--ok:#4a8a5c}}
 *{{box-sizing:border-box}}
 body{{background:var(--bg);color:var(--fg);font:15px/1.6 Georgia,serif;margin:0;padding:0 0 4rem}}
 header{{position:sticky;top:0;background:#161109;border-bottom:1px solid var(--line);
   padding:12px 22px;display:flex;gap:14px;align-items:center;flex-wrap:wrap;z-index:9}}
 h1{{font-size:14px;color:var(--gold);font-weight:normal;margin:0;font-family:monospace}}
 button,.btn{{font:inherit;font-size:13px;padding:.35rem .8rem;border-radius:6px;border:1px solid var(--line);
   background:#1e1a14;color:var(--fg);cursor:pointer;text-decoration:none;display:inline-block;line-height:1.4}}
 button.primary{{background:var(--gold);color:#161109;border-color:var(--gold);font-weight:bold}}
 button:disabled{{opacity:.4;cursor:not-allowed}}
 .btn.ghost{{background:transparent;color:var(--mut)}}
 .warn{{background:#2a2412;color:#e2c98a;padding:.55rem 22px;font-size:13px;border-bottom:1px solid var(--line)}}
 #scroll{{overflow-x:auto;overflow-y:hidden;border-bottom:1px solid var(--line);background:#0b0906;position:relative}}
 #lane{{position:relative;height:150px}}
 #wave{{position:sticky;left:0;top:0;display:block;z-index:1}}
 #rg{{position:absolute;top:14px;height:110px;background:rgba(90,120,190,.30);
   border-left:2px solid var(--cut);border-right:2px solid var(--cut);z-index:3;cursor:grab;display:none}}
 #rg .h{{position:absolute;top:0;bottom:0;width:10px;cursor:ew-resize}}
 #rg .h.l{{left:-5px}} #rg .h.r{{right:-5px}}
 #ph{{position:absolute;top:0;bottom:0;width:2px;background:var(--gold);z-index:5;pointer-events:none}}
 #tools{{display:flex;gap:10px;align-items:center;padding:8px 22px;font-family:monospace;font-size:12px;color:var(--mut)}}
 main{{max-width:900px;margin:0 auto;padding:0 22px}}
 .card{{border:1px solid var(--line);border-radius:8px;padding:14px 16px;margin:14px 0;background:#161109}}
 .card.active{{border-color:var(--gold)}}
 .ctop{{display:flex;gap:10px;align-items:center;font-family:monospace;font-size:12px;color:var(--mut);margin-bottom:6px}}
 .badge{{border:1px solid var(--line);border-radius:4px;padding:1px 6px;color:var(--mut)}}
 .badge.ok{{color:var(--ok);border-color:var(--ok)}}
 .ctext{{font-size:16px;margin-bottom:10px}}
 .work{{display:none;border-top:1px solid var(--line);margin-top:10px;padding-top:10px}}
 .card.active .work{{display:block}}
 .row{{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:8px 0}}
 input[type=range]{{width:180px}}
 .rec-dot{{width:9px;height:9px;border-radius:50%;background:#b53a2f;display:none}}
 .rec-dot.on{{display:inline-block;animation:pulse 1s infinite}}
 @keyframes pulse{{50%{{opacity:.25}}}}
 .mut{{color:var(--mut);font-size:12px}}
 audio{{height:30px;vertical-align:middle}}
 /* themed hover tooltip — same mechanism as the Sala de montaje (edit_timeline.py/theme.py) */
 [data-tip]{{position:relative}}
 [data-tip]:hover::after{{content:attr(data-tip);position:absolute;left:0;top:calc(100% + 8px);
   z-index:60;width:max-content;max-width:22rem;white-space:normal;
   background:#1e1a14;color:var(--fg);border:1px solid var(--line);
   border-radius:6px;padding:.55rem .75rem;font-size:.78rem;font-weight:440;line-height:1.45;
   box-shadow:0 8px 24px rgba(0,0,0,.4);pointer-events:none}}
 [data-tip]:hover::before{{content:"";position:absolute;left:12px;top:calc(100% + 2px);
   border:5px solid transparent;border-bottom-color:var(--line);z-index:61}}
 header [data-tip]:hover::after{{max-width:24rem}}
 [data-tipr][data-tip]:hover::after{{left:auto;right:0}}
 [data-tipr][data-tip]:hover::before{{left:auto;right:12px}}
</style>
<header>
 <h1>Pickups · {e(take.name)}</h1>
 <a class="btn ghost" style="margin-left:auto" href="http://localhost:8765/" data-tipr data-tip="Vuelve al panel de Conquest. Lo que ya aceptaste queda guardado — nada se pierde al salir.">Volver al panel</a>
</header>
<div class="warn">Elige una línea abajo → ajusta la región en la onda (los bordes son la parte que se
 reemplaza) → escucha el <b>original</b> tantas veces como haga falta → graba o sube el pickup → ajusta la
 <b>ganancia</b> escuchando el resultado → <b>Aceptar</b>. Si la línea cae en un tramo <code>a cámara</code>,
 esto solo puede parchear el audio — el vídeo se queda congelado en un fotograma; para esos casos hace falta
 volver a grabar el plano entero.</div>
<div id="tools">
 <button id="play" data-tip="Reproduce o pausa la onda completa desde el cabezal — para orientarte antes de elegir una línea.">▶</button><span id="clock">0:00 / {int(total//60)}:{int(total%60):02d}</span>
 zoom <button id="zo" data-tip="Aleja la onda — ve más segundos a la vez.">−</button><button id="zi" data-tip="Acerca la onda — más precisión para ajustar los bordes de la región.">+</button>
</div>
<div id="scroll"><div id="lane"><canvas id="wave"></canvas><div id="rg"><div class="h l" data-tip="Arrastra para ajustar dónde EMPIEZA el tramo que se va a reemplazar. Que sea justo — ni de más ni de menos."></div><div class="h r" data-tip="Arrastra para ajustar dónde TERMINA el tramo que se va a reemplazar."></div></div><div id="ph"></div></div></div>
<audio id="au" preload="auto" src="/episodes/{e(slug)}/assets/{m4a}"></audio>
<main>
{"".join(cards) if cards else '<p class="mut">Sin candidatos a pickup — trim_talk.py --script no marcó ninguna línea.</p>'}
</main>
<script>
const TAKE={_j.dumps(take.name)}, SLUG={_j.dumps(slug)}, EP={_j.dumps(ep)}, TOTAL={total:.3f};
const PICKUPS={PK}, WORD_BOUNDS={WB};
const au=document.getElementById('au'), scroll=document.getElementById('scroll'), lane=document.getElementById('lane'),
      cv=document.getElementById('wave'), ph=document.getElementById('ph'), rg=document.getElementById('rg'),
      clock=document.getElementById('clock');
const ctx=cv.getContext('2d');
let pps=Math.max(2, Math.min(14, 2200/TOTAL));
let region=null, activeI=-1, sampleUntil=0;
const savedRegions={{}};   // per-card region, so switching cards doesn't discard a hand-adjusted one

function fmt(t){{t=Math.max(0,t);return (t/60|0)+':'+('0'+Math.floor(t%60)).slice(-2);}}
function snapT(t){{let best=t,d=0.2;for(const x of WORD_BOUNDS){{const dd=Math.abs(x-t);if(dd<d){{d=dd;best=x;}}}}return best;}}
function laneW(){{return Math.max(scroll.clientWidth, TOTAL*pps);}}
function sizeWave(){{const vw=scroll.clientWidth, dpr=devicePixelRatio||1;
  cv.width=vw*dpr; cv.height=150*dpr; cv.style.width=vw+'px'; cv.style.height='150px';
  ctx.setTransform(dpr,0,0,dpr,0,0);}}
function drawWave(){{const vw=scroll.clientWidth, x0=scroll.scrollLeft, mid=14+55, PK=JSON.parse({_j.dumps(peaks)})[1];
  ctx.clearRect(0,0,vw,150); ctx.fillStyle='#3a342a'; ctx.beginPath();
  for(let px=0;px<vw;px++){{const t=(x0+px)/pps; if(t>TOTAL)break;
    const i=Math.floor(t/TOTAL*PK.length), h=Math.max(1,(PK[i]||0)/100*52);
    ctx.rect(px,mid-h,1,h*2);}}
  ctx.fill();}}
function layout(){{lane.style.width=laneW()+'px'; sizeWave(); drawWave(); movePh(); drawRegion();}}
function drawRegion(){{
  if(!region){{rg.style.display='none';return;}}
  rg.style.display='block'; rg.style.left=(region.s*pps)+'px'; rg.style.width=Math.max(4,(region.e-region.s)*pps)+'px';
}}
function movePh(){{ph.style.left=(au.currentTime*pps)+'px'; clock.textContent=fmt(au.currentTime)+' / '+fmt(TOTAL);
  if(sampleUntil && au.currentTime>=sampleUntil){{au.pause(); sampleUntil=0;}}}}
function scrollTo(t){{scroll.scrollLeft=Math.max(0, t*pps - scroll.clientWidth/2);}}

document.getElementById('play').onclick=()=>{{sampleUntil=0; au.paused?au.play().catch(()=>{{}}):au.pause();}};
au.addEventListener('play',()=>{{document.getElementById('play').textContent='⏸';tick();}});
au.addEventListener('pause',()=>document.getElementById('play').textContent='▶');
function tick(){{movePh(); if(!au.paused)requestAnimationFrame(tick);}}
document.getElementById('zi').onclick=()=>{{pps=Math.min(60,pps*1.6);layout();}};
document.getElementById('zo').onclick=()=>{{pps=Math.max(1,pps/1.6);layout();}};
scroll.addEventListener('scroll',drawWave);
addEventListener('resize',layout);

// drag the region edges (the body isn't draggable — start/end only, keeps a
// mis-click from silently shrinking the replace span to nothing)
let drag=null;
rg.addEventListener('pointerdown',ev=>{{
  const edge=ev.target.classList.contains('h')?(ev.target.classList.contains('l')?'l':'r'):null;
  if(!edge)return;
  drag={{edge}}; rg.setPointerCapture(ev.pointerId);
}});
rg.addEventListener('pointermove',ev=>{{
  if(!drag||!region)return;
  const x=ev.clientX-lane.getBoundingClientRect().left, t=Math.max(0,Math.min(TOTAL,x/pps));
  if(drag.edge==='l') region.s=Math.min(t,region.e-0.2); else region.e=Math.max(t,region.s+0.2);
  drawRegion();
}});
rg.addEventListener('pointerup',()=>{{
  if(drag&&region){{
    region.s=snapT(region.s); region.e=snapT(region.e); drawRegion();
    if(activeI>=0) savedRegions[activeI]={{s:region.s,e:region.e}};
  }}
  drag=null;
}});

function selectCard(i){{
  activeI=i; document.querySelectorAll('.card').forEach(c=>c.classList.toggle('active', +c.dataset.i===i));
  const anchor=PICKUPS[i].anchor_t||0, saved=savedRegions[i];
  region=saved ? {{s:saved.s, e:saved.e}}
               : {{s:snapT(Math.max(0,anchor-1.2)), e:snapT(Math.min(TOTAL,anchor+3.5))}};
  drawRegion(); scrollTo(saved ? region.s : anchor);
  const card=document.querySelector('.card[data-i="'+i+'"]');
  if(!card.querySelector('.work')) buildWork(card, i);
}}

function buildWork(card, i){{
  const w=document.createElement('div'); w.className='work';
  w.innerHTML=`
    <div class="row"><button class="orig" data-tip="Reproduce el tramo original tal cual quedó grabado, tantas veces como haga falta mientras preparas el pickup.">▶ original</button>
      <span class="mut">reprodúcelo las veces que haga falta mientras preparas el pickup</span></div>
    <div class="row">
      <button class="rec" data-tip="Graba un pickup con el micrófono del navegador (pide permiso la primera vez). Pulsa otra vez para detener.">🎙 grabar</button><span class="rec-dot"></span>
      <span class="mut">o</span>
      <input type="file" class="upl" accept="audio/*,video/*" data-tip="Trae una grabación ya hecha desde tu equipo, en vez de grabar aquí mismo.">
    </div>
    <div class="row newplay" style="display:none">
      <audio class="newau" controls data-tip="El pickup tal como quedó grabado o subido, antes de ajustar la ganancia — usa el slider de al lado para escuchar el efecto en vivo."></audio>
      <label class="mut">ganancia <input type="range" class="gain" min="-12" max="12" step="0.5" value="0" data-tip="Ajusta el volumen del pickup en vivo, antes de aceptarlo — súbelo o bájalo comparando de oído contra el «▶ original». El ajuste automático de sonoridad se hace después, al aceptar.">
        <span class="gainv">0.0 dB</span></label>
      <button class="acc primary" disabled data-tip="Sube el pickup, lo iguala de volumen contra el original (match_audio.py) y lo deja listo — se integra solo la próxima vez que se aplique el recorte de esta toma (marca «Re-sincronizar» en la sala de montaje).">Aceptar</button>
    </div>
    <div class="mut result"></div>`;
  card.appendChild(w);

  const origBtn=w.querySelector('.orig');
  origBtn.onclick=()=>{{
    if(!region)return;
    au.currentTime=region.s; sampleUntil=region.e; au.play().catch(()=>{{}});
  }};

  let mediaRecorder=null, chunks=[], blob=null, ctxA=null, srcNode=null, gainNode=null;
  const recBtn=w.querySelector('.rec'), dot=w.querySelector('.rec-dot'), uplInp=w.querySelector('.upl');
  const newplay=w.querySelector('.newplay'), newau=w.querySelector('.newau'), gain=w.querySelector('.gain'),
        gainv=w.querySelector('.gainv'), accBtn=w.querySelector('.acc'), resultEl=w.querySelector('.result');

  function setBlob(b){{
    blob=b; newau.src=URL.createObjectURL(b); newplay.style.display='flex'; accBtn.disabled=false;
    wireGainPreview();
  }}
  function wireGainPreview(){{
    // live gain preview via Web Audio, without re-encoding the file each nudge.
    // Built ONCE per card: an <audio> element can only ever be attached to one
    // MediaElementSourceNode for its lifetime — re-recording/re-uploading swaps
    // newau.src but must reuse the existing node graph, not recreate it (a
    // second createMediaElementSource() throws InvalidStateError).
    if(srcNode){{ gainNode.gain.value=Math.pow(10, (+gain.value)/20); return; }}
    try{{
      if(!ctxA) ctxA=new (window.AudioContext||window.webkitAudioContext)();
      srcNode=ctxA.createMediaElementSource(newau); gainNode=ctxA.createGain();
      srcNode.connect(gainNode); gainNode.connect(ctxA.destination);
      gainNode.gain.value=Math.pow(10, (+gain.value)/20);
    }}catch(e){{}}
  }}
  gain.addEventListener('input',()=>{{
    gainv.textContent=(+gain.value).toFixed(1)+' dB';
    if(gainNode) gainNode.gain.value=Math.pow(10, (+gain.value)/20);
  }});

  recBtn.onclick=async()=>{{
    if(mediaRecorder && mediaRecorder.state==='recording'){{mediaRecorder.stop(); return;}}
    try{{
      const stream=await navigator.mediaDevices.getUserMedia({{audio:true}});
      chunks=[]; mediaRecorder=new MediaRecorder(stream);
      mediaRecorder.ondataavailable=e=>chunks.push(e.data);
      mediaRecorder.onstop=()=>{{setBlob(new Blob(chunks,{{type:'audio/webm'}})); dot.classList.remove('on');
        stream.getTracks().forEach(t=>t.stop());}};
      mediaRecorder.start(); dot.classList.add('on'); recBtn.textContent='■ detener';
      mediaRecorder.addEventListener('stop',()=>recBtn.textContent='🎙 grabar');
    }}catch(e){{ resultEl.textContent='sin acceso al micrófono: '+e.message; }}
  }};
  uplInp.onchange=()=>{{ if(uplInp.files[0]) setBlob(uplInp.files[0]); }};

  accBtn.onclick=async()=>{{
    if(!blob||!region)return;
    accBtn.disabled=true; resultEl.textContent='subiendo y ajustando el audio…';
    const qs=new URLSearchParams({{ep:EP, take:TAKE, idx:i, start:region.s.toFixed(3), end:region.e.toFixed(3),
      gain:(+gain.value).toFixed(1), text:PICKUPS[i].text}});
    try{{
      const r=await fetch('/pickup-accept?'+qs.toString(), {{method:'POST', body:blob}});
      const j=await r.json();
      if(r.ok && j.ok){{
        resultEl.textContent='✓ aceptado — '+(j.msg||'');
        card.querySelector('.badge').textContent='aceptado ✓'; card.querySelector('.badge').classList.add('ok');
      }} else {{
        resultEl.textContent='error: '+(j.error||r.status); accBtn.disabled=false;
      }}
    }}catch(e){{ resultEl.textContent='sin server — arranca serve.py'; accBtn.disabled=false; }}
  }};
}}

document.querySelectorAll('.card .sel').forEach(btn=>{{
  btn.addEventListener('click',()=>selectCard(+btn.closest('.card').dataset.i));
}});

layout();
</script>
"""
    out = take.with_suffix(".pickup-room.html")
    out.write_text(html, encoding="utf-8")
    print(f"  escrito  {out.name}  ({len(pickups)} candidatos, {len(accepted)} aceptados)")
    return out


def _fmt(t):
    if t is None:
        return "?"
    t = max(0.0, t)
    return f"{int(t // 60)}:{int(t % 60):02d}"


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(2 if a else 0)
    take = Path(a[0]).resolve()
    if not take.is_file():
        sys.exit(f"no existe: {take}")
    build(take)
