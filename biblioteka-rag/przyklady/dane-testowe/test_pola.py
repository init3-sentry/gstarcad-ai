# PROBE — czy pygcad umie TWORZYĆ POLA (Fields)? To BRAMKA odblokowująca ~9 narzędzi
# z listy Lee Maca (Area Field, Length Field, Field Objects, Field Arithmetic itd. — 11 pozycji
# oznaczonych 🕓 w analizie zależy od tej jednej odpowiedzi).
#
# Co wiadomo ze stubów: gcdbMakeFieldCode (buduje kod pola) + GcDbDatabase.evaluateFields
# + encja.hasFields()/getField() ISTNIEJĄ. ALE nie ma konstruktora GcDbField ani write-side
# setField(). Czyli „odczyt/ewaluacja pól = tak, ale TWORZENIE pola z kodu = pod znakiem zapytania".
# Ten probe sprawdza to na żywo i raportuje KAŻDY krok, żebyśmy klasyfikowali z dowodem, nie zgadywali.
#
# Użycie: APPLOAD tego pliku → komenda TESTPOLA. Czytaj wynik w wierszu poleceń (5 kroków + werdykt).
from pygcad.core import *
from pygcad.core.runtime import *
from pygcad.pygrx import *


def _ms():
    db = gcdbWorkingDatabase()
    st, bt = db.getBlockTable(GcDb.kForRead)
    if st != Gcad.eOk:
        return None
    st, ms = bt.getAt(GCDB_MODEL_SPACE, GcDb.kForWrite)
    bt.close()
    return ms if st == Gcad.eOk else None


@command(local_name='TESTPOLA')
def testpola():
    try:
        gcutPrintf("\n=== PROBE POL (Fields) — bramka ~9 narzedzi ===")
        db = gcdbWorkingDatabase()

        # KROK 1: zbuduj KOD POLA (formula 2+2). Hyperlink bywa wybredny na None -> fallback.
        code = None
        for hl in (None, "___fallback___"):
            try:
                arg = None if hl is None else GcHyperlink()
                rc, code = gcdbMakeFieldCode("(2+2)", "AcExpr", "", arg)
                gcutPrintf("\n[1] gcdbMakeFieldCode rc=%s (hyperlink=%s) -> kod=%s"
                           % (str(rc), "None" if hl is None else "GcHyperlink()", repr(code)[:100]))
                if code:
                    break
            except Exception as e:
                gcutPrintf("\n[1] gcdbMakeFieldCode(%s) PADL: %s: %s"
                           % ("None" if hl is None else "GcHyperlink()", type(e).__name__, str(e)))

        # KROK 2: utworz TEKST zawierajacy kod pola (jesli kod sie zbudowal — uzyj go; inaczej surowy)
        surowy = "%<\\AcExpr 2+2 \\f \"%lu2\">%"
        tekst_kod = code if code else surowy
        ms = _ms()
        if ms is None:
            gcutPrintf("\n[2] BLAD: brak model space."); return
        txt = GcDbText(GcGePoint3d(0, 0, 0), tekst_kod)
        txt.setHeight(2.5)
        st, oid = ms.appendGcDbEntity(txt)
        txt.close()
        ms.close()
        gcutPrintf("\n[2] tekst z kodem pola dodany (append=%s, kod=%s)" % (str(st), "z gcdbMakeFieldCode" if code else "surowy"))

        # KROK 3: czy encja REJESTRUJE pole?
        try:
            st, obj = gcdbOpenObject(oid, GcDb.kForRead)
            gcutPrintf("\n[3] hasFields() = %s   <-- True = pygcad WIDZI pole w tym tekscie" % str(obj.hasFields()))
            obj.close()
        except Exception as e:
            gcutPrintf("\n[3] hasFields PADL: %s: %s" % (type(e).__name__, str(e)))

        # KROK 4: EWALUACJA pol w bazie
        try:
            rc = db.evaluateFields(0)
            gcutPrintf("\n[4] db.evaluateFields(0) rc=%s" % str(rc))
        except Exception as e:
            gcutPrintf("\n[4] evaluateFields PADL: %s: %s" % (type(e).__name__, str(e)))

        # KROK 5: czy istnieje write-side setField (nawet jesli nie ma w stubach)? + co pokazuje tekst
        try:
            st, obj = gcdbOpenObject(oid, GcDb.kForRead)
            gcutPrintf("\n[5] encja ma metode setField()? %s   <-- klucz do TWORZENIA pol" % str(hasattr(obj, "setField")))
            try:
                gcutPrintf("\n[5] tekst po ewaluacji = %s" % repr(obj.textString())[:100])
            except Exception:
                pass
            obj.close()
        except Exception as e:
            gcutPrintf("\n[5] PADL: %s: %s" % (type(e).__name__, str(e)))

        gcutPrintf("\n=== JAK CZYTAC ===")
        gcutPrintf("\n  hasFields=True + tekst pokazuje '4'  -> POLA DZIALAJA -> ~9 narzedzi -> 🟢")
        gcutPrintf("\n  hasFields=False / tekst = literalny kod -> tworzenie pol z kodu NIE dziala -> zostaja 🕓/🔴")
        gcutPrintf("\n  (Wpisz ZOOM potem E, zeby zobaczyc tekst na rysunku.)")

    except Exception as err:
        gcutPrintf("\n[TESTPOLA BLAD] %s: %s" % (type(err).__name__, str(err)))
