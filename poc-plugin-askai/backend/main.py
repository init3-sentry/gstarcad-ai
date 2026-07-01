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


STUB_CODE = """# Wygenerowane przez gs-ai PoC (tryb stub — sweep-2, retest Text + Polyline 2D)
# Test 1: GcDbText poprawnym konstruktorem (nie bezargumentowym z przewodnika)
# Test 2: GcDbPolyline (2D) w izolacji, po swiezym restarcie CAD zeby baza byla czysta
from pygcad.core.runtime import *
from pygcad.pygrx import *

def openMS():
    database = gcdbWorkingDatabase()
    (status, blockTbl) = database.getBlockTable(GcDb.OpenMode.kForRead)
    (status, record) = blockTbl.getAt(GCDB_MODEL_SPACE, GcDb.OpenMode.kForWrite)
    blockTbl.close()
    return record

# Test 1: GcDbText poprawnym konstruktorem (point, string)
try:
    record = openMS()
    text = GcDbText(GcGePoint3d(10, -90, 0), "PoC")
    (status, objId) = record.appendGcDbEntity(text)
    record.close()
    text.close()
    gcedPrompt("[SWEEP2 1/2] GcDbText OK: 'PoC' w (10,-90) konstruktor 2-arg")
except Exception as err:
    gcedPrompt("[SWEEP2 1/2] GcDbText FAIL: " + type(err).__name__ + ": " + str(err))

# Test 2: GcDbPolyline (2D) prostokat 100x50 w (10,-190)
try:
    record = openMS()
    poly = GcDbPolyline()
    poly.addVertexAt(0, GcGePoint2d(10, -190))
    poly.addVertexAt(1, GcGePoint2d(110, -190))
    poly.addVertexAt(2, GcGePoint2d(110, -140))
    poly.addVertexAt(3, GcGePoint2d(10, -140))
    poly.setClosed(True)
    (status, objId) = record.appendGcDbEntity(poly)
    record.close()
    poly.close()
    gcedPrompt("[SWEEP2 2/2] GcDbPolyline (2D) OK: prostokat (10,-190)-(110,-140)")
except Exception as err:
    gcedPrompt("[SWEEP2 2/2] GcDbPolyline (2D) FAIL: " + type(err).__name__ + ": " + str(err))

gcedPrompt("[SWEEP2] Zakonczono retest Text + Polyline 2D")
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
    except Exception:
        user_prompt = ""

    if not user_prompt:
        async def empty_stream():
            yield "# Błąd: brak pola 'prompt' w body żądania.\n"
        return StreamingResponse(empty_stream(), media_type="text/plain; charset=utf-8")

    log.info(f"prompt (len={len(user_prompt)}): {user_prompt[:120]}")

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
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            log.error(f"Anthropic error: {type(e).__name__}: {e}")
            yield f"\n# Błąd Anthropic: {type(e).__name__}: {e}\n"

    return StreamingResponse(anthropic_stream(), media_type="text/plain; charset=utf-8")
