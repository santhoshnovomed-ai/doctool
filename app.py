"""
Serena Specialized Hospital — Document Tool
============================================
Flask backend + pywebview native window.
Downloads use native Windows Save dialog via exposed Python API.
"""

import base64, io, os, re, sys, tempfile, threading, time, zipfile
from pathlib import Path
from flask import Flask, request, jsonify, Response

import _assets
import defusedxml.minidom

# ── Text replacements ─────────────────────────────────────────────────────────
TEXT_REPLACEMENTS = [
    ("Novomed Plastic Surgery Hospital LLC.", "Serena Specialized Hospital LLC"),
    ("NOVOMED PLASTIC SURGERY HOSPITAL LLC.", "SERENA SPECIALIZED HOSPITAL LLC"),
    ("Novomed Plastic Surgery Hospital LLC",  "Serena Specialized Hospital LLC"),
    ("NOVOMED PLASTIC SURGERY HOSPITAL LLC",  "SERENA SPECIALIZED HOSPITAL LLC"),
    ("Novomed Plastic Surgery Hospital",      "Serena Specialized Hospital"),
    ("NOVOMED PLASTIC SURGERY HOSPITAL",      "SERENA SPECIALIZED HOSPITAL"),
    ("NOVOMED",                               "SERENA"),
    ("Novomed",                               "Serena"),
]
URL_RE = re.compile(r"(https?://[^\s<>\"']+|www\.[^\s<>\"']+)", re.IGNORECASE)

# ── Run-merging ───────────────────────────────────────────────────────────────
def _find_elems(root, tag):
    results = []
    def walk(n):
        if n.nodeType == n.ELEMENT_NODE:
            nm = n.localName or n.tagName
            if nm == tag or nm.endswith(f":{tag}"): results.append(n)
            for c in n.childNodes: walk(c)
    walk(root); return results

def _get_child(parent, tag):
    for c in parent.childNodes:
        if c.nodeType == c.ELEMENT_NODE:
            nm = c.localName or c.tagName
            if nm == tag or nm.endswith(f":{tag}"): return c
    return None

def _get_children(parent, tag):
    return [c for c in parent.childNodes if c.nodeType == c.ELEMENT_NODE
            and (c.localName or c.tagName) in (tag, f"w:{tag}")]

def _next_sib(node):
    s = node.nextSibling
    while s:
        if s.nodeType == s.ELEMENT_NODE: return s
        s = s.nextSibling
    return None

def _is_run(n): nm = n.localName or n.tagName; return nm == "r" or nm.endswith(":r")

def _is_adj(e1, e2):
    n = e1.nextSibling
    while n:
        if n == e2: return True
        if n.nodeType == n.ELEMENT_NODE: return False
        if n.nodeType == n.TEXT_NODE and n.data.strip(): return False
        n = n.nextSibling
    return False

def _can_merge(r1, r2):
    p1, p2 = _get_child(r1, "rPr"), _get_child(r2, "rPr")
    if (p1 is None) != (p2 is None): return False
    return True if p1 is None else p1.toxml() == p2.toxml()

def _merge_content(tgt, src):
    for c in list(src.childNodes):
        if c.nodeType == c.ELEMENT_NODE:
            nm = c.localName or c.tagName
            if nm not in ("rPr",) and not nm.endswith(":rPr"): tgt.appendChild(c)

def _consolidate(run):
    ts = _get_children(run, "t")
    for i in range(len(ts)-1, 0, -1):
        c, p = ts[i], ts[i-1]
        if _is_adj(p, c):
            pt = p.firstChild.data if p.firstChild else ""
            ct = c.firstChild.data if c.firstChild else ""
            m = pt + ct
            if p.firstChild: p.firstChild.data = m
            else: p.appendChild(run.ownerDocument.createTextNode(m))
            if m.startswith(" ") or m.endswith(" "): p.setAttribute("xml:space", "preserve")
            elif p.hasAttribute("xml:space"): p.removeAttribute("xml:space")
            run.removeChild(c)

def _merge_in(container):
    first = next((c for c in container.childNodes
                  if c.nodeType == c.ELEMENT_NODE and _is_run(c)), None)
    run = first
    while run:
        while True:
            nxt = _next_sib(run)
            if nxt and _is_run(nxt) and _can_merge(run, nxt):
                _merge_content(run, nxt); container.removeChild(nxt)
            else: break
        _consolidate(run)
        s = run.nextSibling; run = None
        while s:
            if s.nodeType == s.ELEMENT_NODE and _is_run(s): run = s; break
            s = s.nextSibling

def merge_runs(xml_bytes):
    try:
        dom = defusedxml.minidom.parseString(xml_bytes.decode("utf-8"))
        root = dom.documentElement
        for e in _find_elems(root, "proofErr"):
            if e.parentNode: e.parentNode.removeChild(e)
        for r in _find_elems(root, "r"):
            for a in list(r.attributes.values()):
                if "rsid" in a.name.lower(): r.removeAttribute(a.name)
        for c in {r.parentNode for r in _find_elems(root, "r")}: _merge_in(c)
        return dom.toxml(encoding="UTF-8")
    except: return xml_bytes

# ── Text replacement ──────────────────────────────────────────────────────────
def replace_safe(text):
    tokens, ctr = {}, [0]
    def stash(m):
        k = f"\x00U{ctr[0]}\x00"; tokens[k] = m.group(0); ctr[0] += 1; return k
    p = URL_RE.sub(stash, text)
    for old, new in TEXT_REPLACEMENTS: p = p.replace(old, new)
    for k, v in tokens.items(): p = p.replace(k, v)
    return p

def replace_xml(xml):
    at, ac = {}, [0]
    def sa(m):
        k = f"\x00A{ac[0]}\x00"; at[k] = m.group(0); ac[0] += 1; return k
    r = re.sub(r'Target="[^"]*novomed[^"]*"', sa, xml, flags=re.IGNORECASE)
    r = re.sub(r'w:name="[^"]*"', sa, r)
    r = replace_safe(r)
    for k, v in at.items(): r = r.replace(k, v)
    return r

# ── DOCX processing ───────────────────────────────────────────────────────────
def process_docx(src_bytes, logo_bytes):
    inb, outb = io.BytesIO(src_bytes), io.BytesIO()
    with zipfile.ZipFile(inb, "r") as zi, \
         zipfile.ZipFile(outb, "w", zipfile.ZIP_DEFLATED) as zo:
        logo_targets = set()
        for item in zi.infolist():
            if item.filename.endswith("header1.xml.rels"):
                t = zi.read(item.filename).decode("utf-8", "ignore")
                m = re.search(r'Id="rId1"[^>]*Target="([^"]+)"', t)
                if m: logo_targets.add("word/" + m.group(1))
        for item in zi.infolist():
            data = zi.read(item.filename)
            if item.filename in logo_targets:
                zo.writestr(item, logo_bytes); continue
            if item.filename.endswith("word/document.xml"):
                data = merge_runs(data)
                try: text = data.decode("utf-8")
                except: text = data.decode("utf-8", "replace")
                zo.writestr(item, replace_xml(text).encode("utf-8")); continue
            if item.filename.endswith(".xml") or item.filename.endswith(".rels"):
                try:
                    text = data.decode("utf-8")
                    data = replace_xml(text).encode("utf-8")
                except: pass
            zo.writestr(item, data)
    return outb.getvalue()

# ── PDF conversion ────────────────────────────────────────────────────────────
def convert_to_pdf(docx_bytes, filename):
    import shutil, subprocess
    candidates = ["soffice", "libreoffice",
                  r"C:\Program Files\LibreOffice\program\soffice.exe",
                  r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"]
    lo = next((c for c in candidates if shutil.which(c) or Path(c).exists()), None)
    if lo:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / filename
            src.write_bytes(docx_bytes)
            subprocess.run([lo, "--headless", "--convert-to", "pdf",
                            "--outdir", tmp, str(src)],
                           capture_output=True, timeout=180)
            pdf = Path(tmp) / (src.stem + ".pdf")
            if pdf.exists(): return pdf.read_bytes(), ""
    try:
        import docx2pdf
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / filename
            out = Path(tmp) / (Path(filename).stem + ".pdf")
            src.write_bytes(docx_bytes)
            docx2pdf.convert(str(src), str(out))
            if out.exists(): return out.read_bytes(), ""
    except: pass
    return None, "No PDF engine. Install LibreOffice: https://www.libreoffice.org/download/"

# ── In-memory file store (for downloads) ─────────────────────────────────────
_file_store: dict[str, tuple[str, bytes]] = {}  # id -> (filename, bytes)

def _store_file(filename: str, data: bytes) -> str:
    import uuid
    fid = str(uuid.uuid4())
    _file_store[fid] = (filename, data)
    return fid

# ── Flask app ─────────────────────────────────────────────────────────────────
flask_app = Flask(__name__)
flask_app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024

LOGO_BYTES = base64.b64decode(_assets.LOGO_B64)

@flask_app.route("/")
def index():
    return Response(_assets.HTML, mimetype="text/html")

@flask_app.route("/rebrand", methods=["POST"])
def rebrand():
    files = request.files.getlist("files")
    if not files: return jsonify(error="No files"), 400
    results = []
    for f in files:
        try:
            data = process_docx(f.read(), LOGO_BYTES)
            fid  = _store_file(f.filename, data)
            results.append({"name": f.filename, "id": fid, "ok": True})
        except Exception as e:
            results.append({"name": f.filename, "error": str(e), "ok": False})
    return jsonify(results=results)

@flask_app.route("/convert", methods=["POST"])
def convert():
    files = request.files.getlist("files")
    if not files: return jsonify(error="No files"), 400
    results = []
    for f in files:
        try:
            pdf, err = convert_to_pdf(f.read(), f.filename)
            if pdf:
                name = Path(f.filename).stem + ".pdf"
                fid  = _store_file(name, pdf)
                results.append({"name": name, "id": fid, "ok": True})
            else:
                results.append({"name": f.filename, "error": err, "ok": False})
        except Exception as e:
            results.append({"name": f.filename, "error": str(e), "ok": False})
    return jsonify(results=results)

@flask_app.route("/download/<fid>")
def download(fid):
    from flask import send_file as sf
    if fid not in _file_store:
        return "File not found", 404
    filename, data = _file_store[fid]
    return sf(io.BytesIO(data), as_attachment=True,
               download_name=filename)

@flask_app.route("/download_zip/<tab>")
def download_zip(tab):
    from flask import send_file as sf
    # Collect all stored files whose names match the tab type
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        count = 0
        for fid, (fname, data) in list(_file_store.items()):
            is_pdf  = fname.endswith(".pdf")
            is_docx = fname.endswith(".docx")
            if (tab == "convert" and is_pdf) or (tab == "rebrand" and is_docx):
                zf.writestr(fname, data)
                count += 1
    if count == 0:
        return "No files", 404
    buf.seek(0)
    zname = "Serena_PDFs.zip" if tab == "convert" else "Serena_Rebranded.zip"
    return sf(buf, as_attachment=True, download_name=zname,
               mimetype="application/zip")

@flask_app.route("/engines")
def engines():
    import shutil
    result = []
    lo_candidates = ["libreoffice", "soffice",
                     r"C:\Program Files\LibreOffice\program\soffice.exe",
                     r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"]
    lo = next((c for c in lo_candidates if shutil.which(c) or Path(c).exists()), None)
    result.append({"name": "LibreOffice", "ok": bool(lo),
                   "note": lo if lo else "Not found — install from libreoffice.org"})
    try:
        import docx2pdf
        if sys.platform == "win32":
            try:
                import win32com.client
                result.append({"name": "Microsoft Word", "ok": True, "note": "Ready"})
            except:
                result.append({"name": "Microsoft Word", "ok": False, "note": "pywin32 missing"})
        else:
            result.append({"name": "Microsoft Word", "ok": False, "note": "Windows only"})
    except:
        result.append({"name": "Microsoft Word", "ok": False, "note": "docx2pdf not installed"})
    return jsonify(engines=result)

# ── pywebview exposed API ─────────────────────────────────────────────────────
# These functions are called directly from JavaScript via window.pywebview.api.*
class PyAPI:
    """Python functions exposed to JavaScript."""

    def save_file(self, file_id: str, default_name: str) -> dict:
        """Show native Save dialog and write the file."""
        import webview
        if file_id not in _file_store:
            return {"ok": False, "error": "File not found"}

        filename, data = _file_store[file_id]

        # Determine file type filter
        if default_name.endswith(".pdf"):
            file_types = ("PDF Files (*.pdf)",)
        else:
            file_types = ("Word Documents (*.docx)",)

        win = webview.windows[0]
        paths = win.create_file_dialog(
            webview.FileDialog.SAVE,
            save_filename=default_name,
            file_types=file_types,
        )

        if paths:
            save_path = paths[0] if isinstance(paths, (list, tuple)) else paths
            # Ensure correct extension
            if default_name.endswith(".pdf") and not save_path.endswith(".pdf"):
                save_path += ".pdf"
            elif default_name.endswith(".docx") and not save_path.endswith(".docx"):
                save_path += ".docx"
            try:
                Path(save_path).write_bytes(data)
                return {"ok": True, "path": save_path}
            except Exception as e:
                return {"ok": False, "error": str(e)}

        return {"ok": False, "error": "cancelled"}

    def save_all_zip(self, tab: str) -> dict:
        """Save all processed files as a ZIP via native Save dialog."""
        import webview
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            count = 0
            for fid, (fname, data) in list(_file_store.items()):
                if (tab == "convert" and fname.endswith(".pdf")) or \
                   (tab == "rebrand" and fname.endswith(".docx")):
                    zf.writestr(fname, data)
                    count += 1
        if count == 0:
            return {"ok": False, "error": "No files to zip"}

        zname = "Serena_PDFs.zip" if tab == "convert" else "Serena_Rebranded.zip"
        win = webview.windows[0]
        paths = win.create_file_dialog(
            webview.FileDialog.SAVE,
            save_filename=zname,
            file_types=("ZIP Files (*.zip)",),
        )
        if paths:
            save_path = paths[0] if isinstance(paths, (list, tuple)) else paths
            if not save_path.endswith(".zip"): save_path += ".zip"
            try:
                Path(save_path).write_bytes(buf.getvalue())
                return {"ok": True, "path": save_path}
            except Exception as e:
                return {"ok": False, "error": str(e)}
        return {"ok": False, "error": "cancelled"}


# ── Entry point ───────────────────────────────────────────────────────────────
def start_flask():
    flask_app.run(host="127.0.0.1", port=5757, debug=False, use_reloader=False)

def main():
    import webview

    api = PyAPI()

    # Start Flask
    threading.Thread(target=start_flask, daemon=True).start()
    time.sleep(0.6)

    win = webview.create_window(
        "Serena Specialized Hospital — Document Tool",
        url="http://127.0.0.1:5757",
        width=1100, height=800,
        min_size=(900, 620),
        resizable=True,
        js_api=api,           # <-- exposes PyAPI methods to JS
    )
    webview.start(gui="edgechromium")

if __name__ == "__main__":
    main()
