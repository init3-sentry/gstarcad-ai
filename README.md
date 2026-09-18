# gstarcad-ai

Native Python tools for GstarCAD 2027. Built and maintained by **TMSys** (Poland), the official GstarCAD distributor for Poland.

GstarCAD is the only mainstream CAD system in the affordable tier (alongside AutoCAD, BricsCAD, ZWCAD, ARES) that supports native Python with 790+ programming interfaces and a `@command` decorator that turns any Python function into a fully-fledged CAD command. This project leverages that capability with three deliverables:

1. **A ready-made tool set for GstarCAD** — an add-in the user installs with one file. It adds commands that do the repetitive work: stair and roof generators, layer standards, area and length take-offs, drawing frames, level marks, map underlays from public Polish geodata.
2. **A download site** (`web-app/`) — `ai.gstarcad.pl`, where a GstarCAD user gets the installer and the tool catalogue.
3. **A knowledge base for AI models** (`biblioteka-rag/`) — a system prompt and reference materials that teach ChatGPT, Claude, Gemini and other LLMs how to write code that actually works in GstarCAD, rather than hallucinated AutoCAD-style code.

> **Direction change, July 2026.** An earlier version of this page described a chat service at `ai.gstarcad.pl` that would generate a command from a plain-language description, billed per token. **That model is parked.** It proved to be a curiosity rather than a product. The site is a download page for finished tools instead. See `PRZECZYTAJ-NAJPIERW.md` (revision 2.0) and `PLAN.md`.

## Project status

**Released.** The first public version shipped on 2 September 2026, together with GstarCAD 2027. Development continues — the repository is built openly, so visitors are welcome to read the code, raise issues, and follow progress through the review reports in `przeglady/`.

The tool catalogue with current status is kept in [`NARZEDZIA.md`](NARZEDZIA.md). ⚠️ `PLAN.md` still carries the roadmap as of 30 July 2026 and has not been revised since the release.

## Project language

This repository follows a deliberate language policy:

| Layer | Language |
|---|---|
| Source code (identifiers, comments, technical READMEs) | English |
| User-facing documentation (guides, blog content, marketing) | Native Polish; English and German translations as the project expands internationally |
| Internal team communication | Polish |

This means that the master `README.md` (this file) is in English so it reaches the widest audience, but the team-facing onboarding document (`PRZECZYTAJ-NAJPIERW.md`) and the roadmap (`PLAN.md`) are in Polish.

## For Polish-speaking visitors

Witamy w projekcie **gstarcad-ai**. Główne dokumenty dla osób polskojęzycznych znajdują się w plikach:

- [`NARZEDZIA.md`](NARZEDZIA.md) — katalog narzędzi: co działa, co jest w testach, co wycofane
- [`PRZECZYTAJ-NAJPIERW.md`](PRZECZYTAJ-NAJPIERW.md) — wprowadzenie do projektu, do kogo jest skierowany, jak się włączyć
- [`PLAN.md`](PLAN.md) — mapa drogowa (⚠️ stan na 30 lipca 2026, nieodświeżona po premierze)
- [`dla-pomocy-technicznej/`](dla-pomocy-technicznej/) — pakiet wprowadzający dla zespołu pomocy technicznej TMSys

Strona dla użytkowników końcowych działa pod adresem `ai.gstarcad.pl` — stąd pobiera się instalator narzędzi.

## Repository structure

```
gstarcad-ai/
├── README.md                          ← this file (English)
├── NARZEDZIA.md                       ← tool catalogue and acceptance status (Polish)
├── PRZECZYTAJ-NAJPIERW.md             ← team onboarding (Polish)
├── PLAN.md                            ← roadmap (Polish; as of 30 July 2026)
├── tasks/                             ← individual task descriptions (T-001, T-002, ...)
├── przeglady/                         ← review reports
├── biblioteka-rag/                    ← AI knowledge base for pygcad
│   ├── przewodnik-systemowy.md        ← pointer; the operational system prompt lives in the internal repo
│   ├── api-signatures-reference.md    ← pygcad API signatures
│   ├── oficjalne-materialy-gstarcad-2027/ ← official pygcad samples + manual (from the GstarCAD 2027 installation)
│   └── przyklady/                     ← working .py example commands (see folder README)
├── skrypty/                           ← shipped tool sources
├── instalator/                        ← installer
├── strona/                            ← materials for the public site
├── szyfrowanie/                       ← source protection (Cython)
├── testy/                             ← tests
├── tools/                             ← helper tooling (incl. python-runtime notes)
├── poc-plugin-askai/                  ← ASKAI plugin proof of concept (historical; code moved to the internal repo)
├── web-app/                           ← ai.gstarcad.pl — the download page
├── dla-pomocy-technicznej/            ← onboarding pack for the support team
├── dla-marketingu/                    ← Polish-language marketing materials
└── skrypty-mistrzowskie/              ← master script library
```

**Note on `poc-plugin-askai/`.** The folders here are empty — the proof-of-concept code and its system prompt live in the internal repository (`gstarcad-ai-wewnetrzne/produkt-i-badania/poc-plugin-askai/`). Documents in this repo that point at it name the internal path. If you work with the support team and do not have that repo, ask Dawid for a copy.

## License

This repository is distributed under the MIT License — see [`LICENSE`](LICENSE). Commercial use, modification, and redistribution are all permitted with attribution.

## About TMSys and GstarCAD in Poland

TMSys is the official GstarCAD distributor for Poland, serving over 60 000 active CAD users across the country since 2010. GstarCAD itself is developed by GstarSoft (Suzhou, China) — a publicly-traded company that has been building CAD software for over 25 years and is now the world's third-largest CAD vendor by user base. This project sits in TMSys's product development pipeline as the public-facing AI initiative for the Polish and German-speaking markets.

For commercial inquiries: contact TMSys directly via [tmsys.pl](https://tmsys.pl). For project contributions: see the issues tab and `tasks/` folder.

---

*Maintained by Dawid Jakubowski (Product Manager, GstarCAD nationwide — TMSys) with the GstarCAD support team (Jakub Moszko, Tomasz Gach, Rafał Trzusło) and Robert Nowakowski — long-time TMSys collaborator, owner of a Polish CAD training company, host of the "Rysując w CAD" podcast, and 20+ year CAD industry veteran.*
