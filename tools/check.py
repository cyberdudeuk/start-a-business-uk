#!/usr/bin/env python3
"""Checks every published page. Exit 1 on any problem.

C1  no page links back to a private Claude artifact (claude.ai/artifact)
C2  every link between pages of the family resolves to a published page
C3  no email address is published (contact is by form only)
C4  retired names never appear (Office of the Chief Data Officer, OCDO)
C5  every page carries the colophon exactly once: not official, AI disclosure, contact form, licence, QR code
C6  every page has one <title> and the family is complete (hub plus 18 pages)
C7  the latest recheck is applied: its page exists, no moved address remains, no corrected wording remains
C8  no link carries a tracking parameter (utm_, gad_, gclid and the like)

Run:  python3 tools/check.py
      python3 tools/check.py --negative   prove each check fails on a deliberate break (vaccination)
"""
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import publish

EMAIL = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}')
NOT_EMAIL = re.compile(r'@\d|\.(?:png|jpg|svg|woff2?|js|css)$')  # font axes like wght@62..125, file names
REL = re.compile(r'''(?:href=|"u"\s*:\s*|'u'\s*:\s*)["'](\.{0,2}/?[a-z0-9-]*/?)["']''')


def pages(root):
    return {aid: publish.ROOT.__class__(root) / ('index.html' if aid == publish.HUB else f'{slug}/index.html')
            for aid, slug in [(publish.HUB, '')] + list(publish.PAGES.items())}


def problems(root):
    out = []
    files = pages(root)
    for f in files.values():
        if not f.exists():
            out.append(f'C6 missing page {f.relative_to(root)}')
            continue
        t = f.read_text(encoding='utf-8')
        name = str(f.relative_to(root))
        if 'claude.ai/artifact/' in t:
            out.append(f'C1 {name} still links to a Claude artifact')
        for m in REL.finditer(t):
            link = m.group(1)
            if link in ('', '#') or link.startswith('#') or not re.fullmatch(r'(\./|\.\./)?([a-z0-9-]+/)?', link):
                continue
            target = (f.parent / link / 'index.html').resolve()
            if not target.exists():
                out.append(f'C2 {name} links to {link}, which is not a published page')
        mails = [x for x in EMAIL.findall(t) if not NOT_EMAIL.search(x)]
        if mails:
            out.append(f'C3 {name} publishes email address(es): {sorted(set(mails))[:3]}')
        if re.search(r'Office of the Chief Data Officer|\bOCDO\b', t):
            out.append(f'C4 {name} uses a retired name')
        n = t.count(publish.MARK)
        block = t.split(publish.MARK, 1)[1] if n else ''
        if n != 1 or not all(k in block for k in ('Not an official government service', 'AI assistance', 'contact form', 'Licence', 'QR code')):
            out.append(f'C5 {name} has {n} colophon(s) or one missing a required part')
        if len(re.findall(r'<title>', t)) < 1:
            out.append(f'C6 {name} has no title')
    track = re.compile(r'https?://[^"\'\s<>]*[?&](utm_[a-z]+|gad_[a-z]+|gclid|gbraid|wbraid|fbclid|msclkid|mc_cid|mc_eid|_gl)=', re.IGNORECASE)
    for f in [*files.values(), root / 'recheck' / 'index.html']:
        if f.exists() and track.search(f.read_text(encoding='utf-8')):
            out.append(f'C8 {f.relative_to(root)} has a link with a tracking parameter: {track.search(f.read_text(encoding="utf-8")).group(0)[:90]}')
    rc = publish.recheck()
    rp = root / 'recheck' / 'index.html'
    if not rp.exists():
        out.append('C7 the recheck page is missing')
    for f in files.values():
        if not f.exists():
            continue
        t = f.read_text(encoding='utf-8')
        name = str(f.relative_to(root))
        stale = [u for u in rc['url_updates'] if publish.url_pattern(u).search(t)]
        if stale:
            out.append(f'C7 {name} still cites {len(stale)} moved address(es), e.g. {stale[0]}')
        if any(c['old'] in t for c in rc['corrections']):
            out.append(f'C7 {name} still carries wording the recheck corrected')
        if 'recheck/' not in t.split(publish.MARK, 1)[-1]:
            out.append(f'C7 {name} does not link to the recheck page')
    return out


BREAKS = {
    'C1': lambda r: _edit(r, 'your-plan/index.html', lambda t: t + '<a href="https://claude.ai/artifact/LLNBnnGC25rGHLh7gAsqBM">x</a>'),
    'C2': lambda r: _edit(r, 'index.html', lambda t: t + '<a href="no-such-page/">x</a>'),
    'C3': lambda r: _edit(r, 'standards/index.html', lambda t: t + 'write to someone@example.gov.uk'),
    'C4': lambda r: _edit(r, 'index.html', lambda t: t + 'OCDO'),
    'C5': lambda r: _edit(r, 'four-nations/index.html', lambda t: t.replace(publish.MARK, '')),
    'C6': lambda r: (r / 'knowledge-layer' / 'index.html').unlink(),
    'C8': lambda r: _edit(r, 'standards/index.html', lambda t: t + '<a href="https://www.gov.uk/x?utm_source=y">x</a>'),
    'C7': lambda r: _edit(r, 'every-step/index.html', lambda t: t + '<a href="https://www.great.gov.uk/">x</a>'),
}


def _edit(root, rel, fn):
    p = root / rel
    p.write_text(fn(p.read_text(encoding='utf-8')), encoding='utf-8')


def negative():
    failed = []
    for code, brk in BREAKS.items():
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t) / 'site'
            shutil.copytree(ROOT, tmp, ignore=shutil.ignore_patterns('.git'))
            brk(tmp)
            caught = any(p.startswith(code) for p in problems(tmp))
            print(f'vaccination {code}: {"caught" if caught else "NOT CAUGHT"}')
            if not caught:
                failed.append(code)
    return 1 if failed else 0


if __name__ == '__main__':
    if '--negative' in sys.argv:
        sys.exit(negative())
    found = problems(ROOT)
    print('FAIL\n' + '\n'.join(found) if found else f'PASS: 8 checks on {len(pages(ROOT))} pages')
    sys.exit(1 if found else 0)
