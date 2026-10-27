#!/usr/bin/env python3
"""Like Home — редизайн (Urban Industrial × Swiss Typography). Генератор статичного сайта.

Контент: data/pages.json (тексты страниц оригинала, tools/extract.py) и data/facts.json
(проверенные факты с указанием источника). Ничего не придумывает: компоновка новая, слова — оригинала.

  python3 tools/extract.py      # пересобрать data/pages.json из снимка source/pages
  python3 build.py              # предпросмотр: noindex, без Метрики, форма честно сообщает, что отправка — на боевом сайте
  python3 build.py --prod       # боевая сборка: index, Метрика 88450058, форма → /send_booking.php
"""
import json
import re
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "dist"
PROD = "--prod" in sys.argv
F = json.loads((ROOT / "data/facts.json").read_text())
P = json.loads((ROOT / "data/pages.json").read_text())
ORIGIN = "https://likehome-hostel.ru"
PHONE, TEL = F["phone"]["text"], F["phone"]["href"]
e = escape

NAV = [("rooms", "Номера"), ("prices", "Цены"), ("dlya-yuridicheskih-lic", "Для компаний"),
       ("how-to-get", "Как добраться"), ("faq", "FAQ"), ("otzyvy-o-nas", "Отзывы"), ("kontakty", "Контакты")]
SEO_PAGES = ["razmeshchenie-brigad", "dlya-vahtovikov", "dlya-komandirovannyh", "obshchezhitie-dlya-rabochih",
             "dolgosrochnoe-prozhivanie", "dlya-smennogo-personala"]

METRIKA = ('<script>(function(m,e,t,r,i,k,a){m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};m[i].l=1*new Date();'
           'for(var j=0;j<document.scripts.length;j++){if(document.scripts[j].src===r){return;}}'
           'k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)})'
           '(window,document,"script","https://mc.yandex.ru/metrika/tag.js","ym");'
           f'ym({F["metrika"]["id"]},"init",{{clickmap:true,trackLinks:true,accurateTrackBounce:true,webvisor:true}});</script>'
           f'<noscript><div><img src="https://mc.yandex.ru/watch/{F["metrika"]["id"]}" style="position:absolute;left:-9999px" alt=""></div></noscript>')

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Inter+Tight:wght@500;600;700;800'
         '&family=Inter:wght@400;500;600&display=swap&subset=cyrillic">')

LOGO = ('<svg class="logo-mark" viewBox="0 0 96 32" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="square">'
        '<path d="M3 26V9M3 20h25v6M9 17.5v-3.5h7.5l3.5 3.5"/></g><path d="M36 4v24" stroke="currentColor" stroke-width="1.6"/>'
        '<text x="44" y="24.5" font-family="Inter Tight, Arial, sans-serif" font-size="22" font-weight="600" fill="currentColor" letter-spacing="1">LH</text></svg>')


def page_by(slug):
    return P["index.html" if slug == "" else f"{slug}.html"]


def pic(n, alt, cls="", sizes="100vw", eager=False):
    srcset = ", ".join(f"assets/img/rooms/room-{n}-{w}.webp {w}w" for w in (640, 1280, 1920))
    load = 'fetchpriority="high" loading="eager"' if eager else 'loading="lazy"'
    return (f'<picture class="{cls}"><source type="image/webp" srcset="{srcset}" sizes="{sizes}">'
            f'<img src="assets/img/rooms/room-{n}.jpg" alt="{e(alt)}" width="1920" height="1440" {load} decoding="async"></picture>')


def stop(num, label, tone=""):
    """Подпись раздела в виде остановки на линии: номер + название + отрезок пути."""
    return (f'<div class="stop {tone}" data-reveal><span class="stop-dot" aria-hidden="true"></span>'
            f'<span class="stop-num">{num}</span><span class="stop-label">{e(label)}</span><span class="stop-rule" aria-hidden="true"></span></div>')


def head(slug, extra_schema=None):
    p = page_by(slug)
    canonical = ORIGIN + "/" + slug if slug else ORIGIN + "/"
    robots = "index, follow" if PROD else "noindex, nofollow"
    org = {"@type": ["Hostel", "LodgingBusiness"], "@id": ORIGIN + "/#hostel", "name": F["brand"]["name"], "url": ORIGIN + "/",
           "telephone": PHONE, "priceRange": "от 599 ₽ в сутки за место",
           "address": {"@type": "PostalAddress", "streetAddress": "Лихачёвский проезд, д. 5, стр. 11", "addressLocality": "Долгопрудный",
                       "addressRegion": "Московская область", "addressCountry": "RU"},
           "geo": {"@type": "GeoCoordinates", "latitude": F["address"]["geo"][0], "longitude": F["address"]["geo"][1]},
           "checkinTime": "14:00", "image": ORIGIN + "/12.jpg"}
    graph = [org, {"@type": "WebPage", "@id": canonical + "#page", "url": canonical, "name": p["title"], "description": p["description"],
                   "inLanguage": "ru", "about": {"@id": ORIGIN + "/#hostel"}}] + (extra_schema or [])
    schema = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False).replace("<", "\\u003c")
    return (f'<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
            f'<title>{e(p["title"])}</title><meta name="description" content="{e(p["description"])}"><meta name="robots" content="{robots}">'
            f'<link rel="canonical" href="{canonical}"><meta name="theme-color" content="#171B1C">'
            f'<meta property="og:type" content="website"><meta property="og:locale" content="ru_RU"><meta property="og:title" content="{e(p["title"])}">'
            f'<meta property="og:description" content="{e(p["description"])}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{ORIGIN}/12.jpg">'
            f'<link rel="icon" href="assets/img/favicon.png" type="image/png">{FONTS}<link rel="stylesheet" href="assets/css/site.css?v={VER}">'
            f'<script type="application/ld+json">{schema}</script>{METRIKA if PROD else ""}</head>')


def header(active):
    links = "".join(f'<a href="{s}"{" aria-current=page" if s == active else ""}>{e(t)}</a>' for s, t in NAV)
    return (f'<a class="skip" href="#main">К содержанию</a>'
            f'<header class="hdr" data-hdr><div class="hdr-in"><a class="logo" href="./" aria-label="Like Home — на главную">{LOGO}<span>LIKE HOME</span></a>'
            f'<nav class="hdr-nav" aria-label="Разделы">{links}</nav>'
            f'<div class="hdr-act"><a class="hdr-tel" href="{TEL}">{PHONE}</a><a class="btn btn-lime btn-s" href="#zayavka" data-to-form>Заявка</a>'
            f'<button class="burger" type="button" aria-label="Меню" aria-expanded="false" aria-controls="menu" data-burger><span></span><span></span></button></div></div></header>'
            f'<div class="menu" id="menu" hidden data-menu><nav aria-label="Меню">'
            + "".join(f'<a href="{s}"><span>{i:02d}</span>{e(t)}</a>' for i, (s, t) in enumerate([("", "Главная")] + NAV, 1))
            + f'</nav><div class="menu-foot"><a class="menu-tel" href="{TEL}">{PHONE}</a><p>{e(F["schedule"]["requests"])} · {e(F["schedule"]["checkin"])}</p></div></div>')


def form_block(title="Оставить заявку на заселение", lead="Оставьте заявку — уточним наличие мест и назовём стоимость под ваш срок."):
    """Форма — те же поля, что принимает боевой /send_booking.php. Отдельных полей «компания» и «сотрудников»
    обработчик не принимает, поэтому их нет: подстановка вела бы к потере данных."""
    return (f'<section class="sec sec-form" id="zayavka" aria-labelledby="zayavka-h"><div class="wrap form-grid">'
            f'<div class="form-intro">{stop("09", "Корпоративная заявка", "on-dark")}'
            f'<h2 class="h2" id="zayavka-h" data-reveal>{e(title)}</h2><p class="lead" data-reveal>{e(lead)}</p>'
            f'<dl class="form-facts" data-reveal><div><dt>Что нужно от вас</dt><dd>Реквизиты организации, срок размещения и количество сотрудников. Остальное подскажем по заявке.</dd></div>'
            f'<div><dt>Телефон</dt><dd><a class="big-tel" href="{TEL}">{PHONE}</a></dd></div>'
            f'<div><dt>Режим</dt><dd>{e(F["schedule"]["requests"])}<br>{e(F["schedule"]["checkin"])}</dd></div></dl></div>'
            f'<form class="lead-form" action="send_booking.php" method="post" novalidate data-form>'
            f'<div class="field"><label for="f-name">Контактное лицо</label><input id="f-name" name="name" autocomplete="name" required minlength="2"></div>'
            f'<div class="field"><label for="f-phone">Телефон</label><input id="f-phone" name="phone" type="tel" inputmode="tel" autocomplete="tel" required placeholder="+7"></div>'
            f'<div class="field-row"><div class="field"><label for="f-in">Дата заезда</label><input id="f-in" name="checkin" type="date" required></div>'
            f'<div class="field"><label for="f-days">Срок, дней</label><input id="f-days" name="days" type="number" inputmode="numeric" min="30" max="60" value="30" required>'
            f'<small>Минимальный срок — 30 дней</small></div></div>'
            f'<input class="hp" name="website" tabindex="-1" autocomplete="off" aria-hidden="true">'
            f'<label class="check"><input type="checkbox" name="consent" value="1" required><span>Согласен на обработку персональных данных согласно '
            f'<a href="politika-personalnyh-dannyh">политике</a></span></label>'
            f'<button class="btn btn-lime btn-l" type="submit"><span>Отправить заявку</span><i aria-hidden="true">→</i></button>'
            f'<p class="form-msg" role="status" aria-live="polite" data-msg></p></form></div></section>')


def footer():
    seo = "".join(f'<li><a href="{s}">{e(page_by(s)["h1"])}</a></li>' for s in SEO_PAGES)
    nav = "".join(f'<li><a href="{s}">{e(t)}</a></li>' for s, t in [("", "Главная")] + NAV)
    L = F["legal"]
    return (f'<footer class="ftr"><div class="wrap"><div class="ftr-top"><a class="logo logo-l" href="./">{LOGO}<span>LIKE HOME</span></a>'
            f'<p class="ftr-claim">Хостел для рабочих и сотрудников организаций в Долгопрудном, в 2 минутах от МЦД Новодачная.</p></div>'
            f'<div class="ftr-grid"><div><h2 class="ftr-h">Контакты</h2><a class="ftr-tel" href="{TEL}">{PHONE}</a>'
            f'<p>{e(F["address"]["full"])}</p><p>{e(F["schedule"]["requests"])}<br>{e(F["schedule"]["checkin"])}</p></div>'
            f'<div><h2 class="ftr-h">Разделы</h2><ul>{nav}</ul></div><div><h2 class="ftr-h">Форматы размещения</h2><ul>{seo}</ul></div>'
            f'<div><h2 class="ftr-h">Исполнитель</h2><p>{e(L["name"])}<br>ИНН {L["inn"]}<br>ОГРНИП {L["ogrnip"]}<br>{e(L["registry"])}</p>'
            f'<ul><li><a href="oferta">Договор публичной оферты</a></li><li><a href="politika-personalnyh-dannyh">Политика обработки персональных данных</a></li></ul></div></div>'
            f'<div class="ftr-bot"><span>© 2026 Like Home</span><span class="mono">55.9223° N · 37.5259° E</span></div></div></footer>'
            f'<div class="dock" data-dock><a class="dock-call" href="{TEL}">Позвонить</a><a class="dock-form" href="#zayavka" data-to-form>Заявка</a></div>'
            f'<script src="assets/js/site.js?v={VER}" defer></script>')


def facts_rail():
    return ('<dl class="rail">'
            f'<div class="rail-cell"><dt>{e(F["price"]["unit"])}</dt><dd><small>от</small>599<span>₽</span></dd></div>'
            f'<div class="rail-cell"><dt>минимальный срок</dt><dd>30<span>дней</span></dd></div>'
            f'<div class="rail-cell"><dt>минимальный объём</dt><dd>1<span>комната</span></dd></div>'
            f'<div class="rail-cell"><dt>мест в комнате</dt><dd class="rail-rooms">8<b>·</b>10<b>·</b>12</dd></div></dl>')


def route_svg(extra=""):
    """Собственная схема маршрута: линия, остановка «МЦД Новодачная», точка Like Home. Без официальной символики МЦД."""
    return (f'<svg class="route" viewBox="0 0 600 220" role="img" aria-label="Схема: от МЦД Новодачная до Like Home около 2 минут пешком">'
            '<path class="route-rail" d="M0 150 H600"/><path class="route-walk" d="M170 150 C 230 150, 250 70, 330 70 H430" data-draw/>'
            '<circle class="route-st" cx="170" cy="150" r="10"/><circle class="route-home" cx="430" cy="70" r="12"/>'
            '<text x="170" y="192" text-anchor="middle" class="route-t">МЦД НОВОДАЧНАЯ</text>'
            '<text x="430" y="40" text-anchor="middle" class="route-t route-t-lime">LIKE HOME</text>'
            '<text x="300" y="118" text-anchor="middle" class="route-t route-t-s">≈ 2 МИН ПЕШКОМ</text>'
            f'{extra}</svg>')


def doc(slug, body, extra_schema=None, active=None):
    return head(slug, extra_schema) + f'<body class="pg-{slug or "home"}">' + header(active or slug) + f'<main id="main">{body}</main>' + footer() + '</body></html>'


def faq_schema(pairs):
    return [{"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in pairs]}]


def faq_list(pairs):
    return '<div class="faq">' + "".join(
        f'<details class="faq-i" data-reveal><summary><span class="faq-n">{i:02d}</span><span class="faq-q">{e(q)}</span><i aria-hidden="true"></i></summary>'
        f'<div class="faq-a"><p>{e(a)}</p></div></details>' for i, (q, a) in enumerate(pairs, 1)) + '</div>'


def corp_faq():
    """FAQ в корпоративной модели: вопросы /faq, согласованные с работой только с юрлицами."""
    items = P["faq.html"]["sections"][0]["items"]
    want = ["Кто может у вас заселиться?", "Какой минимальный срок и объём размещения?", "Что входит в стоимость проживания?",
            "Какие документы оформляются?", "Можно ли поселить всю бригаду в одну комнату?", "Во сколько можно заселиться?",
            "Далеко ли идти от МЦД?", "Как узнать точную цену?"]
    by = {i["title"]: " ".join(i["text"]) for i in items}
    return [(q, by[q]) for q in want if q in by]


# ── главная ──────────────────────────────────────────────────────────────────
def home():
    idx = P["index.html"]
    corp = P["dlya-yuridicheskih-lic.html"]
    rooms = P["rooms.html"]
    sec = {s["h2"]: s for s in idx["sections"]}
    adv = sec["Всё нужное для спокойного проживания"]
    equip = next(s for s in rooms["sections"] if s["h2"] == "Что входит в место")
    work = next(s for s in corp["sections"] if s["h2"] == "Как мы работаем с организациями")
    know = next(s for s in corp["sections"] if s["h2"] == "Что важно знать до заключения договора")
    steps = next(s for s in corp["sections"] if s["h2"] == "Как оформляется договор")
    orgs = sec["Размещаем сотрудников компаний"]

    hero = (f'<section class="hero" aria-labelledby="h1"><div class="hero-grid wrap">'
            f'<div class="hero-copy"><p class="hero-eyebrow mono" data-reveal><span class="tag-lime">Только юрлица</span> {e(F["model"]["text"])}</p>'
            f'<h1 class="hero-h1" id="h1" data-split><span class="l">Хостел</span><span class="l">в Долгопрудном</span><span class="l l-lime">у МЦД Новодачная</span></h1>'
            f'<p class="hero-lead" data-reveal>{e(corp["hero"]["lead"][0])}</p>'
            f'<div class="hero-cta" data-reveal><a class="btn btn-lime btn-l" href="#zayavka" data-to-form><span>Оставить заявку</span><i aria-hidden="true">→</i></a>'
            f'<a class="hero-tel" href="{TEL}"><small>{e(F["schedule"]["requests"])}</small>{PHONE}</a></div></div>'
            f'<figure class="hero-media" data-mask>{pic(12, "12-ти местный номер Like Home", "hero-pic", "(max-width: 900px) 100vw, 42vw", True)}'
            f'<figcaption class="mono"><span>12</span> мест · комната Like Home</figcaption>'
            f'<div class="hero-pin mono" aria-hidden="true"><i></i>{e(F["address"]["short"])}</div></figure></div>'
            f'<div class="wrap">{facts_rail()}</div></section>')

    # 02 — преимущества: крупные факты, а не карточки
    advantages = (f'<section class="sec sec-adv" aria-labelledby="adv-h"><div class="wrap">{stop("02", adv["eyebrow"] or "Почему Like Home")}'
                  f'<div class="adv-head"><h2 class="h2" id="adv-h" data-reveal>{e(adv["h2"])}</h2>'
                  f'<p class="lead" data-reveal>Рядом транспорт, чистые комнаты и всё необходимое на каждый день.</p></div>'
                  f'<ol class="adv-list">' + "".join(
                      f'<li class="adv-i adv-{k}" data-reveal><span class="adv-n mono">{k:02d}</span><h3>{e(it["title"])}</h3><p>{e(" ".join(it["text"]))}</p></li>'
                      for k, it in enumerate(adv["items"], 1)) + '</ol></div></section>')

    # 03 — комнаты: переключатель 8 / 10 / 12
    room_tabs = "".join(f'<button class="rm-tab{" is-on" if r["places"] == 8 else ""}" type="button" role="tab" aria-selected="{"true" if r["places"] == 8 else "false"}" '
                        f'aria-controls="rm-{r["places"]}" id="rt-{r["places"]}" data-room="{r["places"]}"><span>{r["places"]:02d}</span>мест</button>' for r in F["rooms"])
    room_panes = "".join(
        f'<div class="rm-pane{" is-on" if r["places"] == 8 else ""}" id="rm-{r["places"]}" role="tabpanel" aria-labelledby="rt-{r["places"]}" {"" if r["places"] == 8 else "hidden"}>'
        f'{pic(r["img"], r["title"] + " Like Home", "rm-pic", "(max-width: 900px) 100vw, 60vw")}'
        f'<div class="rm-cap"><span class="rm-big">{r["places"]}</span><span class="rm-title">{e(r["title"])}</span></div></div>' for r in F["rooms"])
    rooms_sec = (f'<section class="sec sec-rooms" aria-labelledby="rooms-h"><div class="wrap">{stop("03", "Номера", "on-dark")}'
                 f'<div class="rooms-grid"><div class="rooms-copy"><h2 class="h2" id="rooms-h" data-reveal>Комнаты на 8, 10 и 12 мест</h2>'
                 f'<p class="lead" data-reveal>{e(rooms["sections"][0]["intro"][0] if rooms["sections"][0]["intro"] else "")}</p>'
                 f'<div class="rm-tabs" role="tablist" aria-label="Тип комнаты">{room_tabs}</div>'
                 f'<h3 class="h4">Что входит в место</h3><ul class="equip">' + "".join(
                     f'<li><b>{e(it["title"])}</b><span>{e(" ".join(it["text"]))}</span></li>' for it in equip["items"]) +
                 f'</ul><a class="more" href="rooms">Смотреть номера и что входит в место →</a></div>'
                 f'<div class="rooms-stage" data-mask>{room_panes}</div></div></div></section>')

    # 04 — условия для компаний: табло
    terms = (f'<section class="sec sec-terms" aria-labelledby="terms-h"><div class="wrap">{stop("04", "Для организаций")}'
             f'<div class="terms-head"><h2 class="h2" id="terms-h" data-reveal>{e(orgs["h2"])}</h2>'
             f'<p class="lead" data-reveal>Работаем с юридическими лицами и ИП: договор, закрывающие документы, оплата по счёту. Бригаду можно разместить вместе — от одной комнаты.</p></div>'
             f'<div class="board" role="list">' + "".join(
                 f'<div class="board-row" role="listitem" data-reveal><span class="board-n mono">{k:02d}</span><h3>{e(it["title"])}</h3><p>{e(" ".join(it["text"]))}</p></div>'
                 for k, it in enumerate(work["items"] + know["items"], 1)) +
             f'</div><div class="terms-foot"><a class="btn btn-dark" href="dlya-yuridicheskih-lic"><span>Условия для юридических лиц</span><i aria-hidden="true">→</i></a>'
             f'<a class="more" href="prices">Цены и что входит в стоимость →</a></div></div></section>')

    # 05 — для кого (форматы размещения) — ссылки на SEO-страницы
    formats = (f'<section class="sec sec-formats" aria-labelledby="fmt-h"><div class="wrap">{stop("05", "Форматы размещения", "on-dark")}'
               f'<h2 class="h2 sr-only" id="fmt-h">Форматы размещения</h2><ul class="fmt">' + "".join(
                   f'<li data-reveal><a href="{it["link"]["href"].strip("/")}"><span class="fmt-t">{e(it["title"])}</span><span class="fmt-d">{e(" ".join(it["text"]))}</span><i aria-hidden="true">↗</i></a></li>'
                   for it in orgs["items"] if it.get("link")) + '</ul></div></section>')

    # 06 — местоположение
    loc = sec["Удобно добираться каждый день"]
    location = (f'<section class="sec sec-loc" aria-labelledby="loc-h"><div class="wrap">{stop("06", loc["eyebrow"] or "Локация", "on-dark")}'
                f'<div class="loc-grid"><div class="loc-copy"><h2 class="h2" id="loc-h" data-reveal>{e(loc["h2"])}</h2>'
                f'<p class="lead" data-reveal>Долгопрудный, Лихачёвский проезд, 5, стр. 11. От МЦД Новодачная — около 2 минут пешком, до метро Физтех — примерно 10 минут.</p>'
                f'<ul class="dirs mono" data-reveal>' + "".join(f'<li>{e(d)}</li>' for d in F["metro"]["directions"]) + '</ul>'
                f'<a class="more more-lime" href="how-to-get">Как добраться подробно →</a></div>'
                f'<div class="loc-vis"><div class="route-box" data-reveal>{route_svg()}</div>'
                f'<div class="map" data-map data-src="{e(F["map"]["src"])}"><div class="map-ph"><span class="mono">55.9223° N · 37.5259° E</span><b>Лихачёвский проезд, 5, стр. 11</b><button class="map-load" type="button">Показать карту</button></div>'
                f'<noscript><a href="{e(F["map"]["src"])}">Открыть карту</a></noscript></div></div></div></div></section>')

    # 07 — процесс
    process = (f'<section class="sec sec-steps" aria-labelledby="steps-h"><div class="wrap">{stop("07", steps["eyebrow"] or "Оформление")}'
               f'<h2 class="h2" id="steps-h" data-reveal>{e(steps["h2"])}</h2><ol class="steps" data-line>' + "".join(
                   f'<li data-reveal><span class="steps-dot" aria-hidden="true"></span><span class="steps-n mono">{k:02d}</span>'
                   f'<h3>{e(re.sub(r"^[0-9]+\. ", "", it["title"]))}</h3><p>{e(" ".join(it["text"]))}</p></li>' for k, it in enumerate(steps["items"], 1)) +
               '</ol></div></section>')

    # 08 — FAQ + отзывы
    pairs = corp_faq()[:6]
    revs = F["reviews"]["items"][:3]
    faq = (f'<section class="sec sec-faq" aria-labelledby="faq-h"><div class="wrap faq-grid"><div>{stop("08", "Вопросы")}'
           f'<h2 class="h2" id="faq-h" data-reveal>Частые вопросы</h2><a class="more" href="faq">Все вопросы и ответы →</a>'
           f'<div class="quotes"><p class="mono quotes-h">Отзывы гостей</p>' + "".join(
               f'<blockquote data-reveal><p>{e(r["text"])}</p><cite>{e(r["author"])}</cite></blockquote>' for r in revs) +
           f'<a class="more" href="otzyvy-o-nas">Все отзывы →</a></div></div>{faq_list(pairs)}</div></section>')

    body = hero + advantages + rooms_sec + terms + formats + location + process + faq + form_block(
        "Хотите разместить сотрудников?", "Оставьте заявку — уточним наличие мест и назовём стоимость под ваш срок.")
    return doc("", body, faq_schema(pairs))


# ── внутренние страницы ──────────────────────────────────────────────────────
def page_hero(p, num="01", aside=""):
    lead = "".join(f'<p class="ph-lead" data-reveal>{e(x)}</p>' for x in p["hero"]["lead"][:1])
    eyebrow = p["hero"]["eyebrow"] or ""
    return (f'<section class="ph" aria-labelledby="h1"><div class="wrap ph-grid"><div>'
            f'<nav class="crumbs mono" aria-label="Навигация"><a href="./">Главная</a><span>/</span><span>{e(p["h1"][:60])}</span></nav>'
            f'{stop(num, eyebrow or "Like Home", "on-dark")}<h1 class="ph-h1" id="h1" data-split>{e(p["h1"])}</h1>{lead}'
            f'<div class="ph-cta" data-reveal><a class="btn btn-lime" href="#zayavka" data-to-form><span>Оставить заявку</span><i aria-hidden="true">→</i></a>'
            f'<a class="ph-tel" href="{TEL}">{PHONE}</a></div></div>{aside}</div></section>')


def render_sections(sections, start=2, skip=()):
    out, n = [], start
    for s in sections:
        if s["h2"] in skip or s["eyebrow"] == "Заявка" or s["h2"].startswith("Рассчитаем") or s["h2"].startswith("Хотите"):
            continue
        if not s["items"] and not s["links"] and not s["faq"]:
            continue  # призыв «позвоните / оставьте заявку» — его заменяет общая форма внизу страницы
        intro = "".join(f'<p class="lead">{e(x)}</p>' for x in s["intro"])
        items = ""
        if s["items"]:
            items = '<div class="grid-items">' + "".join(
                f'<article class="gi" data-reveal><span class="gi-n mono">{k:02d}</span><h3>{e(re.sub(r"^[0-9]+\. ", "", it["title"]))}</h3>'
                + "".join(f'<p>{e(t)}</p>' for t in it["text"])
                + (f'<p class="gi-price mono">{e(it["price"])}</p>' if it.get("price") else "")
                + (f'<a class="more" href="{it["link"]["href"].strip("/")}">{e(it["link"]["text"])}</a>' if it.get("link") else "")
                + '</article>' for k, it in enumerate(s["items"], 1)) + '</div>'
        links = ""
        if s["links"]:
            links = '<ul class="fmt fmt-s">' + "".join(
                f'<li><a href="{l["href"].strip("/")}"><span class="fmt-t">{e(l["text"])}</span><i aria-hidden="true">↗</i></a></li>' for l in s["links"]) + '</ul>'
        tone = " sec-alt" if n % 2 else " sec-l"
        out.append(f'<section class="sec{tone}"><div class="wrap">{stop(f"{n:02d}", s["eyebrow"] or s["h2"])}'
                   f'<div class="sec-head"><h2 class="h2" data-reveal>{e(s["h2"])}</h2>{intro}</div>{items}{links}</div></section>')
        n += 1
    return "".join(out), n


def legal_block():
    L = F["legal"]
    return ('<dl class="legal" data-reveal>'
            f'<div><dt>Исполнитель</dt><dd>{e(L["name"])}</dd></div><div><dt>ИНН</dt><dd class="mono">{L["inn"]}</dd></div>'
            f'<div><dt>ОГРНИП</dt><dd class="mono">{L["ogrnip"]}</dd></div><div><dt>Адрес объекта</dt><dd>{e(F["address"]["full"])}</dd></div>'
            f'<div><dt>Телефон</dt><dd><a href="{TEL}">{PHONE}</a></dd></div>'
            f'<div><dt>Документы</dt><dd><a href="oferta">Договор публичной оферты</a> · <a href="politika-personalnyh-dannyh">Политика обработки персональных данных</a></dd></div></dl>')


def generic(slug, aside=""):
    p = page_by(slug)
    skip = ("С кем вы заключаете договор",)
    secs, n = render_sections(p["sections"], skip=skip)
    extra = ""
    if slug == "dlya-yuridicheskih-lic":
        extra = (f'<section class="sec sec-alt"><div class="wrap">{stop(f"{n:02d}", "Исполнитель")}<div class="sec-head">'
                 f'<h2 class="h2" data-reveal>С кем вы заключаете договор</h2><p class="lead">Работаем официально. Реквизиты исполнителя открыты — их можно проверить до подписания документов.</p></div>{legal_block()}</div></section>')
    return doc(slug, page_hero(p, aside=aside) + secs + extra + form_block())


def rooms_page():
    p = page_by("rooms")
    gallery = ('<section class="sec sec-rooms"><div class="wrap">' + stop("02", "Комнаты", "on-dark") +
               f'<div class="sec-head"><h2 class="h2" data-reveal>{e(p["sections"][0]["h2"])}</h2><p class="lead">{e(p["sections"][0]["intro"][0])}</p></div>'
               '<div class="rooms-row">' + "".join(
                   f'<figure class="room-card" data-mask>{pic(r["img"], r["title"] + " Like Home", "", "(max-width: 900px) 100vw, 33vw")}'
                   f'<figcaption><span class="rm-big">{r["places"]}</span><span>{e(r["title"])}</span></figcaption></figure>' for r in F["rooms"]) + '</div></div></section>')
    secs, _ = render_sections(p["sections"][1:], start=3)
    return doc("rooms", page_hero(p) + gallery + secs + form_block())


def prices_page():
    p = page_by("prices")
    fmt = p["sections"][0]
    board = ('<section class="sec"><div class="wrap">' + stop("02", fmt["eyebrow"] or "Форматы") +
             f'<div class="sec-head"><h2 class="h2" data-reveal>{e(fmt["h2"])}</h2></div><div class="price-board">' + "".join(
                 f'<article class="pb-row" data-reveal><h3>{e(it["title"])}</h3><p class="pb-price">{e(it["price"] or "")}</p>'
                 f'<div class="pb-text">' + "".join(f'<p>{e(t)}</p>' for t in it["text"]) + '</div></article>' for it in fmt["items"]) +
             '</div></div></section>')
    secs, _ = render_sections(p["sections"][1:], start=3)
    aside = f'<div class="ph-aside">{facts_rail()}</div>'
    return doc("prices", page_hero(p, aside=aside) + board + secs + form_block())


def contacts_page():
    p = page_by("kontakty")
    contacts = ('<section class="sec"><div class="wrap">' + stop("02", "Контакты") + '<div class="loc-grid loc-light">'
                f'<div><dl class="legal" data-reveal><div><dt>Телефон</dt><dd><a class="big-tel" href="{TEL}">{PHONE}</a><br>Заявки принимаем круглосуточно, 24/7</dd></div>'
                f'<div><dt>Адрес</dt><dd>{e(F["address"]["full"])}</dd></div>'
                f'<div><dt>Условия</dt><dd>Работаем только с юридическими лицами<br>Заселение от одной комнаты, от 30 дней<br>Заселение с 14:00 до 22:00<br>Заявки принимаем круглосуточно</dd></div></dl>'
                f'<h2 class="h4">Реквизиты</h2>{legal_block()}</div>'
                f'<div class="map map-tall" data-map data-src="{e(F["map"]["src"])}"><div class="map-ph"><span class="mono">55.9223° N · 37.5259° E</span><b>Лихачёвский проезд, 5, стр. 11</b><button class="map-load" type="button">Показать карту</button></div></div></div></div></section>')
    secs, _ = render_sections(p["sections"][1:], start=3)
    return doc("kontakty", page_hero(p) + contacts + secs + form_block())


def how_page():
    p = page_by("how-to-get")
    vis = (f'<section class="sec sec-loc"><div class="wrap">{stop("02", "Схема", "on-dark")}<div class="loc-grid"><div class="loc-copy">'
           f'<h2 class="h2" data-reveal>Лихачёвский проезд, 5, стр. 11</h2><p class="lead">От МЦД Новодачная — около 2 минут пешком, до метро Физтех — примерно 10 минут.</p>'
           f'<ul class="dirs mono">' + "".join(f'<li>{e(d)}</li>' for d in F["metro"]["directions"]) + '</ul></div>'
           f'<div class="loc-vis"><div class="route-box" data-reveal>{route_svg()}</div>'
           f'<div class="map" data-map data-src="{e(F["map"]["src"])}"><div class="map-ph"><span class="mono">55.9223° N · 37.5259° E</span><b>Лихачёвский проезд, 5, стр. 11</b><button class="map-load" type="button">Показать карту</button></div></div></div></div></div></section>')
    secs, _ = render_sections(p["sections"], start=3)
    return doc("how-to-get", page_hero(p) + vis + secs + form_block())


def faq_page():
    p = page_by("faq")
    pairs = [(it["title"], " ".join(it["text"])) for it in p["sections"][0]["items"]]
    body = page_hero(p) + (f'<section class="sec"><div class="wrap">{stop("02", "Вопросы")}<div class="sec-head">'
                           f'<h2 class="h2" data-reveal>{e(p["sections"][0]["h2"])}</h2>'
                           + "".join(f'<p class="lead">{e(x)}</p>' for x in p["sections"][0]["intro"]) + f'</div>{faq_list(pairs)}</div></section>')
    return doc("faq", body + form_block(), faq_schema(pairs))


def reviews_page():
    p = page_by("otzyvy-o-nas")
    body = page_hero(p) + (f'<section class="sec"><div class="wrap">{stop("02", "Отзывы клиентов")}<div class="quotes quotes-page">' + "".join(
        f'<blockquote data-reveal><span class="mono">{k:02d}</span><p>{e(r["text"])}</p><cite>{e(r["author"])}</cite></blockquote>'
        for k, r in enumerate(F["reviews"]["items"], 1)) + '</div></div></section>')
    return doc("otzyvy-o-nas", body + form_block())


def oferta_page():
    p = page_by("oferta")
    doc_link = (f'<section class="sec"><div class="wrap">{stop("02", "Документы")}<div class="sec-head">'
                f'<h2 class="h2" data-reveal>Договор публичной оферты на предоставление мест для временного проживания (аренда койко-мест)</h2></div>'
                f'<a class="btn btn-dark" href="assets/docs/dogovor_dp.pdf" download><span>Скачать договор оферты (PDF)</span><i aria-hidden="true">↓</i></a></div></section>')
    secs, _ = render_sections(p["sections"], start=3)
    return doc("oferta", page_hero(p) + doc_link + secs + form_block())


def policy_page():
    p = page_by("politika-personalnyh-dannyh")
    txt = p.get("raw_text", [])
    body_html = []
    for t in txt:
        if re.match(r"^\d+(\.\d+)*\.?\s", t) and len(t) < 120 and not re.match(r"^\d+\.\d+\.", t):
            body_html.append(f'<h2 class="h4">{e(t)}</h2>')
        else:
            body_html.append(f'<p>{e(t)}</p>')
    body = page_hero(p) + f'<section class="sec"><div class="wrap"><div class="prose">{"".join(body_html)}</div></div></section>'
    return doc("politika-personalnyh-dannyh", body)


def not_found():
    body = ('<section class="ph ph-404"><div class="wrap"><p class="mono">404</p><h1 class="ph-h1">Такой страницы нет</h1>'
            '<p class="ph-lead">Возможно, адрес изменился. Перейдите на главную или позвоните нам.</p>'
            f'<div class="ph-cta"><a class="btn btn-lime" href="./"><span>На главную</span></a><a class="ph-tel" href="{TEL}">{PHONE}</a></div></div></section>')
    return head("", None).replace("<meta name=\"robots\" content=\"index, follow\">", '<meta name="robots" content="noindex, follow">') + \
        '<body class="pg-404">' + header("") + f'<main id="main">{body}</main>' + footer() + '</body></html>'


def main():
    global VER
    import hashlib
    VER = hashlib.md5((ROOT / "assets/css/site.css").read_bytes() + (ROOT / "assets/js/site.js").read_bytes()).hexdigest()[:8]
    OUT.mkdir(exist_ok=True)
    pages = {"index.html": home(), "rooms.html": rooms_page(), "prices.html": prices_page(), "kontakty.html": contacts_page(),
             "how-to-get.html": how_page(), "faq.html": faq_page(), "otzyvy-o-nas.html": reviews_page(), "oferta.html": oferta_page(),
             "politika-personalnyh-dannyh.html": policy_page(), "dlya-yuridicheskih-lic.html": generic("dlya-yuridicheskih-lic"), "404.html": not_found()}
    for s in SEO_PAGES:
        pages[f"{s}.html"] = generic(s)
    for name, html_ in pages.items():
        (OUT / name).write_text(html_, encoding="utf-8")
    # статика
    import shutil
    if (OUT / "assets").exists():
        shutil.rmtree(OUT / "assets")
    shutil.copytree(ROOT / "assets", OUT / "assets")
    (OUT / "robots.txt").write_text((ROOT / "source/robots.txt").read_text() if PROD else "User-agent: *\nDisallow: /\n")
    (OUT / "sitemap.xml").write_text((ROOT / "source/sitemap.xml").read_text())
    (OUT / ".nojekyll").write_text("")
    print(f"{len(pages)} страниц → {OUT} ({'PROD' if PROD else 'preview'})")


VER = "dev"
if __name__ == "__main__":
    main()
