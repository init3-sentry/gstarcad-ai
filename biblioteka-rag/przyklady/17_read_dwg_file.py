# Wzorcowa komenda 17 — Odczyt zewnętrznego pliku DWG bez otwierania go w edytorze.
#
# Demonstruje wczytanie pliku DWG do osobnej bazy danych (GcDbDatabase) i
# przejrzenie jego zawartości — bez otwierania rysunku w interfejsie GstarCAD-a.
# Przydatne do inwentaryzacji / audytu wielu plików wsadowo. Wzorzec z oficjalnego
# samples testdb.py (funkcja PyRead).
#
# Sposób użycia: APPLOAD, następnie CZYTAJ_DWG. Komenda czyta plik
# "test1.dwg" z Pulpitu (np. utworzony wzorcem 10 ZAPISZ_MIGAWKE_DWG) i wypisuje
# listę typów obiektów w nim zawartych.
#
# Konwencje (v2 przewodnika + testdb.py):
#   - GcDbDatabase(False, False) — pusta baza BEZ domyślnej zawartości, do wczytania z pliku
#   - database.readDwgFile(sciezka) != Gcad.eOk oznacza błąd odczytu
#   - iteracja model space wczytanej bazy jak w bieżącym rysunku (newIterator + getEntity)

from pygcad.core.runtime import *
from pygcad.pygrx import *
import os


@command(local_name='CZYTAJ_DWG')
def readExternalDwg():
    """Czyta zewnętrzny plik DWG do osobnej bazy i wypisuje typy obiektów."""
    try:
        filePath = os.path.join(os.path.expanduser("~"), "Desktop", "test1.dwg")

        if not os.path.exists(filePath):
            gcutPrintf(f"\nBrak pliku: {filePath}")
            gcutPrintf("\nUtwórz go najpierw wzorcem 10 (ZAPISZ_MIGAWKE_DWG) albo wskaż inny plik.")
            return

        # Pusta baza (bez domyślnej zawartości) do wczytania z pliku
        database = GcDbDatabase(False, False)
        if database.readDwgFile(filePath) != Gcad.eOk:
            gcutPrintf(f"\n[BŁĄD] Nie można wczytać pliku: {filePath}")
            return

        # Otwórz model space wczytanej bazy
        status, blockTable = database.getBlockTable(GcDb.kForRead)
        if status != Gcad.eOk:
            gcutPrintf("\n[BŁĄD] Nie można otworzyć tabeli bloków wczytanego pliku.")
            return
        status, modelSpace = blockTable.getAt(GCDB_MODEL_SPACE, GcDb.kForRead)
        blockTable.close()
        if status != Gcad.eOk:
            gcutPrintf("\n[BŁĄD] Nie można otworzyć przestrzeni modelu wczytanego pliku.")
            return

        status, iterator = modelSpace.newIterator()
        if status != Gcad.eOk:
            modelSpace.close()
            gcutPrintf("\n[BŁĄD] Nie można utworzyć iteratora.")
            return

        counts = {}
        total = 0
        iterator.start()
        while not iterator.done():
            status, entity = iterator.getEntity()
            if status == Gcad.eOk and entity is not None:
                try:
                    className = entity.isA().name()
                except Exception:
                    className = "(nieznany typ)"
                counts[className] = counts.get(className, 0) + 1
                total += 1
            iterator.step()
        modelSpace.close()

        gcutPrintf(f"\n=== Zawartość {os.path.basename(filePath)} ({total} obiektów) ===")
        for className, count in sorted(counts.items(), key=lambda kv: -kv[1]):
            gcutPrintf(f"\n  {className:<28} {count:>5}")

    except Exception as err:
        gcutPrintf(f"\n[BŁĄD] przy odczycie pliku DWG: {err}")
