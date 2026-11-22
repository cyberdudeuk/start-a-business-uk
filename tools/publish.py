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
    url = SITE if aid == HUB else f'{SITE}{PAGES[aid]}/'
    code = 'SAB-UK-' + ('HOME' if aid == HUB else PAGES[aid].upper())[:24]
    return f'''{MARK}
<aside class="pgw-colophon" aria-label="About this publication" style="max-width:1120px;margin:40px auto 24px;padding:18px 22px;border:1px solid currentColor;border-radius:12px;font:14px/1.5 system-ui,sans-serif;display:flex;flex-wrap:wrap;gap:18px;align-items:center;opacity:.92">
<div style="flex:1 1 340px;min-width:0">
<p style="margin:0 0 6px"><strong>Not an official government service.</strong> An independent, evidence-led guide by Emanuel Silva, part of
<a href="https://cyberdudeuk.github.io/">Public Good Works</a>. Every claim carries its source; check GOV.UK, nidirect, mygov.scot or gov.wales before you act.</p>
<p style="margin:0 0 6px">Drafted and checked with AI assistance (Claude); the author reviewed and is responsible for it. Some features, such as the page assistant, work only inside Claude and are hidden here.</p>
<p style="margin:0">Questions, corrections or ideas: use the <a href="{CONTACT}">contact form</a> (no email address is published).
Code MIT; content Open Government Licence v3.0, see the <a href="https://github.com/cyberdudeuk/start-a-business-uk">repository</a>.</p>
</div>
<div style="display:flex;gap:14px;align-items:center">{qr_svg(url)}<span style="display:inline-flex;flex-direction:column;gap:4px;align-items:flex-start">{barcode_svg(code)}<code style="font-size:11px">{code}</code></span></div>
</aside>'''


def publish(src):
    missing = [a for a in [HUB, *PAGES] if not (src / f'{a}.html').exists()]
    if missing:
        raise SystemExit('missing exports: ' + ', '.join(missing))
    for aid in [HUB, *PAGES]:
        text = rewrite((src / f'{aid}.html').read_text(encoding='utf-8'), aid)
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
