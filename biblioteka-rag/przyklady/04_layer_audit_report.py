# Wzorcowa komenda 04 — Audyt warstw rysunku z eksportem raportu do pliku.
#
# Demonstruje iterację po tabeli warstw wg kanonicznego wzorca z oficjalnego
# samples tbliter.py (newIterator + iterator.start + iterator.done + iterator.step,
# rekord otwierany bez argumentu trybu). Odczytuje nazwę i indeks koloru każdej
# warstwy oraz — defensywnie, per-property try/except — flagi frozen/off/locked.
# Generuje raport tekstowy i zapisuje go na Pulpicie użytkownika.
#
# Sposób użycia: APPLOAD w GstarCAD 2026/2027, następnie wpisz AUDYT_WARSTW.
# Po wykonaniu komendy raport pojawi się na Pulpicie w pliku
# o nazwie "raport_warstw_audyt.txt".
#
# Konwencje (v2 przewodnika-systemowego):
#   - Iteracja tabeli symboli per tbliter.py: newIterator -> start -> while not done -> step
#   - iterator.getRecord() bez trybu; rekord dostajemy do odczytu i sami zamykamy
#   - Nazwa warstwy: (status, name) = record.getName() — tuple unpack per tbliter.py
#   - Właściwości frozen/off/locked nie są jeszcze zweryfikowane empirycznie
#     na LayerTableRecord (2026-07-09) — pobieramy defensywnie, z fallbackiem "?".

from pygcad.core.runtime import *
from pygcad.pygrx import *
import os
from datetime import datetime


def _safeCall(func, default="?"):
    """Wywołuje func() i zwraca wynik; przy dowolnym wyjątku zwraca default.
    Używane dla properties LayerTableRecord, których jeszcze nie zweryfikowaliśmy
    empirycznie (isFrozen/isOff/isLocked/colorIndex) — chcemy, żeby audyt
    ukończył się nawet gdy któraś z metod nie istnieje w danej wersji API."""
    try:
        return func()
    except Exception:
        return default


@command(local_name='AUDYT_WARSTW')
def auditLayersToFile():
    """Iteruje po warstwach rysunku i zapisuje raport tekstowy na Pulpicie."""
    try:
        database = gcdbWorkingDatabase()

        # Kanoniczny pattern iteracji tabeli symboli (per tbliter.py):
        # otwieramy tabelę przez gcdbOpenObject(tableId, tryb), potem cast.
        status, obj = gcdbOpenObject(database.layerTableId(), GcDb.kForRead)
        if status != Gcad.eOk:
            gcutPrintf("\n[BŁĄD] Nie można otworzyć tabeli warstw.")
            return
        layerTable = GcDbLayerTable.cast(obj)

        status, iterator = layerTable.newIterator()
        if status != Gcad.eOk:
            layerTable.close()
            gcutPrintf("\n[BŁĄD] Nie można utworzyć iteratora tabeli warstw.")
            return

        currentDateTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        reportLines = [
            "Raport audytu warstw rysunku",
            f"Wygenerowany: {currentDateTime}",
            "=" * 60,
            "",
            f"{'Nazwa warstwy':<30} {'Kolor':>6} {'Zamr.':>6} {'Ukryta':>6} {'Zabl.':>6}",
            "-" * 60,
        ]

        layerCount = 0
        frozenCount = 0
        hiddenCount = 0
        lockedCount = 0

        iterator.start()
        while not iterator.done():
            status, record = iterator.getRecord()
            if status != Gcad.eOk:
                iterator.step()
                continue

            statusName, layerName = record.getName()
            if statusName != Gcad.eOk:
                layerName = "?"

            colorIdx = _safeCall(record.colorIndex)
            isFrozen = _safeCall(record.isFrozen, False)
            isHidden = _safeCall(record.isOff, False)
            isLocked = _safeCall(record.isLocked, False)

            record.close()

            frozenMark = "TAK" if isFrozen is True else ("nie" if isFrozen is False else "?")
            hiddenMark = "TAK" if isHidden is True else ("nie" if isHidden is False else "?")
            lockedMark = "TAK" if isLocked is True else ("nie" if isLocked is False else "?")

            reportLines.append(
                f"{layerName:<30} {str(colorIdx):>6} {frozenMark:>6} {hiddenMark:>6} {lockedMark:>6}"
            )

            layerCount += 1
            if isFrozen is True:
                frozenCount += 1
            if isHidden is True:
                hiddenCount += 1
            if isLocked is True:
                lockedCount += 1

            iterator.step()

        layerTable.close()

        reportLines.extend([
            "",
            "-" * 60,
            f"Łączna liczba warstw: {layerCount}",
            f"Warstw zamrożonych:   {frozenCount}",
            f"Warstw ukrytych:      {hiddenCount}",
            f"Warstw zablokowanych: {lockedCount}",
            "",
        ])

        reportText = "\n".join(reportLines)

        # Zapisz raport na Pulpicie użytkownika
        desktopPath = os.path.expanduser("~/Desktop")
        reportPath = os.path.join(desktopPath, "raport_warstw_audyt.txt")

        with open(reportPath, "w", encoding="utf-8") as fp:
            fp.write(reportText)

        gcutPrintf(f"\nRaport audytu warstw zapisany: {reportPath}")
        gcutPrintf(
            f"\nZnaleziono {layerCount} warstw: {frozenCount} zamrożonych, "
            f"{hiddenCount} ukrytych, {lockedCount} zablokowanych."
        )

    except Exception as err:
        gcutPrintf(f"\n[BŁĄD] przy audycie warstw: {err}")
