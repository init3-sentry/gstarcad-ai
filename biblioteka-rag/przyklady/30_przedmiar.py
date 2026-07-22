# GSAI_PRZEDMIAR — przedmiar: pole + obwod wskazanych obiektow -> CSV (otwiera sie w Excelu).
#
# Kandydat na platny "rodzynek" (research popytu 2026-07-22/23, 3 zrodla + Reddit r/AutoCAD:
# "Query polygons areas -> Excel table", "find area of multiple rooms" 33 komentarze, "coordinates to excel").
#
# NATIVE-CHECK (protokol par.4) — UCZCIWIE, nie udaje ze nie ma:
#   GstarCAD MA natywnie: AREATABLE (tabela pol w rysunku), CAOT_AUTOXLSTABLE_* (linkowane tabele EXCEL),
#   DATAEXTRACTION (kreator ekstrakcji do pliku). ALE to ciezkie/wieloklikowe/kreatorowe.
#   Luka = PROSTE jednoklikowe "zaznacz -> gotowy CSV z polem+obwodem per obiekt + suma".
#   Nasza wartosc = PROSTOTA. Czy luka prostoty uzasadnia budowe -> ocena praktyka (Robert), scope.
#
# WYJSCIE: CSV (nie .xlsx) — zero zaleznosci (openpyxl bywa nieobecny, jak PIL w #32); CSV otwiera sie w Excelu.
#   Separator ";" + przecinek dziesietny + utf-8-sig (BOM) = polski Excel czyta poprawnie, z polskimi znakami.
#
# Uzycie: APPLOAD, komenda GSAI_PRZEDMIAR: zaznacz zamkniete obiekty -> podaj sciezke CSV.
# STATUS: selekcja + getArea + length = zwalidowane API (par.2). Test zespolu potwierdza dzialanie na realnych rysunkach.

from pygcad.core.runtime import *
from pygcad.pygrx import *


def _obwod(entity):
    """Obwod (dlugosc krzywej zamknietej) BEZ .cast(). Zwraca float albo None."""
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


def _pole(entity):
    """Pole obiektu. Zwraca float albo None (obiekt bez pola / otwarty)."""
    try:
        st, a = entity.getArea()
        if st == Gcad.eOk:
            return a
    except (AttributeError, TypeError):
        pass
    return None


@command(local_name='GSAI_PRZEDMIAR')
def przedmiar():
    """Zaznacz zamkniete obiekty -> CSV z polem, obwodem i suma."""
    try:
        gcutPrintf("\nWskaz zamkniete obiekty (polilinie/okregi/regiony/kreskowania), zakoncz Enter-em.")
        sset = gds_name()
        gcedSSGet(None, None, None, None, sset)

        status, length = gcedSSLength(sset)
        if status != RTNORM or length <= 0:
            gcedSSFree(sset)
            gcutPrintf("\nNic nie wybrano. Operacja anulowana.")
            return

        status, sciezka = gcedGetString(1, "\nSciezka pliku CSV <C:/przedmiar.csv>: ")
        if status != RTNORM:
            gcedSSFree(sset)
            gcutPrintf("\nAnulowano.")
            return
        sciezka = (sciezka or "").strip() or "C:/przedmiar.csv"

        wiersze = []
        sumaPola = 0.0
        sumaObw = 0.0
        liczone = 0
        pominiete = 0

        entName = gds_name()
        entId = GcDbObjectId()

        for i in range(length):
            try:
                gcedSSName(sset, i, entName)
                gcdbGetObjectId(entId, entName)
                st, ent = gcdbOpenGcDbEntity(entId, GcDb.kForRead, False)
                if st != Gcad.eOk or ent is None:
                    pominiete += 1
                    continue
                try:
                    pole = _pole(ent)
                    obw = _obwod(ent)
                    typ = type(ent).__name__
                    try:
                        warstwa = ent.layer()
                    except Exception:
                        warstwa = ""
                finally:
                    ent.close()
                if pole is None:
                    pominiete += 1
                    continue
                sumaPola += pole
                if obw is not None:
                    sumaObw += obw
                liczone += 1
                wiersze.append((liczone, warstwa, typ, pole, obw if obw is not None else 0.0))
            except Exception as itemErr:
                pominiete += 1
                gcutPrintf("\nPominieto obiekt %d: %s" % (i, itemErr))

        gcedSSFree(sset)

        if liczone == 0:
            gcutPrintf("\nZaden wskazany obiekt nie ma pola. Anulowano.")
            return

        # Zbuduj CSV w pamieci PRZED otwarciem pliku (ochrona przed truncate przy bledzie formatowania)
        def n(x):
            return ("%.4f" % x).replace(".", ",")

        linie = ["Lp;Warstwa;Typ;Pole;Obwod"]
        for lp, w, t, p, o in wiersze:
            linie.append("%d;%s;%s;%s;%s" % (lp, w, t, n(p), n(o)))
        linie.append("SUMA;;;%s;%s" % (n(sumaPola), n(sumaObw)))
        dane = ("\r\n".join(linie) + "\r\n").encode("utf-8-sig")

        with open(sciezka, "wb") as f:
            f.write(dane)

        gcutPrintf("\n=== PRZEDMIAR ===")
        gcutPrintf("\nObiektow policzono: %d   (pominieto bez pola/blad: %d)" % (liczone, pominiete))
        gcutPrintf("\nSuma pola: %s   Suma obwodu: %s" % (n(sumaPola), n(sumaObw)))
        gcutPrintf("\nZapisano CSV: %s" % sciezka)

    except Exception as err:
        gcutPrintf("\n[GSAI_PRZEDMIAR BLAD] %s: %s" % (type(err).__name__, err))
