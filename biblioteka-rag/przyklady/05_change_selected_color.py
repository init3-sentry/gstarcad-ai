# Wzorcowa komenda 05 — Masowa zmiana koloru zaznaczonych obiektów.
#
# Demonstruje pracę z selection set wg kanonicznego wzorca z oficjalnego
# samples entsel.py: gcedSSGet z 5-argumentowym podpisem, gcedSSLength,
# iterowanie gcedSSName + gcdbGetObjectId + gcdbOpenGcDbEntity, obowiązkowe
# gcedSSFree na końcu.
#
# Sposób użycia: APPLOAD w GstarCAD 2026/2027, następnie wpisz
# ZMIEN_KOLOR_NA_ZIELONY. GstarCAD poprosi o zaznaczenie obiektów
# (oknem, krzyżem, klikaniem pojedynczych). Po Enterze wszystkie
# wskazane obiekty zmienią kolor na zielony (indeks ACI 3).
#
# Historia wzorca: pierwsza wersja (2026-06-30) używała
# `if status != 5100: return` — literał 5100 NIE jest statusem sukcesu
# dla gcedSSGet. Kanoniczny status sukcesu dla operacji użytkownika
# to symboliczne RTNORM. Skutek błędu: komenda zawsze wchodziła w gałąź
# "Anulowano" nawet po poprawnym zaznaczeniu. Poprawka wprowadzona
# 2026-07-09 (v2 przewodnika-systemowego).
#
# Konwencje (v2 przewodnika-systemowego):
#   - gcedSSGet zwraca RTNORM przy sukcesie (NIE Gcad.eOk, NIE literał 5100)
#   - selection set trzymamy w gds_name(); obowiązek gcedSSFree(sset) na końcu
#   - gcdbOpenGcDbEntity zwraca już GcDbEntity — nie trzeba isKindOf/cast

from pygcad.core.runtime import *
from pygcad.pygrx import *


@command(local_name='ZMIEN_KOLOR_NA_ZIELONY')
def changeSelectedToGreen():
    """Zmienia kolor wszystkich zaznaczonych obiektów na zielony."""
    try:
        TARGET_COLOR = 3  # 3 = zielony (indeks ACI, standard AutoCAD/GstarCAD)

        gcutPrintf("\nWybierz obiekty do zmiany koloru, zakończ Enter-em.")

        # Selection set trzymany w gds_name() — kanoniczny bufor selection.
        # 5-arg podpis gcedSSGet(mode, pt1, pt2, filter, ssname). Same None
        # = tryb interaktywny (użytkownik wybiera). 'A' zamiast pierwszego
        # None wybrałoby wszystkie obiekty rysunku bez pytania.
        sset = gds_name()
        gcedSSGet(None, None, None, None, sset)

        status, length = gcedSSLength(sset)
        if status != RTNORM or length <= 0:
            gcedSSFree(sset)
            gcutPrintf("\nNic nie wybrano. Operacja anulowana.")
            return

        modifiedCount = 0
        skippedCount = 0

        entName = gds_name()
        entId = GcDbObjectId()

        for i in range(length):
            try:
                # Pobierz nazwę i-tej encji w selection set, potem zamień
                # ją na trwały ObjectId (bezpieczniejszy uchwyt do bazy).
                gcedSSName(sset, i, entName)
                gcdbGetObjectId(entId, entName)

                # gcdbOpenGcDbEntity zwraca już GcDbEntity — bez potrzeby
                # isKindOf/cast (per entsel.py). Trzeci argument False =
                # nie otwieraj erased entities.
                status, entity = gcdbOpenGcDbEntity(entId, GcDb.kForWrite, False)
                if status != Gcad.eOk or entity is None:
                    skippedCount += 1
                    continue

                entity.setColorIndex(TARGET_COLOR)
                entity.close()
                modifiedCount += 1

            except Exception as itemErr:
                # Pojedyncza encja mogła być np. na warstwie zablokowanej —
                # pomijamy ją, ale całej komendy nie wywalamy.
                gcutPrintf(f"\nPominięto obiekt {i}: {itemErr}")
                skippedCount += 1

        # Selection set trzeba zwolnić zawsze (per entsel.py)
        gcedSSFree(sset)

        gcutPrintf(
            f"\nZmiana koloru zakończona. Zmodyfikowano: {modifiedCount}, "
            f"pominięto: {skippedCount}."
        )

    except Exception as err:
        gcutPrintf(f"\n[BŁĄD] przy zmianie koloru: {err}")
