# Starting a business in the UK: the whole journey

[![Checks](https://github.com/cyberdudeuk/start-a-business-uk/actions/workflows/checks.yml/badge.svg)](https://github.com/cyberdudeuk/start-a-business-uk/actions/workflows/checks.yml)

**Everything you have to do to start a business in the UK, in order, with every claim traced to its source.**

### [Open the guide →](https://cyberdudeuk.github.io/start-a-business-uk/)

| | |
|---|---|
| **What it is** | Nineteen linked pages: a founder's plan, every step, public body and identifier, the rules an activity triggers, tailored circumstances, every way in and out of owning a business, the four nations, an international comparison, service blueprints, a knowledge layer and a verification register |
| **Status** | Prototype (release 11.0). Independent work; **not an official government service**. Content built and verified 17 September 2026; sources and time-sensitive facts [rechecked 22 November 2026](https://cyberdudeuk.github.io/start-a-business-uk/recheck/). Check GOV.UK, nidirect, mygov.scot or gov.wales before you act |
| **Who it is for** | People starting a business, people who advise them, and the service teams who design the journey |
| **Contact** | By [contact form](https://github.com/cyberdudeuk/start-a-business-uk/issues/new?template=contact.yml) only. There is no email route |
| **Part of** | [Public Good Works](https://cyberdudeuk.github.io/), the launchpad for every project in this account |

## The pages

| Page | Address |
|---|---|
| [Starting a business in the UK: the whole journey](./) (home) | `/` |
| [Your plan: what you have to do, in order](your-plan/) | `your-plan/` |
| [Before the register: evidence on the pre-registration boundary](before-the-register/) | `before-the-register/` |
| [Starting a business in the UK: every step, body and identifier](every-step/) | `every-step/` |
| [Whatever you are setting up: forms, activities, money and support](whatever-you-are-setting-up/) | `whatever-you-are-setting-up/` |
| [What binds this business: activity to regulation](what-binds-this-business/) | `what-binds-this-business/` |
| [Rules, trade and the bodies behind them](rules-trade-and-bodies/) | `rules-trade-and-bodies/` |
| [When the standard route does not fit: tailoring the journey to circumstances](your-circumstances/) | `your-circumstances/` |
| [Every way in, and every way out: front doors to owning a business](every-way-in/) | `every-way-in/` |
| [From starting to closing: the whole life of a business](whole-life-of-a-business/) | `whole-life-of-a-business/` |
| [Skills, qualifications and finding your people](skills-and-communities/) | `skills-and-communities/` |
| [Four nations, one register: starting a business across the UK](four-nations/) | `four-nations/` |
| [The UK, compared: starting a business across government](the-uk-compared/) | `the-uk-compared/` |
| [Starting a business: twenty years of government trying to join it up](twenty-years-of-joining-up/) | `twenty-years-of-joining-up/` |
| [Standards for the journey: starting a business](standards/) | `standards/` |
| [Service blueprints, personas and inclusion](service-blueprints/) | `service-blueprints/` |
| [The knowledge layer: graph, glossary, dictionary and ontology](knowledge-layer/) | `knowledge-layer/` |
| [Verification register: every claim and its source](verification-register/) | `verification-register/` |
| [How this was built and how it is run](how-this-was-built/) | `how-this-was-built/` |

## How it is published

The pages were built and verified as linked Claude artifacts. `tools/publish.py` turns an export of each into this
site: the home page at the root, every other page in its own folder, links between pages made relative, retired names
corrected, and a colophon added to every page (not official, AI disclosure, contact form, licence, QR code and barcode).
GitHub Pages serves the `main` branch as it is: there is no build step.

```bash
python3 tools/publish.py /path/to/exports   # after re-exporting pages; needs segno and python-barcode
python3 tools/check.py                      # 8 checks on every page
python3 tools/check.py --negative           # proves each check fails on a deliberate break
```

Every page also checks itself in your browser on load (structure, links, accessibility basics, its own age) and says
so at the foot of the page. Features that need Claude, such as the page assistant, hide themselves here.

## Rechecks

Each recheck is recorded in `data/recheck-YYYY-MM-DD.json`: what was requested, the facts checked against official
sources, wording corrected, addresses that moved (applied to every page, with tracking parameters stripped) and
sources that have gone. `tools/publish.py` applies it on every publish and builds the public
[recheck page](https://cyberdudeuk.github.io/start-a-business-uk/recheck/); check C7 fails if any of it is undone.

## Running it: effort for one person

| Task | When | Effort |
|---|---|---|
| Nothing: the site is static and checks run on every push | Always | None |
| Recheck sources and time-sensitive facts (scripted link check, then official sources for fees, thresholds and dates) | Each quarter, or when a rule changes | Half a day |
| Replace or withdraw claims resting on sources that have gone (43 at the last recheck) | After each recheck | A day for the current backlog |
| Answer contact-form issues | As they come | Minutes each |

The pages flag their own age: from 90 days after the build date they say re-verification is due.

## Licence

Code: [MIT](LICENSE). Content: [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/),
because it describes and quotes UK public sector information. Sources quoted keep their own licences.
Cite it with [CITATION.cff](CITATION.cff). Security: [SECURITY.md](SECURITY.md).
