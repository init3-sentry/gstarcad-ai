# GSAI CHROPOWATOSC — symbol struktury geometrycznej powierzchni.
# GSAI_CHROP : wskaz punkt na powierzchni -> symbol + wartosc (np. "Ra 3.2").
#
# NORMA: PN-EN ISO 21920-1:2022 (aktualna; zastapila ISO 1302:2002, wycofana 2021).
# SYMBOL graficzny (haczyk) jest PRZENIESIONY z ISO 1302 bez zmian -> geometria ponizej
# pozostaje wazna. ISO 21920 zmienila WARTOSC/opis (parametry + warunki pomiaru,
# domyslna regula 16% -> regula "max"), a wartosc user wpisuje jako wolny tekst,
# wiec narzedzie przyjmuje zarowno "Ra 3.2" jak i pelny spec wg 21920.
#
# Geometria symbolu (zweryfikowana w ISO 1302:2002, tozsama w ISO 21920):
#   §3.1  symbol podstawowy: dwa ramiona NIEROWNEJ dlugosci pod 60 st. do linii powierzchni,
#         wierzcholek NA DOLE, krotkie ramie z lewej, dlugie z prawej.
#   §3.2  usuniecie materialu WYMAGANE  -> belka zamykajaca ptaszek.
#   §3.3  usuniecie materialu ZABRONIONE -> okrag wpisany w ptaszek.
#   §3.5  dodatkowe dane -> linia (polka) dodana do DLUZSZEGO ramienia.
#   §4.1  wartosc chropowatosci -> pozycja "a"; przy dwoch granicach a1 nad a2.
# Proporcje wg ISO 1302:2002 tabl. A.1:  H1 = 1,4*h   H2(min) = 3*h   grubosc linii ~ h/10
# (h = wysokosc cyfr, brana z TEXTSIZE rysunku).
from pygcad.core import *
from pygcad.core.runtime import *
from pygcad.pygrx import *
import math

DEG60 = math.radians(60.0)
TAN60 = math.tan(DEG60)


def _open_ms():
    db = gcdbWorkingDatabase()
    s, bt = db.getBlockTable(GcDb.kForRead)
    s, ms = bt.getAt(GCDB_MODEL_SPACE, GcDb.kForWrite)
    bt.close()
    return ms


def _h():
    # wysokosc cyfr h = TEXTSIZE rysunku; gdy 0 lub brak -> 2.5 (najmniejsza z tabl. A.1).
    # Wzorzec odczytu zmiennej systemowej: resbuf + gcedGetVar (wzorzec 16, zwalidowany).
    try:
        rb = resbuf()
        gcedGetVar("TEXTSIZE", rb)
        h = float(rb.resval.rreal)
    except Exception:
        h = 0.0
    return h if h > 0 else 2.5


def _line(ms, x1, y1, x2, y2):
    ln = GcDbLine(GcGePoint3d(x1, y1, 0), GcGePoint3d(x2, y2, 0))
    ms.appendGcDbEntity(ln)
    ln.close()


def _text(ms, x, y, s, h, just=None):
    t = GcDbText(GcGePoint3d(x, y, 0), s)
    t.setHeight(h)
    ms.appendGcDbEntity(t)
    t.close()


def _rysuj(px, py, wartosc, typ):
    """px,py = wierzcholek ptaszka (punkt na powierzchni). typ: Dowolna|Obrobka|BezObrobki."""
    h = _h()
    H1 = 1.4 * h          # wysokosc krotkiego ramienia (ISO 1302:2002 tabl. A.1)
    H2 = 3.0 * h          # wysokosc dlugiego ramienia (minimum wg normy)
    ms = _open_ms()

    # ramiona pod 60 st. do poziomu, wierzcholek na dole
    lx, ly = px - H1 / TAN60, py + H1      # gora krotkiego (lewego) ramienia
    rx, ry = px + H2 / TAN60, py + H2      # gora dlugiego (prawego) ramienia
    _line(ms, px, py, lx, ly)              # krotkie ramie
    _line(ms, px, py, rx, ry)              # dlugie ramie

    if typ == "Obrobka":
        # §3.2 belka zamykajaca ptaszek na poziomie H1 (od lewego ramienia do prawego)
        _line(ms, lx, ly, px + H1 / TAN60, py + H1)
    elif typ == "BezObrobki":
        # §3.3 okrag wpisany, styczny do obu ramion (kat rozwarcia ptaszka = 60 st.,
        # dwusieczna pionowa -> r = d*sin(30) = d/2). Gora okregu na poziomie H1:
        # d + r = H1  ->  d = 2*H1/3,  r = H1/3
        r = H1 / 3.0
        c = GcDbCircle(GcGePoint3d(px, py + 2.0 * H1 / 3.0, 0), GcGeVector3d(0, 0, 1), r)
        ms.appendGcDbEntity(c)
        c.close()

    # §4.1 wartosc w pozycji "a" — w widelkach, na lewo od dlugiego ramienia, nad belka/okregiem
    if wartosc:
        ty = py + H1 + 0.35 * h                       # nad poziomem H1
        tx = px + (ty - py) / TAN60 + 0.4 * h         # tuz na prawo od linii dlugiego ramienia
        _text(ms, tx, ty, wartosc, h)
        # §3.5 polka na dluzszym ramieniu — podpiera opis
        _line(ms, rx, ry, rx + 0.8 * h + 0.6 * h * len(wartosc), ry)

    ms.close()
    gcutPrintf("\n[Chropowatosc] symbol wstawiony (h=%.2f, H1=%.2f, H2=%.2f, typ: %s)." % (h, H1, H2, typ))


@command(local_name='GSAI_CHROP', global_name='GSAI_ROUGHNESS', group_name='GSAI')
def chropowatosc():
    try:
        pt = GcGePoint3d()
        if gcedGetPoint(None, "\nWskaz punkt na powierzchni (wierzcholek symbolu): ", pt) != RTNORM:
            gcutPrintf("\nAnulowano.")
            return
        st, wartosc = gcedGetString(1, "\nWartosc (np. Ra 3.2), Enter = bez wartosci: ")
        if st != RTNORM:
            wartosc = ""
        gcedInitGet(0, "Dowolna Obrobka BezObrobki")
        rc, kw = gcedGetKword("\nTyp [Dowolna/Obrobka/BezObrobki] <Obrobka>: ")
        if rc == RTNONE:
            kw = "Obrobka"
        elif rc != RTNORM:
            gcutPrintf("\nAnulowano.")
            return
        _rysuj(pt.x, pt.y, (wartosc or "").strip(), kw)
    except Exception as e:
        gcutPrintf("\n[Chropowatosc BLAD] %s: %s" % (type(e).__name__, e))
