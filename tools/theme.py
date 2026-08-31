# -*- coding: utf-8 -*-
"""
theme.py — THE design system for every Conquest HTML surface (dashboard, cost,
review pages, file views, directory listings).

──────────────────────────────────────────────────────────────────────────────
PRESENTATION ONLY.  Do NOT read this file to understand pipeline logic, stage
data, gates, queues or episode state — none of that lives here. It holds CSS
strings and one HTML wrapper. Read it *only* when the task is "change how the
pages look". Any agent draining the dashboard queue or folding a gate never
needs to open this file.
──────────────────────────────────────────────────────────────────────────────

Consumers import three names and nothing else:
    from theme import CSS, HELPERS, shell
`review_ui.py` re-exports them as STYLE / HELPERS / page for older callers.

Design brief: modern fintech/crypto dashboard (Revolut-ish) — bold, clean,
tech. Warm-dark base kept from the brand; gold kept as the primary; a lime
sibling + calm blue/green/terracotta added in the same saturation band for
state. No emoji anywhere — hierarchy comes from weight, size, colour, state.
"""

# ── design tokens ────────────────────────────────────────────────────────────
# Token NAMES are frozen (every review tool references them). Only values move.
TOKENS = """
:root{
  color-scheme:dark;
  /* ground */
  --bg:#0f0e0b; --bg-2:#0a0908;
  --surface:#1a1813; --surface-2:#232019; --surface-3:#2d2920;
  --line:#37322727; --line-2:#413b2d;
  /* ink */
  --fg:#f4efe1; --bone:#eee6d0; --muted:#9c927a; --faint:#6a6353;
  /* brand */
  --gold:#c9a24a; --gold-ink:#17130a; --gold-soft:#c9a24a1c; --gold-line:#c9a24a55;
  /* lime sibling — gold hue nudged to green, same saturation band; hero / active */
  --lime:#cdd94e; --lime-ink:#181a06; --lime-soft:#cdd94e1c; --lime-line:#cdd94e55;
  /* state */
  --pos:#63cf8b; --pos-soft:#63cf8b1c;
  --neg:#d98a5f; --neg-soft:#d98a5f1a; --neg-line:#d98a5f55;
  --info:#77a6de; --info-soft:#77a6de18;
  /* solid state fills (full-colour cards, contrasting text) */
  --done-fill:#2a2413; --done-ink:#e7c983;
  /* tables — a lighter grey-warm black, minimum-recommended contrast off --bg */
  --table-bg:#161512; --table-head:#201d17; --cell-line:#3a352a;
  /* geometry */
  --r:16px; --r-sm:10px; --r-pill:999px;
  --pad:1.15rem;
  --shadow:0 1px 0 #ffffff07 inset, 0 14px 34px -20px #000c;
  --shadow-lift:0 1px 0 #ffffff0d inset, 0 18px 40px -18px #000d;
  --hatch:repeating-linear-gradient(-45deg,#ffffff06 0 6px,transparent 6px 12px);
  --mono:ui-monospace,"SF Mono",SFMono-Regular,Menlo,monospace;
  --sans:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
}
"""

# ── base elements ────────────────────────────────────────────────────────────
BASE = """
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);
  font:15px/1.55 var(--sans);letter-spacing:-.006em;
  -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
a{color:var(--gold);text-decoration:none}
a:hover{text-decoration:underline}
::selection{background:var(--lime);color:var(--lime-ink)}
:focus-visible{outline:2px solid var(--lime);outline-offset:2px}

h1,h2,h3,h4{margin:0;color:var(--bone);letter-spacing:-.02em}
h1{font-size:1.15rem;font-weight:680}
h1.brand{font-size:1.5rem;font-weight:760;color:var(--gold);letter-spacing:-.03em}
h1.brand .of{color:var(--faint);font-weight:600;font-size:.62em;letter-spacing:.04em;
  text-transform:uppercase;margin-left:.4rem;vertical-align:.12em}
h2{font-size:.7rem;font-weight:680;text-transform:uppercase;letter-spacing:.09em;
  color:var(--muted);margin:0 0 1rem;padding:0}
h3{font-size:.9rem;font-weight:640}
h4{font-size:.72rem;font-weight:680;text-transform:uppercase;letter-spacing:.08em;color:var(--gold)}
p{margin:.5rem 0}
hr{border:0;border-top:1px solid var(--line);margin:1.5rem 0}
small,.small{font-size:.78rem;color:var(--muted)}
b,strong{font-weight:640;color:var(--bone)}
code,kbd{font-family:var(--mono);font-size:.82em;color:var(--muted)}
kbd{background:var(--surface-2);border:1px solid var(--line-2);border-radius:5px;padding:.05rem .35rem}

/* app frame */
header{position:sticky;top:0;z-index:20;display:flex;gap:.85rem;align-items:center;
  flex-wrap:wrap;padding:.85rem 1.5rem;min-height:3.6rem;
  background:var(--bg);border-bottom:1px solid var(--line)}
header h1{margin-right:.4rem}
main{max-width:1500px;margin:0 auto;padding:1.75rem 1.5rem 4rem}
section{margin:0 0 2.5rem}

/* buttons — pill, quiet by default, one loud primary; gold hairline so they
   stay scannable on the dark ground */
button,.btn{font:inherit;font-size:.82rem;font-weight:560;line-height:1;
  display:inline-flex;align-items:center;gap:.4rem;
  padding:.6rem .95rem;border:1px solid var(--gold-line);border-radius:var(--r-pill);
  background:var(--surface-2);color:var(--bone);cursor:pointer;text-decoration:none;
  transition:background .12s,border-color .12s,transform .06s,filter .12s}
button:hover,.btn:hover{background:var(--surface-3);border-color:var(--gold);text-decoration:none}
button:active,.btn:active{transform:translateY(1px)}
button.primary,.btn.primary{background:var(--gold);color:var(--gold-ink);
  border-color:var(--gold);font-weight:660}
button.primary:hover,.btn.primary:hover{background:var(--gold);filter:brightness(1.07)}
button.accent,.btn.accent{background:var(--lime);color:var(--lime-ink);border-color:var(--lime);font-weight:660}
button.accent:hover,.btn.accent:hover{filter:brightness(1.06)}
button.ghost,.btn.ghost{background:transparent;border-color:var(--gold-line);color:var(--bone)}
button.ghost:hover,.btn.ghost:hover{background:var(--gold-soft);border-color:var(--gold)}
button:disabled,.btn:disabled{opacity:.45;cursor:not-allowed}

/* fields */
input[type=text],input[type=number],textarea,select{width:100%;font:inherit;font-size:.85rem;
  padding:.58rem .7rem;border:1px solid var(--line-2);border-radius:var(--r-sm);
  background:var(--bg-2);color:var(--fg)}
input::placeholder,textarea::placeholder{color:var(--faint)}
input:focus,textarea:focus,select:focus{outline:none;border-color:var(--lime);
  box-shadow:0 0 0 3px var(--lime-soft)}
textarea{min-height:2.7rem;resize:vertical;line-height:1.5}
input[type=checkbox],input[type=radio]{accent-color:var(--lime)}
label{cursor:pointer}

/* tables — used a lot. Card-like: lighter grey-warm ground, rounded, ruled
   rows + columns for legibility. Header rows are the first <tr> (no <thead>). */
table{width:100%;border-collapse:separate;border-spacing:0;font-size:.83rem;margin:.9rem 0;
  background:var(--table-bg);border:1px solid var(--line-2);border-radius:var(--r-sm);overflow:hidden}
th,td{text-align:left;padding:.55rem .75rem;vertical-align:top;
  border-bottom:1px solid var(--cell-line);border-right:1px solid var(--cell-line)}
th:last-child,td:last-child{border-right:0}
tr:last-child th,tr:last-child td{border-bottom:0}
th{background:var(--table-head);color:var(--muted);
  font-size:.68rem;font-weight:680;text-transform:uppercase;letter-spacing:.06em;
  border-bottom:1px solid var(--line-2)}
tr:hover td{background:#ffffff06}
td b{font-variant-numeric:tabular-nums;color:var(--fg)}

blockquote{border-left:2px solid var(--gold-line);margin:1rem 0;padding:.4rem 0 .4rem .9rem;
  color:var(--muted);font-size:.9rem}
details{font-size:.83rem;color:var(--muted)}
summary{cursor:pointer;list-style:none}
summary::-webkit-details-marker{display:none}
summary::before{content:"›";display:inline-block;margin-right:.45rem;color:var(--faint);
  transition:transform .12s}
details[open]>summary::before{transform:rotate(90deg)}
pre,pre.box{white-space:pre-wrap;background:var(--surface-2);color:var(--fg);
  padding:.7rem;border-radius:var(--r-sm);max-height:16rem;overflow:auto;
  font-family:var(--mono);font-size:.76rem;margin:.45rem 0}
"""

# ── shared components ────────────────────────────────────────────────────────
COMPONENTS = """
/* generic layout helpers */
.grid{display:grid;gap:1rem;grid-template-columns:repeat(auto-fill,minmax(340px,1fr))}
.row{display:flex;gap:.6rem;flex-wrap:wrap;align-items:center}
.row>*{flex:1}
.spacer{margin-left:auto}
.hint{color:var(--muted);font-size:.85rem;margin:.3rem 0 1.25rem;max-width:82ch}
.empty,.muted{color:var(--muted)}
.empty{font-style:italic}
.count{color:var(--muted);font-size:.82rem;font-variant-numeric:tabular-nums}

/* status pill + dot (session state, tiers, gates) */
.pill{display:inline-flex;align-items:center;gap:.4rem;font-size:.74rem;font-weight:560;
  padding:.32rem .7rem;border-radius:var(--r-pill);background:var(--surface-2);
  color:var(--muted);border:1px solid var(--line-2)}
.pill .dot{width:.5rem;height:.5rem;border-radius:50%;background:currentColor;flex:none}
.pill.on{color:var(--pos);border-color:var(--pos)}
.pill.warn{color:var(--gold);border-color:var(--gold-line)}
.pill.off{color:var(--faint)}

/* tag / chip */
.tag{display:inline-block;background:var(--surface-2);color:var(--muted);
  padding:.12rem .5rem;border-radius:6px;font-size:.72rem;font-weight:540;
  border:1px solid var(--line)}
.tag.warn{background:var(--gold-soft);color:var(--gold);border-color:var(--gold-line)}
.tag.mono{font-family:var(--mono);letter-spacing:-.02em}

/* card — gold hairline so it reads as an actionable unit on the dark ground */
.card{border:1px solid var(--gold-line);border-radius:var(--r);background:var(--surface);
  padding:var(--pad);display:flex;flex-direction:column;gap:.65rem;box-shadow:var(--shadow)}
.card:has(input[value=aprobar]:checked),.card.done{border-color:var(--lime);background:var(--lime-soft)}
.card:has(input[value=descartar]:checked){border-color:var(--neg);background:var(--neg-soft)}

/* stat block — the big fintech number */
.stats{display:flex;flex-wrap:wrap;gap:1.6rem}
.stat{display:flex;flex-direction:column;gap:.2rem}
.stat .k{font-size:.68rem;font-weight:680;text-transform:uppercase;letter-spacing:.08em;color:var(--faint)}
.stat .v{font-size:clamp(1.5rem,3.4vw,2.15rem);font-weight:640;line-height:1;
  color:var(--fg);font-variant-numeric:tabular-nums;letter-spacing:-.03em}
.stat .v.sm{font-size:1.25rem}
.stat .sub{font-size:.76rem;color:var(--muted)}
.delta{font-size:.8rem;font-weight:620;font-variant-numeric:tabular-nums}
.delta.pos{color:var(--pos)} .delta.neg{color:var(--neg)}

/* welcome banner (dashboard top) */
.welcome{border:1px solid var(--gold-line);border-radius:var(--r);background:var(--surface);
  padding:1.15rem 1.35rem;margin:0 0 1.4rem;box-shadow:var(--shadow)}
.welcome h2{border:0;text-transform:none;letter-spacing:-.02em;font-size:1.15rem;
  font-weight:700;color:var(--bone);margin:0 0 .3rem}
.welcome h2 b{color:var(--gold)}
.welcome p{font-size:.88rem;color:var(--muted);margin:0;max-width:80ch}

/* episode cards — full-width, tall, gold-framed, stacked vertically */
.epgrid{display:flex;flex-direction:column;gap:1.2rem}
.epc{display:flex;flex-direction:column;min-height:34rem;
  border:1px solid var(--gold-line);border-radius:var(--r);background:var(--surface);
  padding:1.7rem 1.8rem;box-shadow:var(--shadow)}
.epch{display:flex;align-items:center;gap:.55rem;flex-wrap:wrap;margin-bottom:1rem}
.epch b{font-size:1.05rem;font-weight:680}
.epch .id{font-family:var(--mono);font-size:.78rem;color:var(--gold);
  background:var(--gold-soft);border:1px solid var(--gold-line);border-radius:6px;padding:.1rem .45rem}
.now{font-size:.86rem;color:var(--muted);margin-top:.9rem}
.now b{color:var(--fg)}
.notes{font-size:.82rem;color:var(--muted);margin:.6rem 0 0;padding-left:.7rem;
  border-left:2px solid var(--gold-line)}
.btns{display:flex;gap:.5rem;flex-wrap:wrap;margin-top:auto;padding-top:1rem}

/* stage strip — 2 rows of 6 tiles. state = full-colour fill, no side bar */
.strip{display:grid;grid-template-columns:repeat(6,1fr);grid-auto-rows:minmax(8.5rem,1fr);
  gap:.5rem;margin:.5rem 0 .3rem}
@media(max-width:900px){.strip{grid-template-columns:repeat(3,1fr)}}
@media(max-width:460px){.strip{grid-template-columns:repeat(2,1fr)}}
.sc{position:relative;display:flex;flex-direction:column;
  border:1px solid var(--line-2);border-radius:var(--r-sm);
  background:var(--surface-2);padding:.65rem .6rem .6rem;text-decoration:none;
  color:var(--muted);overflow:hidden;transition:border-color .12s,transform .06s,filter .12s}
.sc .scn{display:inline-flex;align-items:center;justify-content:center;width:1.4rem;height:1.4rem;
  border-radius:50%;background:var(--surface-3);color:var(--muted);
  font-size:.72rem;font-weight:700;font-variant-numeric:tabular-nums;margin-bottom:.4rem}
.sc b{display:block;color:var(--bone);font-size:.79rem;font-weight:650;letter-spacing:-.01em;
  line-height:1.2}
.sc .scd{display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;
  margin-top:.28rem;font-size:.7rem;line-height:1.3;color:var(--muted)}
/* bottom phantom pill: "Ver más" (reachable) / "Pendiente" (future) */
.sc .scpill{margin-top:auto;align-self:flex-start;
  display:inline-block;padding:.22rem .6rem;border-radius:var(--r-pill);
  border:1px solid var(--gold-line);background:transparent;
  font-size:.64rem;font-weight:600;letter-spacing:.02em;color:var(--bone);
  margin-top:.7rem}
.sc .scpill.pend{border-color:var(--line-2);color:var(--faint)}
a.sc:hover{text-decoration:none;filter:brightness(1.12)}
a.sc:hover .scpill{background:var(--gold-soft);border-color:var(--gold)}
/* pending: dark + hatch, still framed so it's scannable */
.sc:not(a){opacity:.85}
.sc:not(a)::after{content:"";position:absolute;inset:0;background:var(--hatch);pointer-events:none;opacity:.6}
/* done: full gold-tinted fill, warm ink */
.sc.done{background:var(--done-fill);border-color:var(--gold-line);color:var(--done-ink)}
.sc.done b{color:var(--done-ink)}
.sc.done .scd{color:#b7a072}
.sc.done .scn{background:var(--gold);color:var(--gold-ink)}
.sc.done .scpill{border-color:#8a6f38;color:var(--done-ink)}
/* current: full lime fill, dark ink */
.sc.cur{background:var(--lime);border-color:var(--lime)}
.sc.cur b,.sc.cur .scd,.sc.cur .scn{color:var(--lime-ink)}
.sc.cur .scd{opacity:.8}
.sc.cur .scn{background:var(--lime-ink);color:var(--lime)}
.sc.cur .scpill{border-color:#5b6321;color:var(--lime-ink)}
a.sc.cur:hover .scpill,a.sc.done:hover .scpill{background:#0002}
.sc.cur.exportado{background:var(--gold);border-color:var(--gold)}
.sc.cur.exportado b,.sc.cur.exportado .scd{color:var(--gold-ink)}
.sc.cur.exportado .scn{background:var(--gold-ink);color:var(--gold)}
.sc.cur.firmado{background:var(--pos);border-color:var(--pos)}
.sc.cur.firmado b,.sc.cur.firmado .scd{color:#0c1f14}
.sc.cur.firmado .scn{background:#0c1f14;color:var(--pos)}

/* disclosure blocks: tips + context manifest */
details.tips{border:1px solid var(--gold-line);border-radius:var(--r);background:var(--surface);
  padding:.8rem 1.05rem;margin:0 0 1.6rem;box-shadow:var(--shadow)}
details.tips>summary{font-weight:620;color:var(--bone);font-size:.9rem}
details.tips h4{margin:1rem 0 .3rem}
details.tips p{font-size:.85rem;margin:.35rem 0}
details.tips ul{margin:.4rem 0 .7rem;padding-left:1.1rem;font-size:.85rem}
details.tips li{margin:.35rem 0}
details.man{font-size:.8rem;color:var(--muted);margin:.5rem 0}
details.man>summary{color:var(--faint);font-weight:560}
details.man code{font-size:.74rem}
details.man>div{margin-top:.4rem;padding:.55rem .7rem;background:var(--bg-2);
  border:1px solid var(--line);border-radius:var(--r-sm);line-height:1.9}

/* KPI / data table */
table.kpi{margin:.4rem 0}
table.kpi td{font-variant-numeric:tabular-nums}

/* verdict / option rows (idea + research + metrics) */
.verdict{display:flex;gap:.9rem;flex-wrap:wrap}
.verdict label{display:flex;gap:.35rem;align-items:center;font-size:.8rem;color:var(--muted)}
label.opt{display:flex;gap:.55rem;align-items:flex-start;font-size:.84rem;padding:.3rem .1rem}
label.opt input{margin-top:.15rem}

/* themed hover tooltip — replaces native title= (mechanism unchanged) */
[data-tip]{position:relative}
[data-tip]:hover::after{content:attr(data-tip);position:absolute;left:0;top:calc(100% + 8px);
  z-index:60;width:max-content;max-width:22rem;white-space:normal;
  background:var(--surface-3);color:var(--fg);border:1px solid var(--line-2);
  border-radius:var(--r-sm);padding:.55rem .75rem;font-size:.78rem;font-weight:440;line-height:1.45;
  box-shadow:var(--shadow-lift);pointer-events:none}
[data-tip]:hover::before{content:"";position:absolute;left:12px;top:calc(100% + 2px);
  border:5px solid transparent;border-bottom-color:var(--line-2);z-index:61}
header [data-tip]:hover::after{max-width:24rem}
[data-tipr][data-tip]:hover::after{left:auto;right:0}
[data-tipr][data-tip]:hover::before{left:auto;right:12px}

/* markdown file view (serve.py /view, cost.html) */
.doc{max-width:900px}
.doc h1{font-size:1.4rem;margin:.2rem 0 1rem}
.doc h2{border:0;font-size:.72rem;margin:2rem 0 .6rem}
.doc h3{margin:1.4rem 0 .4rem}
.doc li{margin:.25rem 0}
.doc table{margin:.8rem 0}
"""

CSS = "<style>" + TOKENS + BASE + COMPONENTS + "</style>"

# ── shared browser JS ────────────────────────────────────────────────────────
HELPERS = """
const DASH="http://localhost:8765";
function jget(k,d){try{return JSON.parse(localStorage.getItem(k))??d}catch(e){return d}}
async function saveTxt(name,txt,doneMsg){
  try{
    const fh=await window.showSaveFilePicker({suggestedName:name,
      types:[{description:'texto',accept:{'text/plain':['.txt']}}]});
    const w=await fh.createWritable(); await w.write(txt); await w.close();
    if(doneMsg)alert(doneMsg); return;
  }catch(e){if(e&&e.name==='AbortError')return;}
  navigator.clipboard&&navigator.clipboard.writeText(txt).catch(()=>{});
  const a=document.createElement('a');
  a.href=URL.createObjectURL(new Blob([txt],{type:'text/plain'}));
  a.download=name; a.click();
}
// finishStage: try the local dashboard server (1-click gate). Fall back to
// a plain download if it isn't running. epid/stage identify the episode.
async function finishStage(name,txt,epid,stage,doneMsg,payload){
  if(epid&&stage!=null){
    try{
      const r=await fetch(DASH+"/finish",{method:"POST",
        headers:{"content-type":"application/json"},
        body:JSON.stringify({ep:epid,stage:stage,payload:Object.assign({txt:txt},payload||{})})});
      if(r.ok){const j=await r.json();
        alert("Stage "+stage+" cerrado.\\n"+(j.msg||"")+"\\n\\nEl panel se ha actualizado.");
        return;}
    }catch(e){/* server off -> fall through to download */}
  }
  return saveTxt(name,txt,doneMsg+"\\n\\n(server no detectado — descarga; luego: python tools/advance.py "+(epid||"E0XX")+")");
}
"""


# ── the one HTML wrapper ─────────────────────────────────────────────────────
def shell(title, header_html="", body_html="", script_html="", extra_css="", head_extra=""):
    """Full document. extra_css is a raw <style>…</style> string of page-specific rules."""
    head = ('<!doctype html><html lang="es"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f"<title>{title}</title>{CSS}{extra_css}{head_extra}</head><body>\n")
    hdr = f"<header>{header_html}</header>\n" if header_html else ""
    scr = f"<script>{HELPERS}{script_html}</script>\n" if (script_html or header_html) else ""
    return head + hdr + f"<main>{body_html}</main>\n" + scr + "</body></html>\n"
