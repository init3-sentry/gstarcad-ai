# Wzorcowa komenda 12 — Inwentaryzacja obiektów rysunku wg typu.
#
# Demonstruje iterację po wszystkich encjach w przestrzeni modelu i klasyfikację
# każdej po nazwie klasy (isA().name()). Generuje zestawienie „ile linii, ile
# okręgów, ile tekstów..." w rysunku. Wzorzec iteracji model space + isA().name()
# kanoniczny z oficjalnego samples testdb.py (funkcja PyRead).
#
# Sposób użycia: APPLOAD w GstarCAD 2026/2027, następnie wpisz ZLICZ_OBIEKTY.
# Komenda wypisze w command line zestawienie typów obiektów w bieżącym rysunku.
#
# Konwencje (v2 przewodnika + testdb.py):
#   - iteracja po model space: blockRecord.newIterator() + start/done/step
#   - iterator.getEntity() zwraca (status, encja)
#   - typ encji: entity.isA().name() — zwraca nazwę klasy jako string
#     (na GstarCAD nazwy klas mają prefiks AcDb, np. "AcDbLine", "AcDbCircle")

from pygcad.core.runtime import *
from pygcad.pygrx import *


@command(local_name='ZLICZ_OBIEKTY')
def countEntitiesByType():
    """Iteruje po encjach model space i zlicza je wg nazwy klasy."""
    try:
        database = gcdbWorkingDatabase()

        status, blockTable = database.getBlockTable(GcDb.kForRead)
        if status != Gcad.eOk:
            gcutPrintf("\n[BŁĄD] Nie można otworzyć tabeli bloków.")
            return

        status, modelSpace = blockTable.getAt(GCDB_MODEL_SPACE, GcDb.kForRead)
        blockTable.close()
        if status != Gcad.eOk:
            gcutPrintf("\n[BŁĄD] Nie można otworzyć przestrzeni modelu.")
            return

        status, iterator = modelSpace.newIterator()
        if status != Gcad.eOk:
            modelSpace.close()
            gcutPrintf("\n[BŁĄD] Nie można utworzyć iteratora przestrzeni modelu.")
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

        if total == 0:
            gcutPrintf("\nRysunek jest pusty — brak obiektów do zliczenia.")
            return

        gcutPrintf(f"\n=== Inwentaryzacja obiektów ({total} łącznie) ===")
        # Sortuj malejąco po liczności dla czytelności
        for className, count in sorted(counts.items(), key=lambda kv: -kv[1]):
            gcutPrintf(f"\n  {className:<28} {count:>5}")

    except Exception as err:
        gcutPrintf(f"\n[BŁĄD] przy zliczaniu obiektów: {err}")
