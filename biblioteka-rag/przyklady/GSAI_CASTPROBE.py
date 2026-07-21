# GSAI_CASTPROBE — izoluje przyczynę crashu WARSTWY. Robi TYLKO ścieżkę cast/isInUse,
# nic więcej. Odpalać na PUSTYM, świeżym rysunku (jest tam warstwa "0" do rzutowania,
# a zero pracy do stracenia gdyby GS padł).
#
# Jak czytać wynik: każdy krok zapisuje "okruszek" do pliku z FLUSH — plik przeżyje nawet
# twardy crash GstarCAD. Po przebiegu otwórz:  C:\Users\Public\castprobe.txt
#   - kończy się "KONIEC OK"        -> cast ANI isInUse nie crashują (WARSTWY pada gdzie indziej)
#   - ostatnia linia "PRZED cast"   -> winny jest GcDbLayerTableRecord.cast()
#   - ostatnia linia "PRZED isInUse" -> winny jest isInUse()
#   - "[WYJATEK PYTHON]"            -> to nie crash, tylko wyjątek (przepisz treść)
#
# Ścieżka wierna WARSTWY (28_layer_report.py: getLayerTable -> newIterator -> getRecord
# -> getName -> GcDbLayerTableRecord.cast -> isInUse), ale tylko PIERWSZY rekord i nic poza tym.
#
# Użycie: APPLOAD -> nowy pusty rysunek -> GSAI_CASTPROBE -> otwórz C:\Users\Public\castprobe.txt

# @KATALOG
# nazwa: Sonda cast (diagnostyka crashu)
# komenda: GSAI_CASTPROBE

from pygcad.core import *
from pygcad.core.runtime import *
from pygcad.pygrx import *

_LOG = r"C:\Users\Public\castprobe.txt"


def _mark(msg):
    """Okruszek: zapis do pliku z flush (przeżyje crash) + do linii poleceń."""
    try:
        with open(_LOG, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
            f.flush()
    except Exception:
        pass
    try:
        gcutPrintf("\n[CASTPROBE] " + msg)
    except Exception:
        pass


@command(local_name='GSAI_CASTPROBE', global_name='GSAI_CASTPROBE', group_name='GSAI')
def castprobe():
    """Izoluje .cast()/isInUse() z WARSTWY. Odpalac na PUSTYM rysunku. Log: C:\\Users\\Public\\castprobe.txt"""
    _mark("=== START (nowy przebieg) ===")
    lt = None
    rec = None
    try:
        db = gcdbWorkingDatabase()
        st, lt = db.getLayerTable(GcDb.kForRead)
        _mark("po getLayerTable st=%s" % st)
        if st != Gcad.eOk or lt is None:
            _mark("brak tabeli warstw — koniec")
            return
        st, it = lt.newIterator()
        _mark("po newIterator st=%s done=%s" % (st, it.done()))
        if it.done():
            _mark("iterator pusty — koniec")
            return
        st2, rec = it.getRecord(GcDb.kForRead)
        _mark("po getRecord st=%s rec_is_none=%s" % (st2, rec is None))
        if rec is None:
            _mark("rec None — koniec")
            return
        stn, nazwa = rec.getName()
        _mark("po getName nazwa=%r" % nazwa)

        _mark("PRZED cast  <-- jesli tu sie urwie, winny jest .cast()")
        lrec = GcDbLayerTableRecord.cast(rec)
        _mark("PO cast (cast NIE crashuje) lrec_is_none=%s" % (lrec is None))

        if lrec is not None:
            _mark("PRZED isInUse  <-- jesli tu sie urwie, winny jest isInUse()")
            used = lrec.isInUse()
            _mark("PO isInUse=%s (isInUse NIE crashuje)" % used)

        _mark("=== KONIEC OK — ani cast ani isInUse nie crashuja ===")
    except Exception as err:
        _mark("[WYJATEK PYTHON] %s: %s" % (type(err).__name__, err))
    finally:
        try:
            if rec is not None:
                rec.close()
        except Exception:
            pass
        try:
            if lt is not None:
                lt.close()
        except Exception:
            pass
