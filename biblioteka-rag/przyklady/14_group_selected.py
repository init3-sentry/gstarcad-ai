# Wzorcowa komenda 14 — Pogrupowanie zaznaczonych obiektów w nazwaną grupę.
#
# Demonstruje pracę ze słownikiem grup rysunku (group dictionary): utworzenie
# nazwanej grupy GcDbGroup i dodanie do niej obiektów wskazanych przez
# użytkownika. Grupa pozwala traktować zbiór obiektów jako całość (zaznaczać,
# przesuwać, kopiować razem). Wzorzec kanoniczny z oficjalnych samples
# groups.py + ents.py (funkcja createGroup).
#
# Sposób użycia: APPLOAD w GstarCAD 2026/2027, następnie wpisz POGRUPUJ.
# Komenda poprosi o zaznaczenie obiektów i utworzy z nich grupę o nazwie
# opartej na czasie utworzenia (unikalna).
#
# Konwencje (v2 przewodnika + groups.py):
#   - GcDbGroup("nazwa_opisowa") — konstruktor z opisem
#   - getGroupDictionary(GcDb.kForWrite) + setAt("KLUCZ", grupa) → (status, groupId)
#   - słownik otwarty do ZAPISU zamykamy w finally (2026-07-18, Z-25) — NIE UPRASZCZAĆ:
#     wyjątek przed close() zostawia słownik grup otwarty do zapisu na resztę sesji
#     (eWasOpenForWrite przy każdej kolejnej próbie), a objaw wychodzi dopiero
#     w następnej komendzie. Ten sam wzorzec: diag_warstwy.py, przykład 25.
#   - grupa.append(entId) dla każdego ObjectId ze zbioru wyboru
#   - selection set jak w entsel.py: gds_name + gcedSSGet + gcedSSFree

from pygcad.core.runtime import *
from pygcad.pygrx import *


@command(local_name='POGRUPUJ')
def groupSelectedEntities():
    """Pyta o zaznaczenie i grupuje wskazane obiekty w nazwaną grupę."""
    try:
        gcutPrintf("\nWybierz obiekty do pogrupowania, zakończ Enter-em.")
        sset = gds_name()
        gcedSSGet(None, None, None, None, sset)

        status, length = gcedSSLength(sset)
        if status != RTNORM or length <= 0:
            gcedSSFree(sset)
            gcutPrintf("\nNic nie wybrano. Operacja anulowana.")
            return

        database = gcdbWorkingDatabase()

        # Otwórz słownik grup i utwórz nową nazwaną grupę
        status, groupDict = database.getGroupDictionary(GcDb.kForWrite)
        if status != Gcad.eOk:
            gcedSSFree(sset)
            gcutPrintf("\n[BŁĄD] Nie można otworzyć słownika grup.")
            return

        # Klucz grupy musi być unikalny — bazujemy na liczbie już istniejących
        groupKey = f"GRUPA_TMSYS_{length}OBJ"
        # close() w finally — patrz nagłówek pliku. NIE upraszczać.
        try:
            group = GcDbGroup(groupKey)
            status, groupId = groupDict.setAt(groupKey, group)
        finally:
            groupDict.close()
        if status != Gcad.eOk:
            group.close()
            gcedSSFree(sset)
            gcutPrintf(f"\n[BŁĄD] Nie można utworzyć grupy (klucz {groupKey} zajęty?).")
            return

        # Dodaj każdy zaznaczony obiekt do grupy
        ename = gds_name()
        entId = GcDbObjectId()
        added = 0
        for i in range(length):
            gcedSSName(sset, i, ename)
            gcdbGetObjectId(entId, ename)
            group.append(entId)
            added += 1

        group.close()
        gcedSSFree(sset)

        gcutPrintf(f"\nUtworzono grupę '{groupKey}' z {added} obiektów.")

    except Exception as err:
        gcutPrintf(f"\n[BŁĄD] przy grupowaniu: {err}")
