# Serena Specialized Hospital — Document Tool

Standalone Windows `.exe` — no Python, no install, just double-click.

## How to get your EXE (5 steps)

**Step 1** — Go to [github.com](https://github.com) and sign in (free account)

**Step 2** — Create new **private** repository named `serena-doc-tool`

**Step 3** — Upload ALL files from this ZIP (keep the `.github/workflows/` folder)

**Step 4** — Click the **Actions** tab → watch **Build Windows EXE** run (~4 min)

**Step 5** — When green ✅ appears → click the run → **Artifacts** → download `Serena_Doc_Tool_Windows.zip` → unzip → double-click `Serena_Doc_Tool.exe`

---

## What the app does

Built with Flask + pywebview (native Windows WebView2 window — no browser needed).

**Tab 1 — Rebrand DOCX**
- Swaps Novomed logo → Serena Specialized Hospital logo (high-res)
- Replaces all clinic name text in header, footer and body
- Document numbers (NPSH/POL/RAD…) preserved
- URLs (www.novomed.com) preserved

**Tab 2 — Convert DOCX → PDF**
- Uses Microsoft Word if installed (best quality)
- Or LibreOffice (free: libreoffice.org)
