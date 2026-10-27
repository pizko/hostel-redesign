#!/usr/bin/env python3
"""Извлекает контент страниц оригинального likehome-hostel.ru (снимок в source/pages, 27.10.2026)
в data/pages.json: метаданные, первый экран и секции. Тексты переносятся дословно — генератор
только раскладывает их по новой сетке. Ничего не дописывает."""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source" / "pages"
SKIP = {"booking.html", "404.html"}


def clean(x):
    x = re.sub(r"(?i)<br\s*/?>", " ", x or "")
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", x))).strip()


def first(rx, s, flags=re.S):
    m = re.search(rx, s, flags)
    return m.group(1) if m else ""


def blocks_in_order(s):
    """Плоский список значимых элементов секции в порядке появления."""
    out = []
    pat = re.compile(r"(?s)<(h2|h3|h4|p|li|summary|details|blockquote|figcaption|strong|a|dt|dd|span|div)(\s[^>]*)?>(.*?)</\1>")
    for m in pat.finditer(s):
        tag, attrs, inner = m.group(1), m.group(2) or "", m.group(3)
        cls = first(r'class="([^"]*)"', attrs)
        out.append((tag, cls, inner, attrs))
    return out


def parse_section(sec):
    d = {"eyebrow": "", "h2": "", "intro": [], "items": [], "links": [], "faq": [], "quotes": [], "price_cards": []}
    sec = re.sub(r"(?s)<(svg|script|style)[^>]*>.*?</\1>", "", sec)
    d["h2"] = clean(first(r"<h2[^>]*>(.*?)</h2>", sec))
    head = first(r'(?s)<div class="section__head"[^>]*>(.*?)</div>', sec)
    if head:
        d["eyebrow"] = clean(first(r'<p class="eyebrow"[^>]*>(.*?)</p>', head))
        d["intro"] = [clean(p) for p in re.findall(r"<p(?![^>]*eyebrow)[^>]*>(.*?)</p>", head, re.S) if clean(p)]
    else:
        d["eyebrow"] = clean(first(r'<p class="eyebrow"[^>]*>(.*?)</p>', sec))
    # FAQ: details/summary
    for q, a in re.findall(r"(?s)<details[^>]*>\s*<summary[^>]*>(.*?)</summary>(.*?)</details>", sec):
        d["faq"].append({"q": clean(q), "a": clean(a)})
    if not d["faq"]:
        for q, a in re.findall(r'(?s)<(?:h3|div)[^>]*class="[^"]*faq[^"]*q[^"]*"[^>]*>(.*?)</(?:h3|div)>\s*<(?:p|div)[^>]*>(.*?)</(?:p|div)>', sec):
            d["faq"].append({"q": clean(q), "a": clean(a)})
    # отзывы
    for q in re.findall(r"(?s)<blockquote[^>]*>(.*?)</blockquote>", sec):
        txt = re.sub(r"(?s)<(cite|footer|figcaption)[^>]*>.*?</\1>", "", q)
        who = clean(first(r"<(?:cite|footer|figcaption|strong)[^>]*>(.*?)</(?:cite|footer|figcaption|strong)>", q))
        d["quotes"].append({"text": clean(txt), "author": who})
    # пункты: h3 + следующий за ним текст
    if not d["faq"]:
        parts = re.split(r"(?s)(<h3[^>]*>.*?</h3>)", sec)
        for i in range(1, len(parts), 2):
            title = clean(parts[i])
            body = parts[i + 1] if i + 1 < len(parts) else ""
            body = re.split(r"(?s)<h2|<section", body)[0]
            paras = [clean(p) for p in re.findall(r"<p[^>]*>(.*?)</p>", body, re.S) if clean(p)]
            link = re.search(r'(?s)<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', body)
            num = clean(first(r'<span class="[^"]*(?:num|step|index)[^"]*"[^>]*>(.*?)</span>', parts[i - 1][-400:]))
            price = clean(first(r'<(?:div|p|span|strong)[^>]*class="[^"]*price[^"]*"[^>]*>(.*?)</(?:div|p|span|strong)>', body))
            if title:
                d["items"].append({"title": title, "text": paras, "price": price,
                                   "link": {"href": link.group(1), "text": clean(link.group(2))} if link else None})
    # ссылки-списки (перелинковка)
    for ul in re.findall(r"(?s)<ul[^>]*>(.*?)</ul>", sec):
        for href, txt in re.findall(r'(?s)<li[^>]*>\s*<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', ul):
            d["links"].append({"href": href, "text": clean(txt)})
    return d


def parse_page(path):
    s = path.read_text(encoding="utf-8", errors="replace")
    p = {
        "file": path.name,
        "url": "https://likehome-hostel.ru/" + ("" if path.name == "index.html" else path.stem),
        "title": clean(first(r"<title>(.*?)</title>", s)),
        "description": html.unescape(first(r'name="description" content="([^"]*)"', s)),
        "canonical": first(r'rel="canonical" href="([^"]*)"', s),
        "h1": clean(first(r"<h1[^>]*>(.*?)</h1>", s)),
    }
    main = first(r"(?s)<main[^>]*>(.*)</main>", s) or s
    hero = first(r'(?s)<section class="[^"]*hero[^"]*"[^>]*>(.*?)</section>', main)
    p["hero"] = {
        "eyebrow": clean(first(r'<p class="eyebrow"[^>]*>(.*?)</p>', hero)),
        "lead": [clean(x) for x in re.findall(r'<p class="[^"]*(?:hero__lead|lead)[^"]*"[^>]*>(.*?)</p>', hero, re.S)],
        "facts": [clean(x) for x in re.findall(r'<li[^>]*>(.*?)</li>', hero, re.S)],
    }
    p["sections"] = []
    for sec in re.findall(r'(?s)<section(?! class="[^"]*hero)[^>]*>(.*?)</section>', main):
        d = parse_section(sec)
        if d["h2"] or d["items"] or d["faq"] or d["quotes"]:
            p["sections"].append(d)
    if path.name == "politika-personalnyh-dannyh.html" or path.name == "oferta.html":
        body = re.sub(r"(?s)<(script|style|svg|form)[^>]*>.*?</\1>", "", main)
        p["raw_text"] = [clean(x) for x in re.findall(r"(?s)<(?:h2|h3|p|li)[^>]*>(.*?)</(?:h2|h3|p|li)>", body) if clean(x)]
    return p


def main():
    pages = {p.name: parse_page(p) for p in sorted(SRC.glob("*.html")) if p.name not in SKIP}
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data" / "pages.json").write_text(json.dumps(pages, ensure_ascii=False, indent=1))
    for k, v in pages.items():
        n_items = sum(len(s["items"]) for s in v["sections"])
        n_faq = sum(len(s["faq"]) for s in v["sections"])
        n_q = sum(len(s["quotes"]) for s in v["sections"])
        print(f"{k:36} секций {len(v['sections']):2}  пунктов {n_items:2}  FAQ {n_faq:2}  отзывов {n_q}")


if __name__ == "__main__":
    sys.exit(main())
