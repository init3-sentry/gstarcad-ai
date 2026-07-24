# GSAI_WEKTORYZUJ (PROTOTYP) — skan rysunku -> polilinie w rysunku. CALOSC LOKALNIE.
#
# Po co: klienci maja skany starych map i rysunkow budynkow; przerysowywanie recznie
# zjada roboczogodziny. To pierwszy dowod, ze da sie to zrobic W CALOSCI na maszynie
# klienta — rysunek nie wychodzi nigdzie, zero chmury, zero RODO.
#
# WYMAGA (jednorazowo, wg wyniku #32):
#   "<sciezka>\python.exe" -m pip install numpy pillow
#   Sciezke poda GSAI_PYENV. numpy juz macie — dochodzi tylko pillow (~3 MB).
#
# Zaleznosci CELOWO ograniczone do numpy + Pillow (~16 MB). Bez scikit-image, bez
# OpenCV, bez scipy — te ciagna ~300 MB i u klienta zamienilyby sie w instalator,
# ktorego nikt nie postawi. Otsu i Zhang-Suen napisane wprost na numpy.
#
# Zwalidowane offline przed wyslaniem (MBP):
#   - moja szkieletyzacja vs scikit-image (wzorzec): zgodnosc 99,77-99,97%
#   - moj prog Otsu vs scikit-image: identyczny
#   - syntetyczny rzut 7 scian z szumem: 0,13 s, sciana 598 px -> 2 wierzcholki
#   - skan A1 @ 300 DPI (69 Mpx): 5,0 s
#
# Ograniczenia, o ktorych trzeba wiedziec:
#   - to CENTERLINE: kreska staje sie JEDNA linia wzdluz osi. Grubosc kreski GINIE.
#   - luki i okregi wychodza jako lamane (dopasowanie lukow to nastepny etap)
#   - tekst na rysunku zostanie potraktowany jak geometria (to normalne na tym etapie)
#   - kolor: obraz jest splaszczany do szarosci. Mapy kolorowe = osobny temat

from pygcad.core import *
from pygcad.core.runtime import *
from pygcad.pygrx import *
import os
import time

try:
    import numpy as np
except ImportError:
    np = None

def otsu(szary):
    """Prog Otsu — maksymalizacja wariancji miedzyklasowej. Czysty numpy."""
    hist = np.bincount(szary.ravel(), minlength=256).astype(np.float64)
    p = hist / hist.sum()
    omega = np.cumsum(p)                       # waga klasy tla
    mu = np.cumsum(p * np.arange(256))         # srednia narastajaca
    mu_t = mu[-1]
    with np.errstate(divide="ignore", invalid="ignore"):
        sigma_b = (mu_t * omega - mu) ** 2 / (omega * (1.0 - omega))
    sigma_b = np.nan_to_num(sigma_b)
    # POPRAWKA: obraz czysto bimodalny (0/255, bez poltonow) daje PLASKIE maksimum
    # wariancji dla progow 0..254 -> argmax bralby PIERWSZY (prog=0), a "szary < 0"
    # to pusta maska = zero linii (bug wykryty 2026-07-23 na czystym rzucie testowym).
    # Bierzemy SRODEK plateau maksimum -> dla bimodalnego wychodzi ~127. Dla obrazow
    # z poltonami (skany) plateau jest jednopunktowe, wiec zachowanie bez zmian.
    mx = sigma_b.max()
    idx = np.where(sigma_b >= mx - 1e-9)[0]
    return int(round(idx.mean()))


def _sasiedzi(bw):
    """Zwraca 8 sasiadow (P2..P9 wg Zhang-Suen) jako tablice bool, zgodnie w ruchu zegara.
    Kolejnosc: P2=N, P3=NE, P4=E, P5=SE, P6=S, P7=SW, P8=W, P9=NW."""
    p = np.zeros((8,) + bw.shape, dtype=bool)
    p[0][1:, :] = bw[:-1, :]        # P2 N
    p[1][1:, :-1] = bw[:-1, 1:]     # P3 NE
    p[2][:, :-1] = bw[:, 1:]        # P4 E
    p[3][:-1, :-1] = bw[1:, 1:]     # P5 SE
    p[4][:-1, :] = bw[1:, :]        # P6 S
    p[5][:-1, 1:] = bw[1:, :-1]     # P7 SW
    p[6][:, 1:] = bw[:, :-1]        # P8 W
    p[7][1:, 1:] = bw[:-1, :-1]     # P9 NW
    return p


def szkieletyzuj(bw, max_iter=100):
    """Zhang-Suen (Comm. ACM 1984) zwektoryzowany w numpy.

    Klasyczna implementacja idzie piksel po pikselu — tu kazda iteracja to kilkanascie
    operacji na calej tablicy, wiec koszt jest liniowy i liczony w milisekundach.
    Liczba iteracji ~ polowa grubosci kreski, wiec dla kreski 5 px to ~3 przebiegi.
    """
    bw = bw.astype(bool).copy()
    for _ in range(max_iter):
        zmiana = False
        for krok in (0, 1):
            p = _sasiedzi(bw)
            B = p.sum(axis=0)                       # liczba sasiadow-czarnych
            # A = liczba przejsc 0->1 w sekwencji P2..P9,P2 (obieg zgodny z zegarem)
            seq = np.concatenate([p, p[:1]], axis=0)
            A = ((~seq[:-1]) & seq[1:]).sum(axis=0)
            if krok == 0:
                c1 = (~p[0]) | (~p[2]) | (~p[4])    # P2*P4*P6 == 0
                c2 = (~p[2]) | (~p[4]) | (~p[6])    # P4*P6*P8 == 0
            else:
                c1 = (~p[0]) | (~p[2]) | (~p[6])    # P2*P4*P8 == 0
                c2 = (~p[0]) | (~p[4]) | (~p[6])    # P2*P6*P8 == 0
            usun = bw & (B >= 2) & (B <= 6) & (A == 1) & c1 & c2
            if usun.any():
                bw &= ~usun
                zmiana = True
        if not zmiana:
            break
    return bw


def otworz(bw, iteracje=1):
    """Otwarcie morfologiczne (erozja -> dylatacja) — usuwa drobny szum (despeckle).
    Bez scipy: erozja = AND wszystkich sasiadow, dylatacja = OR."""
    def eroduj(a):
        p = _sasiedzi(a)
        return a & p.all(axis=0)

    def dylatuj(a):
        p = _sasiedzi(a)
        return a | p.any(axis=0)

    for _ in range(iteracje):
        bw = eroduj(bw)
    for _ in range(iteracje):
        bw = dylatuj(bw)
    return bw


def _liczba_przejsc(szkielet):
    """Liczba przejsc 0->1 w pierscieniu 8 sasiadow (crossing number) dla kazdego piksela.

    TO, a nie liczba sasiadow, rozstrzyga czy piksel jest skrzyzowaniem:
      1 = koniec linii, 2 = zwykla sciezka, >=3 = prawdziwe rozgalezienie.

    Dlaczego to istotne: kazda linia, ktora nie jest pozioma ani pionowa, po
    szkieletyzacji staje sie SCHODKIEM, a piksel schodka ma TRZECH sasiadow — mimo ze
    to zwykla prosta sciezka. Liczenie sasiadow uznaje wiec kazdy zakret za skrzyzowanie
    i rwie krzywe na strzepy. Dwaj sasiedzi schodka lezą OBOK SIEBIE w pierscieniu, wiec
    daja JEDNO przejscie — i crossing number poprawnie mowi "sciezka".
    Wykryte na realnym skanie MPZP (Rafal, #33): syntetyczny test mial same sciany
    poziome i pionowe, wiec nigdy tego nie dotknal. Mapa to same krzywe -> tracer rwal
    granice stref na kawalki po ~79 px zamiast ciagnac cala krzywa."""
    p = _sasiedzi(szkielet)
    seq = np.concatenate([p, p[:1]], axis=0)          # P2..P9,P2 — pierscien domkniety
    return ((~seq[:-1]) & seq[1:]).sum(axis=0)


def trasuj(szkielet, min_dlugosc=8):
    """Szkielet -> lancuchy pikseli. Rozgalezienia urywaja lancuch, zeby skrzyzowania
    nie sklejaly wszystkiego w jednego weza."""
    H, W = szkielet.shape
    ys, xs = np.nonzero(szkielet)
    if len(ys) == 0:
        return []
    zbior = set(zip(ys.tolist(), xs.tolist()))
    # KOLEJNOSC MA ZNACZENIE: najpierw pion/poziom, dopiero potem ukosne.
    # Na schodku piksel ma sasiada "na skroty" (nastepny-nastepny po przekatnej).
    # Idac po surowej liscie tracer potrafi ten skrot wybrac i PRZESKOCZYC piksel,
    # co rwie krzywa i zostawia sieroty. Sasiad w pionie/poziomie to zawsze ten
    # wlasciwy nastepny krok. (Drugi blad z tej samej rodziny co crossing number —
    # oba widoczne dopiero na krzywych, nie na syntetycznych prostych scianach.)
    ruchy = [(-1, 0), (1, 0), (0, -1), (0, 1),          # 4-spojnosc — priorytet
             (-1, -1), (-1, 1), (1, -1), (1, 1)]        # ukosne — dopiero gdy nie ma innych

    def sasiedzi_pkt(q):
        y, x = q
        return [(y + dy, x + dx) for dy, dx in ruchy if (y + dy, x + dx) in zbior]

    # stopien liczony PRZEJSCIAMI, nie sasiadami — patrz _liczba_przejsc()
    przej = _liczba_przejsc(szkielet)
    stopien = {q: int(przej[q[0], q[1]]) for q in zbior}
    koncowki = [q for q, s in stopien.items() if s != 2]

    uzyte = set()
    lancuchy = []

    def idz(start, drugi):
        lan = [start, drugi]
        uzyte.add(frozenset((start, drugi)))
        biezacy, poprzedni = drugi, start
        while stopien.get(biezacy, 0) == 2:
            nast = [q for q in sasiedzi_pkt(biezacy) if q != poprzedni]
            if not nast:
                break
            krawedz = frozenset((biezacy, nast[0]))
            if krawedz in uzyte:
                break
            uzyte.add(krawedz)
            poprzedni, biezacy = biezacy, nast[0]
            lan.append(biezacy)
        return lan

    for q in koncowki:                       # od wezlow i koncow
        for s in sasiedzi_pkt(q):
            if frozenset((q, s)) not in uzyte:
                lancuchy.append(idz(q, s))
    for q in zbior:                          # petle zamkniete bez wezlow
        if stopien.get(q, 0) == 2:
            for s in sasiedzi_pkt(q):
                if frozenset((q, s)) not in uzyte:
                    lancuchy.append(idz(q, s))
    return [l for l in lancuchy if len(l) >= min_dlugosc]


def rdp(punkty, eps):
    """Ramer-Douglas-Peucker — upraszcza lancuch pikseli do wierzcholkow polilinii.
    Iteracyjnie (nie rekurencyjnie), zeby dlugi lancuch nie przepelnil stosu."""
    if len(punkty) < 3:
        return list(punkty)
    zostaw = np.zeros(len(punkty), dtype=bool)
    zostaw[0] = zostaw[-1] = True
    stos = [(0, len(punkty) - 1)]
    P = np.asarray(punkty, dtype=np.float64)
    while stos:
        i, j = stos.pop()
        if j <= i + 1:
            continue
        a, b = P[i], P[j]
        ab = b - a
        norma = np.hypot(*ab)
        seg = P[i + 1:j]
        if norma < 1e-9:
            d = np.hypot(*(seg - a).T)
        else:
            # iloczyn wektorowy 2D liczony wprost — np.cross dla wektorow 2D zostal
            # USUNIETY w numpy 2.0 (a klient ma 2.4.x), wiec nie ma do czego siegac
            v = seg - a
            d = np.abs(ab[0] * v[:, 1] - ab[1] * v[:, 0]) / norma   # odleglosc od cieciwy
        k = int(np.argmax(d))
        if d[k] > eps:
            k += i + 1
            zostaw[k] = True
            stos.append((i, k))
            stos.append((k, j))
    return [tuple(p) for p in P[zostaw]]


def _dlugosc_lamanej(p):
    """Suma dlugosci segmentow lamanej (w pikselach)."""
    s = 0.0
    for i in range(len(p) - 1):
        s += ((p[i + 1][0] - p[i][0]) ** 2 + (p[i + 1][1] - p[i][1]) ** 2) ** 0.5
    return s


def domknij_konce(polilinie, tol=14.0, max_klaster=3, min_dlugosc_linii=40.0):
    """Snapuje bliskie KONCE lancuchow do wspolnego punktu (centroid klastra).
    Zamyka szpary i ostrzy narozniki: szkielet urywa lancuch na wezle 1-2 px od sasiada
    i zaokragla rogi (ukos zamiast ostrego kata), wiec konce w rogu/skrzyzowaniu sa rozjechane.

    ZABEZPIECZENIA (empiryczne, po tescie na realnym skanie geodezyjnym 2026-07-24 — bez nich
    domykanie robilo promieniste "gwiazdy" na gestych punktach pomiarowych i zlewalo linie):
      - `min_dlugosc_linii` — w domykaniu bierze udzial TYLKO koniec dlugiej linii; krotkie
        lamane (opisy, cyfry, szum) sa pomijane, wiec sie nie zlewaja.
      - `max_klaster` — snapujemy tylko MALE skupiska koncow (rog/T/X = 2-3 konce); geste
        skupisko (>max_klaster) zostawiamy nietkniete, zeby nie robic gwiazdy.
      - `tol` umiarkowany (~pol grubosci kreski).
    Rusza TYLKO konce (nie srodkowe wierzcholki) i tylko skupiska 2..max_klaster."""
    if not polilinie:
        return polilinie
    konce = []                                   # [pl_idx, wierzch_idx, x, y]
    for i, pl in enumerate(polilinie):
        if len(pl) >= 2 and _dlugosc_lamanej(pl) >= min_dlugosc_linii:
            konce.append([i, 0, pl[0][0], pl[0][1]])
            konce.append([i, len(pl) - 1, pl[-1][0], pl[-1][1]])
    n = len(konce)
    parent = list(range(n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    t2 = tol * tol
    for a in range(n):
        for b in range(a + 1, n):
            dx = konce[a][2] - konce[b][2]
            dy = konce[a][3] - konce[b][3]
            if dx * dx + dy * dy <= t2:
                parent[find(a)] = find(b)

    grupy = {}
    for k in range(n):
        r = find(k)
        if r not in grupy:
            grupy[r] = []
        grupy[r].append(k)

    pl2 = [list(p) for p in polilinie]
    for _, idxs in grupy.items():
        if len(idxs) < 2 or len(idxs) > max_klaster:   # samotny lub geste skupisko — zostaw
            continue
        cx = sum(konce[k][2] for k in idxs) / len(idxs)
        cy = sum(konce[k][3] for k in idxs) / len(idxs)
        for k in idxs:
            pl2[konce[k][0]][konce[k][1]] = (cx, cy)

    # sprzataj zdegenerowane: usun kolejne identyczne wierzcholki, odrzuc polilinie < 2 pkt
    wynik = []
    for p in pl2:
        czysta = [p[0]]
        for v in p[1:]:
            if v != czysta[-1]:
                czysta.append(v)
        if len(czysta) >= 2:
            wynik.append([tuple(v) for v in czysta])
    return wynik


def wektoryzuj(szary, eps=1.5, despeckle=False, min_dlugosc=8, domykaj=True, tol_domk=14.0):
    """Obraz w skali szarosci (uint8) -> lista polilinii [(x, y), ...] w pikselach.
    UWAGA: zwraca x=kolumna, y=wiersz. Zamiana na uklad rysunku jest po stronie CAD.

    despeckle=False DOMYSLNIE — przemyslane, nie zaniedbanie.
    Otwarcie morfologiczne maska 3x3 NISZCZY CALKOWICIE kreske <=2 px, bo taka kreska
    nie ma ani jednego piksela z kompletem 8 sasiadow. ZMIERZONE: 1 px -> 0, 2 px -> 0,
    3 px -> caly. A <=2 px to linie wymiarowe, kreskowanie i wyblakle kreski starych
    rysunkow — czyli dokladnie to, po co to budujemy. Wykryte na podgladzie wizualnym:
    linia wymiarowa znikala z wyniku bez sladu w liczbach.
    Smieci odsiewa filtr min_dlugosc PO trasowaniu: plamka daje krotki lancuch i wypada.
    ZMIERZONE: 200 plam szumu -> 0 smieciowych polilinii, a kreski 1/2/4 px zachowane.
    despeckle=True zostawione dla skanow tak brudnych, ze inaczej sie nie da."""
    prog = otsu(szary)
    bw = szary < prog                       # kreska ciemna na jasnym papierze
    if despeckle:
        bw = otworz(bw, 1)
    szk = szkieletyzuj(bw)
    lancuchy = trasuj(szk, min_dlugosc=min_dlugosc)
    polilinie = []
    for lan in lancuchy:
        pkt = rdp([(x, y) for (y, x) in lan], eps)   # (wiersz,kol) -> (x,y)
        if len(pkt) >= 2:
            polilinie.append(pkt)
    if domykaj:                                       # zamknij szpary + ostrzej narozniki
        polilinie = domknij_konce(polilinie, tol=tol_domk)
    return polilinie, prog, int(szk.sum())


# ─────────────────────────────────────────────────────────────────────────────
# Komenda GstarCAD
# ─────────────────────────────────────────────────────────────────────────────
def _open_ms():
    db = gcdbWorkingDatabase()
    st, bt = db.getBlockTable(GcDb.kForRead)
    if st != Gcad.eOk:
        return None
    st, ms = bt.getAt(GCDB_MODEL_SPACE, GcDb.kForWrite)
    bt.close()
    return ms if st == Gcad.eOk else None


@command(local_name='GSAI_WEKTORYZUJ', global_name='GSAI_WEKTORYZUJ', group_name='GSAI')
def wektoryzuj_cmd():
    """Wskaz plik ze skanem -> polilinie w rysunku. Nic nie wychodzi z tego komputera."""
    try:
        if np is None:
            gcutPrintf("\n[WEKTOR] Brak numpy. Odpal GSAI_PYENV — poda gotowa komende pip.")
            return
        try:
            from PIL import Image
        except ImportError:
            gcutPrintf("\n[WEKTOR] Brak biblioteki Pillow. Odpal GSAI_PYENV po sciezke i wklej:")
            gcutPrintf("\n         \"<sciezka>\\python.exe\" -m pip install pillow")
            return

        rbf = resbuf()
        rc = gcedGetFileD("Wskaz skan do wektoryzacji", "", "png;jpg;jpeg;tif;tiff;bmp", 0, rbf)
        if rc != RTNORM:
            gcutPrintf("\nAnulowano.")
            return
        path = rbf.resval.rstring

        # gcedGetPoint przyjmuje punkt jako parametr WYJSCIOWY (nie zwraca krotki
        # jak gcedGetReal) — wzorzec zwalidowany na zywo w geoportal.py
        pt = GcGePoint3d()
        if gcedGetPoint(None, "\nWskaz lewy dolny naroznik wstawienia: ", pt) != RTNORM:
            gcutPrintf("\nAnulowano.")
            return

        # UWAGA: gcedGetReal NIE zwraca krotki. pygcad wystawia go jako
        #   (prompt: str, result: float) -> int
        # czyli z parametrem wyjsciowym, ktorego z Pythona nie da sie wypelnic
        # (float jest niezmienny). Wzorzec 02 w bibliotece uczy blednej formy
        #   status, radius = gcedGetReal(prompt)
        # i wlasnie na tym wywrocilo sie u Jakuba (#32, 2026-07-16).
        # Do czasu wyjasnienia: pytamy tekstem i parsujemy sami. Dziala pewnie.
        st, txt = gcedGetString(1, "\nSzerokosc rysunku w jednostkach (np. 10000 dla 10 m): ")
        if st != RTNORM or not txt or not txt.strip():
            gcutPrintf("\nAnulowano.")
            return
        try:
            szer = float(txt.strip().replace(",", "."))    # przecinek dziesietny PL
        except ValueError:
            gcutPrintf("\n[WEKTOR] '%s' to nie jest liczba. Anulowano." % txt)
            return
        if szer <= 0:
            gcutPrintf("\n[WEKTOR] Szerokosc musi byc dodatnia. Anulowano.")
            return

        gcutPrintf("\n[WEKTOR] Wczytuje obraz...")
        t0 = time.time()
        im = Image.open(path).convert("L")          # do skali szarosci
        szary = np.asarray(im, dtype=np.uint8)
        H, W = szary.shape
        gcutPrintf("\n[WEKTOR] %d x %d px (%.1f Mpx). Licze — to potrwa kilka sekund..."
                   % (W, H, W * H / 1e6))

        pol, prog, npix = wektoryzuj(szary, eps=1.5)
        dt = time.time() - t0
        if not pol:
            gcutPrintf("\n[WEKTOR] Nie znalazlem zadnych linii. Za jasny skan albo za duzo szumu?")
            return

        skala = float(szer) / float(W)               # jednostki rysunku na piksel
        x0, y0 = pt[0], pt[1]

        ms = _open_ms()
        if ms is None:
            gcutPrintf("\n[WEKTOR] Nie moge otworzyc przestrzeni modelu.")
            return
        # Model space ZAWSZE zamkniety — otwarta blokada zapisu wywraca program
        # przy autozapisie kilkanascie minut pozniej.
        ile = 0
        try:
            for linia in pol:
                pl = GcDbPolyline()
                try:
                    for i, (px, py) in enumerate(linia):
                        # obraz liczy wiersze z gory, CAD ma Y do gory -> odbicie
                        X = x0 + px * skala
                        Y = y0 + (H - py) * skala
                        pl.addVertexAt(i, GcGePoint2d(X, Y))
                    ms.appendGcDbEntity(pl)
                    ile += 1
                finally:
                    pl.close()
        finally:
            ms.close()

        wierz = sum(len(p) for p in pol)
        gcutPrintf("\n[WEKTOR] Gotowe w %.1f s." % dt)
        gcutPrintf("\n         Wstawiono %d polilinii, %d wierzcholkow." % (ile, wierz))
        gcutPrintf("\n         Prog jasnosci: %d | pikseli linii: %d (kompresja %.0f×)"
                   % (prog, npix, npix / max(1, wierz)))
        gcutPrintf("\n         Nic nie wyszlo z tego komputera — liczone lokalnie.")
        gcutPrintf("\n         Zrob ZOOM > Zakres (ZE), zeby zobaczyc.")

    except Exception as err:
        gcutPrintf("\n[WEKTOR BLAD] %s: %s" % (type(err).__name__, err))
