# Wzorcowa komenda 06 — Wymiar liniowy z tekstem etykiety.
#
# Demonstruje dodawanie wymiaru aligned (równoległego do mierzonej krawędzi)
# do rysunku. Wzorzec kanoniczny z oficjalnego samples ployline_dim.py.
#
# Sposób użycia: APPLOAD w GstarCAD 2026/2027, następnie wpisz WYMIAR_LINIOWY.
# Komenda poprosi o dwa punkty (końce mierzonego odcinka), a wymiar zostanie
# umieszczony 100 jednostek nad drugim punktem z etykietą pokazującą rzeczywistą
# długość odcinka w milimetrach.
#
# Konwencje (v2 przewodnika-systemowego + ployline_dim.py):
#   - GcDbAlignedDimension(pt1, pt2, textPt, strText) — 4 punkty GcGePoint3d
#     + tekst etykiety (może być pusty — GstarCAD wygeneruje wartość automatycznie)
#   - Wymiar dodaje się do model space jak zwykłą encję: appendGcDbEntity
#   - textPt (trzeci punkt) określa pozycję linii wymiarowej — zwykle offset
#     od mierzonego odcinka w kierunku prostopadłym

from pygcad.core.runtime import *
from pygcad.pygrx import *
import math


@command(local_name='WYMIAR_LINIOWY')
def drawAlignedDimension():
    """Pyta użytkownika o dwa punkty i wstawia wymiar liniowy z etykietą."""
    try:
        # Pobierz pierwszy punkt od użytkownika
        pt1 = GcGePoint3d()
        status = gcedGetPoint(None, "\nWskaż pierwszy punkt wymiaru: ", pt1)
        if status != RTNORM:
            gcutPrintf("\nAnulowano.")
            return

        # Pobierz drugi punkt od użytkownika
        pt2 = GcGePoint3d()
        status = gcedGetPoint(None, "\nWskaż drugi punkt wymiaru: ", pt2)
        if status != RTNORM:
            gcutPrintf("\nAnulowano.")
            return

        # Oblicz rzeczywistą długość odcinka i tekst etykiety
        dx = pt2.x - pt1.x
        dy = pt2.y - pt1.y
        dz = pt2.z - pt1.z
        length = math.sqrt(dx * dx + dy * dy + dz * dz)
        labelText = f"{length:.2f}"

        # Punkt trzeci: offset 100 jednostek prostopadle "w górę" (Y)
        # od środka odcinka — proste, przewidywalne umieszczenie linii wymiarowej
        midX = (pt1.x + pt2.x) / 2.0
        midY = (pt1.y + pt2.y) / 2.0
        textPt = GcGePoint3d(midX, midY + 100.0, 0.0)

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

        # Utwórz wymiar aligned (kanoniczny konstruktor z ployline_dim.py)
        dim = GcDbAlignedDimension(pt1, pt2, textPt, labelText)

        status, dimId = modelSpace.appendGcDbEntity(dim)
        if status != Gcad.eOk:
            gcutPrintf("\n[BŁĄD] Nie można dodać wymiaru do przestrzeni modelu.")

        modelSpace.close()
        dim.close()

        gcutPrintf(f"\nWymiar liniowy o długości {labelText} wstawiony.")

    except Exception as err:
        gcutPrintf(f"\n[BŁĄD] przy rysowaniu wymiaru: {err}")
