# GSAI_PRZEDMIAR — przedmiar: pole + obwod wskazanych obiektow -> CSV (otwiera sie w Excelu).
#
# Kandydat na platny "rodzynek" (research popytu 2026-07-22/23, 3 zrodla + Reddit r/AutoCAD).
#
# NATIVE-CHECK (protokol par.4): GstarCAD MA AREATABLE / CAOT_AUTOXLSTABLE / DATAEXTRACTION,
#   ale ciezkie/wieloklikowe. Luka = PROSTE jednoklikowe "zaznacz -> gotowy CSV + suma".
#
# WERSJA v2 (2026-07-27) — 5 poprawek Roberta (robert#6):
#   1. numeracja w rysunku zgodna z Lp w CSV (etykieta przy obiekcie),
#   2. auto-numer pliku (nie nadpisuje poprzedniego dokumentu),
#   3. wynik w m / m2 mimo rysowania w cm (przelicznik jednostki),
#   4. Excel/CSV sam sie otwiera po zapisie,
#   5. kolorowanie: policzone -> szary, NIEpoliczone (rozbite/otwarte) -> czerwony (QA wzrokowe).
#   Punkty 1 i 5 MODYFIKUJA rysunek -> OPCJA [T/N], domyslnie N (zachowanie read-only jak v1).
#   API zweryfikowane w stubach 2026-07-27 (getGeomExtents/GcDbText 2-arg/setColorIndex/getPointAtDist).
#
# WERSJA v2.1 (2026-07-29) — UX: jednostka + numery/kolor w JEDNYM oknie (idiom _panel z geoportalu:
#   tk.StringVar/IntVar + Radiobutton/Checkbutton + OK/Anuluj, fallback na linie polecen). Dwa pytania
#   z linii polecen -> jedno okno + Anuluj (ktorego dotad nie bylo). Sciezka CSV zostaje na natywnym
#   "Zapisz jako". Zero nowego API (czysty tkinter stdlib), nie tyka encji -> BUG-10-safe.
#
# WYJSCIE: CSV (utf-8-sig, separator ";", przecinek dziesietny) — polski Excel czyta z polskimi znakami.
# Uzycie: APPLOAD, komenda GSAI_PRZEDMIAR.
# STATUS v2: API zweryfikowane offline; warstwa zapisu (numery/kolor) = pierwsza walidacja zespolu.

from pygcad.core.runtime import *
from pygcad.pygrx import *
import os

_TYPY_PL = {
    "Polyline": "Polilinia", "Polyline2d": "Polilinia", "2dPolyline": "Polilinia",
    "Line": "Linia", "Circle": "Okrąg", "Arc": "Łuk", "Ellipse": "Elipsa",
    "Spline": "Splajn", "Region": "Region", "Hatch": "Kreskowanie",
    "Face": "Powierzchnia 3D", "Solid": "Bryła", "Solid3d": "Bryła 3D",
    "MText": "Tekst wielowierszowy", "Text": "Tekst", "BlockReference": "Blok",
}

# przeliczniki jednostki rysunku -> METRY (dlugosc) i METRY KWADRATOWE (pole)
_JEDNOSTKI = {
    "mm": (1000.0, 1000000.0),
    "cm": (100.0, 10000.0),
    "m": (1.0, 1.0),
}


def _nazwa_typu(ent):
    t = type(ent).__name__
    if t.startswith("GcDb"):
        t = t[4:]
    return _TYPY_PL.get(t, t)


def _obwod(entity):
    """Obwod BEZ .cast(). Regiony maja getPerimeter(); krzywe getEndParam/getDistAtParam; fallback length()."""
    try:
        st, p = entity.getPerimeter()
        if st == Gcad.eOk:
            return p
    except (AttributeError, TypeError):
        pass
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
    """Pole obiektu. None gdy otwarty/nieobslugiwany. Region bez getArea (BUG-09) -> None -> UWAGA BOUNDARY."""
    try:
        st, a = entity.getArea()
        if st == Gcad.eOk:
            return a
    except (AttributeError, TypeError):
        pass
    return None


def _srodek(entity):
    """Srodek obwiedni obiektu (do numeracji). Zwraca (x,y,z) albo None."""
    try:
        ext = GcDbExtents()
        if entity.getGeomExtents(ext) == Gcad.eOk:
            mn = ext.minPoint()
            mx = ext.maxPoint()
            return ((mn[0] + mx[0]) / 2.0, (mn[1] + mx[1]) / 2.0, (mn[2] + mx[2]) / 2.0), (mn, mx)
    except (AttributeError, TypeError):
        pass
    return None, None


def _wolna_sciezka(p):
    """Poprawka #2: jesli plik istnieje -> nastepny wolny _NNN (nie nadpisuje poprzedniego dokumentu)."""
    if not os.path.exists(p):
        return p
    baza, ext = os.path.splitext(p)
    i = 1
    while i < 1000:
        kand = "%s_%03d%s" % (baza, i, ext)
        if not os.path.exists(kand):
            return kand
        i += 1
    return p


def _wybierz_plik_csv():
    """Natywne okno 'Zapisz jako' (tkinter, stdlib). Zwraca sciezke / '' (anulowano) / None (okno niedostepne)."""
    try:
        import tkinter as tk
        from tkinter import filedialog
    except Exception:
        return None
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        pulpit = os.path.join(os.path.expanduser("~"), "Desktop")
        if not os.path.isdir(pulpit):
            pulpit = os.path.expanduser("~")
        p = filedialog.asksaveasfilename(
            title="Zapisz przedmiar jako", defaultextension=".csv",
            initialfile="przedmiar.csv", initialdir=pulpit,
            filetypes=[("Plik CSV", "*.csv"), ("Wszystkie pliki", "*.*")])
        root.destroy()
        return p
    except Exception:
        return None


def _pytaj_jednostke():
    """Poprawka #3: jednostka rysunku -> przelicznik na m/m2. Domyslnie cm (rysunki architektoniczne)."""
    st, txt = gcedGetString(0, "\nW jakiej jednostce rysujecie? [mm/cm/m] <cm>: ")
    j = (txt or "").strip().lower() if st == RTNORM else ""
    if j not in _JEDNOSTKI:
        j = "cm"
    return j, _JEDNOSTKI[j]


def _panel_opcje():
    """Jedno okno: jednostka rysunku (radio) + numery/kolor (checkbox) + OK/Anuluj.
    Zwraca dict {ok, jednostka, adnotuj}. Fallback na linie polecen gdy tkinter niedostepny.
    Wzorzec: _panel() z geoportal.py (sprawdzony na LC). Zero API pygcad w oknie -> BUG-10-safe."""
    try:
        import tkinter as tk
        res = {"ok": False, "jednostka": "cm", "adnotuj": False}
        root = tk.Tk()
        root.title("GSAI Przedmiar")
        try:
            root.attributes("-topmost", True)
        except Exception:
            pass
        vj = tk.StringVar(value="cm")
        va = tk.IntVar(value=0)
        tk.Label(root, text="Jednostka rysunku (wynik zawsze w m / m2):",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=12, pady=(12, 4))
        fr_j = tk.Frame(root)
        fr_j.pack(anchor="w", padx=18)
        for kod, opis in (("mm", "milimetry"), ("cm", "centymetry"), ("m", "metry")):
            tk.Radiobutton(fr_j, text="%s  (%s)" % (kod, opis), variable=vj, value=kod).pack(anchor="w")
        tk.Label(root, text="Zapis do rysunku:",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=12, pady=(10, 4))
        tk.Checkbutton(root, text="Wstaw numery + koloruj (policzone=szary, niepoliczone=czerwony)",
                       variable=va).pack(anchor="w", padx=18)
        tk.Label(root, text="Domyslnie rysunek nietkniety (tylko CSV). Cofniesz jednym Undo.",
                 fg="#666").pack(anchor="w", padx=18, pady=(0, 4))

        def _ok():
            res["ok"] = True
            res["jednostka"] = vj.get()
            res["adnotuj"] = bool(va.get())
            root.destroy()

        fr = tk.Frame(root)
        fr.pack(pady=12, padx=12)
        tk.Button(fr, text="OK", width=10, command=_ok).pack(side="left", padx=6)
        tk.Button(fr, text="Anuluj", width=10, command=root.destroy).pack(side="left", padx=6)
        root.update()
        root.mainloop()
        return res
    except Exception as ex:
        gcutPrintf("\n[Panel] tkinter niedostepny (%s) — pytania z linii polecen." % type(ex).__name__)
        jedn, _ = _pytaj_jednostke()
        adn = False
        st, tt = gcedGetString(0, "\nWstawic numery i zaznaczyc kolorem policzone/niepoliczone? [T/N] <N>: ")
        if st == RTNORM and (tt or "").strip().lower() in ("t", "tak", "y", "yes"):
            adn = True
        return {"ok": True, "jednostka": jedn, "adnotuj": adn}


def _open_ms_write():
    db = gcdbWorkingDatabase()
    st, bt = db.getBlockTable(GcDb.kForRead)
    if st != Gcad.eOk:
        return None
    st, ms = bt.getAt(GCDB_MODEL_SPACE, GcDb.kForWrite)
    bt.close()
    return ms if st == Gcad.eOk else None


@command(local_name='GSAI_PRZEDMIAR')
def przedmiar():
    """Zaznacz obiekty -> CSV (pole, obwod, suma) w m/m2 + opcjonalnie numery i kolor w rysunku."""
    try:
        gcutPrintf("\nWskaz zamkniete obiekty (polilinie/okregi/regiony/kreskowania), zakoncz Enter-em.")
        sset = gds_name()
        gcedSSGet(None, None, None, None, sset)

        status, length = gcedSSLength(sset)
        if status != RTNORM or length <= 0:
            gcedSSFree(sset)
            gcutPrintf("\nNic nie wybrano. Operacja anulowana.")
            return

        # v2.1: jednostka + adnotacja w jednym oknie (idiom _panel), Anuluj konczy komende.
        opcje = _panel_opcje()
        if not opcje.get("ok"):
            gcedSSFree(sset)
            gcutPrintf("\nAnulowano.")
            return
        jedn = opcje.get("jednostka") if opcje.get("jednostka") in _JEDNOSTKI else "cm"
        dziel_dl, dziel_pole = _JEDNOSTKI[jedn]
        adnotuj = bool(opcje.get("adnotuj"))

        # sciezka pliku (okno tkinter -> fallback linia polecen)
        _pulpit = os.path.join(os.path.expanduser("~"), "Desktop")
        if not os.path.isdir(_pulpit):
            _pulpit = os.path.expanduser("~")
        _domyslny = os.path.join(_pulpit, "przedmiar.csv")
        sciezka = _wybierz_plik_csv()
        if sciezka == "":
            gcedSSFree(sset)
            gcutPrintf("\nAnulowano (zamknieto okno zapisu).")
            return
        if sciezka is None:
            status, sciezka = gcedGetString(1, "\nSciezka pliku CSV <%s>: " % _domyslny)
            if status != RTNORM:
                gcedSSFree(sset)
                gcutPrintf("\nAnulowano.")
                return
            sciezka = (sciezka or "").strip() or _domyslny
        sciezka_final = _wolna_sciezka(sciezka)   # poprawka #2: nie nadpisuj poprzedniego

        wiersze = []
        adnot = []            # (index_w_sset, czy_policzony, lp_lub_None, srodek_lub_None)
        sumaPola = 0.0
        sumaObw = 0.0
        liczone = 0
        pominiete = 0
        pominiete_typy = {}
        gmin = [None, None]   # obwiednia calej selekcji (do wysokosci tekstu)
        gmax = [None, None]

        entName = gds_name()
        entId = GcDbObjectId()

        for i in range(length):
            czy_policzony = False
            lp_biez = None
            srodek = None
            try:
                gcedSSName(sset, i, entName)
                gcdbGetObjectId(entId, entName)
                st, ent = gcdbOpenGcDbEntity(entId, GcDb.kForRead, False)
                if st != Gcad.eOk or ent is None:
                    pominiete += 1
                    adnot.append((i, False, None, None))
                    continue
                try:
                    pole = _pole(ent)
                    obw = _obwod(ent)
                    typ = _nazwa_typu(ent)
                    srodek, mnmx = _srodek(ent)
                    if mnmx is not None:
                        mn, mx = mnmx
                        for k in (0, 1):
                            gmin[k] = mn[k] if gmin[k] is None else min(gmin[k], mn[k])
                            gmax[k] = mx[k] if gmax[k] is None else max(gmax[k], mx[k])
                    try:
                        warstwa = ent.layer()
                    except Exception:
                        warstwa = ""
                finally:
                    ent.close()
                if pole is None:
                    pominiete += 1
                    pominiete_typy[typ] = pominiete_typy.get(typ, 0) + 1
                    adnot.append((i, False, None, None))
                    continue
                sumaPola += pole
                if obw is not None:
                    sumaObw += obw
                liczone += 1
                lp_biez = liczone
                czy_policzony = True
                wiersze.append((liczone, warstwa, typ, pole / dziel_pole, (obw / dziel_dl) if obw is not None else 0.0))
            except Exception as itemErr:
                pominiete += 1
                gcutPrintf("\nPominieto obiekt %d: %s" % (i, itemErr))
            adnot.append((i, czy_policzony, lp_biez, srodek))

        if liczone == 0:
            gcedSSFree(sset)
            gcutPrintf("\nZaden obiekt nie mial odczytywalnego pola. Anulowano.")
            if pominiete_typy:
                opis = ", ".join("%s x%d" % (t, c) for t, c in pominiete_typy.items())
                gcutPrintf("\nTypy bez odczytu pola przez API: %s" % opis)
                gcutPrintf("\n(Region: pygcad nie udostepnia pola bez castu — zamien na polilinie komenda BOUNDARY.)")
            return

        # CSV w pamieci PRZED otwarciem pliku (ochrona przed truncate przy bledzie formatowania)
        def n(x):
            return ("%.4f" % x).replace(".", ",")

        linie = ["Lp;Warstwa;Typ;Obszar [m2];Długość (Obwód) [m]"]
        for lp, w, t, p, o in wiersze:
            linie.append("%d;%s;%s;%s;%s" % (lp, w, t, n(p), n(o)))
        linie.append("SUMA;;;%s;%s" % (n(sumaPola / dziel_pole), n(sumaObw / dziel_dl)))
        dane = ("\r\n".join(linie) + "\r\n").encode("utf-8-sig")

        with open(sciezka_final, "wb") as f:
            f.write(dane)

        # Poprawka #1/#5: wpisz numery + kolory do rysunku (opcja). Model space i encje ZAWSZE w try/finally.
        wpisano_num = 0
        if adnotuj:
            # wysokosc tekstu z obwiedni selekcji (dziala i dla cm, i dla m)
            if gmin[0] is not None and gmax[0] is not None:
                przekatna = ((gmax[0] - gmin[0]) ** 2 + (gmax[1] - gmin[1]) ** 2) ** 0.5
                h = przekatna / 120.0
            else:
                h = 0.0
            if h <= 0:
                h = 2.5
            ms = _open_ms_write()
            if ms is None:
                gcutPrintf("\n[UWAGA] Nie moge otworzyc przestrzeni modelu — pomijam numery/kolor, CSV zapisany.")
            else:
                try:
                    eName = gds_name()
                    eId = GcDbObjectId()
                    for (i, czy_pol, lp_a, srodek) in adnot:
                        # kolor: policzone = szary (8), niepoliczone = czerwony (1)
                        try:
                            gcedSSName(sset, i, eName)
                            gcdbGetObjectId(eId, eName)
                            st, e2 = gcdbOpenGcDbEntity(eId, GcDb.kForWrite, False)
                            if st == Gcad.eOk and e2 is not None:
                                try:
                                    e2.setColorIndex(8 if czy_pol else 1)
                                finally:
                                    e2.close()
                        except Exception:
                            pass
                        # numer tylko dla policzonych, w srodku obwiedni
                        if czy_pol and lp_a is not None and srodek is not None:
                            try:
                                pkt = GcGePoint3d(srodek[0], srodek[1], srodek[2])
                                txt = GcDbText(pkt, str(lp_a))
                                try:
                                    txt.setHeight(h)
                                    ms.appendGcDbEntity(txt)
                                    wpisano_num += 1
                                finally:
                                    txt.close()
                            except Exception:
                                pass
                finally:
                    ms.close()

        gcedSSFree(sset)

        gcutPrintf("\n=== PRZEDMIAR ===")
        gcutPrintf("\nJednostka rysunku: %s -> wynik w m / m2" % jedn)
        gcutPrintf("\nObiektow policzono: %d   (pominieto bez pola/blad: %d)" % (liczone, pominiete))
        if pominiete_typy:
            opis = ", ".join("%s x%d" % (t, c) for t, c in pominiete_typy.items())
            gcutPrintf("\nBez odczytu pola przez API (np. Region -> BOUNDARY): %s" % opis)
        gcutPrintf("\nSuma pola: %s m2   Suma obwodu: %s m" % (n(sumaPola / dziel_pole), n(sumaObw / dziel_dl)))
        if adnotuj:
            gcutPrintf("\nRysunek: wpisano %d numerow; policzone=szary(8), niepoliczone=czerwony(1). Cofniesz jednym Undo." % wpisano_num)
        if sciezka_final != sciezka:
            gcutPrintf("\nPlik istnial — zapisano jako: %s" % sciezka_final)
        else:
            gcutPrintf("\nZapisano CSV: %s" % sciezka_final)

        # Poprawka #4: otworz plik w domyslnym programie (Excel).
        try:
            os.startfile(sciezka_final)
        except Exception:
            pass

    except Exception as err:
        gcutPrintf("\n[GSAI_PRZEDMIAR BLAD] %s: %s" % (type(err).__name__, err))
