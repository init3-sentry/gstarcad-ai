# DIAGNOSTYKA CRASHA PRZY ZAPISIE — GstarCAD wyłącza się po EKSPORT? nie, po ZAPISIE
# (ZAMIEN_TEKST/IMPORT/RENUMERUJ). Odczyt (EKSPORT) = 47 atrybutow OK, zapis = pad.
# Ten probe robi JEDEN zapis atrybutu z markerami [a]..[f], zeby zobaczyc GDZIE pada:
#   - jesli widzisz [a][b][c][d][e] i DOPIERO POTEM GstarCAD sie zamyka -> problem to
#     sprzatanie/GC po komendzie (cykl zycia wrapperow), nie sam zapis.
#   - jesli pada w srodku (np. widzisz [b] ale nie [c]) -> ta operacja jest winna.
#
# NIEINWAZYJNE: zapisuje atrybutowi jego WLASNA wartosc z powrotem (nic nie zmienia w rysunku).
# Uzycie: otworz 30993 -> APPLOAD -> TESTZAPIS. Skopiuj cala konsole (nawet jesli GstarCAD padnie,
# markery zdazyly sie wypisac) i odeslij.
from pygcad.core.runtime import *
from pygcad.pygrx import *


@command(local_name='TESTZAPIS')
def testzapis():
    try:
        gcutPrintf("\n=== TEST ZAPISU 1 ATRYBUTU (markery [a]..[f]) ===")
        db = gcdbWorkingDatabase()
        s, bt = db.getBlockTable(GcDb.kForRead)
        s, ms = bt.getAt(GCDB_MODEL_SPACE, GcDb.kForRead)
        bt.close()
        s, it = ms.newIterator()
        it.start()
        ids = []
        while not it.done():
            s, ent = it.getEntity()
            if s == Gcad.eOk and ent is not None:
                try:
                    if "BlockReference" in ent.isA().name():
                        ids.append(ent.objectId())
                except Exception:
                    pass
                ent.close()
            it.step()
        ms.close()
        gcutPrintf("\nBlock refs: %d" % len(ids))

        zrobione = False
        for oid in ids:
            if zrobione:
                break
            s, obj = gcdbOpenObject(oid, GcDb.kForWrite)
            if s != Gcad.eOk or obj is None:
                continue
            ref = GcDbBlockReference.cast(obj)
            if ref is None:
                obj.close()
                continue
            try:
                ait = ref.attributeIterator()
                if ait.done():
                    ref.close()
                    continue
                aid = ait.objectId()
                sa, attr = ref.openAttribute(aid, GcDb.kForWrite)
                if sa == Gcad.eOk and attr is not None:
                    gcutPrintf("\n[a] mam atrybut, przed odczytem")
                    stara = ""
                    try:
                        stara = attr.textString()
                    except Exception as e:
                        gcutPrintf("\n[!] textString padl: %s" % str(e))
                    gcutPrintf("\n[b] odczyt OK (stara='%s'), przed setTextString" % stara)
                    attr.setTextString(stara)   # zapis TEJ SAMEJ wartosci — nieinwazyjne
                    gcutPrintf("\n[c] po setTextString")
                    attr.close()
                    gcutPrintf("\n[d] po attr.close()")
                    zrobione = True
                ref.close()
                gcutPrintf("\n[e] po ref.close()")
            except Exception as e:
                gcutPrintf("\n[X] wyjatek: %s: %s" % (type(e).__name__, str(e)))
                try:
                    ref.close()
                except Exception:
                    pass
                break
        gcutPrintf("\n[f] KONIEC komendy. Jesli GstarCAD zamknie sie PO tym markerze -> to sprzatanie/GC po zapisie.")

    except Exception as err:
        gcutPrintf("\n[TESTZAPIS BLAD] %s: %s" % (type(err).__name__, str(err)))
