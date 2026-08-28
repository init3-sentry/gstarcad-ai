# GSAI_DL — suma długości zaznaczonych obiektów (port Lee Mac "tlen", www.lee-mac.com).
#
# Ból geodety/projektanta: policzyć ŁĄCZNĄ długość wielu obiektów naraz (linie, łuki,
# polilinie, okręgi, elipsy, splajny). GstarCAD natywnie nie sumuje długości wielu obiektów
# jednym ruchem (LIST = pojedynczo, AREA = pole). Lee Mac zrobił to w LISP (tlen); tu port
# na pygcad do wpięcia w zestaw GSAI. Popyt wyartykułowany (recon #25 "suma długości").
#
# Jak liczy (uniwersalnie): każdą encję traktuje jak krzywą i bierze
# getDistAtParam(getEndParam()) = długość od początku do końca. Dla okręgu = obwód, dla
# zamkniętej polilinii = obwód. Obiekty nie-krzywe (tekst, blok) są pomijane.
# API zweryfikowane w stubach pygrx.pyi: GcDbCurve.getEndParam / getDistAtParam -> (status, float);
# length() na części klas (fallback).
#
# ⚠️ ŚWIADOMIE BEZ .cast(): pygcadowy .cast() jest podejrzany o crash GstarCAD (patrz WARSTWY —
# jedyna nasza komenda z .cast(), jedyna która wywala GS). Tu wołamy metody krzywej WPROST na
# otwartej encji; jeśli pygcad nie zwraca konkretnego typu, obiekt jest po prostu pomijany.
# Zero .cast() = zero tego ryzyka. Wszystko w try/except per obiekt — jeden problem nie wywraca komendy.
#
# Idiom selekcji jak wzorzec 05 (gcedSSGet -> SSLength -> SSName -> gcdbOpenGcDbEntity).
# Tylko CZYTA — nic nie zmienia.
#
# Użycie: APPLOAD tego pliku -> komenda GSAI_DL -> zaznacz obiekty, Enter.

# @KATALOG
# nazwa: Suma długości
# komenda: GSAI_DL

from pygcad.core import *
from pygcad.core.runtime import *
from pygcad.pygrx import *


def _dlugosc_krzywej(entity):
    """Długość krzywej BEZ .cast() (podejrzany o crash). Zwraca float albo None jak się nie da."""
    # 1) getDistAtParam(getEndParam()) — uniwersalne dla krzywych
    try:
        st, ep = entity.getEndParam()
        if st == Gcad.eOk:
            st2, d = entity.getDistAtParam(ep)
            if st2 == Gcad.eOk:
                return d
    except (AttributeError, TypeError):
        pass
    # 2) fallback: length() (np. GcDbLine)
    try:
        st, d = entity.length()
        if st == Gcad.eOk:
            return d
    except (AttributeError, TypeError):
        pass
    return None


@command(local_name='GSAI_DL', global_name='GSAI_TLEN', group_name='GSAI')
def dlugosc():
    """Sumuje długość zaznaczonych obiektów (linie/łuki/polilinie/okręgi/elipsy/splajny). Tylko czyta."""
    try:
        gcutPrintf("\nWybierz obiekty do zsumowania dlugosci, zakoncz Enter-em.")
        sset = gds_name()
        gcedSSGet(None, None, None, None, sset)

        status, length = gcedSSLength(sset)
        if status != RTNORM or length <= 0:
            gcedSSFree(sset)
            gcutPrintf("\nNic nie wybrano. Operacja anulowana.")
            return

        total = 0.0
        liczone = 0      # ile obiektów realnie policzono (krzywe)
        pominiete = 0    # ile pominięto (nie-krzywe / błąd)

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
                gcutPrintf(f"\nPominieto obiekt {i}: {itemErr}")

        gcedSSFree(sset)

        gcutPrintf("\n=== SUMA DLUGOSCI ===")
        gcutPrintf(f"\nPoliczono obiektow: {liczone}   (pominieto nie-krzywe/blad: {pominiete})")
        gcutPrintf(f"\nLaczna dlugosc: {total:.4f}   (jednostki rysunku)")

    except Exception as err:
        gcutPrintf(f"\n[DLUGOSC BLAD] {type(err).__name__}: {err}")
