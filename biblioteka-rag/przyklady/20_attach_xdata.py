# Wzorcowa komenda 20 — Doczepienie metadanych (XData) do obiektu.
#
# Demonstruje przypięcie do obiektu niewidocznych danych rozszerzonych (Extended
# Data / XData) — np. numeru inwentarzowego, kodu materiału, notatki. XData
# podróżuje z obiektem, zapisuje się w DWG, i można ją później odczytać. To
# podstawa integracji CAD z bazami danych / kosztorysami. Wzorzec z oficjalnego
# samples xdata.py (funkcja add_x_data).
#
# Sposób użycia: APPLOAD, następnie OZNACZ_OBIEKT. Wskaż obiekt — komenda przypnie
# do niego XData aplikacji "TMSYS" z tekstem "oznaczony przez gstarcad-ai".
# Odczyt tej XData pokazuje oficjalny sample xdata.py (PyPrintXdata).
#
# Konwencje (v2 przewodnika + xdata.py):
#   - resbuf (result buffer) to łańcuch krotek (typ, wartość); XData to taki łańcuch
#   - kod 1001 (kDxfRegAppName) = nazwa aplikacji; 1000 (kDxfXdAsciiString) = tekst
#   - gcdbRegApp(nazwa) rejestruje aplikację ZANIM przypniemy jej XData
#   - gcutNewRb(kod) tworzy element bufora; .rbnext łączy je w łańcuch
#   - obj.upgradeOpen() podnosi z odczytu do zapisu przed setXData
#   - ZAWSZE gcutRelRb(rb) na końcu — zwolnienie bufora

from pygcad.core.runtime import *
from pygcad.pygrx import *

kDxfXdAsciiString = 1000
kDxfRegAppName = 1001

APP_NAME = "TMSYS"
XDATA_TEXT = "oznaczony przez gstarcad-ai"


@command(local_name='OZNACZ_OBIEKT')
def attachXData():
    """Wskazuje obiekt i przypina do niego XData aplikacji TMSYS."""
    try:
        en = gds_name()
        pt = gds_point()
        rc = gcedEntSel("\nWskaż obiekt do oznaczenia: ", en, pt)
        if rc != RTNORM:
            gcutPrintf("\nNic nie wybrano. Operacja anulowana.")
            return

        entId = GcDbObjectId()
        gcdbGetObjectId(entId, en)

        status, obj = gcdbOpenObject(entId, GcDb.kForRead)
        if status != Gcad.eOk:
            gcutPrintf("\n[BŁĄD] Nie można otworzyć wskazanego obiektu.")
            return

        # Zarejestruj aplikację (idempotentne — można wołać wielokrotnie)
        gcdbRegApp(APP_NAME)

        # Zbuduj łańcuch resbuf: [1001: nazwa aplikacji] -> [1000: tekst]
        rb = gcutNewRb(kDxfRegAppName)
        rb.resval.rstring = APP_NAME
        rb.rbnext = gcutNewRb(kDxfXdAsciiString)
        rb.rbnext.resval.rstring = XDATA_TEXT

        # Podnieś obiekt do zapisu i przypnij XData
        obj.upgradeOpen()
        obj.setXData(rb)
        obj.close()

        # Zwolnij bufor
        gcutRelRb(rb)

        gcutPrintf(f"\nObiekt oznaczony XData aplikacji '{APP_NAME}': \"{XDATA_TEXT}\".")

    except Exception as err:
        gcutPrintf(f"\n[BŁĄD] przy oznaczaniu obiektu: {err}")
