# Wzorcowa komenda 19 — Głęboka kopia obiektu (deep clone) w bieżącym rysunku.
#
# Demonstruje mechanizm głębokiego klonowania: tworzy pełną, niezależną kopię
# wskazanego obiektu wraz ze wszystkimi jego obiektami zależnymi. W odróżnieniu
# od zwykłego skopiowania encji, deepClone poprawnie kopiuje też definicje, do
# których obiekt się odwołuje (np. referencja bloku razem z definicją). Wzorzec
# z oficjalnego samples deepClone.py.
#
# Sposób użycia: APPLOAD, następnie KLONUJ. Wskaż dowolny obiekt — powstanie
# jego głęboka kopia w tym samym rysunku (w tym samym miejscu, do przesunięcia
# ręcznie).
#
# Konwencje (v2 przewodnika + deepClone.py):
#   - gcedEntSel zwraca RTNORM; gcdbGetObjectId zamienia name -> ObjectId
#   - GcDbObjectIdArray() — tablica id do sklonowania; ids.append(entId)
#   - GcDbIdMapping() — mapa oryginał->kopia wypełniana przez deepCloneObjects
#   - database.deepCloneObjects(ids, ownerId, idMapping, False) -> (status, lista par)
#   - ownerId = id model space (getObjIdAt(GCDB_MODEL_SPACE))

from pygcad.core.runtime import *
from pygcad.pygrx import *


@command(local_name='KLONUJ')
def deepCloneEntity():
    """Wskazuje obiekt i tworzy jego głęboką kopię w bieżącym rysunku."""
    try:
        en = gds_name()
        pt = gds_point()
        rc = gcedEntSel("\nWskaż obiekt do sklonowania: ", en, pt)
        if rc != RTNORM:
            gcutPrintf("\nNic nie wybrano. Operacja anulowana.")
            return

        entId = GcDbObjectId()
        gcdbGetObjectId(entId, en)

        database = gcdbWorkingDatabase()

        # Id model space jako właściciel kopii
        status, blockTable = database.getBlockTable(GcDb.kForRead)
        if status != Gcad.eOk:
            gcutPrintf("\n[BŁĄD] Nie można otworzyć tabeli bloków.")
            return
        status, msId = blockTable.getObjIdAt(GCDB_MODEL_SPACE)
        blockTable.close()
        if status != Gcad.eOk:
            gcutPrintf("\n[BŁĄD] Nie można pobrać id przestrzeni modelu.")
            return

        # Tablica obiektów do sklonowania (tu jeden)
        ids = GcDbObjectIdArray()
        ids.append(entId)

        # Mapa id oryginał -> kopia (wypełniana przez deepCloneObjects)
        idMap = GcDbIdMapping()
        status, pairs = database.deepCloneObjects(ids, msId, idMap, False)
        if status != Gcad.eOk:
            gcutPrintf("\n[BŁĄD] Głębokie klonowanie nie powiodło się.")
            return

        gcutPrintf(f"\nSklonowano obiekt. Utworzono {len(pairs)} nowych obiektów.")
        gcutPrintf("\n(Kopia leży na oryginale — przesuń ją poleceniem MOVE.)")

    except Exception as err:
        gcutPrintf(f"\n[BŁĄD] przy klonowaniu: {err}")
