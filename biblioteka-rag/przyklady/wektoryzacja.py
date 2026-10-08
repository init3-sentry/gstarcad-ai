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
#   - adaptacyjne prostowanie: 3 realne skany klienta (survey/mapa/kataster), narzut ~0 s;
#     syntetyki: prosta-z-szumem 129->2 wierzch., nar, ostry; luk R=800 17->17 (NIE splaszcza)
#
# Ograniczenia, o ktorych trzeba wiedziec:
#   - to CENTERLINE: kreska staje sie JEDNA linia wzdluz osi. Grubosc kreski GINIE.
#   - luki i okregi wychodza jako lamane (dopasowanie lukow to nastepny etap)
#   - PROSTOWANIE (prostuj=True, domyslnie): rozpoznaje dlugie proste przebiegi mimo szumu i
#     splaszcza je do jednego odcinka; zakrety, luki i detal zostaja NIETKNIETE jak RDP(eps).
#     Na odrecznych skanach zysk jest umiarkowany (linie faluja u zrodla), na kreslonych
#     linijka/maszynowo — duzy. Wylaczenie: wektoryzuj(..., prostuj=False).
#   - tekst: OPCJA pomijaj_tekst (w komendzie pytanie [T/N], domyslnie N) wycina skupiska
#     opisow/cyfr, ZOSTAWIAJAC geometrie (krzyzyki/strzalki/znaczniki/linie/ramki). Lapie opisy
#     inline (tez OBROCONE), naglowki, TABELE i wieloliniowe AKAPITY (rozklad skupiska na
#     gesto-wypelnione wiersze). Zdegradowany druk OK. Pojedyncze, osamotnione etykiety moga
#     zostac (bezpieczny kierunek bledu). OCR = wersja 2.0 (osobny segment, decyzja — ADR 05).
#   - kolor: obraz jest splaszczany do szarosci. Mapy kolorowe = osobny temat
#   - PORZADKOWANIE (08.10, skan dachu Rafala #190): linie prawie poziome/pionowe -> dokladnie
#     H/V (tylko gdy przesuniecie <= 2 px, wiec ukosne granice map zostaja), domykanie rogow
#     przez PRZECIECIE linii (nie srodek ciezkosci — ten przekrzywial proste), sklejanie
#     kawalkow jednej prostej przecietej na skrzyzowaniu albo w wyblaklym miejscu (linie
#     kreskowe zostaja przerywane). Pomiar: produkt-i-badania/wektoryzacja-poprawki-2026-10-08.md
#     w gstarcad-ai-wewnetrzne.

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


# ─────────────────────────────────────────────────────────────────────────────
# Adaptacyjne prostowanie (wynik #32 — zbilansuj proste vs detal na NIEROWNYCH skanach)
#
# Problem: RDP ma jeden globalny prog. Podnosisz -> proste gladkie, ale gina detale.
# Obnizasz -> detale zyja, ale proste sa poszarpane. Jednym pokretlem nie da sie obu naraz.
# Globalne wygladzanie i prosty greedy zawiodly (marginalne albo psuly detal — 2026-07-24).
#
# Rozwiazanie wielo-skalowe: rozpoznaj, GDZIE linia jest lokalnie prosta MIMO szumu (prostuj),
# a gdzie realnie zakreca (zostaw detal). Klucz — residuum dopasowania prostej (TLS) liczone
# na SUROWYCH pikselach: szum na prostej ma male, znoszace sie odchylki (residuum NIE rosnie
# ze skala); prawdziwy zakret/luk -> residuum ROSNIE i przebieg sie urywa. Do rozroznienia
# "szum na prostej" vs "lagodny luk" usredniamy odchylke: szum wygasa, garb luku przetrwa.
#
# Wlasnosc bezpieczenstwa: ruszamy TYLKO to, co udowodnimy jako dluga prosta. Zakrety, luki,
# drobne symbole -> bit-w-bit jak RDP(eps). Zero ryzyka utraty detalu.
def _rdp_indices(P, eps):
    """Jak rdp(), ale zwraca POSORTOWANE indeksy zachowanych punktow w P (nie punkty).
    Potrzebne, zeby zmapowac wierzcholek na pozycje w gestym lancuchu."""
    n = len(P)
    if n < 3:
        return list(range(n))
    zostaw = np.zeros(n, dtype=bool)
    zostaw[0] = zostaw[-1] = True
    stos = [(0, n - 1)]
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
            v = seg - a
            d = np.abs(ab[0] * v[:, 1] - ab[1] * v[:, 0]) / norma
        k = int(np.argmax(d))
        if d[k] > eps:
            k += i + 1
            zostaw[k] = True
            stos.append((i, k))
            stos.append((k, j))
    return np.nonzero(zostaw)[0].tolist()


def _prefiksy(P):
    """Sumy prefiksowe x,y,xx,yy,xy (z wiodacym zerem) -> TLS na dowolnym zakresie w O(1)."""
    x = P[:, 0]
    y = P[:, 1]
    z = np.zeros(1)
    return {"x": np.concatenate([z, np.cumsum(x)]),
            "y": np.concatenate([z, np.cumsum(y)]),
            "xx": np.concatenate([z, np.cumsum(x * x)]),
            "yy": np.concatenate([z, np.cumsum(y * y)]),
            "xy": np.concatenate([z, np.cumsum(x * y)])}


def _tls_zakres(pref, i, j):
    """TLS (PCA) po pikselach [i..j] wlacznie z sum prefiksowych. O(1).
    Zwraca (cx,cy,dx,dy,rms_perp): centroid, kierunek jednostkowy, RMS odleglosci prostopadlej."""
    n = j - i + 1
    if n < 2:
        return None
    sx = pref["x"][j + 1] - pref["x"][i]
    sy = pref["y"][j + 1] - pref["y"][i]
    cx = sx / n
    cy = sy / n
    cxx = (pref["xx"][j + 1] - pref["xx"][i]) - n * cx * cx
    cyy = (pref["yy"][j + 1] - pref["yy"][i]) - n * cy * cy
    cxy = (pref["xy"][j + 1] - pref["xy"][i]) - n * cx * cy
    tr = cxx + cyy
    det = cxx * cyy - cxy * cxy
    disc = max(0.0, (0.5 * tr) ** 2 - det)
    s = disc ** 0.5
    l1 = 0.5 * tr + s        # wariancja WZDLUZ linii (wieksza)
    l2 = 0.5 * tr - s        # wariancja PROSTOPADLA (mniejsza) = residuum^2 * n
    if abs(cxy) > 1e-12:
        dx, dy = l1 - cyy, cxy
    else:
        dx, dy = (1.0, 0.0) if cxx >= cyy else (0.0, 1.0)
    nrm = (dx * dx + dy * dy) ** 0.5
    if nrm < 1e-12:
        dx, dy = 1.0, 0.0
    else:
        dx, dy = dx / nrm, dy / nrm
    return cx, cy, dx, dy, (max(0.0, l2) / n) ** 0.5


def _maxdev(P, i, j, cx, cy, dx, dy):
    """Maksymalna odleglosc PROSTOPADLA pikseli [i..j] od prostej (punkt c, kierunek d)."""
    seg = P[i:j + 1]
    return float(np.abs((seg[:, 0] - cx) * dy - (seg[:, 1] - cy) * dx).max())


def _prosta_a_nie_luk(P, i, j, lin, flat_abs=1.3, okno=9):
    """Czy [i..j] to PROSTA z szumem (splaszczyc) czy realny LUK (zostawic detal)?
    Rozdzielamy skladowa strukturalna (nisko-czest.) od szumu (wysoko-czest.) w odchylce
    prostopadlej: szum usredniamy oknem -> gasnie; garb luku przetrwa usrednienie.
    Splaszczam, gdy po wygladzeniu max |odchylka| <= flat_abs (garbu nie ma -> to byl szum)."""
    cx, cy, dx, dy = lin
    seg = P[i:j + 1]
    s = (seg[:, 0] - cx) * dy - (seg[:, 1] - cy) * dx      # signed perp = vx*dy - vy*dx
    m = len(s)
    if m < 3:
        return True
    k = min(okno, m if m % 2 else m - 1)
    if k < 3:
        return float(np.abs(s).max()) <= flat_abs
    gl = np.convolve(s, np.ones(k) / k, mode="valid")
    return float(np.abs(gl).max()) <= flat_abs


def _przeciecie(l1, l2):
    """Punkt przeciecia dwoch prostych (cx,cy,dx,dy). None gdy prawie rownolegle."""
    cx1, cy1, dx1, dy1 = l1
    cx2, cy2, dx2, dy2 = l2
    den = dx1 * dy2 - dy1 * dx2
    if abs(den) < 1e-6:
        return None
    t = ((cx2 - cx1) * dy2 - (cy2 - cy1) * dx2) / den
    return (cx1 + t * dx1, cy1 + t * dy1)


def _rzut(px, py, lin):
    """Rzut prostopadly punktu (px,py) na prosta lin=(cx,cy,dx,dy)."""
    cx, cy, dx, dy = lin
    t = (px - cx) * dx + (py - cy) * dy
    return (cx + t * dx, cy + t * dy)


def prostuj_lancuch(chain_xy, eps=1.5, tol=2.5, min_prosta=25.0, min_wierzch=3):
    """Adaptacyjne prostowanie POJEDYNCZEGO lancucha (gesta lista pikseli (x,y)) -> polilinia.
      1. RDP(eps) daje wierzcholki bazowe (detale zachowane 1:1 jak dotad).
      2. Rosniemy maksymalne "proste przebiegi": zakres pikseli dopasowywalny JEDNA prosta (TLS)
         z RMS <= tol i maxdev <= 1.6*tol. Luk -> residuum rosnie -> przebieg sie urywa.
      3. Dlugi prosty przebieg (>= min_prosta px, wchlonal >= min_wierzch wierzch. RDP i przeszedl
         test prosta-nie-luk) -> JEDEN odcinek = rzut na dopasowana prosta (znika poszarpanie).
         Krotki/zakrzywiony -> wierzcholki RDP NIETKNIETE (detal zyje).
      4. Narozniki: dwie proste -> wspolny wierzcholek = ICH PRZECIECIE (ostry rog)."""
    if len(chain_xy) < 4:
        return [tuple(map(float, p)) for p in chain_xy]
    P = np.asarray(chain_xy, dtype=np.float64)
    idx = _rdp_indices(P, eps)
    if len(idx) < 3:
        return [tuple(P[k]) for k in idx]
    pref = _prefiksy(P)

    def arclen(i, j):
        d = np.diff(P[i:j + 1], axis=0)
        return float(np.hypot(d[:, 0], d[:, 1]).sum())

    tol_max = 1.6 * tol
    runs = []                                            # (i_pocz, i_kon, 'prosta'/'detal', lin|None)
    v = 0
    while v < len(idx) - 1:
        a = idx[v]
        w = v + 1
        best = None
        while w < len(idx):
            b = idx[w]
            lin = _tls_zakres(pref, a, b)
            if lin is None:
                break
            cx, cy, dx, dy, rms = lin
            if rms <= tol and _maxdev(P, a, b, cx, cy, dx, dy) <= tol_max:
                best = (w, (cx, cy, dx, dy))
                w += 1
            else:
                break
        prosta = (best is not None
                  and (best[0] - v) >= min_wierzch
                  and arclen(a, idx[best[0]]) >= min_prosta
                  and _prosta_a_nie_luk(P, a, idx[best[0]], best[1]))
        if prosta:
            runs.append((a, idx[best[0]], "prosta", best[1]))
            v = best[0]
        else:
            runs.append((a, idx[v + 1], "detal", None))
            v += 1

    m = len(runs)
    bv = [None] * (m + 1)

    def linia(k):
        return runs[k][3] if runs[k][2] == "prosta" else None

    l0 = linia(0)
    bv[0] = _rzut(P[runs[0][0], 0], P[runs[0][0], 1], l0) if l0 else tuple(P[runs[0][0]])
    lN = linia(m - 1)
    bv[m] = _rzut(P[runs[-1][1], 0], P[runs[-1][1], 1], lN) if lN else tuple(P[runs[-1][1]])
    for k in range(1, m):
        lp, ln = linia(k - 1), linia(k)
        gi = runs[k][0]
        gp = (float(P[gi, 0]), float(P[gi, 1]))
        if lp and ln:
            pkt = _przeciecie(lp, ln)
            bv[k] = pkt if pkt is not None else _rzut(gp[0], gp[1], lp)
        elif lp:
            bv[k] = _rzut(gp[0], gp[1], lp)
        elif ln:
            bv[k] = _rzut(gp[0], gp[1], ln)
        else:
            bv[k] = gp

    out = [bv[0]]
    for k in range(m):
        if bv[k + 1] != out[-1]:
            out.append(bv[k + 1])
    return out


def _dlugosc_lamanej(p):
    """Suma dlugosci segmentow lamanej (w pikselach)."""
    s = 0.0
    for i in range(len(p) - 1):
        s += ((p[i + 1][0] - p[i][0]) ** 2 + (p[i + 1][1] - p[i][1]) ** 2) ** 0.5
    return s


def _kierunek_konca(pl, wierzch):
    """Kierunek odcinka koncowego polilinii, skierowany NA ZEWNATRZ (od wnetrza do konca),
    plus jego dlugosc. wierzch = 0 (poczatek) albo len(pl)-1 (koniec)."""
    if wierzch == 0:
        a, b = pl[1], pl[0]
    else:
        a, b = pl[-2], pl[-1]
    dx, dy = b[0] - a[0], b[1] - a[1]
    l = (dx * dx + dy * dy) ** 0.5
    if l < 1e-9:
        return None, 0.0
    return (dx / l, dy / l), l


def _sklej_bliskie(punkty, promien):
    """Union-find punktow (x, y) blizszych niz promien. Siatka komorek zamiast O(n^2) —
    na skanie 300 dpi koncow sa tysiace. Zwraca liste grup (listy indeksow)."""
    from collections import defaultdict
    n = len(punkty)
    parent = list(range(n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    kom = defaultdict(list)
    for k, (x, y) in enumerate(punkty):
        kom[(int(x // promien), int(y // promien))].append(k)
    r2 = promien * promien
    for (cx, cy), lst in kom.items():
        sas = []
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                sas += kom.get((cx + ddx, cy + ddy), [])
        for a in lst:
            for b in sas:
                if b <= a:
                    continue
                dx = punkty[a][0] - punkty[b][0]
                dy = punkty[a][1] - punkty[b][1]
                if dx * dx + dy * dy <= r2:
                    parent[find(a)] = find(b)
    grupy = defaultdict(list)
    for k in range(n):
        grupy[find(k)].append(k)
    return list(grupy.values())


def domknij_konce(polilinie, tol=14.0, max_klaster=3, min_dlugosc_linii=40.0, max_skret_deg=4.0):
    """Snapuje bliskie KONCE lancuchow do wspolnego punktu.
    Zamyka szpary i ostrzy narozniki: szkielet urywa lancuch na wezle 1-2 px od sasiada
    i zaokragla rogi (ukos zamiast ostrego kata), wiec konce w rogu/skrzyzowaniu sa rozjechane.

    PUNKT DOCELOWY (zmiana 08.10, skan dachu Rafala #190): przeciecie linii koncowych
    metoda najmniejszych kwadratow, NIE srodek ciezkosci koncow. Srodek ciezkosci przesuwal
    koniec dlugiej prostej w bok o kilka px i ja PRZEKRZYWIAL (na dachu: dolna krawedz
    swietlika i pion osi wychodzily ukosem przez pol swietlika). Przeciecie lezy NA obu
    liniach, wiec rog jest ostry, a linie zostaja proste.
      - same rownolegle konce (kat < 15 st.) -> nie ma rogu, nic nie ruszamy
        (przerwe w JEDNEJ prostej skleja polacz_wspolliniowe()).
      - punkt dalej niz tol od ktoregos konca -> nic nie ruszamy.
      - koniec dlugiej linii (>= 3*tol), ktora skrecilaby o wiecej niz max_skret_deg -> zostaje.

    ZABEZPIECZENIA z 2026-07-24 (bez nich domykanie robilo promieniste "gwiazdy" na gestych
    punktach pomiarowych i zlewalo linie) zostaja:
      - `min_dlugosc_linii` — w domykaniu bierze udzial TYLKO koniec dlugiej linii; krotkie
        lamane (opisy, cyfry, szum) sa pomijane, wiec sie nie zlewaja.
      - `max_klaster` — snapujemy tylko MALE skupiska koncow (rog/T/X = 2-3 konce); geste
        skupisko (>max_klaster) zostawiamy nietkniete, zeby nie robic gwiazdy.
    Rusza TYLKO konce (nie srodkowe wierzcholki)."""
    if not polilinie:
        return polilinie
    konce = []                                   # [pl_idx, wierzch_idx, x, y]
    for i, pl in enumerate(polilinie):
        if len(pl) >= 2 and _dlugosc_lamanej(pl) >= min_dlugosc_linii:
            konce.append([i, 0, pl[0][0], pl[0][1]])
            konce.append([i, len(pl) - 1, pl[-1][0], pl[-1][1]])

    pl2 = [list(p) for p in polilinie]
    prog_kata = 1.0 - np.cos(np.radians(15.0))   # min. wartosc wlasna = linie nierownolegle
    max_skret = np.radians(max_skret_deg)
    for idxs in _sklej_bliskie([(k[2], k[3]) for k in konce], tol):
        if len(idxs) < 2 or len(idxs) > max_klaster:   # samotny lub geste skupisko — zostaw
            continue
        # punkt najblizszy wszystkim liniom koncowym: sum(I - d d^T) p = sum(I - d d^T) e
        A = np.zeros((2, 2))
        bb = np.zeros(2)
        linie = []
        for k in idxs:
            pi, vi, x, y = konce[k]
            d, l = _kierunek_konca(polilinie[pi], vi)
            if d is None:
                linie = []
                break
            Pm = np.eye(2) - np.outer(d, d)
            A += Pm
            bb += Pm @ np.array([x, y])
            linie.append((k, d, l))
        if not linie or np.linalg.eigvalsh(A)[0] < prog_kata:
            continue
        cel = np.linalg.solve(A, bb)
        if any(np.hypot(cel[0] - konce[k][2], cel[1] - konce[k][3]) > tol for k in idxs):
            continue
        for k, d, l in linie:
            pi, vi = konce[k][0], konce[k][1]
            pl = polilinie[pi]
            sasiad = pl[1] if vi == 0 else pl[-2]
            nx, ny = cel[0] - sasiad[0], cel[1] - sasiad[1]
            nl = (nx * nx + ny * ny) ** 0.5
            if nl < 1e-9:
                continue
            kat = np.arccos(max(-1.0, min(1.0, (nx * d[0] + ny * d[1]) / nl)))
            if l >= 3.0 * tol and kat > max_skret:
                continue                          # przekrzywiloby dluga prosta — zostaw
            pl2[pi][vi] = (float(cel[0]), float(cel[1]))

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


# ─────────────────────────────────────────────────────────────────────────────
# Porzadkowanie geometrii (08.10, skan dachu Rafala #190 + #33)
#
# Po trasowaniu linia ze skanu jest "prawie" pozioma (0,1-0,3 st. szumu), sciany i ramki
# porwane na skrzyzowaniach (szkielet tnie lancuch na kazdym wezle) i w miejscach, gdzie
# kreska na skanie wyblakla. W CAD to boli: ORTO nie trzyma, prostokat to 4-8 kawalkow,
# a uzytkownik i tak musi to sam sklejac.
def prostuj_do_osi(polilinie, tol_deg=1.5, min_odc=12.0, max_przes=2.0):
    """Odcinki prawie poziome/pionowe -> DOKLADNIE poziome/pionowe.
    Ciag kolejnych odcinkow H dostaje wspolne Y (srednia wazona dlugoscia), V -> wspolne X.
    Wierzcholek miedzy H i V bierze Y z H i X z V -> naroznik dokladnie 90 st.

    BEZPIECZNIK max_przes: prostujemy tylko wtedy, gdy zaden wierzcholek nie przesunie sie
    o wiecej niz max_przes px. Szum skanu na prostej to ulamki piksela-2 px; prawdziwa
    granica dzialki pod katem 1 st. na 500 px to ~9 px — zostaje nietknieta (mapy!)."""
    tg = np.tan(np.radians(tol_deg))
    wynik = []
    for p in polilinie:
        p = [list(v) for v in p]
        typ = []
        for a, b in zip(p[:-1], p[1:]):
            dx, dy = abs(b[0] - a[0]), abs(b[1] - a[1])
            l = (dx * dx + dy * dy) ** 0.5
            if l >= min_odc and dy <= tg * dx:
                typ.append("H")
            elif l >= min_odc and dx <= tg * dy:
                typ.append("V")
            else:
                typ.append(None)
        i = 0
        while i < len(typ):
            t = typ[i]
            if t is None:
                i += 1
                continue
            j = i
            while j + 1 < len(typ) and typ[j + 1] == t:
                j += 1
            os_ = 1 if t == "H" else 0          # H -> wspolne Y (indeks 1), V -> wspolne X (0)
            sw = 0.0
            sl = 0.0
            for k in range(i, j + 1):
                a, b = p[k], p[k + 1]
                l = ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5
                sw += l * (a[os_] + b[os_]) / 2.0
                sl += l
            m = sw / sl
            if max(abs(p[k][os_] - m) for k in range(i, j + 2)) <= max_przes:
                for k in range(i, j + 2):
                    p[k][os_] = m
            i = j + 1
        wynik.append([tuple(v) for v in p])
    return wynik


def usun_wspolliniowe(p, tol_px=0.75):
    """Usuwa wierzcholki lezace na prostej miedzy sasiadami (odchylka <= tol_px, bez zawracania).
    Po sklejeniu dwoch kawalkow jednej prostej w miejscu szwu zostaja 2 zbedne wierzcholki."""
    if len(p) < 3:
        return p
    out = [p[0]]
    for k in range(1, len(p) - 1):
        a, v, b = out[-1], p[k], p[k + 1]
        abx, aby = b[0] - a[0], b[1] - a[1]
        n = (abx * abx + aby * aby) ** 0.5
        if n > 1e-9:
            d = abs(abx * (v[1] - a[1]) - aby * (v[0] - a[0])) / n
            t = ((v[0] - a[0]) * abx + (v[1] - a[1]) * aby) / (n * n)
            if d <= tol_px and 0.0 < t < 1.0:
                continue
        out.append(v)
    out.append(p[-1])
    return out


def polacz_wspolliniowe(polilinie, max_szpara=14.0, frakcja=0.25, min_szpara=3.0,
                        tol_kat_deg=3.0, tol_bok=2.0, min_odc=10.0):
    """Skleja polilinie, ktore sa kawalkami JEDNEJ prostej: przerwa w wyblaklej kresce,
    skrzyzowanie X/T przeciete przez szkielet. Warunki: konce naprzeciw siebie, kierunki
    zgodne (<= tol_kat_deg), przesuniecie boczne <= tol_bok px, a szpara
        <= min(max_szpara, max(min_szpara, frakcja * krotszy odcinek koncowy)).
    FRAKCJA chroni linie KRESKOWE i OSIOWE: kreska 40 px z przerwa 15 px nie spelnia
    15 <= 0,25*40, wiec zostaje przerywana. max_szpara chroni otwory (drzwi) w scianach."""
    from collections import defaultdict
    konce = []                                   # (pl, koniec 0/1, x, y, ux, uy, dl)
    for i, p in enumerate(polilinie):
        if len(p) < 2:
            continue
        for kon in (0, 1):
            d, l = _kierunek_konca(p, 0 if kon == 0 else len(p) - 1)
            if d is None or l < min_odc:
                continue
            v = p[0] if kon == 0 else p[-1]
            konce.append((i, kon, v[0], v[1], d[0], d[1], l))
    cos_t = np.cos(np.radians(tol_kat_deg))
    kom = defaultdict(list)
    for k, e in enumerate(konce):
        kom[(int(e[2] // max_szpara), int(e[3] // max_szpara))].append(k)
    pary = []
    for k, e in enumerate(konce):
        cx, cy = int(e[2] // max_szpara), int(e[3] // max_szpara)
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                for m in kom.get((cx + ddx, cy + ddy), []):
                    if m <= k:
                        continue
                    f = konce[m]
                    if f[0] == e[0]:
                        continue
                    if e[4] * f[4] + e[5] * f[5] > -cos_t:      # musza patrzec na siebie
                        continue
                    vx, vy = f[2] - e[2], f[3] - e[3]
                    wzdl = vx * e[4] + vy * e[5]
                    if wzdl < -1.0:
                        continue
                    if abs(vx * e[5] - vy * e[4]) > tol_bok or abs(vx * f[5] - vy * f[4]) > tol_bok:
                        continue
                    szp = (vx * vx + vy * vy) ** 0.5
                    lim = min(max_szpara, max(min_szpara, frakcja * min(e[6], f[6])))
                    if szp <= lim:
                        pary.append((szp, k, m))
    pary.sort()
    lacz = {}                                    # (pl, koniec) -> (pl, koniec)
    for _, k, m in pary:
        a = (konce[k][0], konce[k][1])
        b = (konce[m][0], konce[m][1])
        if a in lacz or b in lacz:
            continue
        lacz[a] = b
        lacz[b] = a

    uzyte = set()
    wynik = []
    for i in range(len(polilinie)):
        if i in uzyte:
            continue
        # cofnij sie do poczatku lancucha (wolnego konca); petla zamknieta -> start gdziekolwiek
        pl, we = i, 0
        widziane = {i}
        while (pl, we) in lacz:
            npl, nk = lacz[(pl, we)]
            if npl in widziane:
                break
            widziane.add(npl)
            pl, we = npl, 1 - nk
        out = []
        while pl not in uzyte:                   # idz do przodu, wchodzac koncem `we`
            uzyte.add(pl)
            p = polilinie[pl]
            out.extend(p if we == 0 else list(reversed(p)))
            nast = lacz.get((pl, 1 - we))
            if nast is None:
                break
            pl, we = nast
        if not out:
            continue
        czysta = [out[0]]
        for v in out[1:]:
            if v != czysta[-1]:
                czysta.append(v)
        if len(czysta) >= 2:
            wynik.append(usun_wspolliniowe([tuple(v) for v in czysta]))
    return wynik


# ─────────────────────────────────────────────────────────────────────────────
# Oddzielanie tekstu od linii — OPCJA (pomijaj_tekst), BEZ OCR (OCR = wersja 2.0, decyzja Dawida)
#
# Kryteria Jakuba (#32): ZOSTAJE geometria — linie, krzyzyki punktow, strzalki, znaczniki
# geodezyjne, drobne symbole; POMIJAMY tylko skupiska cyfr/opisow (numery, wartosci, etykiety).
#
# Metoda: skladowe spojne (CC) ORYGINALU (nie rozmazanego — bo tekst na skanie czesto DOTYKA
# linii i rozmazanie zlepiloby je z siatka linii). Znaki to CC wielkosci litery, skupiaja sie
# w slowa. Klasyfikacja po SKUPISKU: wiele glifow wielkosci znaku ulozonych w CIENKIE PASMO
# (wiersz, dowolny kat) -> TEKST. Krzyzyk/strzalka/pojedynczy znacznik oraz kreskowany krzyzyk
# (rozpada sie na kropki mniejsze od znaku) -> ZOSTAJE. Odpornosc na zdegradowany DRUK: dolny
# prog glifu niski, a przed zlepkiem chroni ksztalt skupiska (PCA) + wymog realnej wysokosci znaku.
#
# STAN: dziala na inline-owych opisach/cyfrach (tez obroconych). ZNANE LUKI (nastepna iteracja):
# tekst w komorkach TABEL i wieloliniowe AKAPITY czesto zostaja (glify dotykaja ramek / blok 2D
# jest swiadomie omijany, zeby nie ruszyc pol znacznikow). Domyslnie WYLACZONE.
def _etykietuj_cc(bw):
    """Skladowe spojne (8-spojnosc) — scanline union-find na pikselach maski. Czysty numpy+py.
    Zwraca (lab HxW int32, liczba_CC). 0 = tlo."""
    H, W = bw.shape
    idx = np.full((H, W), -1, dtype=np.int64)
    ink = np.flatnonzero(bw)
    idx.flat[ink] = np.arange(len(ink))
    K = len(ink)
    if K == 0:
        return np.zeros((H, W), dtype=np.int32), 0
    parent = np.arange(K, dtype=np.int64)

    def find(a):
        root = a
        while parent[root] != root:
            root = parent[root]
        while parent[a] != root:
            parent[a], a = root, parent[a]
        return root

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    a = idx[:, :]
    pary = []                                       # krawedzie do juz-odwiedzonych sasiadow: W,N,NW,NE
    m = (a[:, 1:] >= 0) & (a[:, :-1] >= 0); pary.append((a[:, 1:][m], a[:, :-1][m]))
    m = (a[1:, :] >= 0) & (a[:-1, :] >= 0); pary.append((a[1:, :][m], a[:-1, :][m]))
    m = (a[1:, 1:] >= 0) & (a[:-1, :-1] >= 0); pary.append((a[1:, 1:][m], a[:-1, :-1][m]))
    m = (a[1:, :-1] >= 0) & (a[:-1, 1:] >= 0); pary.append((a[1:, :-1][m], a[:-1, 1:][m]))
    for u, v in pary:
        for p, q in zip(u.tolist(), v.tolist()):
            union(p, q)

    root = np.array([find(i) for i in range(K)], dtype=np.int64)
    uniq, inv = np.unique(root, return_inverse=True)
    lab = np.zeros((H, W), dtype=np.int32)
    lab.flat[ink] = inv.astype(np.int32) + 1
    return lab, len(uniq)


def _staty_cc(lab, ncc):
    """Per-CC: area, bbox, srodek, wys, szer, przekatna."""
    H, W = lab.shape
    ys, xs = np.nonzero(lab)
    ids = lab[ys, xs] - 1
    area = np.bincount(ids, minlength=ncc)
    rmin = np.full(ncc, H, np.int32); rmax = np.zeros(ncc, np.int32)
    cmin = np.full(ncc, W, np.int32); cmax = np.zeros(ncc, np.int32)
    np.minimum.at(rmin, ids, ys); np.maximum.at(rmax, ids, ys)
    np.minimum.at(cmin, ids, xs); np.maximum.at(cmax, ids, xs)
    h = (rmax - rmin + 1).astype(np.float64)
    w = (cmax - cmin + 1).astype(np.float64)
    return dict(area=area, h=h, w=w, cy=(rmin + rmax) / 2.0, cx=(cmin + cmax) / 2.0,
                diag=np.hypot(h, w))


def maska_tekstu(bw, glif_px=None, min_glifow=3, promien_k=None):
    """Maska bool (HxW) pikseli uznanych za TEKST (do usuniecia). Patrz naglowek sekcji.
    glif_px auto = min(H,W)/90; promien_k auto = 2.2*glif_px (odstepy w slowie)."""
    from collections import defaultdict
    H, W = bw.shape
    if glif_px is None:
        glif_px = max(8.0, min(H, W) / 90.0)
    if promien_k is None:
        promien_k = 2.2 * glif_px

    lab, ncc = _etykietuj_cc(bw)
    if ncc == 0:
        return np.zeros((H, W), dtype=bool)
    s = _staty_cc(lab, ncc)

    # kandydat na glif: skladowa wielkosci znaku. Dolny prog niski (fragmenty degradacji),
    # przed kropka/kreska chroni pozniej ksztalt skupiska + wymog realnej wysokosci znaku.
    wyp = s["area"] / np.maximum(1.0, s["h"] * s["w"])
    glif = ((s["h"] <= 1.25 * glif_px) & (s["w"] <= 1.25 * glif_px)
            & (s["diag"] <= 1.8 * glif_px)
            & (s["h"] >= 0.22 * glif_px) & (s["w"] >= 0.12 * glif_px)
            & (s["area"] >= max(8.0, 0.04 * glif_px * glif_px))
            & (wyp <= 0.93))
    gi = np.flatnonzero(glif)
    if len(gi) < min_glifow:
        return np.zeros((H, W), dtype=bool)

    cx = s["cx"][gi]; cy = s["cy"][gi]; gh = s["h"][gi]
    gx = np.floor(cx / promien_k).astype(np.int64)
    gyy = np.floor(cy / promien_k).astype(np.int64)
    komorki = defaultdict(list)
    for k in range(len(gi)):
        komorki[(gyy[k], gx[k])].append(k)

    par = list(range(len(gi)))
    def f(a):
        while par[a] != a:
            par[a] = par[par[a]]; a = par[a]
        return a
    r2 = promien_k * promien_k
    for (yy, xx), lst in komorki.items():
        sas = []
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                sas += komorki.get((yy + dy, xx + dx), [])
        for a in lst:
            for b in sas:
                if b <= a:
                    continue
                if (cx[a]-cx[b])**2 + (cy[a]-cy[b])**2 <= r2:
                    ra, rb = f(a), f(b)
                    if ra != rb:
                        par[max(ra, rb)] = min(ra, rb)

    grupy = defaultdict(list)
    for k in range(len(gi)):
        grupy[f(k)].append(k)

    def geste_wiersze(czl):
        """Rozklad skupiska 2D na poziome WIERSZE; zwraca glify z wierszy GESTO wypelnionych
        znakami (tabela/akapit). Rzadki wiersz (pole znacznikow) odpada -> geometria zostaje."""
        order = czl[np.argsort(cy[czl])]
        pasma = []; cur = [order[0]]
        for k in order[1:]:
            if cy[k] - cy[cur[-1]] <= 0.7 * glif_px:    # ta sama linia bazowa
                cur.append(k)
            else:
                pasma.append(cur); cur = [k]
        pasma.append(cur)
        out = []
        for b in pasma:
            b = np.array(b)
            if len(b) < min_glifow or gh[b].max() < 0.5 * glif_px:
                continue
            gaps = np.diff(np.sort(cx[b]))
            if len(gaps) and np.median(gaps) <= 1.8 * glif_px:   # gesto upakowany wiersz = tekst
                out.append(b)
        return out

    tekst_cc = []
    for _, czl in grupy.items():
        if len(czl) < min_glifow:
            continue
        czl = np.array(czl)
        if gh[czl].max() < 0.5 * glif_px:               # same drobinki (kropki krzyzyka) -> nie tekst
            continue
        # ksztalt skupiska (PCA srodkow). Cienkie PASMO pod dowolnym katem -> tekst (inline, obrocone).
        px = cx[czl]; py = cy[czl]
        mx = px.mean(); my = py.mean()
        dxx = float(((px-mx)**2).mean()); dyy = float(((py-my)**2).mean())
        dxy = float(((px-mx)*(py-my)).mean())
        tr = dxx + dyy; det = dxx*dyy - dxy*dxy
        disc = max(0.0, (0.5*tr)**2 - det) ** 0.5
        minor = max(0.0, 0.5*tr - disc) ** 0.5
        major = max(0.0, 0.5*tr + disc) ** 0.5
        if minor <= 1.3 * glif_px and major <= 60.0 * glif_px:
            for k in czl:
                tekst_cc.append(int(gi[k]))
        else:
            # skupisko 2D (tabela / akapit / pole): tnij na wiersze, bierz tylko GESTE
            for b in geste_wiersze(czl):
                for k in b:
                    tekst_cc.append(int(gi[k]))

    if not tekst_cc:
        return np.zeros((H, W), dtype=bool)
    czy = np.zeros(ncc + 1, dtype=bool)
    czy[np.array(tekst_cc) + 1] = True
    return czy[lab]


def wektoryzuj(szary, eps=1.5, despeckle=False, min_dlugosc=8, domykaj=True, tol_domk=14.0,
               prostuj=True, tol_prost=2.5, min_prosta=25.0, pomijaj_tekst=False,
               do_osi=True, laczenie=True):
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
    despeckle=True zostawione dla skanow tak brudnych, ze inaczej sie nie da.

    do_osi / laczenie (08.10, #190/#33): prostowanie prawie-poziomych/pionowych do osi
    i sklejanie porwanych kawalkow jednej prostej. Wylaczenie: do_osi=False, laczenie=False
    (wtedy wynik jak przed 08.10, poza poprawionym domykaniem)."""
    prog = otsu(szary)
    bw = szary < prog                       # kreska ciemna na jasnym papierze
    if pomijaj_tekst:                        # OPCJA: wywal skupiska opisow/cyfr (geometria zostaje)
        bw = bw & ~maska_tekstu(bw)
    if despeckle:
        bw = otworz(bw, 1)
    szk = szkieletyzuj(bw)
    lancuchy = trasuj(szk, min_dlugosc=min_dlugosc)
    polilinie = []
    for lan in lancuchy:
        ch = [(x, y) for (y, x) in lan]              # (wiersz,kol) -> (x,y)
        if prostuj:                                  # adaptacyjne prostowanie (proste vs detal)
            pkt = prostuj_lancuch(ch, eps=eps, tol=tol_prost, min_prosta=min_prosta)
        else:
            pkt = rdp(ch, eps)
        if len(pkt) >= 2:
            polilinie.append(pkt)
    if do_osi:                                        # prawie H/V -> dokladnie H/V
        polilinie = prostuj_do_osi(polilinie)
    if domykaj:                                       # zamknij szpary + ostrzej narozniki
        polilinie = domknij_konce(polilinie, tol=tol_domk)
    if laczenie:                                      # sklej kawalki jednej prostej
        polilinie = polacz_wspolliniowe(polilinie, max_szpara=tol_domk)
    if do_osi:                                        # szwy po sklejeniu -> jeszcze raz
        polilinie = prostuj_do_osi(polilinie)
        polilinie = [usun_wspolliniowe(p) for p in polilinie]
        polilinie = prostuj_do_osi(polilinie)
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

        # OPCJA (retest #32): pomijanie skupisk opisow/cyfr. Domyslnie NIE — geometria 1:1.
        # T = sprobuj wyciac tekst (krzyzyki/linie/znaczniki zostaja). Prototyp: tabele i
        # akapity moga zostac. Prostowanie linii jest ZAWSZE wlaczone, niezaleznie od tego.
        pomijaj = False
        st, tt = gcedGetString(1, "\nPomijac skupiska opisow/cyfr? [T/N] <N>: ")
        if st == RTNORM and tt and tt.strip().lower() in ("t", "tak", "y", "yes"):
            pomijaj = True

        gcutPrintf("\n[WEKTOR] Wczytuje obraz...")
        t0 = time.time()
        im = Image.open(path).convert("L")          # do skali szarosci
        szary = np.asarray(im, dtype=np.uint8)
        H, W = szary.shape
        gcutPrintf("\n[WEKTOR] %d x %d px (%.1f Mpx)%s. Licze — to potrwa kilka sekund..."
                   % (W, H, W * H / 1e6, " | pomijam tekst" if pomijaj else ""))

        pol, prog, npix = wektoryzuj(szary, eps=1.5, pomijaj_tekst=pomijaj)
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
