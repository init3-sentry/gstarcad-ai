# Przewodnik systemowy pygcad — POINTER (zdegradowany 2026-07-12)

> ⚠️ **Ten plik NIE jest już źródłem prawdy.** Konsolidacja SoT 2026-07-12 (decyzja: jeden SoT operacyjny, weryfikowalny przez regenerację). Nie edytuj tego pliku — edytuj właściwy SoT poniżej.

## Gdzie teraz żyje treść

| Co | SoT — edytuj TU |
|---|---|
| **Operacyjny system prompt** (to, co realnie jedzie do modelu; edycja → deploy → weryfikacja regeneracją) | `poc-plugin-askai/backend/system-prompt.md` |
| **Referencja sygnatur API ze stubów** (text/attribute I/O per klasa, atrybuty bloków, handle, input/selection, metody-których-nie-ma) | `biblioteka-rag/api-signatures-reference.md` |
| **Znane problemy + lekcje** (luki wiązania, hatch przez MPolygon, streaming, modeless…) | `poc-plugin-askai/ZNANE-PROBLEMY.md` |

## Dlaczego degradacja

Historycznie ten plik był SoT, a `backend/system-prompt.md` był jego kopią ładowaną przez kontener. W praktyce rozjechały się: empiryczne ustalenia (LC 2026-07-10/12 — GcDbText render, hatch przez `GcDbMPolygon`, `setDimscale`, status wzorców) wchodziły do wersji backendowej, bo to ona faktycznie jedzie do modelu i jest weryfikowalna. Utrzymywanie dwóch ręcznie synchronizowanych przewodników = dryf. Backendowy został SoT operacyjnym; unikalny annex sygnatur API wydzielony do `api-signatures-reference.md` (dalej karmi RAG).

Pełna historia treści v1–v2.2 (kanoniczne wzorce, pitfalls, annex) jest w historii gita tego pliku.
