# Wzorcowa komenda 07 — Etykieta tekstowa w wybranym punkcie.
#
# Demonstruje wstawianie prostego tekstu jednowierszowego (GcDbText) do rysunku.
# Użytkownik podaje punkt wstawienia i treść etykiety, wysokość tekstu wynosi
# 25 jednostek rysunku (domyślne, można dostosować w kodzie).
#
# Sposób użycia: APPLOAD w GstarCAD 2026/2027, następnie wpisz WSTAW_ETYKIETE.
# Komenda zapyta o punkt wstawienia i treść etykiety, po czym umieści tekst
# w rysunku.
#
# Konwencje (v2 przewodnika-systemowego):
#   - GcDbText(GcGePoint3d, str) — konstruktor 2-argumentowy (punkt + treść)
#     UWAGA: GcDbText() bez argumentów rzuca TypeError (empirycznie 2026-07-01)
#   - Wysokość tekstu ustawiamy przez text.setHeight(value) po konstrukcji
#   - Dodajemy jak zwykłą encję: modelSpace.appendGcDbEntity(text)
#
# Uwaga o statusie tego wzorca: konstruktor GcDbText(punkt, string) jest
# udokumentowany w v2 przewodnika, ale nie był jeszcze empirycznie zweryfikowany
# end-to-end na dedykowanej instancji (planowana walidacja przy najbliższej
# sesji z LC — patrz README.md sekcja "🔴 do weryfikacji").

from pygcad.core.runtime import *
from pygcad.pygrx import *


@command(local_name='WSTAW_ETYKIETE')
def insertTextLabel():
    """Pyta o punkt i treść, wstawia etykietę tekstową do rysunku."""
    try:
        TEXT_HEIGHT = 25.0  # wysokość znaków w jednostkach rysunku

        # Pobierz punkt wstawienia
        insertPoint = GcGePoint3d()
        status = gcedGetPoint(None, "\nWskaż punkt wstawienia etykiety: ", insertPoint)
        if status != RTNORM:
            gcutPrintf("\nAnulowano.")
            return

        # Pobierz treść etykiety (gcedGetString — analogicznie do gcedGetReal)
        status, labelText = gcedGetString(0, "\nPodaj treść etykiety: ")
        if status != RTNORM:
            gcutPrintf("\nAnulowano.")
            return

        if not labelText or not labelText.strip():
            gcutPrintf("\nTreść etykiety pusta. Operacja anulowana.")
            return

        # Otwórz model space
        database = gcdbWorkingDatabase()

        status, blockTable = database.getBlockTable(GcDb.kForRead)
        if status != Gcad.eOk:
            gcutPrintf("\n[BŁĄD] Nie można otworzyć tabeli bloków.")
            return

        status, modelSpace = blockTable.getAt(GCDB_MODEL_SPACE, GcDb.kForWrite)
        blockTable.close()
        if status != Gcad.eOk:
            gcutPrintf("\n[BŁĄD] Nie można otworzyć przestrzeni modelu.")
            return

        # Utwórz obiekt tekstu (2-arg constructor per v2 przewodnika)
        text = GcDbText(insertPoint, labelText)
        text.setHeight(TEXT_HEIGHT)

        status, textId = modelSpace.appendGcDbEntity(text)
        if status != Gcad.eOk:
            gcutPrintf("\n[BŁĄD] Nie można dodać tekstu do przestrzeni modelu.")

        modelSpace.close()
        text.close()

        gcutPrintf(f"\nEtykieta \"{labelText}\" wstawiona (wysokość {TEXT_HEIGHT}).")

    except Exception as err:
        gcutPrintf(f"\n[BŁĄD] przy wstawianiu etykiety: {err}")
