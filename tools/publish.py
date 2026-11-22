#!/usr/bin/env python3
"""Publish the Starting a business in the UK pages from their Claude artifact exports.

The family was built as 19 linked Claude artifacts. This turns one export of each (saved as <artifact id>.html in a
folder) into the GitHub Pages site: the hub at the root, every other page in its own folder, links between pages made
relative, the one link to another published project pointed at its site, retired names corrected, and the standard
colophon added to every page.

Run:  python3 tools/publish.py /path/to/exports
Then: python3 tools/check.py
"""
import html
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = 'https://cyberdudeuk.github.io/start-a-business-uk/'
CONTACT = 'https://github.com/cyberdudeuk/start-a-business-uk/issues/new?template=contact.yml'
HUB = '58dStrh7nS26SuvD5oighj'
# Every page in the family: artifact id -> folder. The order is the hub's own reading order.
PAGES = {
    'LLNBnnGC25rGHLh7gAsqBM': 'your-plan',
    'VtTnZmHX7RQ8QtkD2qS2Rc': 'before-the-register',
    'HNw4kAKtkkAC4Dki8MF2WZ': 'every-step',
    'PUyeWNZAePqiTzo4hTuaFt': 'whatever-you-are-setting-up',
    '2Aa11zYNCdP5KkwSJUPe6w': 'what-binds-this-business',
    '62cTiUZiUWC5hKW8vubCSn': 'rules-trade-and-bodies',
    '69RUHRCB7eoEDtpQmBQcCF': 'your-circumstances',
    '4RpcuNY4q9fHCBfQ55e5tu': 'every-way-in',
    'HfcZAKPTWNvQWgBqNZi2Ac': 'whole-life-of-a-business',
    'LsvbCitXmmUNRkoAm8wUXN': 'skills-and-communities',
    'CHa4car5CcYiRmVSk3nzjx': 'four-nations',
    'NCw5VZ6nnXwNL5rATDyRzS': 'the-uk-compared',
    '3REo2dfZ4JngmGS71aHfXr': 'twenty-years-of-joining-up',
    '7M6omgVJjcD3euCwrdvPiV': 'standards',
    'PCZ6bFsGLqmAGqoyy3TL9d': 'service-blueprints',
    'JyuYMMh31QL4hCqSwiBuzf': 'knowledge-layer',
    'EPbYgJxvewzppkfMyWDWxe': 'verification-register',
    '5umUj4ekvdvz9rWvZMhzkn': 'how-this-was-built',
}
# Pages outside the family that are published elsewhere.
ELSEWHERE = {'VtxD1e8ZSzBR4NWP2RTB7y': 'https://cyberdudeuk.github.io/black-mixed-heritage/'}
# Names that must never appear (standing rule, 15 Nov 2026): the directorate was restructured and renamed.
RENAMES = [(re.compile(r'Office of the Chief Data Officer \(OCDO\)'), 'Government Data Directorate'),
           (re.compile(r'Office of the Chief Data Officer'), 'Government Data Directorate'),
           (re.compile(r'\bOCDO\b'), 'Government Data Directorate')]
LINK = re.compile(r'https://claude\.ai/artifact/([A-Za-z0-9]{20,24})')
MARK = '<!-- colophon: added by tools/publish.py -->'
RECHECK = ROOT / 'data' / 'recheck-2026-11-22.json'  # the latest recheck: moved sources, corrected facts, gone sources
STAMP = ('Last updated 17 September 2026.', 'Last updated 17 September 2026; sources and time-sensitive facts rechecked 22 November 2026 (see the recheck page).')


def recheck():
    return json.loads(RECHECK.read_text(encoding='utf-8'))


TRACKING = re.compile(r'^(utm_|gad_|gclid|gbraid|wbraid|fbclid|msclkid|mc_cid|mc_eid|_ga|_gl)', re.IGNORECASE)


def untracked(url):
    """The address without advertising or analytics tracking parameters (C8)."""
    from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
    p = urlsplit(url)
    q = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True) if not TRACKING.match(k)]
    return urlunsplit((p.scheme, p.netloc, p.path, urlencode(q), p.fragment))


def url_pattern(url):
    """The address as a whole token: not a prefix of a longer address."""
    return re.compile(re.escape(url) + r'(?=["\'\s<>\\),]|$)')


def apply_recheck(text, rc):
    for old, move in sorted(rc['url_updates'].items(), key=lambda kv: -len(kv[0])):
        to = untracked(move['to'])
        text = url_pattern(old).sub(lambda _m, to=to: to, text)
    for c in rc['corrections']:
        text = text.replace(c['old'], c['new'])
    return text.replace(*STAMP)


def out_path(aid):
    return ROOT / 'index.html' if aid == HUB else ROOT / PAGES[aid] / 'index.html'


def href(target, here):
    """The relative address of one family page from another."""
    up = '' if here == HUB else '../'
    return up if target == HUB and up else ('./' if target == HUB else f'{up}{PAGES[target]}/')


def rewrite(text, here):
    def sub(m):
        aid = m.group(1)
        if aid == HUB or aid in PAGES:
            return href(aid, here)
        if aid in ELSEWHERE:
            return ELSEWHERE[aid]
        raise SystemExit(f'unknown artifact link {aid} in {here}: add it to PAGES or ELSEWHERE')
    text = LINK.sub(sub, text)
    for rx, new in RENAMES:
        text = rx.sub(new, text)
    return text


def qr_svg(url):
    import segno
    buf = io.BytesIO()
    q = segno.make(url, error='m')
    q.save(buf, kind='svg', scale=4, border=1, xmldecl=False, svgns=True, dark='#0b0c0c', light='#ffffff')
    w, h = q.symbol_size(scale=4, border=1)
    return buf.getvalue().decode().replace(f'width="{w}" height="{h}"',
                                           f'width="88" height="88" viewBox="0 0 {w} {h}" role="img" aria-label="QR code for {html.escape(url)}"', 1)


def barcode_svg(text):
    import barcode
    from barcode.writer import SVGWriter
    buf = io.BytesIO()
    barcode.get('code128', text, writer=SVGWriter()).write(buf, options={'write_text': False, 'module_height': 12, 'quiet_zone': 2})
    s = buf.getvalue().decode()
    s = s[s.find('<svg'):]
    m = re.search(r'width="([\d.]+)mm" height="([\d.]+)mm"', s)
    return s.replace(m.group(0), f'width="168" height="48" viewBox="0 0 {m.group(1)} {m.group(2)}" preserveAspectRatio="none" role="img" aria-label="Barcode {html.escape(text)}"', 1)


def colophon(aid):
    slug = '' if aid == HUB else ('recheck' if aid == 'recheck' else PAGES[aid])
    url = f'{SITE}{slug}/' if slug else SITE
    code = 'SAB-UK-' + (slug.upper() or 'HOME')[:24]
    return f'''{MARK}
<aside class="pgw-colophon" aria-label="About this publication" style="max-width:1120px;margin:40px auto 24px;padding:18px 22px;border:1px solid currentColor;border-radius:12px;font:14px/1.5 system-ui,sans-serif;display:flex;flex-wrap:wrap;gap:18px;align-items:center;opacity:.92">
<div style="flex:1 1 340px;min-width:0">
<p style="margin:0 0 6px"><strong>Not an official government service.</strong> An independent, evidence-led guide by Emanuel Silva, part of
<a href="https://cyberdudeuk.github.io/">Public Good Works</a>. Every claim carries its source; check GOV.UK, nidirect, mygov.scot or gov.wales before you act.</p>
<p style="margin:0 0 6px">Drafted and checked with AI assistance (Claude); the author reviewed and is responsible for it. Some features, such as the page assistant, work only inside Claude and are hidden here.</p>
<p style="margin:0 0 6px">Sources and time-sensitive facts rechecked on 22 November 2026: <a href="{'' if aid == HUB else '../'}recheck/">what was confirmed, corrected and found gone</a>.</p>
<p style="margin:0">Questions, corrections or ideas: use the <a href="{CONTACT}">contact form</a> (no email address is published).
Code MIT; content Open Government Licence v3.0, see the <a href="https://github.com/cyberdudeuk/start-a-business-uk">repository</a>.</p>
</div>
<div style="display:flex;gap:14px;align-items:center">{qr_svg(url)}<span style="display:inline-flex;flex-direction:column;gap:4px;align-items:flex-start">{barcode_svg(code)}<code style="font-size:11px">{code}</code></span></div>
</aside>'''


def recheck_page():
    rc = recheck()
    e = html.escape
    s = rc['summary']
    def link(u):
        return f'<a href="{e(u)}">{e(u)}</a>'
    facts = ''.join(f'<tr><td>{e(f["fact"])}</td><td>{e(f["status"])}</td><td>{link(f["source"])}</td></tr>' for f in rc['facts'])
    fixes = ''.join(f'<li><del>{e(c["old"])}</del><br><ins>{e(c["new"])}</ins></li>' for c in rc['corrections'])
    gone = ''.join(f'<tr><td>{link(g["url"])}</td><td>{g["status"]}</td><td>{e(", ".join(g["pages"]))}</td></tr>' for g in rc['gone'])
    moved = ''.join(f'<tr><td>{e(untracked(u))}</td><td>{link(untracked(m["to"]))}</td><td>{e(m["kind"])}</td></tr>' for u, m in sorted(rc['url_updates'].items()))
    unr = ''.join(f'<li>{link(x["url"])} ({e(x["status"])})</li>' for x in rc['not_reachable'])
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Recheck of 22 November 2026: Starting a business in the UK</title>
<style>body{{font:16px/1.55 system-ui,sans-serif;max-width:72rem;margin:0 auto;padding:1.5rem;color:#0b0c0c;background:#fff}}a{{color:#1d4ed8;overflow-wrap:anywhere}}
table{{border-collapse:collapse;width:100%;font-size:.9rem;margin:.5rem 0 1.5rem}}th,td{{border-top:1px solid #ccc;padding:.4rem .5rem;text-align:left;vertical-align:top}}
.wrap{{overflow-x:auto}}del{{color:#8a1c1c}}ins{{color:#0b6e3a;text-decoration:none}}li{{margin:.5rem 0}}.stats{{display:flex;flex-wrap:wrap;gap:1rem}}.stats p{{margin:0;padding:.8rem 1rem;border:1px solid #ccc;border-radius:10px}}.stats b{{display:block;font-size:1.6rem}}
@media (prefers-color-scheme:dark){{body{{background:#0f1720;color:#e8eef3}}a{{color:#8fb3ff}}th,td{{border-color:#334}}del{{color:#ff9a9a}}ins{{color:#7ee2a8}}}}</style></head>
<body><main id="main"><p><a href="../">Starting a business in the UK</a></p>
<h1>Recheck of 22 November 2026</h1>
<p>The guide's content was built and verified on {e(rc['content_built'])}. On {e(rc['checked'])} every source it cites was requested again and the facts most likely to have changed were checked against the official source. {e(rc['method'])}</p>
<div class="stats"><p><b>{s['sources']}</b>sources requested</p><p><b>{s['answering']}</b>answering</p><p><b>{s['moved']}</b>moved, now linked at their new address</p><p><b>{s['gone']}</b>gone, listed below</p><p><b>{s['not_reachable_by_the_checker']}</b>refused an automated check</p></div>
<h2>Time-sensitive facts</h2><div class="wrap"><table><thead><tr><th scope="col">Fact</th><th scope="col">Result</th><th scope="col">Official source</th></tr></thead><tbody>{facts}</tbody></table></div>
<h2>Corrected in the pages</h2><ul>{fixes}</ul>
<h2>Sources that have gone ({s['gone']})</h2><p>These pages no longer exist. Most are support schemes that have closed or moved. The claims that rest on them are kept, marked by this list, until each is replaced or withdrawn: <a href="https://github.com/cyberdudeuk/start-a-business-uk/issues/new?template=contact.yml">tell us</a> if you know where one went.</p>
<div class="wrap"><table><thead><tr><th scope="col">Address</th><th scope="col">Status</th><th scope="col">Cited on</th></tr></thead><tbody>{gone}</tbody></table></div>
<h2>Sources that moved ({s['moved']})</h2><p>Every page now links to the new address.</p>
<div class="wrap"><table><thead><tr><th scope="col">Was</th><th scope="col">Now</th><th scope="col">Kind</th></tr></thead><tbody>{moved}</tbody></table></div>
<h2>Refused an automated check ({s['not_reachable_by_the_checker']})</h2><p>Mostly sites that block automated requests; not evidence that the page has gone.</p><ul>{unr}</ul>
</main></body></html>
'''


def publish(src):
    missing = [a for a in [HUB, *PAGES] if not (src / f'{a}.html').exists()]
    if missing:
        raise SystemExit('missing exports: ' + ', '.join(missing))
    rc = recheck()
    texts = {}
    for aid in [HUB, *PAGES]:
        texts[aid] = apply_recheck(rewrite((src / f'{aid}.html').read_text(encoding='utf-8'), aid), rc)
    unused = [c['old'][:60] for c in rc['corrections'] if not any(c['new'] in t for t in texts.values())]
    if unused:
        raise SystemExit('corrections that matched nothing (wording changed?): ' + '; '.join(unused))
    (ROOT / 'recheck').mkdir(exist_ok=True)
    (ROOT / 'recheck' / 'index.html').write_text(recheck_page() + colophon('recheck'), encoding='utf-8')
    for aid in [HUB, *PAGES]:
        text = texts[aid]
        if MARK not in text:
            i = text.lower().rfind('</body>')
            text = text[:i] + colophon(aid) + '\n' + text[i:] if i >= 0 else text + colophon(aid)
        dest = out_path(aid)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding='utf-8')
    print(f'published {1 + len(PAGES)} pages')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    publish(Path(sys.argv[1]))
