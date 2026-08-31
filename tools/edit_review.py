#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
edit_review.py — Stage 9 review surface (brain/16). Same idea as the Stage 7
style pass, for the edit: Usuario 001 watches every generated clip and either
ticks it OK or writes what to fix.

Scans the episode folder:
  assets/kb/*.mp4          Ken Burns clips  (from tools/kenburns.py --all)
  assets/*.trimmed.mp4     trimmed takes    (from tools/trim_talk.py)
  assets/*.cuts.md         the cut list for each take

Writes:
  07c-edit.html   the review page  (gitignored)
  (editor exports)  07c-review.txt   approvals + feedback  (tracked)

Loop: run kenburns/trim -> edit_review -> editor reviews -> exports 07c-review.txt
-> Claude re-runs the tools per the feedback -> edit_review again -> until all OK.

Usage
  python tools/edit_review.py E0XX-slug
"""
import re
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
import theme as T  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
EP_DIR = ROOT / "episodes"
REVIEW_HTML = "07c-edit.html"
REVIEW_TXT = "07c-review.txt"


def probe(path):
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height:format=duration",
             "-of", "csv=p=0", str(path)],
            capture_output=True, text=True, timeout=20)
        nums = re.findall(r"[\d.]+", r.stdout)
        w, h, d = (nums + ["0", "0", "0"])[:3]
        return int(float(w)), int(float(h)), float(d)
    except Exception:
        return 0, 0, 0.0


def scan(slug):
    ep = EP_DIR / slug
    if not ep.is_dir():
        sys.exit(f"no existe {ep}")
    kb = sorted((ep / "assets" / "kb").glob("*.mp4")) if (ep / "assets" / "kb").is_dir() else []
    trims = sorted((ep / "assets").glob("*.trimmed.mp4"))
    kb_items, trim_items = [], []
    for f in kb:
        w, h, d = probe(f)
        m = re.match(r"(beat[A-Za-z0-9+-]+)", f.name)
        kb_items.append({"id": f.stem, "beat": m.group(1) if m else f.stem,
                         "rel": f"assets/kb/{f.name}", "w": w, "h": h, "dur": d})
    for f in trims:
        w, h, d = probe(f)
        cuts = f.with_name(f.name.replace(".trimmed.mp4", ".cuts.md"))
        summary, detail = "", ""
        if cuts.exists():
            t = cuts.read_text(encoding="utf-8")
            sm = re.search(r"^- (cortes:.+)$", t, re.M)
            summary = sm.group(1) if sm else ""
            detail = t
        trim_items.append({"id": f.name.replace(".trimmed.mp4", ""),
                           "rel": f"assets/{f.name}", "w": w, "h": h, "dur": d,
                           "summary": summary, "detail": detail})
    return kb_items, trim_items


def build(slug, kb, trims):
    import html as _h
    e = _h.escape

    def clip(kind, it, meta, extra=""):
        return (
            f'<div class="clip" data-kind="{kind}" data-id="{e(it["id"])}">'
            f'<video controls preload="metadata" src="{e(it["rel"])}"></video>'
            f'<div class="meta">{meta}</div>{extra}'
            f'<label class="ok"><input type="checkbox" class="approve"> aprobado</label>'
            f'<textarea class="fb" placeholder="qué corregir…"></textarea>'
            '</div>')

    kb_html = "".join(
        clip("kb", it,
             f'{e(it["beat"])} · {it["w"]}x{it["h"]} · {it["dur"]:.1f}s')
        for it in kb) or '<p class="empty">sin clips en assets/kb/ — corre <code>python tools/kenburns.py '\
        f'{e(slug)} --all</code></p>'

    tr_html = "".join(
        clip("trim", it,
             f'{e(it["id"])} · {it["w"]}x{it["h"]} · {it["dur"]:.1f}s · {e(it["summary"])}',
             extra=(f'<details><summary>ver cortes</summary><pre>{e(it["detail"])}</pre></details>'
                    if it["detail"] else ""))
        for it in trims) or '<p class="empty">sin tomas en assets/*.trimmed.mp4 — corre '\
        '<code>python tools/trim_talk.py assets/T1.mp4</code></p>'

    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Edit review — {e(slug)}</title>
{T.CSS}
<style>
 .clip{{border:1px solid var(--line-2);border-radius:var(--r);background:var(--surface);
   padding:.85rem;display:flex;flex-direction:column;gap:.55rem;box-shadow:var(--shadow)}}
 .clip:has(.approve:checked){{border-color:var(--lime-line);background:var(--lime-soft)}}
 .clip:has(.fb:not(:placeholder-shown)){{border-color:var(--gold-line)}}
 video{{width:100%;border-radius:var(--r-sm);background:#000;aspect-ratio:16/9}}
 .ok{{display:flex;align-items:center;gap:.45rem;font-size:.82rem}}
 .ok input{{width:18px;height:18px}}
 textarea.fb{{min-height:2.4rem;font-size:.8rem}}
 #cnt{{color:var(--muted);font-size:.82rem;font-variant-numeric:tabular-nums}}
</style></head><body>
<header>
 <h1>Edit review · {e(slug)}</h1>
 <span id="cnt"></span>
 <button class="primary" id="exp">Exportar {REVIEW_TXT}</button>
 <button id="clr">Limpiar</button>
 <span style="color:var(--muted);font-size:.8rem">guárdalo en la carpeta del episodio</span>
</header>
<main>
 <section><h2>Ken Burns — {len(kb)} clips</h2>
  <p class="hint">Aprueba cada clip, o escribe qué corregir (p. ej. «más lento», «empieza más
   a la izquierda», «dir arriba», «déjalo estático», «dura 4 s»). Claude re-genera con tu
   feedback y vuelves a revisar.</p>
  <div class="grid">{kb_html}</div>
 </section>
 <section><h2>Trim — {len(trims)} tomas</h2>
  <p class="hint">Aprueba cada toma trimmeada, o escribe correcciones (p. ej. «mantener la
   pausa en 00:12», «cortar antes en 02:03», «no cortes el "eh" de 03:04»). Claude re-corre
   el trim con <code>--keep</code> y ajustes.</p>
  <div class="grid">{tr_html}</div>
 </section>
</main>
<script>
const SLUG="{e(slug)}", LS="conquest-edit:"+SLUG;
const clips=[...document.querySelectorAll('.clip')];
const cnt=document.getElementById('cnt');
function jget(k,d){{try{{return JSON.parse(localStorage.getItem(k))??d}}catch(e){{return d}}}}
function key(c){{return c.dataset.kind+':'+c.dataset.id}}
function sync(){{
  const st={{}}; let ok=0,fb=0;
  clips.forEach(c=>{{
    const a=c.querySelector('.approve').checked, t=c.querySelector('.fb').value.trim();
    st[key(c)]={{a,t}};
    if(a)ok++; if(t)fb++;
  }});
  localStorage.setItem(LS,JSON.stringify(st));
  const n=clips.length;
  cnt.textContent=ok+' / '+n+' aprobados'+(fb?('  ·  '+fb+' con feedback'):'')
    +(ok===n&&n?'  ·  listo para b-roll':'');
}}
const init=jget(LS,{{}});
clips.forEach(c=>{{
  const s=init[key(c)]; if(s){{c.querySelector('.approve').checked=!!s.a; c.querySelector('.fb').value=s.t||'';}}
  c.querySelectorAll('input,textarea').forEach(x=>x.addEventListener('input',sync));
  c.querySelector('.approve').addEventListener('change',sync);
}});
sync();
document.getElementById('clr').onclick=()=>{{
  clips.forEach(c=>{{c.querySelector('.approve').checked=false; c.querySelector('.fb').value='';}}); sync();
}};
document.getElementById('exp').onclick=async()=>{{
  const L=['# {REVIEW_TXT} — generado por {REVIEW_HTML}',
           '# <kind>  <id>  APROBADO | FIX: <texto>'];
  for(const grp of ['kb','trim']){{
    const rows=clips.filter(c=>c.dataset.kind===grp).map(c=>{{
      const a=c.querySelector('.approve').checked, t=c.querySelector('.fb').value.trim();
      return grp+'  '+c.dataset.id+'  '+(t?('FIX: '+t.replace(/\\s+/g,' ')):(a?'APROBADO':'PENDIENTE'));
    }});
    if(rows.length){{L.push('# --- '+(grp==='kb'?'KEN BURNS':'TRIM')+' ---'); L.push(...rows);}}
  }}
  const txt=L.join('\\n')+'\\n';
  try{{
    const r=await fetch('http://localhost:8765/finish',{{method:'POST',
      headers:{{'content-type':'application/json'}},
      body:JSON.stringify({{ep:'{slug}'.slice(0,4),stage:9,payload:{{txt:txt}}}})}});
    if(r.ok){{const j=await r.json();
      alert('Stage 9 cerrado.\\n'+(j.msg||'')+'\\nDashboard actualizado.');return;}}
  }}catch(e){{}}
  try{{
    const fh=await window.showSaveFilePicker({{suggestedName:'{REVIEW_TXT}',
      types:[{{description:'texto',accept:{{'text/plain':['.txt']}}}}]}});
    const w=await fh.createWritable(); await w.write(txt); await w.close();
    alert('Guardado (server no detectado). Corre: python tools/advance.py fold {slug[:4]}');
    return;
  }}catch(e){{if(e&&e.name==='AbortError')return;}}
  navigator.clipboard&&navigator.clipboard.writeText(txt).catch(()=>{{}});
  const a=document.createElement('a');
  a.href=URL.createObjectURL(new Blob([txt],{{type:'text/plain'}}));
  a.download='{REVIEW_TXT}'; a.click();
}};
</script></body></html>
"""


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        sys.exit(2)
    slug = a[0]
    kb, trims = scan(slug)
    (EP_DIR / slug / REVIEW_HTML).write_text(build(slug, kb, trims), encoding="utf-8")
    print(f"escrito  episodes/{slug}/{REVIEW_HTML}  ({len(kb)} KB, {len(trims)} tomas)")
    print("siguiente: ábrelo, aprueba / deja feedback, «Exportar 07c-review.txt», pásaselo a Claude")
