# -*- coding: utf-8 -*-
"""Generator halaman web novel FALLEN RULE dari make_fallen_rule_docx_v6.py.

Membaca blok chapter_heading()/P() dari generator docx, lalu menghasilkan
satu berkas HTML per bab di website/novel/, mengelola nav prev/next antar
bab, dan memperbarui section Novel di index.html.

Pola:
    - Satu bab dengan gelar PROLOG DIKELOMPOKKAN DENGAN BAB 1 (satu berkas).
    - Bab berikutnya satu berkas per bab (arc1-babN.html).
    - Berkas LAMPIRAN/desain karakter dilewati.

Cara pakai:
    python tools/build_novel_site.py              # bangun ke website (default)
    python tools/build_novel_site.py --src <file> # ganti sumber konten
"""
import argparse
import ast
import html
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SRC = r"D:\Novel\make_fallen_rule_docx_v6.py"
NOVEL_DIR = os.path.join(BASE, "novel")
INDEX = os.path.join(BASE, "index.html")

# Nama gelar bab -> kunci berkas. Dua gelar pertama digabung.
ARC1_TITLES = ["PROLOG", "BAB 1", "BAB 2"]


def esc(t):
    return html.escape(t, quote=True)


def split_heading(text):
    """'BAB 1 — ATURAN PERTAMA' -> (nama, sub)."""
    text = text.replace("\u2014", "-").replace("\u2013", "-")
    if "-" in text:
        name, sub = text.split("-", 1)
        return name.strip().title(), sub.strip().title()
    return text.strip().title(), ""


def block_to_html(blk):
    """Satu blok konten (P) jadi markup HTML bab novel."""
    lines = blk.split("\n")
    marker = lines[0]
    clean = "\n".join(l for l in lines).strip()
    if marker in ("[SYSTEM NOTICE]", "[RULE SETTING]"):
        body = clean[len(marker):].strip()
        out = '<div class="system-box"><p class="sys-head">%s</p></div>' % esc(marker)
        if body:
            out += "<p>" + "<br>".join(esc(l) for l in body.split("\n")) + "</p>"
        return out
    if blk.startswith("[JENDELA KARAKTER"):
        return '<p class="strong-line">' + "<br>".join(esc(l) for l in lines) + "</p>"
    if re.match(r"^[-—]\s*AKHIR\b", clean):
        return '<p class="novel-end">%s</p>' % esc(clean)
    return "<p>" + "<br>".join(esc(l) for l in lines) + "</p>"


def parse_blocks(src_path):
    """Kembalikan daftar (kode, teks) dari AST generator docx."""
    with open(src_path, encoding="utf-8") as f:
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
    return blocks


def split_chapters(blocks):
    """Pisahkan blok per bab. Kembalikan [(titles_key, [(name, text)])]."""
    chapters = []
    current = None
    for name, text in blocks:
        if name == "chapter_heading":
            key = split_heading(text)[0]
            if key.upper() == "LAMPIRAN":
                break
            if current:
                chapters.append(current)
            current = {"key": key, "blocks": [], "text": text}
        elif name == "ref_sheet":
            break
        elif current is not None:
            current["blocks"].append(text)
    if current:
        chapters.append(current)
    return chapters


def group_files(chapters):
    """Prolog digabung dengan Bab 1 -> satu berkas; tiap bab lain satu berkas.

    Kembalikan daftar grup; tiap grup = daftar kamus bab (bisa >1 utk gabungan).
    """
    groups = []
    i = 0
    while i < len(chapters):
        ch = chapters[i]
        if ch["key"].upper() == "PROLOG" and i + 1 < len(chapters):
            groups.append([ch, chapters[i + 1]])
            i += 2
        else:
            groups.append([ch])
            i += 1
    return groups


def render_chapter_html(chap, content_html, prev_link, next_link):
    key = chap["key"]
    name, sub = split_heading(chap["text"]) if chap.get("text") else (key, "")
    title_parts = []
    if key.upper() == "PROLOG":
        title_parts.append("Arc 1: Prolog &amp; Bab 1")
    else:
        t = "%s" % esc(name)
        if sub:
            t += ": %s" % esc(sub)
        title_parts.append(t)
    title = " — ".join(title_parts) + " — FALLEN RULE (Novel)"

    nav = ""
    if prev_link:
        nav += '  <a class="btn" href="%s">&larr; %s</a>\n' % (prev_link[0], prev_link[1])
    nav += '  <a class="btn" href="../index.html">Semua bab</a>\n'
    if next_link:
        nav += '  <a class="btn" href="%s">%s &rarr;</a>\n' % (next_link[0], next_link[1])

    return f"""<!DOCTYPE html>
<html lang="id" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
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
{content_html}
</main>
<nav class="novel-nav">
{nav}</nav>
<footer class="foot">&copy; FALLEN RULE &middot; Novel orisinal &middot; Dibaca gratis</footer>
<script src="../assets/js/app.js"></script>
</body>
</html>
"""


def render_chapter_content(chap, is_first_in_group):
    """Render satu bab: heading + semua paragraf. Pisah dgn chap-break bila bukan pertama."""
    parts = []
    name, sub = split_heading(chap["text"]) if chap.get("text") else (chap["key"], "")
    label = "Prolog" if name.upper() == "PROLOG" else (name if name else key)
    heading = (
        ('<div class="novel-chap-break"></div>\n' if not is_first_in_group else '')
        + '<h1 class="novel-title">%s</h1>\n'
        + '<h2 class="novel-sub">%s</h2>\n'
        + '<div class="novel-sep"></div>'
    ) % (esc(label), esc(sub or ""))
    parts.append(heading)
    for blk in chap["blocks"]:
        if "-LAMPIRAN-" in blk or "REF_SHEET" in blk:
            continue
        for sub_blk in blk.split("\n\n"):
            sub_blk = sub_blk.strip()
            if not sub_blk:
                continue
            parts.append(block_to_html(sub_blk))
    return "\n".join(parts)


def bab_number(key):
    m = re.search(r"bab\s+(\d+)", key, re.IGNORECASE)
    return int(m.group(1)) if m else 0


def file_name_for(key, chapter_no=None):
    if key.upper() == "PROLOG":
        return "arc1-prolog-bab1.html"
    n = bab_number(key) or chapter_no or 1
    return "arc1-bab%d.html" % max(n, 1)


def card_html(group):
    """Kartu episode untuk satu grup bab (dipakai di index.html)."""
    chap = group[0]
    key = chap["key"]
    name, sub = split_heading(chap["text"]) if chap.get("text") else (key, "")
    fname = file_name_for(key, 1)
    if key.upper() == "PROLOG":
        title = "Prolog &amp; Bab 1"
    else:
        title = "%s" % esc(name)
        if sub:
            title += " &#8212; %s" % esc(sub)
    return (
        '    <a class="episode-card" href="novel/%s">\n'
        '      <div class="thumb" style="background-image:url(\'assets/images/ep1/panel-01.webp\')"></div>\n'
        '      <div class="meta">\n'
        '        <span class="badge">Arc 1</span>\n'
        '        <h2>%s</h2>\n'
        '        <p>Naskah lengkap, mode baca nyaman.</p>\n'
        '        <span class="buttons">Baca novel &rarr;</span>\n'
        '      </div>\n'
        '    </a>'
    ) % (fname, title)


def update_index(site_dir, groups, dry=False):
    """Tambahkan kartu bab yang belum ada ke section Novel di index.html.

    Kartu disisipkan berurutan oleh nomor bab ke blok episode-list yang
    mengikuti judul section id="novel". Prolog/Bab 1 = nomor 0.
    """
    idx_path = os.path.join(site_dir, "index.html")
    with open(idx_path, encoding="utf-8") as f:
        html_src = f.read()

    marker = 'id="novel"'
    start = html_src.find(marker)
    if start < 0:
        return idx_path, html_src, 0
    title_end = html_src.find("</section>", start)
    if title_end < 0:
        return idx_path, html_src, 0

    # blok episode-list Novel = section episode-list pertama SETELAH section-title id="novel"
    list_start = html_src.find('class="episode-list"', title_end)
    if list_start < 0:
        list_start = title_end
    sec_end = html_src.find("</section>", list_start)
    if sec_end < 0:
        sec_end = len(html_src)
    region = html_src[list_start:sec_end]

    # 2) daftar kartu lama (start, end, bab_no) untuk anchor episode-card novel
    card_re = re.compile(r'(<a class="episode-card" href="novel/[^"]+">.*?</a>)', re.S)
    cards = []
    for m in card_re.finditer(region):
        href_m = re.search(r'novel/(arc1-[^"#]+)\.html', m.group(1))
        if not href_m:
            continue
        fname = href_m.group(1)
        key = "PROLOG" if "prolog" in fname else "BAB " + re.sub(r"\D", "", fname.split("-")[-1])
        cards.append((m.start(), m.end(), key))

    added = 0
    for group in groups:
        key = group[0]["key"]
        fname = file_name_for(key, 1)
        if ('href="novel/%s"' % fname) in region:
            continue
        target_no = 0 if key.upper() == "PROLOG" else bab_number(key)
        card = "\n" + card_html(group) + "\n"
        insert_at = None
        for cs, ce, ck in cards:
            if (0 if ck.upper() == "PROLOG" else bab_number(ck)) > target_no:
                insert_at = cs
                break
        if insert_at is None:
            insert_at = len(region)
        region = region[:insert_at] + card + region[insert_at:]
        # geser offset kartu lama dan tambah kartu baru ke daftar
        new_start = insert_at + len(card) + 1
        cards = [(cs + len(card), ce + len(card), ck) if cs >= insert_at else (cs, ce, ck)
                 for cs, ce, ck in cards]
        added += 1

    new_src = html_src[:list_start] + region + html_src[sec_end:]
    if not dry and added:
        with open(idx_path, "w", encoding="utf-8") as f:
            f.write(new_src)
    return idx_path, new_src, added


def build(site_dir, out_dir=None, src_path=None):
    src_path = src_path or DEFAULT_SRC
    os.makedirs(out_dir or site_dir, exist_ok=True)
    chapters = split_chapters(parse_blocks(src_path))
    groups = group_files(chapters)

    rendered = []
    for idx, group in enumerate(groups):
        chap = group[0]
        fname = file_name_for(chap["key"], idx + 1)
        prev_link = None
        next_link = None
        if idx > 0:
            pgrp = groups[idx - 1]
            pk = pgrp[0]["key"]
            plabel = "Prolog &amp; Bab 1" if pk.upper() == "PROLOG" else split_heading(pgrp[0]["text"])[0]
            prev_link = (file_name_for(pk, idx), plabel)
        if idx + 1 < len(groups):
            ngrp = groups[idx + 1]
            nk = ngrp[0]["key"]
            nlabel = split_heading(ngrp[0]["text"])[0]
            next_link = (file_name_for(nk, idx + 2), nlabel)
        contents = []
        for pos, sub in enumerate(group):
            contents.append(render_chapter_content(sub, pos == 0))
        content = "\n\n".join(contents)
        doc = render_chapter_html(chap, content, prev_link, next_link)
        rendered.append((fname, doc, chap, prev_link, next_link))
    return rendered, groups


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None, help="folder output utk dry-run (tidak menyentuh website)")
    ap.add_argument("--src", default=None, help="ganti sumber konten dokumen docx")
    ap.add_argument("--no-index", action="store_true", help="jangan perbarui index.html")
    args = ap.parse_args()

    rendered, groups = build(BASE, args.out or NOVEL_DIR, src_path=args.src)
    output_dir = args.out or NOVEL_DIR
    for fname, doc, chap, prev, nxt in rendered:
        path = os.path.join(output_dir, fname)
        with open(path, "w", encoding="utf-8") as f:
            f.write(doc)
        print("TULIS", path)
    print("OK", len(rendered), "berkas bab ->", output_dir)

    if not args.no_index:
        if args.out:
            print("(dry-run: index.html tidak ditulis)")
        else:
            idx_path, new_src, added = update_index(BASE, groups)
            print("INDEX", idx_path, "+%d kartu baru" % added)


if __name__ == "__main__":
    main()