#!/usr/bin/env python3
"""Build the two guides that live natively in this repository, from data/guides.json.

  start-safely/            Start and run a business safely (privacy and safety for survivors of abuse)
  starting-out-or-again/   Starting out, or starting again (young people, women, adults coming back)

Each page is self-contained: no third-party request of any kind, a strict content security policy, no storage, no
forms. The safety page has an Exit control (button and Shift pressed three times) that replaces the page with a weather
page. Words shared across the 360º portals come from data/shared-glossary.json, a copy of the launchpad's file.

Run:  python3 tools/guides.py           write both pages
      python3 tools/guides.py --check   exit 1 if a page is out of step with the data (C9)
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import publish

EXIT_TO = 'https://www.bbc.co.uk/weather'
e = html.escape

ICONS = {  # simple line icons, decorative (aria-hidden)
    'help-now': '<path d="M12 3l9 16H3z"/><path d="M12 10v4M12 17v.01"/>',
    'devices': '<rect x="7" y="2" width="10" height="20" rx="2"/><path d="M11 18h2"/>',
    'structure': '<path d="M4 20V8l8-5 8 5v12"/><path d="M9 20v-6h6v6"/>',
    'registers': '<path d="M5 3h10l4 4v14H5z"/><path d="M9 11h6M9 15h6"/>',
    'training': '<path d="M2 9l10-5 10 5-10 5z"/><path d="M6 11v5c3 2 9 2 12 0v-5"/>',
    'money': '<rect x="3" y="6" width="18" height="12" rx="2"/><circle cx="12" cy="12" r="2.5"/>',
    'young': '<circle cx="12" cy="7" r="3"/><path d="M6 21v-2a6 6 0 0112 0v2"/>',
    'women': '<circle cx="12" cy="8" r="4"/><path d="M12 12v9M9 18h6"/>',
    'learn-first': '<path d="M4 5a2 2 0 012-2h13v16H6a2 2 0 00-2 2z"/><path d="M4 21V5"/>',
    'coming-back': '<path d="M4 12a8 8 0 1 0 3-6.2"/><path d="M4 4v5h5"/>',
    'children': '<circle cx="8" cy="7" r="3"/><circle cx="17" cy="10" r="2.2"/><path d="M3 20v-1a5 5 0 0110 0v1M13.5 20v-.5a3.5 3.5 0 017 0v.5"/>',
}

CSS = '''
:root{--bg:#fff;--fg:#0b0c0c;--muted:#4b5563;--line:#d0d5dc;--brand:#5c5a11;--brand-soft:#f6f5dc;--link:#1d4ed8;--warn:#9b1c1c;--warn-soft:#fdecec;--focus:#ffdd00}
@media (prefers-color-scheme:dark){:root{--bg:#0f1720;--fg:#e8eef3;--muted:#b6c2cf;--line:#334155;--brand:#e1dc76;--brand-soft:#232a14;--link:#9cc0ff;--warn:#ffb4b4;--warn-soft:#3a1717}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);font:1.0625rem/1.6 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
a{color:var(--link);text-underline-offset:.15em;overflow-wrap:anywhere}a:hover{text-decoration-thickness:3px}
:focus-visible{outline:3px solid var(--focus);outline-offset:2px;box-shadow:0 0 0 6px #0b0c0c}
.skip{position:absolute;left:-999px;top:0;background:var(--focus);color:#0b0c0c;padding:.6rem 1rem;z-index:10}.skip:focus{left:.5rem}
.top{border-bottom:4px solid var(--brand);padding:.75rem 1rem}.top p{margin:0;max-width:72rem;margin-inline:auto;font-size:.95rem}
.wrap{max-width:72rem;margin:0 auto;padding:1.25rem 1rem 2rem}main.wrap>h1,main.wrap>.strap,main.wrap>.help{max-width:46rem}
.layout{display:grid;gap:2rem;grid-template-columns:minmax(0,1fr);margin-top:1rem}
@media (min-width:62rem){.layout{grid-template-columns:16rem minmax(0,1fr)}.toc{position:sticky;top:1rem;align-self:start}}
h1{font-size:clamp(1.9rem,4vw,2.6rem);line-height:1.15;margin:.2rem 0 .4rem}.strap{font-size:1.2rem;color:var(--muted);margin:0 0 1rem}
.lede{font-size:1.15rem;max-width:44rem}
.who{background:var(--brand-soft);border-left:6px solid var(--brand);padding:.9rem 1.1rem;border-radius:0 10px 10px 0;max-width:44rem}
.who h2{font-size:1.05rem;margin:0 0 .3rem}.who ul{margin:0;padding-left:1.2rem}
.toc h2{font-size:1rem;margin:0 0 .5rem}.toc ol{margin:0;padding-left:1.3rem}.toc li{margin:.35rem 0}
section.g{border-top:1px solid var(--line);padding-top:1.5rem;margin-top:1.75rem;max-width:46rem}
section.g h2{display:flex;gap:.6rem;align-items:center;font-size:1.5rem;line-height:1.25;margin:0 0 .6rem}
section.g h2 svg{flex:none;width:1.6rem;height:1.6rem;stroke:var(--brand);fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.short{font-weight:600;margin:0 0 1rem}
.item h3{font-size:1.1rem;margin:1.1rem 0 .25rem}.item p{margin:0}
.src{margin-top:1.1rem;font-size:.92rem;color:var(--muted)}.src summary{cursor:pointer;color:var(--fg);font-weight:600}.src ul{padding-left:1.2rem}
.see{margin:.9rem 0 0;font-weight:600}.note{font-size:.92rem;color:var(--muted)}
.help{background:var(--warn-soft);border:2px solid var(--warn);border-radius:10px;padding:.9rem 1.1rem;margin:0 0 1.25rem;max-width:46rem}
.help p{margin:0}.help strong{color:var(--warn)}
.exit{position:sticky;top:0;z-index:5;display:flex;justify-content:flex-end;gap:.75rem;align-items:center;padding:.5rem 1rem;background:var(--bg);border-bottom:1px solid var(--line)}
.exit a{display:inline-block;background:#b10e1e;color:#fff;font-weight:700;padding:.6rem 1.1rem;border-radius:8px;text-decoration:none;border:2px solid #b10e1e}
.exit a:hover{background:#8a0b17}.exit small{color:var(--muted)}
.words dt{font-weight:700;margin-top:.6rem}.words dd{margin:0}
.related{border-top:1px solid var(--line);margin-top:2rem;padding-top:1rem}.related ul{padding-left:1.2rem}
@media (prefers-reduced-motion:no-preference){html{scroll-behavior:smooth}}
@media print{.exit,.toc,.skip{display:none}a::after{content:" (" attr(href) ")";font-size:.85em}}
'''

EXIT_JS = '''
(function(){
  var to = __TO__;
  function leave(ev){ if (ev) ev.preventDefault(); location.replace(to); }
  var a = document.getElementById('exit'); if (a) a.addEventListener('click', leave);
  var n = 0, t = null;
  document.addEventListener('keydown', function(ev){
    if (ev.key !== 'Shift') return;
    n += 1; clearTimeout(t); t = setTimeout(function(){ n = 0; }, 1000);
    if (n >= 3) leave();
  });
})();
'''.replace('__TO__', json.dumps(EXIT_TO))


def data(root=ROOT):
    return json.loads((Path(root) / 'data' / 'guides.json').read_text(encoding='utf-8'))


def glossary(root=ROOT):
    return json.loads((Path(root) / 'data' / 'shared-glossary.json').read_text(encoding='utf-8'))


def icon(sid):
    return f'<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">{ICONS.get(sid, ICONS["registers"])}</svg>'


def page_text(g):
    return ' '.join([g['lede'], *[s['short'] + ' ' + ' '.join(i['p'] for i in s['items']) for s in g['sections']]])


def words(g, gl):
    text = page_text(g)
    used = [t for t in gl['terms'] if re.search(r'\b' + re.escape(t['term']) + r'\b', text, re.IGNORECASE)]
    if not used:
        return ''
    dl = ''.join(f'<dt>{e(t["term"])}</dt><dd>{e(t["definition"])}</dd>' for t in used)
    return (f'<section class="g words" id="words" aria-labelledby="h-words"><h2 id="h-words">Words used on this page</h2>'
            f'<p class="note">The same definitions are used across the 360º portals '
            f'(<a href="https://cyberdudeuk.github.io/data/shared-glossary.json" rel="noreferrer">shared glossary, version {e(gl["version"])}</a>).</p>'
            f'<dl>{dl}</dl></section>')


# Pages named in the text become links the first time they appear in a paragraph (never to the page itself).
NAMED = {'Start and run a business safely': '../start-safely/', 'Starting out, or starting again': '../starting-out-or-again/',
         'Your circumstances': '../your-circumstances/', 'Skills and communities': '../skills-and-communities/'}


def linked(text, here):
    out = e(text)
    for name, url in NAMED.items():
        if url.strip('./') != here and name in text:
            out = out.replace(e(name), f'<a href="{url}">{e(name)}</a>', 1)
    return out


def section(s, checked, here=''):
    items = ''.join(f'<div class="item"><h3>{e(i["h"])}</h3><p>{linked(i["p"], here)}</p></div>' for i in s['items'])
    srcs = ''.join(f'<li><a href="{e(x["u"])}" rel="noreferrer">{e(x["t"])}</a></li>' for x in s['sources'])
    see = f'<p class="see"><a href="{e(s["see"]["u"])}">{e(s["see"]["t"])}</a></p>' if s.get('see') else ''
    note = f'<p class="note">{e(s["note"])}</p>' if s.get('note') else ''
    return (f'<section class="g" id="{e(s["id"])}" aria-labelledby="h-{e(s["id"])}">'
            f'<h2 id="h-{e(s["id"])}">{icon(s["id"])}<span>{e(s["title"])}</span></h2>'
            f'<p class="short">{e(s["short"])}</p>{items}{note}{see}'
            f'<details class="src"><summary>Where this comes from ({len(s["sources"])} sources, checked {e(checked)})</summary><ul>{srcs}</ul></details>'
            f'</section>')


def render(g, d, gl):
    others = [o for o in d['guides'] if o['slug'] != g['slug']]
    csp = ("default-src 'none'; style-src 'unsafe-inline'; img-src data:; "
           + ("script-src 'unsafe-inline'; " if g['safety'] else '') + "base-uri 'none'; form-action 'none'")
    exitbar = (f'<aside class="exit" aria-label="Leave this page quickly"><small>Pressing Shift three times also leaves.</small>'
               f'<a id="exit" href="{EXIT_TO}" rel="noreferrer">Exit this page</a></aside>') if g['safety'] else ''
    help_ = ('<div class="help" role="note"><p><strong>In danger now? Call 999.</strong> If you cannot speak, see '
             '<a href="#help-now">what to do on a silent 999 call</a>. Free helplines for each nation are listed below.</p></div>'
             ) if g['safety'] else ''
    toc = ''.join(f'<li><a href="#{e(s["id"])}">{e(s["title"])}</a></li>' for s in g['sections'])
    who = ''.join(f'<li>{e(w)}</li>' for w in g['who'])
    body = ''.join(section(s, d['checked'], g['slug']) for s in g['sections'])
    related = ''.join(f'<li><a href="../{e(o["slug"])}/">{e(o["title"])}</a>: {e(o["strap"].lower())}</li>' for o in others)
    script = f'<script>{EXIT_JS}</script>' if g['safety'] else ''
    return f'''<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="{csp}">
<meta name="referrer" content="no-referrer">
<meta name="description" content="{e(g['strap'])}. Part of Starting a business in the UK.">
<title>{e(g['title'])}: Starting a business in the UK</title>
<style>{CSS}</style>
</head>
<body>
<a class="skip" href="#main">Skip to main content</a>
{exitbar}
<header class="top"><p><a href="../">Starting a business in the UK</a> · Guide</p></header>
<main id="main" class="wrap">
<h1>{e(g['title'])}</h1>
<p class="strap">{e(g['strap'])}</p>
{help_}
<div class="layout">
<nav class="toc" aria-labelledby="h-toc"><h2 id="h-toc">On this page</h2><ol>{toc}<li><a href="#words">Words used on this page</a></li></ol></nav>
<div class="content">
<p class="lede">{linked(g['lede'], g['slug'])}</p>
<div class="who"><h2>Who this is for</h2><ul>{who}</ul></div>
{body}
{words(g, gl)}
<nav class="related" aria-labelledby="h-related"><h2 id="h-related">Related</h2><ul>{related}<li><a href="../your-circumstances/">Your circumstances</a>: what changes for 45 kinds of founder</li><li><a href="../">All of Starting a business in the UK</a></li></ul></nav>
</div>
</div>
</main>
{publish.colophon(g['slug'])}
{script}
</body>
</html>
'''


def build(root=ROOT):
    d, gl = data(root), glossary(root)
    return {Path(root) / g['slug'] / 'index.html': render(g, d, gl) for g in d['guides']}


if __name__ == '__main__':
    out = build()
    if '--check' in sys.argv:
        stale = [str(p.relative_to(ROOT)) for p, t in out.items() if not p.exists() or p.read_text(encoding='utf-8') != t]
        print('C9 out of step with data/guides.json: ' + ', '.join(stale) if stale else 'guides up to date')
        sys.exit(1 if stale else 0)
    for p, t in out.items():
        p.parent.mkdir(exist_ok=True)
        p.write_text(t, encoding='utf-8')
    print(f'wrote {len(out)} guides')
