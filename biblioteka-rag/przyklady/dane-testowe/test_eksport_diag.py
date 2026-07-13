# DIAGNOSTYKA — dlaczego EKSPORT_ATRYBUTOW zwraca 0 na rysunku z atrybutami.
# Raport chłopaków (30993 New_Block): plik MA 47 atrybutów (potwierdzone skanem: blok
# „METKA ZEWN", tagi NR./POW./POK z wartościami), a narzędzie wyeksportowało 0.
# Ta komenda pokazuje KAŻDY etap BEZ połykania błędów, żeby zlokalizować przyczynę:
#   1) ile encji w model space i jakich klas (czy w ogóle widzimy bloki?)
#   2) ile block references (i pod jaką nazwą klasy — Ac/Gc)
#   3) per blok: attributeIterator() działa? ile atrybutów? jaki wyjątek?
#
# Użycie: otwórz rysunek z blokami-atrybutami (np. 30993) → APPLOAD → EKSPORT_DIAG.
# Skopiuj CAŁY wynik z konsoli i odeślij.
from pygcad.core.runtime import *
from pygcad.pygrx import *


@command(local_name='EKSPORT_DIAG')
def eksport_diag():
    try:
        gcutPrintf("\n=== DIAGNOSTYKA EKSPORTU ATRYBUTOW ===")
        db = gcdbWorkingDatabase()
        s, bt = db.getBlockTable(GcDb.kForRead)
        gcutPrintf("\ngetBlockTable rc=%s" % str(s))
        s, ms = bt.getAt(GCDB_MODEL_SPACE, GcDb.kForRead)
        bt.close()
        if s != Gcad.eOk:
            gcutPrintf("\nBLAD getAt(MODEL) rc=%s" % str(s)); return
        s, it = ms.newIterator()
        it.start()

        klasy = {}
        blockrefs = []
        total = 0
        while not it.done():
            s, ent = it.getEntity()
            if s == Gcad.eOk and ent is not None:
                total += 1
                try:
                    nm = ent.isA().name()
                except Exception as e:
                    nm = "?" + type(e).__name__
                klasy[nm] = klasy.get(nm, 0) + 1
                if "BlockReference" in str(nm):
                    blockrefs.append(ent.objectId())
                ent.close()
            it.step()
        ms.close()

        gcutPrintf("\nEncji w model space: %d" % total)
        gcutPrintf("\nKlasy (top):")
        for k, v in sorted(klasy.items(), key=lambda x: -x[1])[:12]:
            gcutPrintf("\n   %-30s %d" % (k, v))
        gcutPrintf("\nBlock references wykryte: %d" % len(blockrefs))

        total_attr = 0
        for i, oid in enumerate(blockrefs):
            s, ref = gcdbOpenObject(oid, GcDb.kForRead)
            if s != Gcad.eOk or ref is None:
                if i < 10:
                    gcutPrintf("\n  [ref %d] open rc=%s" % (i, str(s)))
                continue
            bname = "?"
            try:
                sr, rec = gcdbOpenObject(ref.blockTableRecord(), GcDb.kForRead)
                if sr == Gcad.eOk and rec is not None:
                    sn, bname = rec.getName()
                    rec.close()
            except Exception as e:
                bname = "?" + type(e).__name__

            cnt = 0
            err = None
            try:
                ait = ref.attributeIterator()
                while not ait.done():
                    aid = ait.objectId()
                    sa, attr = ref.openAttribute(aid, GcDb.kForRead)
                    if sa == Gcad.eOk and attr is not None:
                        cnt += 1
                        if i < 3 and cnt <= 3:
                            try:
                                tg = attr.tag()
                            except Exception as e2:
                                tg = "?" + type(e2).__name__
                            gcutPrintf("\n       tag=%s" % repr(tg))
                        attr.close()
                    else:
                        if i < 3:
                            gcutPrintf("\n       openAttribute rc=%s" % str(sa))
                    ait.step()
            except Exception as e:
                err = "%s: %s" % (type(e).__name__, str(e))
            total_attr += cnt
            if i < 10:
                gcutPrintf("\n  [ref %d] blok=%-16s attr=%d %s" % (i, bname, cnt, ("| WYJATEK: " + err) if err else ""))
            ref.close()

        gcutPrintf("\n=== RAZEM atrybutow: %d ===" % total_attr)
        gcutPrintf("\nCzytanie: block-refs=0 -> nie wykrywamy blokow (klasa inna?).")
        gcutPrintf("\n  bloki sa, ale attr=0 + WYJATEK -> attributeIterator/openAttribute nie dziala na tej wersji.")
        gcutPrintf("\n  bloki sa, attr=0 bez wyjatku -> attributeIterator zwraca puste (moze inny mechanizm atrybutow).")
        gcutPrintf("\n  attr>0 -> odczyt dziala; problem w innym miejscu eksportu.")

    except Exception as err:
        gcutPrintf("\n[EKSPORT_DIAG BLAD] %s: %s" % (type(err).__name__, str(err)))
