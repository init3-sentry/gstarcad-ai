# Wzorcowa komenda 05 — Masowa zmiana koloru zaznaczonych obiektów.
#
# Demonstruje pracę z zaznaczeniem użytkownika (selection set): zapytanie
# o zbiór wyboru przez gcedSSGet, iterację po zaznaczonych obiektach,
# rzutowanie obiektu na typ GcDbEntity (klasa bazowa) i modyfikację jednej
# jego właściwości (koloru).
#
# Sposób użycia: APPLOAD w GstarCAD 2026, następnie wpisz ZMIEN_KOLOR_NA_ZIELONY.
# GstarCAD poprosi Cię o zaznaczenie obiektów (możesz użyć zaznaczania
# oknem, krzyżem albo wskazywania pojedynczych). Po zatwierdzeniu zaznaczenia
# wszystkie wskazane obiekty zmienią kolor na zielony.

from pygcad.core.runtime import *
from pygcad.pygrx import *


@command(local_name='ZMIEN_KOLOR_NA_ZIELONY')
def changeSelectedToGreen():
    """Zmienia kolor wszystkich zaznaczonych obiektów na zielony."""
    try:
        # Stała: zielony to kolor o indeksie 3 w standardowej palecie GstarCAD-a
        TARGET_COLOR = 3

        # Poproś użytkownika o zaznaczenie obiektów
        gcedPrompt("Wybierz obiekty do zmiany koloru, zakończ Enter-em.")
        status, selectionSet = gcedSSGet()

        # Sprawdź czy użytkownik faktycznie coś zaznaczył
        if status != 5100:
            gcedPrompt("Nic nie wybrano. Operacja anulowana.")
            return

        # Pobierz liczbę zaznaczonych obiektów
        count = selectionSet.length()

        if count == 0:
            gcedPrompt("Pusty zbiór wyboru. Operacja anulowana.")
            return

        # Liczniki dla raportu końcowego
        modifiedCount = 0
        skippedCount = 0

        # Iteruj po wszystkich zaznaczonych obiektach
        for i in range(count):
            try:
                # Pobierz identyfikator obiektu o pozycji i w zbiorze wyboru
                status, entityId = selectionSet.getAt(i)

                # Otwórz obiekt do zapisu
                status, entity = gcdbOpenObject(entityId, GcDb.OpenMode.kForWrite)

                # Sprawdź czy obiekt jest pochodną GcDbEntity (czyli ma kolor)
                if entity.isKindOf(GcDbEntity.desc()):
                    # Rzutuj na klasę bazową GcDbEntity (operacja bezpieczna po sprawdzeniu)
                    entityCast = GcDbEntity.cast(entity)
                    # Ustaw nowy indeks koloru
                    entityCast.setColorIndex(TARGET_COLOR)
                    modifiedCount += 1
                else:
                    skippedCount += 1

                # Zwolnij obiekt
                entity.close()

            except Exception as itemErr:
                # Jeśli zmiana koloru dla pojedynczego obiektu zawiodła,
                # pomiń go i kontynuuj — nie wywalaj całej komendy
                gcedPrompt(f"Pominięto obiekt {i}: {itemErr}")
                skippedCount += 1

        # Raport końcowy
        gcedPrompt(
            f"Zmiana koloru zakończona. Zmodyfikowano: {modifiedCount}, "
            f"pominięto: {skippedCount}."
        )

    except Exception as err:
        gcedPrompt(f"---- [BŁĄD] przy zmianie koloru: {err}")
