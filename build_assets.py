"""
build_assets.py — run before PyInstaller to generate _assets.py
"""
import base64
from pathlib import Path

LOGO_B64 = base64.b64encode(Path("serena_logo_hq.png").read_bytes()).decode()

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Serena — Document Tool</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=DM+Sans:wght@300;400;500;600&display=swap');
  :root {
    --navy:#0d1b2a; --gold:#c9a84c; --gold2:#e8c96e; --cream:#f7f3ee;
    --white:#ffffff; --slate:#4a5568; --green:#276749; --red:#c53030;
    --radius:10px; --shadow:0 4px 24px rgba(13,27,42,.10);
  }
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:'DM Sans',sans-serif;background:var(--cream);color:var(--navy);min-height:100vh;display:flex;flex-direction:column}
  header{background:var(--navy);padding:0 40px;display:flex;align-items:center;height:68px;gap:18px;border-bottom:2px solid var(--gold)}
  .logo-img{height:34px;filter:brightness(0) invert(1)}
  .header-title{font-family:'Cormorant Garamond',serif;font-size:1.35rem;font-weight:600;color:var(--white);letter-spacing:.03em}
  .header-sub{font-size:.75rem;color:var(--gold);letter-spacing:.08em;text-transform:uppercase;margin-left:auto}
  .tabs{display:flex;background:var(--navy);padding:0 40px;gap:2px}
  .tab{padding:12px 28px;font-size:.85rem;font-weight:500;letter-spacing:.04em;color:rgba(255,255,255,.5);cursor:pointer;border-bottom:3px solid transparent;transition:all .2s;user-select:none}
  .tab:hover{color:rgba(255,255,255,.85)}
  .tab.active{color:var(--gold);border-bottom-color:var(--gold)}
  main{flex:1;padding:36px 40px;max-width:1000px;margin:0 auto;width:100%}
  .panel{display:none;animation:fadeIn .25s ease}
  .panel.active{display:block}
  @keyframes fadeIn{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}
  .info-card{background:var(--white);border:1px solid #e2e8f0;border-left:4px solid var(--gold);border-radius:var(--radius);padding:20px 24px;margin-bottom:28px;box-shadow:var(--shadow)}
  .info-card h3{font-family:'Cormorant Garamond',serif;font-size:1.1rem;font-weight:700;margin-bottom:14px;color:var(--navy)}
  .change-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px 24px}
  .change-row{display:flex;align-items:baseline;gap:8px;font-size:.82rem;line-height:1.5}
  .change-from{color:#e53e3e;font-weight:500;font-family:'Courier New',monospace;font-size:.78rem}
  .change-arr{color:var(--slate);font-size:.9rem}
  .change-to{color:var(--green);font-weight:500;font-family:'Courier New',monospace;font-size:.78rem}
  .preserve-list{margin-top:10px;display:flex;flex-wrap:wrap;gap:6px}
  .chip{background:#f0fff4;border:1px solid #9ae6b4;color:var(--green);border-radius:20px;padding:2px 10px;font-size:.75rem;font-weight:500}
  .dropzone{border:2px dashed #cbd5e0;border-radius:var(--radius);padding:48px 24px;text-align:center;cursor:pointer;transition:all .2s;background:var(--white);position:relative}
  .dropzone:hover,.dropzone.dragover{border-color:var(--gold);background:#fffdf5}
  .dropzone input[type=file]{position:absolute;inset:0;opacity:0;cursor:pointer;width:100%;height:100%}
  .drop-icon{font-size:2.5rem;margin-bottom:10px}
  .drop-title{font-size:1rem;font-weight:600;margin-bottom:4px}
  .drop-sub{font-size:.82rem;color:var(--slate)}
  .file-list{margin-top:16px;display:flex;flex-direction:column;gap:8px}
  .file-item{background:var(--white);border:1px solid #e2e8f0;border-radius:8px;padding:10px 16px;display:flex;align-items:center;gap:12px;font-size:.85rem}
  .file-icon{font-size:1.2rem}
  .file-name{font-weight:500;flex:1}
  .file-size{color:var(--slate);font-size:.78rem}
  .file-remove{cursor:pointer;color:#a0aec0;font-size:1.1rem;transition:color .15s}
  .file-remove:hover{color:var(--red)}
  .btn{display:inline-flex;align-items:center;gap:8px;padding:12px 28px;border:none;border-radius:8px;font-family:'DM Sans',sans-serif;font-size:.9rem;font-weight:600;cursor:pointer;transition:all .18s;letter-spacing:.02em}
  .btn-primary{background:var(--navy);color:var(--white);box-shadow:0 2px 8px rgba(13,27,42,.25)}
  .btn-primary:hover{background:#1a2e47;transform:translateY(-1px)}
  .btn-primary:disabled{background:#a0aec0;cursor:not-allowed;transform:none}
  .btn-gold{background:var(--gold);color:var(--navy);box-shadow:0 2px 8px rgba(201,168,76,.35)}
  .btn-gold:hover{background:var(--gold2);transform:translateY(-1px)}
  .btn-actions{margin-top:20px;display:flex;gap:12px;align-items:center;flex-wrap:wrap}
  .progress-wrap{margin-top:20px;display:none}
  .progress-wrap.show{display:block}
  .progress-bar-bg{background:#e2e8f0;border-radius:99px;height:6px;overflow:hidden;margin-top:8px}
  .progress-bar{height:100%;background:linear-gradient(90deg,var(--gold),var(--navy));border-radius:99px;transition:width .4s;width:0%}
  .progress-label{font-size:.82rem;color:var(--slate);margin-bottom:4px}
  .results{margin-top:20px;display:flex;flex-direction:column;gap:8px}
  .result-item{border-radius:8px;padding:12px 16px;display:flex;align-items:center;gap:12px;font-size:.85rem}
  .result-ok{background:#f0fff4;border:1px solid #9ae6b4}
  .result-err{background:#fff5f5;border:1px solid #feb2b2}
  .result-icon{font-size:1.1rem}
  .result-name{font-weight:500;flex:1}
  .result-dl{background:var(--gold);color:var(--navy);border:none;border-radius:6px;padding:6px 16px;font-size:.82rem;font-weight:600;cursor:pointer;transition:background .15s;display:inline-flex;align-items:center;gap:6px}
  .result-dl:hover{background:var(--gold2)}
  .result-dl:disabled{background:#e2e8f0;color:#a0aec0;cursor:not-allowed}
  .result-err-msg{color:var(--red);font-size:.78rem;flex:1}
  .engine-card{background:var(--white);border:1px solid #e2e8f0;border-radius:var(--radius);padding:18px 24px;margin-bottom:24px}
  .engine-card h3{font-size:.9rem;font-weight:600;margin-bottom:12px;color:var(--slate);text-transform:uppercase;letter-spacing:.06em}
  .engine-row{display:flex;align-items:center;gap:10px;padding:6px 0;font-size:.85rem;border-bottom:1px solid #f7fafc}
  .engine-row:last-child{border:none}
  .engine-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0}
  .dot-green{background:#48bb78}
  .dot-red{background:#fc8181}
  .engine-name{font-weight:500;width:200px}
  .engine-note{color:var(--slate);font-size:.78rem}
  .saved-badge{background:#f0fff4;border:1px solid #9ae6b4;color:var(--green);border-radius:6px;padding:4px 10px;font-size:.78rem;font-weight:500}
  .toast{position:fixed;bottom:24px;right:24px;background:var(--navy);color:white;padding:12px 20px;border-radius:8px;font-size:.85rem;font-weight:500;box-shadow:0 4px 20px rgba(0,0,0,.3);transform:translateY(80px);opacity:0;transition:all .3s;z-index:999;border-left:3px solid var(--gold)}
  .toast.show{transform:translateY(0);opacity:1}
</style>
</head>
<body>

<header>
  <img class="logo-img" src="data:image/png;base64,LOGO_PLACEHOLDER" alt="Serena Logo">
  <div><div class="header-title">Serena Specialized Hospital</div></div>
  <div class="header-sub">Document Tool</div>
</header>

<div class="tabs">
  <div class="tab active" onclick="switchTab('rebrand')">✏️ &nbsp;Rebrand DOCX</div>
  <div class="tab"        onclick="switchTab('convert')">📄 &nbsp;Convert to PDF</div>
</div>

<main>

<!-- TAB 1 -->
<div class="panel active" id="panel-rebrand">
  <div class="info-card">
    <h3>What gets changed</h3>
    <div class="change-grid">
      <div class="change-row"><span class="change-from">Novomed Plastic Surgery Hospital LLC.</span><span class="change-arr">→</span><span class="change-to">Serena Specialized Hospital LLC</span></div>
      <div class="change-row"><span class="change-from">NOVOMED PLASTIC SURGERY HOSPITAL</span><span class="change-arr">→</span><span class="change-to">SERENA SPECIALIZED HOSPITAL</span></div>
      <div class="change-row"><span class="change-from">Novomed (standalone)</span><span class="change-arr">→</span><span class="change-to">Serena</span></div>
      <div class="change-row"><span class="change-from">Header logo</span><span class="change-arr">→</span><span class="change-to">Serena Specialized Hospital logo (HQ)</span></div>
    </div>
    <div class="preserve-list">
      <span class="chip">✅ NPSH/POL/RAD… unchanged</span>
      <span class="chip">✅ www.novomed.com unchanged</span>
      <span class="chip">✅ NPSH abbreviation unchanged</span>
    </div>
  </div>

  <div class="dropzone" id="drop-rebrand"
       ondragover="onDragOver(event,'drop-rebrand')" ondragleave="onDragLeave('drop-rebrand')" ondrop="onDrop(event,'rebrand')">
    <input type="file" multiple accept=".docx" onchange="onFileInput(event,'rebrand')">
    <div class="drop-icon">📂</div>
    <div class="drop-title">Drop DOCX files here</div>
    <div class="drop-sub">or click to browse — multiple files supported</div>
  </div>
  <div class="file-list" id="files-rebrand"></div>
  <div class="btn-actions">
    <button class="btn btn-primary" id="btn-rebrand" onclick="runProcess('rebrand')" disabled>🔄 &nbsp;Rebrand All</button>
    <button class="btn btn-gold"    id="btn-zip-rebrand" onclick="saveZip('rebrand')" style="display:none">⬇️ &nbsp;Save All as ZIP</button>
  </div>
  <div class="progress-wrap" id="prog-rebrand">
    <div class="progress-label" id="prog-rebrand-lbl">Processing…</div>
    <div class="progress-bar-bg"><div class="progress-bar" id="prog-rebrand-bar"></div></div>
  </div>
  <div class="results" id="results-rebrand"></div>
</div>

<!-- TAB 2 -->
<div class="panel" id="panel-convert">
  <div class="engine-card">
    <h3>PDF Engine Status</h3>
    <div id="engine-status"><div class="engine-row"><div class="engine-note">Checking…</div></div></div>
  </div>

  <div class="dropzone" id="drop-convert"
       ondragover="onDragOver(event,'drop-convert')" ondragleave="onDragLeave('drop-convert')" ondrop="onDrop(event,'convert')">
    <input type="file" multiple accept=".docx" onchange="onFileInput(event,'convert')">
    <div class="drop-icon">📄</div>
    <div class="drop-title">Drop DOCX files here to convert to PDF</div>
    <div class="drop-sub">or click to browse</div>
  </div>
  <div class="file-list" id="files-convert"></div>
  <div class="btn-actions">
    <button class="btn btn-primary" id="btn-convert" onclick="runProcess('convert')" disabled>🖨️ &nbsp;Convert to PDF</button>
    <button class="btn btn-gold"    id="btn-zip-convert" onclick="saveZip('convert')" style="display:none">⬇️ &nbsp;Save All as ZIP</button>
  </div>
  <div class="progress-wrap" id="prog-convert">
    <div class="progress-label" id="prog-convert-lbl">Converting…</div>
    <div class="progress-bar-bg"><div class="progress-bar" id="prog-convert-bar"></div></div>
  </div>
  <div class="results" id="results-convert"></div>
</div>

</main>
<div class="toast" id="toast"></div>

<script>
const state = {rebrand:[], convert:[]};
const resultStore = {rebrand:[], convert:[]};

function switchTab(name){
  document.querySelectorAll('.tab').forEach((t,i)=>t.classList.toggle('active',['rebrand','convert'][i]===name));
  document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));
  document.getElementById('panel-'+name).classList.add('active');
  if(name==='convert') checkEngines();
}

function onDragOver(e,id){e.preventDefault();document.getElementById(id).classList.add('dragover')}
function onDragLeave(id){document.getElementById(id).classList.remove('dragover')}
function onDrop(e,tab){e.preventDefault();document.getElementById('drop-'+tab).classList.remove('dragover');addFiles(Array.from(e.dataTransfer.files).filter(f=>f.name.endsWith('.docx')),tab)}
function onFileInput(e,tab){addFiles(Array.from(e.target.files),tab);e.target.value=''}

function addFiles(files,tab){
  files.forEach(f=>{if(!state[tab].find(x=>x.name===f.name))state[tab].push(f)});
  renderFiles(tab);
}
function removeFile(tab,name){state[tab]=state[tab].filter(f=>f.name!==name);renderFiles(tab)}
function fmtSize(b){return b>1048576?(b/1048576).toFixed(1)+' MB':(b/1024).toFixed(0)+' KB'}

function renderFiles(tab){
  document.getElementById('files-'+tab).innerHTML=state[tab].map(f=>`
    <div class="file-item">
      <span class="file-icon">📄</span>
      <span class="file-name">${f.name}</span>
      <span class="file-size">${fmtSize(f.size)}</span>
      <span class="file-remove" onclick="removeFile('${tab}','${f.name}')">✕</span>
    </div>`).join('');
  document.getElementById('btn-'+tab).disabled=state[tab].length===0;
  document.getElementById('btn-zip-'+tab).style.display='none';
  document.getElementById('results-'+tab).innerHTML='';
}

async function runProcess(tab){
  const files=state[tab];
  if(!files.length) return;
  const endpoint = tab==='rebrand'?'rebrand':'convert';
  const prog=document.getElementById('prog-'+tab);
  const bar=document.getElementById('prog-'+tab+'-bar');
  const lbl=document.getElementById('prog-'+tab+'-lbl');
  const resEl=document.getElementById('results-'+tab);

  prog.classList.add('show'); bar.style.width='5%';
  lbl.textContent='Uploading…'; resEl.innerHTML='';
  document.getElementById('btn-'+tab).disabled=true;
  document.getElementById('btn-zip-'+tab).style.display='none';

  const fd=new FormData();
  files.forEach(f=>fd.append('files',f));

  try{
    bar.style.width='30%'; lbl.textContent='Processing…';
    const resp=await fetch('/'+endpoint,{method:'POST',body:fd});
    bar.style.width='85%';
    const data=await resp.json();
    bar.style.width='100%'; lbl.textContent='Done!';

    const results=data.results||[];
    resultStore[tab]=results;

    resEl.innerHTML=results.map((r,i)=>r.ok
      ?`<div class="result-item result-ok" id="res-${tab}-${i}">
          <span class="result-icon">✅</span>
          <span class="result-name">${r.name}</span>
          <button class="result-dl" id="dl-${tab}-${i}" onclick="saveFile('${tab}',${i})">
            💾 &nbsp;Save File
          </button>
        </div>`
      :`<div class="result-item result-err">
          <span class="result-icon">❌</span>
          <span class="result-name">${r.name}</span>
          <span class="result-err-msg">${r.error}</span>
        </div>`
    ).join('');

    const okCount=results.filter(r=>r.ok).length;
    if(okCount>1) document.getElementById('btn-zip-'+tab).style.display='inline-flex';
    showToast('✅ '+okCount+' file(s) ready — click 💾 Save File to save each one');
    document.getElementById('btn-'+tab).disabled=false;
  }catch(err){
    lbl.textContent='Error: '+err.message;
    bar.style.background='#fc8181';
    document.getElementById('btn-'+tab).disabled=false;
  }
}

async function saveFile(tab, idx){
  const r=resultStore[tab][idx];
  if(!r||!r.ok) return;
  const btn=document.getElementById('dl-'+tab+'-'+idx);
  btn.disabled=true; btn.textContent='Saving…';

  try{
    const result = await window.pywebview.api.save_file(r.id, r.name);
    if(result.ok){
      btn.outerHTML=`<span class="saved-badge">✅ Saved</span>`;
      showToast('✅ Saved: '+result.path.split('\\\\').pop());
    } else if(result.error==='cancelled'){
      btn.disabled=false; btn.innerHTML='💾 &nbsp;Save File';
    } else {
      btn.disabled=false; btn.innerHTML='💾 &nbsp;Save File';
      showToast('❌ Error: '+result.error);
    }
  }catch(e){
    btn.disabled=false; btn.innerHTML='💾 &nbsp;Save File';
    showToast('❌ '+e.message);
  }
}

async function saveZip(tab){
  const btn=document.getElementById('btn-zip-'+tab);
  btn.disabled=true; btn.textContent='Saving…';
  try{
    const result=await window.pywebview.api.save_all_zip(tab);
    if(result.ok){
      showToast('✅ ZIP saved: '+result.path.split('\\\\').pop());
    } else if(result.error!=='cancelled'){
      showToast('❌ '+result.error);
    }
  }catch(e){
    showToast('❌ '+e.message);
  }
  btn.disabled=false;
  btn.innerHTML='⬇️ &nbsp;Save All as ZIP';
}

async function checkEngines(){
  const el=document.getElementById('engine-status');
  try{
    const resp=await fetch('/engines');
    const data=await resp.json();
    el.innerHTML=data.engines.map(e=>`
      <div class="engine-row">
        <div class="engine-dot ${e.ok?'dot-green':'dot-red'}"></div>
        <div class="engine-name">${e.name}</div>
        <div class="engine-note">${e.note||''}</div>
      </div>`).join('');
  }catch(e){el.innerHTML='<div class="engine-row"><div class="engine-note">Could not check</div></div>'}
}

function showToast(msg){
  const t=document.getElementById('toast');
  t.textContent=msg; t.classList.add('show');
  setTimeout(()=>t.classList.remove('show'),3500);
}

checkEngines();
</script>
</body>
</html>"""

HTML = HTML.replace("LOGO_PLACEHOLDER", LOGO_B64)

assets_py = f'# Auto-generated — do not edit\nLOGO_B64 = "{LOGO_B64}"\nHTML = {repr(HTML)}\n'
Path("_assets.py").write_text(assets_py, encoding="utf-8")
print(f"_assets.py written ({len(assets_py)//1024} KB)")
