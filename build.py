#!/usr/bin/env python3
"""Build the static sources site (GitHub Pages) from data/*.json into ./docs.
Only claims with verified=true are published; unverified ones are listed in the build warnings.
  python3 build.py            # writes site/ and descriptions/*.txt
"""
import html, json, shutil, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs"
site = json.loads((ROOT / "data/site.json").read_text(encoding="utf-8"))
eps = sorted((json.loads(p.read_text(encoding="utf-8")) for p in (ROOT / "data").glob("ep*.json")), key=lambda e: e["number"])
e_ = html.escape
KIND = {"lehre": "Lehre des Autors", "deutung": "Unsere Deutung", "szene": "Erfundene Szene"}

CSS = """:root{--bg:#fbfaf7;--fg:#1c2230;--mut:#5d6677;--acc:#9a7424;--line:#e3ddd0;--card:#fff}
@media(prefers-color-scheme:dark){:root{--bg:#0e1626;--fg:#e8e6df;--mut:#9aa3b5;--acc:#d4af5f;--line:#27324a;--card:#141e33}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:17px/1.65 Georgia,'Times New Roman',serif}
main{max-width:760px;margin:0 auto;padding:32px 16px 64px}h1{font-size:1.9rem;line-height:1.25;margin:.2em 0}h2{font-size:1.2rem;margin:2em 0 .6em;color:var(--acc)}
a{color:var(--acc)}.mut{color:var(--mut);font-size:.92rem}.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:10px 0}
.tag{display:inline-block;font:600 .72rem/1 system-ui,sans-serif;letter-spacing:.04em;text-transform:uppercase;border:1px solid var(--line);border-radius:99px;padding:4px 9px;color:var(--mut);margin-bottom:6px}
.tag.lehre{color:var(--acc);border-color:var(--acc)}ul{padding-left:1.2em}nav a{font-size:.95rem}footer{margin-top:3em;border-top:1px solid var(--line);padding-top:1em}"""

def page(title, body, depth=0):
    root = "../" * depth
    return f"""<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e_(title)}</title><meta name="robots" content="index,follow"><link rel="stylesheet" href="{root}style.css"></head><body><main>
<nav><a href="{root}index.html">{e_(site['channel_name'])}: Quellen</a></nav>{body}
<footer class="mut"><p>{e_(site['disclaimer'])}</p><p>Kontakt für Korrekturen: {e_(site['contact'])}</p></footer></main></body></html>"""

def ep_url(ep): return f"{site['base_url']}/folge/{ep['slug']}/"

if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir(); (OUT / "style.css").write_text(CSS, encoding="utf-8"); (OUT / ".nojekyll").write_text("")
(ROOT / "descriptions").mkdir(exist_ok=True)
warn = []
lst = "".join(f'<div class="card"><a href="folge/{e_(ep["slug"])}/index.html"><b>Folge {ep["number"]}: {e_(ep["title"])}</b></a><div class="mut">{e_(ep["summary"])}</div></div>' for ep in eps)
body = f"""<h1>{e_(site['channel_name'])}: Quellen und Belege</h1><p>{e_(site['intro'])}</p>
<p><a href="{e_(site['channel_url'])}">Zum Kanal auf YouTube</a></p><h2>So arbeiten wir</h2><ul>{''.join(f'<li>{e_(m)}</li>' for m in site['method'])}</ul>
<h2>Folgen</h2>{lst}"""
(OUT / "index.html").write_text(page(f"Quellen | {site['channel_name']}", body), encoding="utf-8")
for ep in eps:
    d = OUT / "folge" / ep["slug"]; d.mkdir(parents=True)
    src = {s["id"]: s for s in ep["sources"]}
    ss = "".join(f'<li><b>{e_(s["author"])}</b>, {e_(s["work"])}. {e_(s["edition"])}. <a href="{e_(s["url"])}">Link</a> ({e_(s["status"])})</li>' for s in ep["sources"])
    cl = ""
    for c in ep["claims"]:
        if c["kind"] == "lehre" and not c.get("verified"):
            warn.append(f'ep{ep["number"]}: not published (unverified): {c["text"][:70]}'); continue
        ref = ""
        if c["kind"] == "lehre":
            s = src[c["source"]]; ref = f'<div class="mut">Beleg: {e_(s["author"])}, {e_(s["work"])}, {e_(c["locator"])} (<a href="{e_(s["url"])}">{c["source"]}</a>)</div>'
        cl += f'<div class="card"><span class="tag {c["kind"]}">{KIND[c["kind"]]}</span><div>{e_(c["text"])}</div>{ref}</div>'
    yt = f'<p><a href="{e_(ep["youtube_url"])}">Folge ansehen</a></p>' if ep.get("youtube_url") else ""
    body = f"""<p class="mut">Folge {ep['number']} · Stand {e_(ep['updated'])}</p><h1>{e_(ep['title'])}</h1><p>{e_(ep['summary'])}</p>{yt}
<h2>Quellen</h2><ul>{ss}</ul><h2>Aussagen und Belege</h2>{cl}<h2>Hinweis</h2><p>{e_(ep['caveat'])}</p>"""
    (d / "index.html").write_text(page(f"Folge {ep['number']}: {ep['title']} | Quellen", body, 2), encoding="utf-8")
    (ROOT / "descriptions" / f"ep{ep['number']:02d}.txt").write_text(
        f"Quellen und Belege zu dieser Folge: {ep_url(ep)}\nAlle Folgen: {site['base_url']}/\n", encoding="utf-8")
print(f"built {len(eps)} episode page(s) into {OUT}")
for w in warn: print("WARN", w)
