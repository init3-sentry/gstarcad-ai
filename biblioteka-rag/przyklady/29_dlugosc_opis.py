# GSAI_DL — suma długości wskazanych obiektów + ETYKIETA z przedrostkiem na rysunku.
#
# Zadanie #26 (Z-14). Popyt (Jakub, potwierdzony): branża instalacyjna/sieciowa —
# długości kabli/przewodów, zestawienia materiałowe, kabel między studniami.
#
# Native-check (protokół §4): GstarCAD ma MEASUREGEOM (suma długości) i DIST, ale
# wynik idzie TYLKO do wiersza poleceń — brak natywnej etykiety NA rysunku z przedrostkiem.
# GSAI_DL sumuje luźną selekcję, ale też bez opisu. Ta komenda domyka realną lukę:
# suma długości + trwały opis w rysunku z przedrostkiem (np. "Dł.cał. 1234.56").
#
# Użycie: APPLOAD w GstarCAD 2026/2027, komenda GSAI_DL:
#   1. wskaż obiekty (odcinki/łuki/polilinie), Enter,
#   2. podaj przedrostek opisu (Enter = domyślny "Dł.cał."),
#   3. wskaż punkt wstawienia opisu.
#
# STATUS WERYFIKACJI:
#   🟢 selekcja + suma długości: wzorzec z GSAI_DL (getEndParam/getDistAtParam,
#      fallback length()), bez .cast() (BUG-07), encja w try/finally.
#   🟡 tworzenie tekstu: wzorzec 07_text_label — GcDbText(punkt, treść) 2-arg + setHeight,
#      appendGcDbEntity. UDOKUMENTOWANE (v2 przewodnika), ale NIE zweryfikowane
#      empirycznie na LC. Test zespołu = pierwsza realna walidacja tej ścieżki.

from pygcad.core.runtime import *
from pygcad.pygrx import *

TEXT_HEIGHT = 2.5              # wysokość opisu w jednostkach rysunku; zespół dostroi do skali
DOMYSLNY_PRZEDROSTEK = "Dł.cał."


def _dlugosc_krzywej(entity):
    """Długość krzywej BEZ .cast(). Zwraca float albo None jeśli się nie da."""
    try:
        st, ep = entity.getEndParam()
        if st == Gcad.eOk:
            st2, d = entity.getDistAtParam(ep)
            if st2 == Gcad.eOk:
                return d
    except (AttributeError, TypeError):
        pass
    try:
        st, d = entity.length()
        if st == Gcad.eOk:
            return d
    except (AttributeError, TypeError):
        pass
    return None


@command(local_name='GSAI_DL')
def dlugoscOpis():
    """Sumuje długość wskazanych obiektów i wstawia opis z przedrostkiem w rysunku."""
    try:
        gcutPrintf("\nWskaż obiekty (odcinki/łuki/polilinie) do zsumowania długości, zakończ Enter-em.")
        sset = gds_name()
        gcedSSGet(None, None, None, None, sset)

        status, length = gcedSSLength(sset)
        if status != RTNORM or length <= 0:
            gcedSSFree(sset)
            gcutPrintf("\nNic nie wybrano. Operacja anulowana.")
            return

        total = 0.0
        liczone = 0
        pominiete = 0

        entName = gds_name()
        entId = GcDbObjectId()

        for i in range(length):
            try:
                gcedSSName(sset, i, entName)
                gcdbGetObjectId(entId, entName)
                status, entity = gcdbOpenGcDbEntity(entId, GcDb.kForRead, False)
                if status != Gcad.eOk or entity is None:
                    pominiete += 1
                    continue
                try:
                    d = _dlugosc_krzywej(entity)
                finally:
                    entity.close()
                if d is not None:
                    total += d
                    liczone += 1
                else:
                    pominiete += 1
            except Exception as itemErr:
                pominiete += 1
                gcutPrintf("\nPominieto obiekt %d: %s" % (i, itemErr))

        gcedSSFree(sset)

        if liczone == 0:
            gcutPrintf("\nŻaden wskazany obiekt nie ma mierzalnej długości. Anulowano.")
            return

        # Przedrostek (cronly=1 → dopuszcza spacje w opisie)
        status, przedrostek = gcedGetString(1, "\nPodaj przedrostek opisu <%s>: " % DOMYSLNY_PRZEDROSTEK)
        if status != RTNORM:
            gcutPrintf("\nAnulowano.")
            return
        przedrostek = przedrostek.strip() if przedrostek else ""
        if not przedrostek:
            przedrostek = DOMYSLNY_PRZEDROSTEK

        # Punkt wstawienia opisu
        punkt = GcGePoint3d()
        status = gcedGetPoint(None, "\nWskaż punkt wstawienia opisu: ", punkt)
        if status != RTNORM:
            gcutPrintf("\nAnulowano.")
            return

        tresc = "%s %.2f" % (przedrostek, total)

        # Model space + wstawienie tekstu (wzorzec 07 — 🟡 do weryfikacji na LC)
        database = gcdbWorkingDatabase()
        status, blockTable = database.getBlockTable(GcDb.kForRead)
        if status != Gcad.eOk:
            gcutPrintf("\n[BLAD] Nie można otworzyć tabeli bloków.")
            return
        status, modelSpace = blockTable.getAt(GCDB_MODEL_SPACE, GcDb.kForWrite)
        blockTable.close()
        if status != Gcad.eOk:
            gcutPrintf("\n[BLAD] Nie można otworzyć przestrzeni modelu.")
            return

        text = GcDbText(punkt, tresc)
        text.setHeight(TEXT_HEIGHT)
        status, textId = modelSpace.appendGcDbEntity(text)

        modelSpace.close()
        text.close()

        if status != Gcad.eOk:
            gcutPrintf("\n[BLAD] Nie można dodać opisu do rysunku.")
            return

        gcutPrintf("\n=== OPIS DŁUGOŚCI ===")
        gcutPrintf("\nPoliczono obiektów: %d   (pominięto nie-krzywe/błąd: %d)" % (liczone, pominiete))
        gcutPrintf("\nWstawiono opis: \"%s\"   (wysokość %.2f jedn.)" % (tresc, TEXT_HEIGHT))

    except Exception as err:
        gcutPrintf("\n[GSAI_DL BLAD] %s: %s" % (type(err).__name__, err))
