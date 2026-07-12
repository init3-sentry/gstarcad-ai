# gstarcad-ai

Native Python integration for GstarCAD 2026, delivered with an AI-powered code generator. Built and maintained by **TMSys** (Poland), the official GstarCAD distributor for Poland.

GstarCAD 2026 is the only mainstream CAD system in the affordable tier (alongside AutoCAD, BricsCAD, ZWCAD, ARES) that supports native Python with 790+ programming interfaces and a `@command` decorator that turns any Python function into a fully-fledged CAD command via the `APPLOAD` command. This project leverages that capability with three deliverables:

1. **A knowledge base for AI models** (`biblioteka-rag/`) — a system prompt and reference materials that teach ChatGPT, Claude, Gemini and other LLMs how to write code that actually works in GstarCAD, rather than hallucinated AutoCAD-style code.
2. **A web application** (`web-app/`) — a public service at `ai.gstarcad.pl` where any GstarCAD user can describe the command they need in plain language and receive a ready-to-use `.py` file.
3. **A curated library of master scripts** (`skrypty-mistrzowskie/`) — production-grade Python commands for common engineering tasks: batch layer audits, parametric block generators, PDF export pipelines, drawing diff tools, and more.

## Project status

Active development. First public release planned for Q3 2026. The repository is built openly — visitors are welcome to read the code, raise issues, and follow progress through the weekly review reports in `przeglady/`.

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

- [`PRZECZYTAJ-NAJPIERW.md`](PRZECZYTAJ-NAJPIERW.md) — wprowadzenie do projektu, do kogo jest skierowany, jak się włączyć
- [`PLAN.md`](PLAN.md) — szczegółowa mapa drogowa na sześć miesięcy
- [`dla-pomocy-technicznej/`](dla-pomocy-technicznej/) — pakiet wprowadzający dla zespołu pomocy technicznej TMSys

Strona dla użytkowników końcowych (formularz generowania skryptów dla licencyjnych klientów GstarCAD) zostanie uruchomiona pod adresem `ai.gstarcad.pl` w Q3 2026.

## Repository structure

```
gstarcad-ai/
├── README.md                          ← this file (English)
├── PRZECZYTAJ-NAJPIERW.md             ← team onboarding (Polish)
├── PLAN.md                            ← six-month roadmap (Polish)
├── tasks/                             ← individual task descriptions (T-001, T-002, ...)
├── przeglady/                         ← weekly review reports
├── biblioteka-rag/                    ← AI knowledge base for pygcad
│   ├── przewodnik-systemowy.md        ← POINTER -> poc-plugin-askai/backend/system-prompt.md (operacyjny SoT)
│   ├── oficjalne-materialy-gstarcad-2027/ ← official pygcad samples + manual (from the GstarCAD 2027 installation)
│   └── przyklady/                     ← working .py example commands (5 today, target 20+ by end of July — built up by the support team; see folder README)
├── poc-plugin-askai/                  ← ASKAI plugin proof of concept (plugin + working FastAPI backend)
├── web-app/                           ← the ai.gstarcad.pl web service (planned — backend will grow out of poc-plugin-askai/backend)
│   ├── backend/                       ← FastAPI server, SQLite, Anthropic API
│   └── frontend/                      ← user-facing Polish form
├── dla-pomocy-technicznej/            ← onboarding pack for the support team
├── dla-marketingu/                    ← Polish-language marketing materials
└── skrypty-mistrzowskie/              ← master script library
```

## License

This repository is distributed under the MIT License — see [`LICENSE`](LICENSE). Commercial use, modification, and redistribution are all permitted with attribution.

## About TMSys and GstarCAD in Poland

TMSys is the official GstarCAD distributor for Poland, serving over 60 000 active CAD users across the country since 2010. GstarCAD itself is developed by GstarSoft (Suzhou, China) — a publicly-traded company that has been building CAD software for over 25 years and is now the world's third-largest CAD vendor by user base. This project sits in TMSys's product development pipeline as the public-facing AI initiative for the Polish and German-speaking markets.

For commercial inquiries: contact TMSys directly via [tmsys.pl](https://tmsys.pl). For project contributions: see the issues tab and `tasks/` folder.

---

*Maintained by Dawid Jakubowski (Product Manager, GstarCAD nationwide — TMSys) with the GstarCAD support team (Jakub Moszko, Tomasz Gach, Rafał Trzusło) and Robert Nowakowski — long-time TMSys collaborator, owner of a Polish CAD training company, host of the "Rysując w CAD" podcast, and 20+ year CAD industry veteran.*
