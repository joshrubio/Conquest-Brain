# -*- coding: utf-8 -*-
"""
review_ui.py — shared dark-theme HTML shell for the review pages
(idea_review.py, package_review.py, …). Same look as the Stage 7/9 tools.

Not a CLI. Import STYLE, HELPERS, page().
"""

STYLE = """<style>
 :root{color-scheme:dark;
   --bg:#141310;--surface:#1e1c17;--surface-2:#29261e;--line:#3b362b;
   --fg:#f1ead7;--muted:#a89e83;--gold:#c9a24a;--gold-soft:#c9a24a1f;--bone:#e9e1cb}
 *{box-sizing:border-box}
 body{font:14px/1.5 ui-sans-serif,system-ui,-apple-system,Segoe UI,sans-serif;margin:0;
   background:var(--bg);color:var(--fg)}
 a{color:var(--gold)}
 ::selection{background:var(--gold);color:#1a1610}
 header{position:sticky;top:0;z-index:9;display:flex;gap:1.25rem;align-items:center;
   flex-wrap:wrap;padding:1rem 1.75rem;background:var(--bg);border-bottom:1px solid var(--line);
   min-height:3.6rem}
 header h1{font-size:1rem;margin:0;font-weight:700;letter-spacing:.02em;color:var(--bone)}
 .count{color:var(--muted);font-size:.85rem;font-variant-numeric:tabular-nums}
 button{font:inherit;padding:.5rem 1rem;border:1px solid var(--line);border-radius:9px;
   background:var(--surface-2);color:var(--fg);cursor:pointer;transition:.12s}
 button:hover{border-color:var(--muted)}
 button.primary{background:var(--gold);color:#1a1610;border-color:var(--gold);font-weight:600}
 button.primary:hover{filter:brightness(1.08)}
 main{max-width:1500px;margin:0 auto;padding:1.75rem}
 section{margin:0 0 2.5rem}
 h2{font-size:.95rem;font-weight:700;color:var(--bone);border-bottom:1px solid var(--line);
   padding-bottom:.45rem;margin:0 0 1rem}
 h2 .q,h2 span{font-weight:400;color:var(--muted)}
 h3{font-size:.88rem;color:var(--bone);margin:0 0 .5rem}
 .hint{color:var(--muted);font-size:.82rem;margin:.3rem 0 1.25rem;max-width:80ch}
 .empty{color:var(--muted);font-style:italic}
 .grid{display:grid;gap:1.25rem;grid-template-columns:repeat(auto-fill,minmax(360px,1fr))}
 .card{border:1px solid var(--line);border-radius:12px;background:var(--surface);
   padding:1rem;display:flex;flex-direction:column;gap:.6rem}
 .card:has(input[value=aprobar]:checked),.card.done{border-color:var(--gold);background:var(--gold-soft)}
 .card:has(input[value=descartar]:checked){border-color:#6b3b2a;background:#6b3b2a1a}
 .meta{font-size:.78rem;color:var(--muted)}
 .tag{display:inline-block;background:var(--surface-2);color:var(--muted);
   padding:.05rem .4rem;border-radius:5px;font-size:.72rem}
 label.opt{display:flex;gap:.5rem;align-items:flex-start;font-size:.83rem;cursor:pointer;
   padding:.3rem .1rem}
 label.opt input{margin-top:.15rem;accent-color:var(--gold)}
 code{font-size:.75rem;color:var(--muted);font-family:ui-monospace,monospace}
 input[type=text],input[type=number],textarea,select{width:100%;font:inherit;font-size:.82rem;
   padding:.5rem .65rem;border:1px solid var(--line);border-radius:7px;
   background:var(--bg);color:var(--fg)}
 input:focus,textarea:focus,select:focus{outline:none;border-color:var(--gold)}
 textarea{min-height:2.6rem;resize:vertical}
 .row{display:flex;gap:.6rem;flex-wrap:wrap;align-items:center}
 .row>*{flex:1}
 .verdict{display:flex;gap:.75rem;flex-wrap:wrap}
 .verdict label{display:flex;gap:.3rem;align-items:center;font-size:.8rem;cursor:pointer}
 .verdict input{accent-color:var(--gold)}
 details{font-size:.78rem;color:var(--muted)}
 details pre,pre.box{white-space:pre-wrap;background:var(--surface-2);color:var(--fg);
   padding:.65rem;border-radius:8px;max-height:16rem;overflow:auto;font-size:.75rem;margin:.4rem 0}
</style>"""

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
        alert("Stage "+stage+" cerrado.\\n"+(j.msg||"")+"\\n\\nEl dashboard se ha actualizado.");
        return;}
    }catch(e){/* server off -> fall through to download */}
  }
  return saveTxt(name,txt,doneMsg+"\\n\\n(server no detectado — descarga; luego: python tools/advance.py "+(epid||"E0XX")+")");
}
"""


def page(title, header_html, body_html, script_html):
    return ("<!doctype html><html lang=\"es\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            "<title>" + title + "</title>" + STYLE + "</head><body>\n"
            "<header>" + header_html + "</header>\n"
            "<main>" + body_html + "</main>\n"
            "<script>" + HELPERS + script_html + "</script>\n"
            "</body></html>\n")
