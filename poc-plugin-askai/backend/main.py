"""
gs-ai PoC backend — v0.2 (2026-07-01)

Zmiany względem v0.1 (stub):
  - Podpięcie realnego modelu Anthropic Claude Sonnet 5
  - Graceful fallback do stubu jeśli ANTHROPIC_API_KEY nie jest ustawiony
    (zero downtime — kontener zawsze wstaje, tryb zależy od klucza)
  - System prompt ładowany z pliku system-prompt.md przy starcie
  - Body żądania: {"prompt": "..."} — właściwe parsowanie
  - CORS headers dla przyszłej integracji z ai.gstarcad.pl frontendem
  - Logging żądań do stdout (widoczne przez docker logs gs-ai-poc)
"""

import logging
import os
import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse

try:
    from anthropic import Anthropic
    ANTHROPIC_SDK_AVAILABLE = True
except ImportError:
    ANTHROPIC_SDK_AVAILABLE = False


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("gs-ai")

APP_VERSION = "0.2"
ANTHROPIC_MODEL = "claude-sonnet-5"
ANTHROPIC_MAX_TOKENS = 2048
SYSTEM_PROMPT_PATH = Path(__file__).parent / "system-prompt.md"

# Wczytaj system prompt raz przy starcie
SYSTEM_PROMPT = ""
if SYSTEM_PROMPT_PATH.exists():
    SYSTEM_PROMPT = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    log.info(
        f"System prompt loaded from {SYSTEM_PROMPT_PATH}, "
        f"{len(SYSTEM_PROMPT)} chars"
    )
else:
    log.warning(f"System prompt file not found at {SYSTEM_PROMPT_PATH}")

# Instrukcja doklejana do system promptu w trybie mode=execute (plugin "Wykonaj
# tutaj"). Kod jest wykonywany natychmiast przez exec() w bieżącym rysunku —
# musi rysować od razu, bez @command i bez markdown.
EXECUTE_INSTRUCTION = """--- TRYB WYKONANIA BEZPOŚREDNIEGO (mode=execute) — NADRZĘDNY ---
Twój kod zostanie wykonany NATYCHMIAST przez exec() w bieżącym rysunku (nie przez APPLOAD). Bezwzględnie:
1. Zwróć WYŁĄCZNIE surowy kod Python. ZERO bloków markdown (żadnych ```), zero tekstu przed i po kodzie, zero sekcji "Jak uruchomić". Pierwszy znak odpowiedzi = pierwszy znak kodu (np. "from").
2. NIE używaj dekoratora @command. Kod ma rysować OD RAZU: zdefiniuj funkcję i WYWOŁAJ ją w ostatniej linii pliku (albo pisz logikę na najwyższym poziomie modułu).
3. Rysuj w bieżącym rysunku: gcdbWorkingDatabase() + przestrzeń modelu (GCDB_MODEL_SPACE otwarta na kForWrite).
4. Zamykaj otwarte obiekty; na końcu wywołaj gcedPrompt z krótkim potwierdzeniem po polsku.
Te reguły mają pierwszeństwo przed wcześniejszymi przykładami w stylu @command."""

# Zdecyduj o trybie na podstawie obecności klucza i SDK
API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
if API_KEY and ANTHROPIC_SDK_AVAILABLE and SYSTEM_PROMPT:
    APP_STAGE = "real-anthropic"
    anthropic_client = Anthropic(api_key=API_KEY)
    log.info(f"Anthropic client initialized, model={ANTHROPIC_MODEL}")
else:
    APP_STAGE = "stub"
    anthropic_client = None
    log.info(
        f"Running in STUB mode "
        f"(key={'set' if API_KEY else 'unset'}, "
        f"sdk={'ok' if ANTHROPIC_SDK_AVAILABLE else 'missing'}, "
        f"prompt={'loaded' if SYSTEM_PROMPT else 'missing'})"
    )


app = FastAPI(title="gs-ai PoC backend", version=APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ai.gstarcad.pl", "https://gs-ai.init3.pro"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "User-Agent"],
)


STUB_CODE = """# Wygenerowane przez gs-ai PoC (tryb stub — sweep-4 pomocnicze funkcje + enum + importy)
# Weryfikacja diagnostyczna bez interakcji z uzytkownikiem:
# - Test 1: gcedPrompt vs gcutPrintf istnienie
# - Test 2: gcedGetReal vs gcutGetReal istnienie
# - Test 3: Gcad.eOk enum vs numeric 5100
# - Test 4: submodul pygcad.core.runtime i widoczne symbole w pygcad.core

# Test 1: prompt/printf
try:
    printf_ok = False
    try:
        gcutPrintf
        printf_ok = True
    except NameError:
        pass
    # gcedPrompt zakladamy jako sprawdzony (uzywamy do wypisania wyniku)
    if printf_ok:
        gcutPrintf("\\n[SWEEP4 1/4] gcutPrintf DZIALA - to wypisane przez gcutPrintf, gcedPrompt tez OK")
    else:
        gcedPrompt("[SWEEP4 1/4] gcutPrintf nie istnieje, gcedPrompt jest jedynym pomocnikiem")
except Exception as err:
    gcedPrompt("[SWEEP4 1/4] FAIL: " + type(err).__name__ + ": " + str(err))

# Test 2: GetReal ktora wersja
try:
    ed_real = False
    ut_real = False
    try:
        gcedGetReal
        ed_real = True
    except NameError:
        pass
    try:
        gcutGetReal
        ut_real = True
    except NameError:
        pass
    gcedPrompt("[SWEEP4 2/4] GetReal: gcedGetReal=" + str(ed_real) + ", gcutGetReal=" + str(ut_real))
except Exception as err:
    gcedPrompt("[SWEEP4 2/4] FAIL: " + type(err).__name__ + ": " + str(err))

# Test 3: Gcad.eOk enum
try:
    eOk_val = "brak"
    try:
        eOk_val = str(int(Gcad.eOk))
    except NameError:
        eOk_val = "NameError - Gcad brak w namespace"
    except AttributeError:
        eOk_val = "AttributeError - Gcad.eOk nie istnieje"
    except Exception as e:
        eOk_val = "Wyjatek: " + str(e)
    gcedPrompt("[SWEEP4 3/4] Gcad.eOk = " + eOk_val + " (moj przewodnik zakladal numeric 5100)")
except Exception as err:
    gcedPrompt("[SWEEP4 3/4] FAIL: " + type(err).__name__ + ": " + str(err))

# Test 4: pygcad module structure
try:
    import pygcad
    import pygcad.core
    has_runtime = hasattr(pygcad.core, 'runtime')
    core_symbols = [x for x in dir(pygcad.core) if not x.startswith('_')][:8]
    gcedPrompt("[SWEEP4 4/4] pygcad.core.runtime jako submodul: " + str(has_runtime))
    gcedPrompt("[SWEEP4 4/4b] pygcad.core widoczne (8 pierwszych): " + str(core_symbols))
except Exception as err:
    gcedPrompt("[SWEEP4 4/4] FAIL: " + type(err).__name__ + ": " + str(err))

gcedPrompt("[SWEEP4] Zakonczono weryfikacje pomocniczych funkcji + enum + importow")
"""


@app.get("/", response_class=HTMLResponse)
def root():
    if APP_STAGE == "real-anthropic":
        stage_label = f"REAL Anthropic ({ANTHROPIC_MODEL})"
        stage_color = "#2a7"
    else:
        stage_label = "STUB (brak klucza)"
        stage_color = "#c73"

    return f"""<!doctype html>
<html lang="pl"><head><meta charset="utf-8"><title>gs-ai PoC</title>
<style>body{{font-family:system-ui,sans-serif;max-width:640px;margin:4em auto;padding:0 1em;line-height:1.6}}
code{{background:#f0f0f0;padding:2px 6px;border-radius:3px}}h1{{color:#c73}}
.stage{{padding:6px 12px;border-radius:6px;background:{stage_color};color:white;display:inline-block;font-weight:600}}
@media (prefers-color-scheme:dark){{body{{background:#111;color:#eee}}code{{background:#222;color:#eee}}}}
</style></head>
<body><h1>gs-ai PoC</h1>
<p>Backend proof of concept pluginu ASKAI dla GstarCAD.</p>
<p>Wersja: <code>{APP_VERSION}</code>. Tryb: <span class="stage">{stage_label}</span></p>
<p>Endpointy:</p>
<ul><li><code>GET /health</code> — status JSON</li>
<li><code>POST /api/generate</code> — streaming kodu (body: <code>{{"prompt":"..."}}</code>)</li></ul>
<p>Repozytorium: <a href="https://github.com/init3-sentry/gstarcad-ai">gstarcad-ai</a></p>
</body></html>"""


@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": APP_VERSION,
        "stage": APP_STAGE,
        "model": ANTHROPIC_MODEL if APP_STAGE == "real-anthropic" else None,
        "system_prompt_loaded": bool(SYSTEM_PROMPT),
        "system_prompt_chars": len(SYSTEM_PROMPT),
        "timestamp": time.time(),
    }


@app.post("/api/generate")
async def generate(request: Request):
    try:
        body = await request.json()
        user_prompt = str(body.get("prompt", "")).strip()
        mode = str(body.get("mode", "")).strip().lower()
    except Exception:
        user_prompt = ""
        mode = ""

    if not user_prompt:
        async def empty_stream():
            yield "# Błąd: brak pola 'prompt' w body żądania.\n"
        return StreamingResponse(empty_stream(), media_type="text/plain; charset=utf-8")

    log.info(f"prompt (len={len(user_prompt)}, mode={mode or 'default'}): {user_prompt[:120]}")

    # W trybie execute doklejamy nadrzędną instrukcję: surowy kod, bez @command,
    # rysuje od razu (dla przycisku "Wykonaj tutaj" w pluginie).
    system_prompt = SYSTEM_PROMPT
    if mode == "execute":
        system_prompt = SYSTEM_PROMPT + "\n\n" + EXECUTE_INSTRUCTION

    if APP_STAGE == "stub":
        async def stub_stream():
            for line in STUB_CODE.splitlines(keepends=True):
                yield line
        return StreamingResponse(stub_stream(), media_type="text/plain; charset=utf-8")

    def anthropic_stream():
        try:
            with anthropic_client.messages.stream(
                model=ANTHROPIC_MODEL,
                max_tokens=ANTHROPIC_MAX_TOKENS,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            log.error(f"Anthropic error: {type(e).__name__}: {e}")
            yield f"\n# Błąd Anthropic: {type(e).__name__}: {e}\n"

    return StreamingResponse(anthropic_stream(), media_type="text/plain; charset=utf-8")
