# -*- coding: utf-8 -*-
"""Bangun website/novel/arc1-prolog-bab1.html dari teks konten make_fallen_rule_docx_v4.py (FALLEN RULE v4)."""
import ast
import html
import re

SRC = r"D:\Proyek & Karya\Novel\make_fallen_rule_docx_v4.py"
OUT = r"D:\generate image\komik\FALLEN RULE\website\novel\arc1-prolog-bab1.html"

with open(SRC, encoding="utf-8") as f:
    src = f.read()

tree = ast.parse(src)

blocks = []
for node in tree.body:
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        call = node.value
        name = getattr(call.func, "id", "")
        if name not in ("P", "chapter_heading", "ref_sheet"):
            continue
        if len(call.args) >= 1 and isinstance(call.args[0], ast.Constant):
            blocks.append((name, call.args[0].value))

def esc(t):
    return html.escape(t, quote=True)

def para_html(blk):
    lines = blk.split("\n")
    marker = lines[0]
    if marker in ("[SYSTEM NOTICE]", "[RULE SETTING]"):
        body = "\n".join(lines[1:]).strip()
        out = '<div class="system-box"><p class="sys-head">%s</p></div>' % esc(marker)
        if body:
            out += "<p>" + "<br>".join(esc(l) for l in body.split("\n")) + "</p>"
        return out
    if blk.startswith("[JENDELA KARAKTER"):
        return "<p class=\"strong-line\">" + "<br>".join(esc(l) for l in lines) + "</p>"
    if blk.strip() in ("— AKHIR PROLOG —", "- AKHIR BAB 1 -", "— AKHIR BAB 1 —"):
        return '<p class="novel-end">%s</p>' % esc(blk.strip())
    return "<p>" + "<br>".join(esc(l) for l in lines) + "</p>"

body = []
for name, txt in blocks:
    if name == "chapter_heading":
        title, sub = txt.replace("—", "-").split(" - ", 1)
        title = title.title()
        if "Lampiran" in title:
            break
        sub = sub.title()
        is_bab1 = title.lower().startswith("bab")
        if is_bab1:
            body.append('<div class="novel-chap-break"></div>')
        body.append('<h1 class="novel-title">%s</h1>' % esc(title))
        body.append('<h2 class="novel-sub">%s</h2>' % esc(sub))
        body.append('<div class="novel-sep"></div>')
        continue
    if name == "ref_sheet":
        break
    for blk in txt.split("\n\n"):
        blk = blk.strip()
        if not blk:
            continue
        body.append(para_html(blk))

content = "\n".join(body)

doc = f"""<!DOCTYPE html>
<html lang="id" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Arc 1: Prolog &amp; Bab 1 — FALLEN RULE (Novel)</title>
<link rel="stylesheet" href="../assets/css/style.css">
<link rel="stylesheet" href="../assets/css/novel.css">
</head>
<body>
<header class="topbar">
  <a class="brand" href="../index.html">FALLEN <span>RULE</span></a>
  <nav>
    <a href="../index.html">Beranda</a>
    <span class="nav-label">Novel &middot; Arc 1</span>
    <button id="themeToggle" class="icon-btn" aria-label="Ganti tema">&#9789;</button>
  </nav>
</header>
<main class="novel">
{content}
</main>
<nav class="novel-nav">
  <a class="btn" href="../reader.html?ep=1">&#127916; Baca Komik Episode 1</a>
</nav>
<footer class="foot">&copy; FALLEN RULE &middot; Novel orisinal &middot; Dibaca gratis</footer>
<script src="../assets/js/app.js"></script>
</body>
</html>
"""

with open(OUT, "w", encoding="utf-8") as f:
    f.write(doc)
print("OK", OUT)