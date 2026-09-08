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

Consumers import four names and nothing else:
    from theme import CSS, HELPERS, FAVICON, shell
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
  /* Stage 9 timeline — clip-kind tints (quiet, desaturated; never fight gold) */
  --k-archive:#6f8390; --k-stock:#857c6c; --k-kb:#8b9a68; --k-ai:#9c6f8e;
  --k-graphic:#c9a24a; --k-none:#6a6353;
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
.qline{display:flex;align-items:center;gap:.5rem;font-size:.8rem;color:var(--gold);
  margin:.7rem 0 0;padding:.45rem .65rem;background:var(--gold-soft);
  border:1px solid var(--gold-line);border-radius:var(--r-sm)}
.qline .dot{width:.5rem;height:.5rem;border-radius:50%;background:currentColor;flex:0 0 auto;
  animation:qpulse 1.6s ease-in-out infinite}
@keyframes qpulse{0%,100%{opacity:.35}50%{opacity:1}}
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

# ── Stage 9 timeline (edit_timeline.py only — kept out of the shared CSS) ─────
TIMELINE_CSS = """<style>
body.tl{display:flex;flex-direction:column;min-height:100vh;overflow-x:hidden}
.tl .topbar{flex:0 0 auto;display:flex;align-items:center;gap:.9rem;padding:.7rem 1.15rem;
  background:var(--bg);border-bottom:1px solid var(--line-2)}
.tl .crumb{font-size:.82rem;color:var(--muted)} .tl .crumb b{color:var(--bone);font-weight:620}
.tl .ep{font-family:var(--mono);font-size:.78rem;color:var(--gold);background:var(--gold-soft);
  border:1px solid var(--gold-line);border-radius:6px;padding:.12rem .5rem}

.work{flex:0 0 auto;height:clamp(320px,42vh,380px);display:grid;
  grid-template-columns:minmax(0,1.55fr) minmax(300px,1fr);gap:1px;background:var(--line-2)}
@media(max-width:860px){.work{grid-template-columns:1fr;height:auto}}
.preview{background:var(--bg);display:flex;flex-direction:column;padding:1rem 1.15rem;min-width:0}
.screen{flex:1;position:relative;border-radius:var(--r-sm);overflow:hidden;border:1px solid var(--line-2);
  background:radial-gradient(120% 90% at 50% 0%,#221d14,#0c0b08 70%);display:grid;place-items:center}
.screen::before{content:"";position:absolute;inset:0;pointer-events:none;
  background:linear-gradient(#0000 0 12%,#0009 12% 88%,#0000 88%)}
.screen .frame{position:relative;z-index:1;text-align:center;color:var(--muted);font-size:.82rem}
.screen .big{font-family:var(--mono);font-size:2rem;color:var(--bone);letter-spacing:.02em}
.screen .tag{position:absolute;left:.7rem;bottom:.7rem;z-index:2;font-size:.62rem;font-family:var(--mono);
  color:var(--muted);background:#0008;border:1px solid var(--line-2);border-radius:5px;padding:.16rem .44rem}
.screen .lab{position:absolute;right:.7rem;bottom:.7rem;z-index:2;font-size:.58rem;letter-spacing:.08em;
  text-transform:uppercase;color:var(--neg);background:#0008;border:1px solid var(--neg);border-radius:5px;padding:.16rem .44rem}
.screen video{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;background:#000;z-index:1}
.transport{display:flex;align-items:center;gap:.8rem;padding-top:.7rem}
.play{width:2.2rem;height:2.2rem;border-radius:50%;border:1px solid var(--gold-line);background:var(--surface-2);
  display:grid;place-items:center;flex:none;padding:0}
.play:hover{border-color:var(--gold);background:var(--surface-3)}
.play svg{width:.95rem;height:.95rem;fill:var(--bone)}
.tc{font-family:var(--mono);font-size:.92rem;color:var(--bone)}
.tc .sep{color:var(--faint);margin:0 .3rem}.tc .tot{color:var(--muted)}
.phint{font-size:.7rem;color:var(--faint);margin-left:auto;max-width:20rem;text-align:right}

.inspector{background:var(--bg);padding:1rem 1.15rem;overflow-y:auto;min-width:0}
.insp-empty{color:var(--faint);font-size:.85rem;padding:2rem 0;text-align:center}
.insp-head{display:flex;align-items:baseline;gap:.5rem}
.insp-head h3{font-size:.92rem;margin:0}.insp-head .n{font-family:var(--mono);color:var(--gold);font-size:.85rem}
.insp-sec{font-size:.72rem;color:var(--muted);margin:.15rem 0 .9rem}
.insp-sec .marker{color:var(--gold);font-weight:620}
.field{margin:.7rem 0}.field>.lbl{display:block;margin-bottom:.3rem}
.notebox{background:var(--surface-2);border:1px solid var(--line-2);border-radius:var(--r-sm);
  padding:.5rem .6rem;font-size:.78rem;color:var(--muted);line-height:1.4}
.control{display:flex;align-items:center;gap:.5rem;background:var(--surface-2);border:1px solid var(--line-2);
  border-radius:var(--r-sm);padding:.42rem .56rem;font-size:.82rem}
.control select{all:unset;flex:1;color:var(--fg);font:inherit;min-width:0}
.stepper{display:flex;gap:.3rem}
.stepper button{width:1.9rem;height:1.9rem;border-radius:7px;border:1px solid var(--line-2);
  background:var(--surface-2);font-family:var(--mono);font-size:.9rem;padding:0}
.stepper button:hover{border-color:var(--gold);background:var(--surface-3)}
.stepper .val{flex:1;display:flex;align-items:center;justify-content:center;font-family:var(--mono);
  background:var(--surface-2);border:1px solid var(--line-2);border-radius:7px}
.motionrow{display:flex;flex-wrap:wrap;gap:.34rem}
.mchip{font-size:.72rem;padding:.32rem .58rem;border-radius:var(--r-pill);border:1px solid var(--line-2);
  background:var(--surface-2);color:var(--muted);cursor:pointer}
.mchip[aria-pressed="true"]{border-color:var(--gold);background:var(--gold-soft);color:var(--gold)}
textarea.fixnote{width:100%;min-height:2.6rem;resize:vertical;font:inherit;font-size:.8rem;background:var(--bg-2);
  color:var(--fg);border:1px solid var(--line-2);border-radius:var(--r-sm);padding:.5rem .6rem;line-height:1.45}
.approve{display:flex;align-items:center;gap:.55rem;margin-top:.9rem;font-size:.84rem;padding:.55rem .7rem;
  border-radius:var(--r-sm);border:1px solid var(--line-2);background:var(--surface-2);cursor:pointer}
.approve input{accent-color:var(--pos);width:16px;height:16px}
.approve.on{border-color:var(--pos);color:var(--pos);background:#63cf8b12}

.timeline{flex:1 1 auto;min-height:288px;display:flex;flex-direction:column;background:var(--bg-2);
  border-top:1px solid var(--line-2)}
.tl-bar{flex:0 0 auto;display:flex;align-items:center;gap:.8rem;padding:.5rem 1.15rem;border-bottom:1px solid var(--line)}
.zoom{display:flex;gap:.28rem;align-items:center}
.zoom button{width:1.8rem;height:1.8rem;border-radius:7px;border:1px solid var(--line-2);
  background:var(--surface-2);font-family:var(--mono);padding:0}
.zoom button:hover{border-color:var(--gold)}
.zoom .fit{width:auto;padding:0 .6rem;font-family:var(--sans);font-size:.74rem}
.tl-bar .range{font-family:var(--mono);font-size:.75rem;color:var(--muted)}
.legend{margin-left:auto;display:flex;gap:.7rem;font-size:.68rem;color:var(--muted)}
@media(max-width:900px){.legend{display:none}}
.legend i{display:inline-block;width:.62rem;height:.62rem;border-radius:3px;margin-right:.3rem;vertical-align:-1px}

.minimap{flex:0 0 auto;height:34px;margin:.5rem 1.15rem 0;position:relative;border:1px solid var(--line-2);
  border-radius:6px;overflow:hidden;background:var(--surface);cursor:grab}
.minimap:active{cursor:grabbing}
.mm-canvas{position:absolute;inset:0;width:100%;height:100%}
.mm-window{position:absolute;top:-1px;bottom:-1px;border:1.5px solid var(--gold);background:var(--gold-soft);
  border-radius:4px;pointer-events:none}
.mm-play{position:absolute;top:0;bottom:0;width:1.5px;background:var(--lime)}

.tl-scroll{flex:1 1 auto;min-height:206px;overflow-x:auto;overflow-y:hidden;padding:.55rem 0 .8rem;margin-top:.4rem}
.tl-inner{position:relative;height:100%;min-height:198px;min-width:100%;padding-right:2.5rem}
.lane{position:absolute;left:0;right:0}
.ruler{top:0;height:20px}
.tick{position:absolute;top:0;height:20px;border-left:1px solid var(--line-2);font-family:var(--mono);
  font-size:.62rem;color:var(--faint);padding-left:3px;white-space:nowrap}
.bands{top:22px;height:20px}
.band{position:absolute;top:0;height:20px;border-radius:4px;display:flex;align-items:center;padding:0 .5rem;
  font-size:.62rem;font-weight:700;letter-spacing:.09em;text-transform:uppercase;color:var(--gold);
  background:var(--gold-soft);border:1px solid var(--gold-line);overflow:hidden}
.wave{top:46px;height:40px}
.wave img{position:absolute;left:0;top:0;height:40px;image-rendering:auto;opacity:.85}
.wave .wlbl{position:absolute;left:0;top:2px;font-size:.56rem;letter-spacing:.09em;text-transform:uppercase;
  color:var(--faint);background:#0a0908cc;padding:0 .3rem;border-radius:3px;z-index:1}
.vtrack{top:92px;height:66px}
.mtrack{top:164px;height:30px}

.clip{position:absolute;top:0;height:66px;border-radius:8px;overflow:hidden;cursor:pointer;background:var(--surface);
  border:1px solid var(--line-2);display:flex;flex-direction:column;transition:border-color .1s,transform .06s}
.clip:hover{border-color:var(--faint);transform:translateY(-1px)}
.clip .kbar{height:4px;flex:none}
.clip .body{flex:1;padding:.32rem .44rem;min-width:0;display:flex;flex-direction:column;gap:.1rem}
.clip .cn{font-family:var(--mono);font-size:.66rem;color:var(--muted);display:flex;gap:.3rem}
.clip .ca{font-size:.71rem;color:var(--bone);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.clip .cd{font-size:.63rem;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}
.clip.narrow .ca,.clip.narrow .cd,.clip.narrow .cn span{display:none}
.clip .badge{position:absolute;top:.28rem;right:.3rem;font-size:.55rem;font-weight:700;letter-spacing:.04em;
  padding:.06rem .3rem;border-radius:4px;background:var(--gold);color:var(--gold-ink)}
.clip .fixdot{position:absolute;bottom:.3rem;right:.34rem;width:.5rem;height:.5rem;border-radius:50%;
  background:var(--gold);box-shadow:0 0 0 2px #0006}
.clip .okdot{position:absolute;bottom:.26rem;right:.3rem;width:.62rem;height:.62rem;color:var(--pos)}
.clip.sel{border-color:var(--gold);box-shadow:0 0 0 1px var(--gold),var(--shadow-lift);z-index:5}
.clip.expl::after{content:"";position:absolute;inset:0;pointer-events:none;
  background:repeating-linear-gradient(90deg,#0000 0 5px,#c9a24a14 5px 6px)}
.clip.uncov{background:var(--neg-soft);border-color:var(--neg);border-style:dashed}
.clip.uncov::after{content:"";position:absolute;inset:0;pointer-events:none;
  background:repeating-linear-gradient(-45deg,#0000 0 7px,#d98a5f33 7px 9px)}
.clip.uncov .ca{color:var(--neg)}
.clip.playing{border-color:var(--lime);box-shadow:0 0 0 1px var(--lime)}
.clip .grip{position:absolute;top:0;bottom:0;width:7px;cursor:ew-resize;z-index:6}
.clip .grip.l{left:0}.clip .grip.r{right:0}
.clip .grip:hover{background:var(--gold)}

.mclip{position:absolute;top:0;height:30px;border-radius:7px;background:#2a2b1c;border:1px solid #4b4d2c;
  display:flex;align-items:center;padding:0 .5rem;gap:.4rem;font-size:.66rem;color:#c9d07a;overflow:hidden}
.mclip .wv{flex:1;height:12px;border-radius:2px;opacity:.7;
  background:repeating-linear-gradient(90deg,#c9d07a55 0 2px,#0000 2px 5px)}

.playhead{position:absolute;top:0;width:2px;background:var(--lime);z-index:8;box-shadow:0 0 8px #cdd94e88}
.playhead .grab{position:absolute;top:-3px;left:-6px;width:14px;height:14px;border-radius:3px;
  background:var(--lime);cursor:ew-resize;box-shadow:0 2px 6px #000a}
.snapguide{position:absolute;top:22px;width:1px;background:var(--gold);z-index:7;display:none;box-shadow:0 0 6px var(--gold)}

.statusbar{flex:0 0 auto;display:flex;align-items:center;gap:1.3rem;flex-wrap:wrap;padding:.5rem 1.15rem;
  border-top:1px solid var(--line-2);background:var(--bg);font-size:.74rem;color:var(--muted)}
.statusbar b{color:var(--bone);font-family:var(--mono)}
.statusbar .warn b{color:var(--gold)} .statusbar .ok b{color:var(--pos)} .statusbar .bad b{color:var(--neg)}

.toast{position:fixed;left:50%;bottom:4.4rem;transform:translateX(-50%) translateY(12px);background:var(--surface-3);
  border:1px solid var(--gold-line);border-radius:var(--r-pill);padding:.6rem 1.1rem;font-size:.8rem;color:var(--bone);
  box-shadow:var(--shadow-lift);opacity:0;pointer-events:none;transition:opacity .2s,transform .2s;z-index:40}
.toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
.toast .mono{color:var(--lime);font-family:var(--mono)}
.tltip{position:fixed;z-index:50;background:var(--surface-3);color:var(--fg);border:1px solid var(--line-2);
  border-radius:var(--r-sm);padding:.5rem .66rem;font-size:.74rem;line-height:1.4;max-width:19rem;
  box-shadow:var(--shadow-lift);pointer-events:none;opacity:0;transition:opacity .1s}
.tltip.show{opacity:1} .tltip .k{font-family:var(--mono);color:var(--gold)}
@media(prefers-reduced-motion:reduce){.tl *{transition:none!important}}
</style>"""

# ── favicon — the channel avatar, downscaled (brand/assets/, tracked binaries) ─
FAVICON = ('<link rel="icon" href="/brand/assets/favicon.ico" sizes="any">'
           '<link rel="icon" type="image/png" href="/brand/assets/favicon-32.png">'
           '<link rel="apple-touch-icon" href="/brand/assets/apple-touch-icon.png">')

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
// If the server reports this stage is behind where the episode already is
// (an old review page reopened after later stages ran), it asks to confirm
// before regressing _STATUS.md — the content itself is saved either way.
async function finishStage(name,txt,epid,stage,doneMsg,payload){
  if(epid&&stage!=null){
    try{
      const post=extra=>fetch(DASH+"/finish",{method:"POST",
        headers:{"content-type":"application/json"},
        body:JSON.stringify({ep:epid,stage:stage,payload:Object.assign({txt:txt},payload||{},extra||{})})});
      let r=await post();
      if(r.status===409){
        const j=await r.json().catch(()=>({}));
        if(j.error==="stage_behind"&&confirm(j.msg||"Este episodio ya avanzó más allá de este stage. ¿Reabrirlo igualmente?")){
          r=await post({reopen:true});
        } else {
          alert("Guardado — el contenido se escribió, pero el estado del episodio no se tocó (seguía en un stage más adelantado).");
          return;
        }
      }
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
            f"<title>{title}</title>{FAVICON}{CSS}{extra_css}{head_extra}</head><body>\n")
    hdr = f"<header>{header_html}</header>\n" if header_html else ""
    scr = f"<script>{HELPERS}{script_html}</script>\n" if (script_html or header_html) else ""
    return head + hdr + f"<main>{body_html}</main>\n" + scr + "</body></html>\n"
