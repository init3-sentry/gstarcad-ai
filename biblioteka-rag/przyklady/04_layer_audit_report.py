# Wzorcowa komenda 04 — Audyt warstw rysunku z eksportem raportu do pliku.
#
# Demonstruje iterację po tabeli warstw, odczyt właściwości każdej warstwy
# (nazwa, kolor, status zamrożenia, status ukrycia), generowanie czytelnego
# raportu tekstowego i zapis go do pliku na Pulpicie użytkownika.
#
# Sposób użycia: APPLOAD w GstarCAD 2026, następnie wpisz AUDYT_WARSTW.
# Po wykonaniu komendy raport pojawi się na Pulpicie w pliku
# o nazwie "raport_warstw_audyt.txt".

from pygcad.core.runtime import *
from pygcad.pygrx import *
import os
from datetime import datetime


@command(local_name='AUDYT_WARSTW')
def auditLayersToFile():
    """Iteruje po warstwach rysunku i zapisuje raport tekstowy na Pulpicie."""
    try:
        # Pobierz uchwyt bazy danych
        database = gcdbWorkingDatabase()

        # Otwórz tabelę warstw do odczytu
        status, layerTable = database.getLayerTable(GcDb.OpenMode.kForRead)

        # Przygotuj listę linii raportu (każda linia to osobny element)
        currentDateTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        reportLines = [
            "Raport audytu warstw rysunku",
            f"Wygenerowany: {currentDateTime}",
            "=" * 60,
            "",
            f"{'Nazwa warstwy':<30} {'Kolor':>6} {'Linia':>8} {'Zamr.':>6} {'Ukryta':>6}",
            "-" * 60,
        ]

        # Utwórz iterator po tabeli warstw
        iterator = layerTable.newIterator()
        layerCount = 0
        frozenCount = 0
        hiddenCount = 0

        # Pętla po wszystkich warstwach w tabeli
        while not iterator.done():
            # Otwórz aktualną warstwę do odczytu
            status, currentLayer = iterator.getRecord(GcDb.OpenMode.kForRead)

            # Pobierz właściwości warstwy
            layerName = currentLayer.getName()
            colorIdx = currentLayer.colorIndex()
            isFrozen = currentLayer.isFrozen()
            isHidden = currentLayer.isOff()
            # Typ linii zostawiamy jako tekst, niektóre warstwy mogą mieć styled linetype
            lineTypeId = currentLayer.linetypeObjectId()

            # Format danych do raportu
            frozenMark = "TAK" if isFrozen else "nie"
            hiddenMark = "TAK" if isHidden else "nie"

            reportLines.append(
                f"{layerName:<30} {colorIdx:>6} {'standard':>8} {frozenMark:>6} {hiddenMark:>6}"
            )

            # Statystyki
            layerCount += 1
            if isFrozen:
                frozenCount += 1
            if isHidden:
                hiddenCount += 1

            # Zwolnij obiekt warstwy
            currentLayer.close()

            # Przejdź do następnej warstwy
            iterator.step()

        # Zwolnij tabelę warstw
        layerTable.close()

        # Dodaj podsumowanie na końcu raportu
        reportLines.extend([
            "",
            "-" * 60,
            f"Łączna liczba warstw: {layerCount}",
            f"Warstw zamrożonych:   {frozenCount}",
            f"Warstw ukrytych:      {hiddenCount}",
            "",
        ])

        # Złóż raport w jeden tekst
        reportText = "\n".join(reportLines)

        # Zapisz raport na Pulpicie użytkownika
        desktopPath = os.path.expanduser("~/Desktop")
        reportPath = os.path.join(desktopPath, "raport_warstw_audyt.txt")

        with open(reportPath, "w", encoding="utf-8") as fp:
            fp.write(reportText)

        # Wyświetl komunikat sukcesu w command line
        gcedPrompt(f"Raport audytu warstw zapisany: {reportPath}")
        gcedPrompt(f"Znaleziono {layerCount} warstw, w tym {frozenCount} zamrożonych i {hiddenCount} ukrytych.")

    except Exception as err:
        gcedPrompt(f"---- [BŁĄD] przy audycie warstw: {err}")
