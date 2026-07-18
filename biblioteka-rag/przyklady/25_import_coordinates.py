# Wzorcowa komenda 25 — Import współrzędnych z pliku → punkty w rysunku.
#
# Zamyka pozycję #8 z raportu Roberta („jest eksport współrzędnych, brakuje importu").
# Klasyka geodezyjna: masz plik z numerami i współrzędnymi punktów (z tachimetru,
# z Excela, z Notatnika) i chcesz je wrzucić do rysunku jako PUNKTY (GcDbPoint —
# łapią się osnapem WĘZeł/NODe), każdy z opisem numeru.
#
# REALIA PL (świadomie obsłużone):
#   - Excel PL eksportuje CSV separatorem ŚREDNIK, a przecinek to znak dziesiętny
#     (np. "1;5600123,45;7400987,10"). Notatnik zwykle spacja/tab. Obsługujemy oba:
#     separator = średnik/tab jeśli obecny, inaczej białe znaki; przecinek dziesiętny
#     zamieniany na kropkę PRZY parsowaniu liczby.
#   - PLIK EXCELA MIMO ROZSZERZENIA .csv/.txt — realny przypadek z testów (Tomasz,
#     2026-07-16): plik nazwany „.csv" był w środku skoroszytem .xlsx, a parser
#     tekstowy widział binarny ZIP i zgłaszał „zero poprawnych wierszy". Dlatego typ
#     pliku rozpoznajemy po ZAWARTOŚCI (pierwsze bajty), nie po rozszerzeniu, i .xlsx
#     czytamy wprost (zipfile + re — biblioteka standardowa, zero zależności).
#   - KOLEJNOŚĆ OSI. W geodezji X = północ, Y = wschód. W CAD odwrotnie: x = wschód,
#     y = północ. Plik z tachimetru wstawiony wprost daje rysunek OBRÓCONY. Nie
#     zgadujemy: przeliczamy oba warianty na szerokość/długość i sprawdzamy, który
#     wypada w Polsce (i w pasie swojej strefy). Gdy oba są sensowne — PYTAMY
#     użytkownika, zamiast wybierać po cichu (PL-1992 jest tak niejednoznaczny
#     z natury: obie osie tego samego rzędu, brak struktury stref).
#   - Współrzędne geodezyjne PL (PUWG2000) są rzędu milionów → wysokość opisu i
#     odsunięcie liczone są DYNAMICZNIE z rozpiętości punktów (2% przekątnej), a nie
#     stałą wartością — inaczej tekst byłby niewidoczny albo gigantyczny.
#   - Punkty w CAD są domyślnie niewidoczne (PDMODE=0 = kropka 1px). Best-effort
#     ustawiamy PDMODE=3 (krzyżyk X — klasyczny punkt geodezyjny, czysto) i
#     PDSIZE=-2 (2% ekranu), żeby było je widać.
#   - Wadliwy wiersz NIGDY nie przerywa importu — jest pomijany z podaniem powodu.
#
# Format pliku NIE jest pytaniem — rozpoznajemy go z zawartości (patrz _wykryj_format):
#   XY     : "X Y"            (numer nadawany automatycznie 1,2,3…)
#   XYZ    : "X Y Z"
#   NrXY   : "Nr X Y"         (pierwsza kolumna = numer/nazwa punktu)
#   NrXYZ  : "Nr X Y Z"
# Komenda ZAWSZE mówi, co rozpoznała i co zrobiła z wysokością Z. Pyta wyłącznie
# wtedy, gdy dane są naprawdę dwuznaczne — i wtedy pyta o jedną konkretną rzecz
# („czym jest pierwsza kolumna?"), pokazując przykładowy wiersz, a nie o nazwę formatu.
#
# Sposób użycia: APPLOAD tego pliku → komenda GSAI_IMPORTXYZ → wybierz plik w oknie
# (przeglądasz katalogi, klikasz plik) → punkty i opisy pojawią się w rysunku →
# wpisz ZOOM, potem A (Wszystko) albo E (Zakres), żeby je zobaczyć.
# UWAGA: opcji „Granice/G" ZOOM nie ma.
#
# Konwencje domu: 3 importy, @command, całość w try/except, Gcad.eOk dla bazy /
# RTNORM dla wejścia edytora, model space open→append→close, GcDbText(pt, str).

# @KATALOG
# nazwa: Import współrzędnych
# komenda: GSAI_IMPORTXYZ
# komenda_en: GSAI_IMPORTXYZ
# branza: geodezja
# opis: Wskazujesz plik z Excela lub Notatnika ze współrzędnymi punktów, a one lądują w rysunku jako punkty z opisami numerów. Rozpoznaje układ współrzędnych i prostuje kolejność osi. Koniec ręcznego wstawiania punkt po punkcie.
# przyklad: Wczytanie 300 punktów pomiarowych z pliku od geodety.

from pygcad.core import *
from pygcad.core.runtime import *
from pygcad.pygrx import *
import re
import os
import math
import time
import zipfile


# ─────────────────────────────────────────────────────────────────────────────
# Układy współrzędnych PL — szereg Krügera na GRS80 (własna matematyka, zero
# zależności; zweryfikowana: 16 000 punktów, 4 strefy, odchyłka 0.000000 m
# względem pyproj). Ten sam kod pracuje w narzędziu geoportalowym.
# ─────────────────────────────────────────────────────────────────────────────
_A_GRS80 = 6378137.0
_F_GRS80 = 1.0 / 298.257222101

# srid: (południk środkowy, skala k0, fałszywy wschód FE, fałszywa północ FN)
_UKLADY = {
    2176: (15.0, 0.999923, 5500000.0, 0.0),
    2177: (18.0, 0.999923, 6500000.0, 0.0),
    2178: (21.0, 0.999923, 7500000.0, 0.0),
    2179: (24.0, 0.999923, 8500000.0, 0.0),
    2180: (19.0, 0.9993, 500000.0, -5300000.0),
}


def _wspolczynniki():
    """Współczynniki szeregu Krügera dla GRS80 (rząd 6 — zapas dokładności)."""
    n = _F_GRS80 / (2.0 - _F_GRS80)
    n2, n3, n4, n5, n6 = n * n, n ** 3, n ** 4, n ** 5, n ** 6
    A = _A_GRS80 / (1.0 + n) * (1.0 + n2 / 4.0 + n4 / 64.0 + n6 / 256.0)
    beta = [
        n / 2.0 - 2.0 * n2 / 3.0 + 37.0 * n3 / 96.0 - n4 / 360.0 - 81.0 * n5 / 512.0,
        n2 / 48.0 + n3 / 15.0 - 437.0 * n4 / 1440.0 + 46.0 * n5 / 105.0,
        17.0 * n3 / 480.0 - 37.0 * n4 / 840.0 - 209.0 * n5 / 4480.0,
        4397.0 * n4 / 161280.0 - 11.0 * n5 / 504.0,
        4583.0 * n5 / 161280.0,
    ]
    delta = [
        2.0 * n - 2.0 * n2 / 3.0 - 2.0 * n3 + 116.0 * n4 / 45.0 + 26.0 * n5 / 45.0,
        7.0 * n2 / 3.0 - 8.0 * n3 / 5.0 - 227.0 * n4 / 45.0 + 2704.0 * n5 / 315.0,
        56.0 * n3 / 15.0 - 136.0 * n4 / 35.0 - 1262.0 * n5 / 105.0,
        4279.0 * n4 / 630.0 - 332.0 * n5 / 35.0,
        4174.0 * n5 / 315.0,
    ]
    return A, beta, delta


_A_K, _BETA, _DELTA = _wspolczynniki()


def _do_geo(E, N, srid):
    """Współrzędne płaskie układu → (szerokość, długość) w radianach."""
    lon0, k0, FE, FN = _UKLADY[srid]
    xi = (N - FN) / (k0 * _A_K)
    eta = (E - FE) / (k0 * _A_K)
    xi_p, eta_p = xi, eta
    for j in range(1, 6):
        b = _BETA[j - 1]
        xi_p -= b * math.sin(2.0 * j * xi) * math.cosh(2.0 * j * eta)
        eta_p -= b * math.cos(2.0 * j * xi) * math.sinh(2.0 * j * eta)
    chi = math.asin(max(-1.0, min(1.0, math.sin(xi_p) / math.cosh(eta_p))))
    lat = chi
    for j in range(1, 6):
        lat += _DELTA[j - 1] * math.sin(2.0 * j * chi)
    lon = math.radians(lon0) + math.atan2(math.sinh(eta_p), math.cos(xi_p))
    return lat, lon


_PL_LAT = (48.9, 55.0)
_PL_LON = (13.9, 24.3)


def _sensowny(E, N, srid):
    """Czy (E,N) to wiarygodny punkt w tym układzie: w Polsce ORAZ w pasie swojej strefy.
    Sam test „w Polsce" NIE wystarcza — strefa 5 i PL-1992 mają zakresy osi, które się
    nakładają, więc zamienione współrzędne też trafiają w kraj (sprawdzone empirycznie)."""
    lon0, k0, FE, FN = _UKLADY[srid]
    if srid != 2180 and abs(E - FE) > 120000.0:      # strefa PL-2000 to ±1.5° ≈ ±107 km
        return False
    try:
        lat, lon = _do_geo(E, N, srid)
    except (ValueError, OverflowError, ZeroDivisionError):
        return False
    la, lo = math.degrees(lat), math.degrees(lon)
    if not (_PL_LAT[0] <= la <= _PL_LAT[1] and _PL_LON[0] <= lo <= _PL_LON[1]):
        return False
    if srid != 2180 and abs(lo - lon0) > 1.6:
        return False
    return True


def _uklad_nazwa(srid):
    return {2176: "PL-2000 str.5 (EPSG:2176)", 2177: "PL-2000 str.6 (EPSG:2177)",
            2178: "PL-2000 str.7 (EPSG:2178)", 2179: "PL-2000 str.8 (EPSG:2179)",
            2180: "PL-1992 (EPSG:2180)"}.get(srid, "EPSG:%s" % srid)


def _wykryj_uklad(pary):
    """pary = [(kol1, kol2), …] surowe kolumny z pliku.
    Zwraca listę wariantów [(srid, swap, trafienie), …] posortowaną — tylko te,
    które trafiają ≥90% próbek. Pusta lista = układ lokalny/nierozpoznany.
    swap=True znaczy: kol1 to X geodezyjny (północ), trzeba zamienić na CAD."""
    probki = pary[:200]
    if not probki:
        return []
    out = []
    for srid in (2176, 2177, 2178, 2179, 2180):
        for swap in (False, True):
            ok = 0
            for a, b in probki:
                E, N = (b, a) if swap else (a, b)
                if _sensowny(E, N, srid):
                    ok += 1
            frac = ok / float(len(probki))
            if frac >= 0.9:
                out.append((srid, swap, frac))
    out.sort(key=lambda t: -t[2])
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Czytanie pliku — typ rozpoznawany po ZAWARTOŚCI, nie po rozszerzeniu
# ─────────────────────────────────────────────────────────────────────────────
def _kol_nr(ref):
    """'C7' → 2 (indeks kolumny od zera). Pusta komórka NIE może przesuwać kolumn."""
    m = re.match(r"([A-Z]+)", ref or "")
    if not m:
        return None
    n = 0
    for ch in m.group(1):
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def _czytaj_xlsx(path):
    """Skoroszyt .xlsx → lista wierszy (listy tekstów wg kolumn). Biblioteka standardowa."""
    with zipfile.ZipFile(path) as z:
        nazwy = z.namelist()
        shared = []
        if "xl/sharedStrings.xml" in nazwy:
            xml = z.read("xl/sharedStrings.xml").decode("utf-8", "replace")
            for si in re.findall(r"<si>(.*?)</si>", xml, re.S):
                shared.append("".join(re.findall(r"<t[^>]*>([^<]*)</t>", si)))
        arkusze = sorted(n for n in nazwy if re.match(r"xl/worksheets/sheet\d+\.xml$", n))
        if not arkusze:
            return []
        xml = z.read(arkusze[0]).decode("utf-8", "replace")

    out = []
    for rw in re.findall(r"<row[^>]*>(.*?)</row>", xml, re.S):
        komorki = {}
        for atrs, tresc in re.findall(r"<c\s([^>]*?)(?:/>|>(.*?)</c>)", rw, re.S):
            ref = re.search(r'r="([A-Z]+\d+)"', atrs)
            idx = _kol_nr(ref.group(1)) if ref else None
            if idx is None:
                continue
            typ = re.search(r't="(\w+)"', atrs)
            t = typ.group(1) if typ else "n"
            if t == "s":
                v = re.search(r"<v>([^<]*)</v>", tresc or "")
                try:
                    komorki[idx] = shared[int(v.group(1))] if v else ""
                except (ValueError, IndexError):
                    komorki[idx] = ""
            elif t == "inlineStr":
                komorki[idx] = "".join(re.findall(r"<t[^>]*>([^<]*)</t>", tresc or ""))
            else:
                v = re.search(r"<v>([^<]*)</v>", tresc or "")
                komorki[idx] = v.group(1) if v else ""
        if komorki:
            out.append([komorki.get(i, "") for i in range(max(komorki) + 1)])
    return out


def _czytaj_tekst(path):
    """Plik tekstowy → lista wierszy (listy tokenów). Kodowania PL + separatory PL."""
    data = None
    for enc in ("utf-8-sig", "cp1250", "latin-1"):
        try:
            with open(path, "r", encoding=enc) as fp:
                data = fp.readlines()
            break
        except (UnicodeDecodeError, OSError):
            continue
    if data is None:
        return None
    out = []
    for raw in data:
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("//"):
            continue
        # separator: średnik/tab (Excel PL) jeśli obecny, inaczej białe znaki (Notatnik)
        if ";" in line or "\t" in line:
            toks = [t.strip() for t in re.split(r"[;\t]+", line) if t.strip()]
        else:
            toks = [t.strip() for t in re.split(r"\s+", line) if t.strip()]
        if toks:
            out.append(toks)
    return out


def _typ_pliku(path):
    """Rozpoznaje typ po pierwszych bajtach — rozszerzenie potrafi kłamać."""
    try:
        with open(path, "rb") as fp:
            head = fp.read(8)
    except OSError:
        return None
    if head[:4] == b"PK\x03\x04":
        return "xlsx"                       # skoroszyt (nawet jeśli nazwany .csv)
    if head[:8] == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1":
        return "xls_stary"                  # BIFF — format binarny sprzed 2007
    return "tekst"


def _wczytaj(path):
    """Zwraca (wiersze_tokenow, typ) albo (None, typ) gdy nie da się odczytać."""
    typ = _typ_pliku(path)
    if typ is None:
        return None, None
    if typ == "xlsx":
        return _czytaj_xlsx(path), typ
    if typ == "xls_stary":
        return None, typ
    return _czytaj_tekst(path), typ


def _num(tok):
    """Token → liczba. Przecinek dziesiętny PL → kropka. Spacje tysięczne usuwane."""
    return float(str(tok).replace(" ", "").replace("\xa0", "").replace(",", "."))


def _czy_liczba(tok):
    try:
        _num(tok)
        return True
    except (ValueError, TypeError):
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Rozpoznanie formatu Z ZAWARTOŚCI pliku
#
# DLACZEGO TO ISTNIEJE — dwa razy ten sam błąd, oba razy NIE z winy człowieka:
#   2026-07-16  Tomasz dostaje pytanie „Format pliku [XY/XYZ/NrXY/NrXYZ]" i wpisuje
#               inny format, niż zakładałem.
#   2026-07-17  Tomasz wpisuje „N", chcąc NrXYZ. „N" jest prefiksem NrXY ORAZ NrXYZ.
#               gcedGetKword nie zgłasza niejednoznaczności — bierze pierwsze z listy,
#               czyli NrXY. Parser cichcem ODCINA kolumnę Z i wstawia 24 pikiety na
#               wysokości zero. Zero ostrzeżeń. Dla pikiet wysokość JEST pomiarem.
#
# Skoro pierwszy człowiek, który dotknął tego pytania, dwa razy odpowiedział inaczej,
# niż projekt zakładał, to złe jest PYTANIE, nie odpowiedź. Plik sam mówi, jaki ma
# format — wystarczy go przeczytać.
#
# Zasada: pytamy TYLKO wtedy, gdy dane naprawdę są dwuznaczne, i wtedy pokazujemy
# konkret (gdzie ląduje pierwszy punkt), zamiast żądać nazwy formatu. Ta sama filozofia
# co przy kolejności osi niżej — nie zgadujemy po cichu.
# ─────────────────────────────────────────────────────────────────────────────
def _liczba_kolumn(wiersze):
    """Dominująca liczba kolumn. Wiersze odstające to zwykle nagłówek albo śmieć."""
    licz = {}
    for toks in wiersze:
        licz[len(toks)] = licz.get(len(toks), 0) + 1
    if not licz:
        return 0
    return max(licz.items(), key=lambda kv: (kv[1], kv[0]))[0]


def _pary(dane, i, j):
    out = []
    for toks in dane:
        try:
            out.append((_num(toks[i]), _num(toks[j])))
        except (ValueError, IndexError):
            pass
    return out


def _pierwsza_to_numer(dane):
    """Czy pierwsza kolumna to etykieta punktu, a nie współrzędna?
    True / False / None (nie da się rozstrzygnąć — trzeba spytać człowieka).

    Kolejność prób: od dowodu twardego do poszlaki."""
    if not dane:
        return None

    # 1) DOWÓD: cokolwiek nieliczbowego w 1. kolumnie (np. „P1", „A-12") = etykieta.
    if any(not _czy_liczba(t[0]) for t in dane):
        return True

    # 2) DOWÓD: która PARA kolumn układa się w polski układ współrzędnych?
    #    (0,1) sensowne a (1,2) nie  → pierwsza kolumna to współrzędna.
    #    (1,2) sensowne a (0,1) nie  → pierwsza kolumna to numer.
    #    Ta sama maszyneria, co przy wykrywaniu osi — nie dokładamy heurystyk,
    #    skoro mamy twarde kryterium geodezyjne.
    w01 = _wykryj_uklad(_pary(dane, 0, 1))
    w12 = _wykryj_uklad(_pary(dane, 1, 2))
    if w12 and not w01:
        return True
    if w01 and not w12:
        return False

    # 3) POSZLAKA (układ lokalny/umowny — geodezja nie pomoże): numery punktów
    #    to zwykle rosnące liczby całkowite o rozpiętości nieporównywalnie mniejszej
    #    niż współrzędne.
    try:
        kol0 = [_num(t[0]) for t in dane]
        kol1 = [_num(t[1]) for t in dane]
    except ValueError:
        return None
    if len(kol0) >= 3:
        calkowite = all(abs(v - round(v)) < 1e-9 for v in kol0)
        rosnace = all(kol0[i] < kol0[i + 1] for i in range(len(kol0) - 1))
        rozp0 = max(kol0) - min(kol0)
        rozp1 = max(kol1) - min(kol1)
        if calkowite and rosnace and rozp1 > 1e-6 and rozp0 < rozp1:
            return True

    return None


def _wykryj_format(wiersze):
    """(fmt, opis, dane) — format rozpoznany z zawartości. fmt=None => spytaj człowieka.

    `dane` to wiersze wyglądające na dane (ostatnie dwie kolumny liczbowe) —
    nagłówek i śmieci odpadają, żeby nie zatruwały rozpoznania."""
    n = _liczba_kolumn(wiersze)
    if n < 2:
        return None, "plik ma mniej niz 2 kolumny", []

    # Wiersz z danymi = ma współrzędne, czyli parę liczb na (0,1) albo na (1,2).
    # NIE testujemy dwóch OSTATNICH kolumn: „1 X Y Z SW" (pikieta z kodem) ma na końcu
    # tekst i cały plik wypadłby jako śmieć. Nagłówek „Nr X Y Z" przepada tu sam,
    # bo nie ma ani jednej pary liczb.
    dane = [t for t in wiersze
            if len(t) >= n and ((_czy_liczba(t[0]) and _czy_liczba(t[1])) or
                                (len(t) >= 3 and _czy_liczba(t[1]) and _czy_liczba(t[2])))]
    if not dane:
        return None, "zaden wiersz nie wyglada na dane liczbowe", []

    if n == 2:
        return "XY", "2 kolumny: X Y", dane

    numer = _pierwsza_to_numer(dane)
    if numer is None:
        return None, "%d kolumny — nie wiadomo, czy pierwsza to numer punktu" % n, dane
    if n == 3:
        return ("NrXY", "3 kolumny: Nr X Y", dane) if numer else \
               ("XYZ", "3 kolumny: X Y Z", dane)
    return ("NrXYZ", "%d kolumn: Nr X Y Z" % n, dane) if numer else \
           ("XYZ", "%d kolumn: X Y Z" % n, dane)


def _rozbierz(wiersze, fmt):
    """Wiersze tokenów → (rows, pominiete). rows = [(label, a, b, z)] — a,b SUROWE kolumny
    (kolejność osi rozstrzygana później). pominiete = [(nr_wiersza, powod, tresc)]."""
    potrzeba = {"XY": 2, "XYZ": 3, "NrXY": 3, "NrXYZ": 4}[fmt]
    rows, pominiete = [], []
    auto = 0
    for i, toks in enumerate(wiersze, start=1):
        if len(toks) < potrzeba:
            pominiete.append((i, "za malo kolumn (%d, potrzeba %d)" % (len(toks), potrzeba),
                              " ".join(str(t) for t in toks)[:40]))
            continue
        try:
            if fmt == "XY":
                label, a, b, z = None, _num(toks[0]), _num(toks[1]), 0.0
            elif fmt == "XYZ":
                label, a, b, z = None, _num(toks[0]), _num(toks[1]), _num(toks[2])
            elif fmt == "NrXY":
                label, a, b, z = str(toks[0]), _num(toks[1]), _num(toks[2]), 0.0
            else:
                label, a, b, z = str(toks[0]), _num(toks[1]), _num(toks[2]), _num(toks[3])
        except (ValueError, IndexError):
            powod = "naglowek albo tekst zamiast liczby"
            pominiete.append((i, powod, " ".join(str(t) for t in toks)[:40]))
            continue
        if label is None:
            auto += 1
            label = str(auto)
        rows.append((label, a, b, z))
    return rows, pominiete


# ─────────────────────────────────────────────────────────────────────────────
# Rysowanie
# ─────────────────────────────────────────────────────────────────────────────
_ROWNE_WYSOKOSCI = (0.1, 0.2, 0.25, 0.5, 0.75, 1.0, 1.2, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0,
                    6.0, 7.5, 10.0, 12.5, 15.0, 20.0, 25.0, 30.0, 40.0, 50.0, 75.0, 100.0)


def _rowna_wysokosc(h):
    """Zaokrągla wysokość tekstu do najbliższej „ładnej" wartości.

    Uwaga Roberta Nowakowskiego (2026-07-18): opis punktu dostawał wysokość 1.207,
    bo liczymy ją z rozpiętości rysunku. Geodeta oczekuje 1.2 albo 1.5 — takie
    wartości siedzą w standardach biur i w tabelkach rysunkowych. Ułamek z trzema
    miejscami po przecinku wygląda jak pomyłka, nawet jeśli jest matematycznie dobry.

    Powyżej 100 zaokrąglamy do pełnych dziesiątek — tam i tak nikt nie patrzy na
    dokładność, a chodzi o to, żeby liczba dała się wypowiedzieć.
    """
    if h <= 0:
        return 2.5
    if h > 100.0:
        return round(h / 10.0) * 10.0
    return min(_ROWNE_WYSOKOSCI, key=lambda w: abs(w - h))


def _openModelSpace():
    """Zwraca (ms, db) z modelem otwartym do zapisu, albo (None, None)."""
    db = gcdbWorkingDatabase()
    status, bt = db.getBlockTable(GcDb.kForRead)
    if status != Gcad.eOk:
        return None, None
    status, ms = bt.getAt(GCDB_MODEL_SPACE, GcDb.kForWrite)
    bt.close()
    if status != Gcad.eOk:
        return None, None
    return ms, db


def _nazwa_grupy(db, path):
    """Nazwa grupy z nazwy pliku + data. Unikalna — przy powtórnym imporcie dokleja _2, _3…

    Nazwa musi przeżyć okno dialogowe GROUP, więc tylko litery, cyfry, `_` i `-`."""
    baza = os.path.splitext(os.path.basename(path))[0]
    baza = re.sub(r"[^A-Za-z0-9_-]+", "_", baza).strip("_")[:40] or "IMPORT"
    kand = "PIKIETY_%s_%s" % (time.strftime("%Y-%m-%d"), baza)
    st, gd = db.getGroupDictionary(GcDb.kForRead)
    if st != Gcad.eOk:
        return kand
    try:
        if not gd.has(kand):
            return kand
        for i in range(2, 100):                     # ten sam plik wczytany drugi raz tego dnia
            n = "%s_%d" % (kand, i)
            if not gd.has(n):
                return n
        return "%s_%s" % (kand, time.strftime("%H%M%S"))
    finally:
        gd.close()


def _grupuj(db, ids, nazwa):
    """Wrzuca wstawione encje do NAZWANEJ grupy. Zwraca (ok, powod).

    PO CO — pomysł Roberta Nowakowskiego (2026-07-17), z realnej pracy geodety:
    dostaje poprawione współrzędne i importuje drugi raz. Bez grupy stare punkty ZOSTAJĄ
    i nakładają się na nowe — albo trzeba ręcznie wyszukiwać setki punktów z kilku plików.
    Z grupą: zaznacz → skasuj → wczytaj nową wersję. Jednym ruchem.
    Grupę zawsze można rozbić (UNGROUP), więc nikomu niczego nie zabieramy.

    KSZTAŁT WYWOŁAŃ sprawdzony w stubach (nauczka z BUG-06):
      getGroupDictionary(mode) -> (status, GcDbDictionary)   — jak getBlockTable
      setAt(nazwa, obiekt)     -> (status, GcDbObjectId)
      GcDbGroup(opis, selectable) / append(GcDbObjectIdArray)
    """
    if ids.length() == 0:
        return False, "brak encji"
    st, gd = db.getGroupDictionary(GcDb.kForWrite)
    if st != Gcad.eOk:
        return False, "nie moge otworzyc slownika grup"
    try:
        grp = GcDbGroup("Punkty z importu wspolrzednych", True)
        # Najpierw do słownika (grupa dostaje bazę), DOPIERO potem encje.
        st, gid = gd.setAt(nazwa, grp)
        if st != Gcad.eOk:
            try:
                grp.close()
            except Exception:
                pass
            return False, "setAt: %s" % st
        try:
            grp.append(ids)
        finally:
            grp.close()
        return True, ""
    finally:
        gd.close()


def _setPointDisplayVars():
    """Best-effort: zrób punkty widocznymi (PDMODE/PDSIZE). Niekrytyczne."""
    try:
        rb = resbuf()
        rb.restype = RTSHORT
        rb.resval.rint = 3             # krzyżyk X — klasyczny marker punktu geodezyjnego
        gcedSetVar("PDMODE", rb)
        rb2 = resbuf()
        rb2.restype = RTREAL
        rb2.resval.rreal = -2.0        # ujemne = % rozmiaru ekranu (skaluje się z zoomem)
        gcedSetVar("PDSIZE", rb2)
    except Exception:
        pass                            # brak widoczności punktów nie psuje importu


@command(local_name='GSAI_IMPORTXYZ', global_name='GSAI_IMPORTXYZ', group_name='GSAI')
def importxyz():
    """Wczytaj plik ze współrzędnymi i wstaw punkty + opisy numerów."""
    try:
        # 1) wybór pliku — NATYWNE okno „przeglądaj katalogi i kliknij plik"
        #    (gcedGetFileD) — intuicyjne, nie trzeba wpisywać całej ścieżki.
        #    Fallback: gdyby okno nie zadziałało (wyjątek), pytamy o ścieżkę tekstem,
        #    żeby nie zepsuć już zweryfikowanej drogi.
        path = None
        okno_ok = True
        try:
            rbf = resbuf()
            # (tytul, domyslna nazwa, filtr rozszerzenia, flagi, wynik w resbuf)
            rc = gcedGetFileD("Wybierz plik ze wspolrzednymi (XLSX / CSV / TXT)", "",
                              "xlsx;csv;txt", 0, rbf)
        except Exception:
            okno_ok = False
            rc = None
        if okno_ok:
            if rc == RTNORM:
                try:
                    path = rbf.resval.rstring
                except Exception:
                    path = None
            else:
                gcutPrintf("\nAnulowano (nie wybrano pliku).")   # klik Anuluj w oknie
                return
        if not path:                                              # okno niedostępne → ścieżka tekstem
            status, path = gcedGetString(1, "\nPodaj sciezke do pliku ze wspolrzednymi: ")
            if status != RTNORM or not path or not path.strip():
                gcutPrintf("\nAnulowano.")
                return
        path = path.strip().strip('"')

        # 2) wczytanie — typ po zawartości pliku
        wiersze, typ = _wczytaj(path)
        if typ == "xls_stary":
            gcutPrintf("\n[IMPORTXYZ] To stary binarny .xls (sprzed 2007). Otworz go w Excelu")
            gcutPrintf("\n            i zapisz jako .xlsx albo .txt — wtedy wczytam.")
            return
        if wiersze is None:
            gcutPrintf("\n[BLAD] Nie mozna otworzyc pliku: %s" % path)
            return
        if typ == "xlsx":
            gcutPrintf("\n[IMPORTXYZ] Plik to skoroszyt Excela — czytam arkusz wprost.")

        # 3) FORMAT — z zawartości pliku, nie z pytania. Patrz komentarz przy _wykryj_format:
        #    pytanie o format dwa razy dało cichy zły import (ostatnio: „N" → NrXY zamiast
        #    NrXYZ, kolumna Z wyrzucona bez słowa).
        fmt, opis, dane = _wykryj_format(wiersze)
        if fmt is None:
            # Dwuznaczne NAPRAWDĘ (np. lokalny układ, 3 liczbowe kolumny). Nie pytamy
            # o nazwę formatu — pytamy o jedną konkretną rzecz i pokazujemy przykład.
            gcutPrintf("\n[IMPORTXYZ] %s." % opis)
            if dane:
                p = dane[0]
                gcutPrintf("\n            Pierwszy wiersz danych: %s" % "  ".join(str(t) for t in p[:4]))
                gcutPrintf("\n            Numer     = pierwsza kolumna to numer punktu (%s)" % p[0])
                gcutPrintf("\n            Wspolrzed = pierwsza kolumna to wspolrzedna (%s)" % p[0])
            gcedInitGet(0, "Numer Wspolrzedna")
            rc2, kw2 = gcedGetKword("\nCzym jest pierwsza kolumna? [Numer/Wspolrzedna] <Numer>: ")
            if rc2 == RTNORM and kw2 == "Wspolrzedna":
                numer = False
            elif rc2 in (RTNORM, RTNONE):
                numer = True
            else:
                gcutPrintf("\nAnulowano.")
                return
            n = _liczba_kolumn(wiersze)
            if n == 2:
                fmt = "XY"
            elif n == 3:
                fmt = "NrXY" if numer else "XYZ"
            else:
                fmt = "NrXYZ" if numer else "XYZ"
            opis = "%d kolumn, wybor uzytkownika" % n

        # ZAWSZE mów, co rozpoznałeś — cichy zły format to dokładnie ten bug.
        gcutPrintf("\n[IMPORTXYZ] Rozpoznany format: %s  (%s)" % (fmt, opis))
        if fmt in ("XY", "NrXY"):
            gcutPrintf("\n            Wysokosc Z: brak w pliku — punkty na Z=0.")
        else:
            gcutPrintf("\n            Wysokosc Z: wczytuje z pliku.")

        rows, pominiete = _rozbierz(wiersze, fmt)
        if not rows:
            gcutPrintf("\n[IMPORTXYZ] Zero poprawnych wierszy w formacie %s (pominieto %d)."
                       % (fmt, len(pominiete)))
            for nr, powod, tresc in pominiete[:3]:
                gcutPrintf("\n            linia %d: %s | %s" % (nr, powod, tresc))
            gcutPrintf("\n            Sprawdz, czy format sie zgadza z ukladem kolumn w pliku.")
            return

        # 4) układ + kolejność osi — sprawdzane empirycznie, nie zgadywane
        warianty = _wykryj_uklad([(r[1], r[2]) for r in rows])
        swap = False
        if not warianty:
            gcutPrintf("\n[IMPORTXYZ] Uklad: nierozpoznany (lokalny/umowny) — wspolrzedne bez zmian.")
        elif len(warianty) == 1:
            srid, swap, _ = warianty[0]
            gcutPrintf("\n[IMPORTXYZ] Wykryto uklad: %s" % _uklad_nazwa(srid))
            if swap:
                gcutPrintf("\n            Kolumny w kolejnosci geodezyjnej (X=polnoc) — zamieniam na CAD.")
        else:
            # Niejednoznaczne (typowo PL-1992 albo strefa 5): oba warianty trafiaja
            # w kraj. NIE wybieramy po cichu — pokazujemy, gdzie ląduje 1. punkt.
            gcutPrintf("\n[IMPORTXYZ] Nie da sie jednoznacznie ustalic kolejnosci osi.")
            for srid, sw, _ in warianty[:2]:
                a, b = rows[0][1], rows[0][2]
                E, N = (b, a) if sw else (a, b)
                lat, lon = _do_geo(E, N, srid)
                gcutPrintf("\n   %-4s %s, pierwszy punkt ~ %.4f N  %.4f E"
                           % ("Tak" if not sw else "Zamien", _uklad_nazwa(srid),
                              math.degrees(lat), math.degrees(lon)))
            gcutPrintf("\n   (Tak = kolumny jak w pliku | Zamien = pierwsza kolumna to X geodezyjny)")
            gcedInitGet(0, "Tak Zamien")
            rc2, kw2 = gcedGetKword("\nZamienic osie X/Y? [Tak/Zamien] <Tak>: ")
            swap = (rc2 == RTNORM and kw2 == "Zamien")

        # kolejność osi: CAD x = wschód, y = północ
        punkty = [(lab, (b if swap else a), (a if swap else b), z) for lab, a, b, z in rows]

        # 5) auto-skalowanie opisu z rozpiętości punktów
        xs = [p[1] for p in punkty]
        ys = [p[2] for p in punkty]
        span = max(max(xs) - min(xs), max(ys) - min(ys))
        txtH = _rowna_wysokosc((span * 0.02) if span > 1e-6 else 2.5)
        off = txtH * 0.6

        ms, db_ms = _openModelSpace()
        if ms is None:
            gcutPrintf("\n[BLAD] Nie mozna otworzyc przestrzeni modelu.")
            return

        # Model space MUSI zamknąć się nawet przy wyjątku — otwarta blokada zapisu
        # zostawia bazę rysunku w niespójnym stanie i wywraca program przy autozapisie
        # kilkanaście minut później (diagnoza 2026-07-15).
        placed = 0
        ids = GcDbObjectIdArray()          # zbieramy do grupy — patrz _grupuj()
        try:
            for label, x, y, z in punkty:
                point = GcDbPoint(GcGePoint3d(x, y, z))
                try:
                    stp, oid = ms.appendGcDbEntity(point)
                    if stp == Gcad.eOk:
                        ids.append(oid)
                finally:
                    point.close()
                txt = GcDbText(GcGePoint3d(x + off, y + off, z), str(label))
                try:
                    txt.setHeight(txtH)
                    stt, oidt = ms.appendGcDbEntity(txt)
                    if stt == Gcad.eOk:
                        ids.append(oidt)
                finally:
                    txt.close()
                placed += 1
        finally:
            ms.close()

        _setPointDisplayVars()

        gcutPrintf("\n[IMPORTXYZ] Wstawiono %d punktow (format %s)." % (placed, fmt))

        # Grupowanie NIGDY nie wywraca importu — punkty są już w rysunku i są ważniejsze
        # niż wygoda kasowania. Gdy nie wyjdzie: mówimy, i tyle.
        try:
            nazwa = _nazwa_grupy(db_ms, path)
            ok, powod = _grupuj(db_ms, ids, nazwa)
            if ok:
                gcutPrintf("\n[IMPORTXYZ] Punkty i opisy w grupie: %s" % nazwa)
                gcutPrintf("\n            Import tego samego pliku drugi raz? Wpisz GROUP, zaznacz te")
                gcutPrintf("\n            grupe, skasuj — i wczytaj nowa wersje. Bez szukania po jednym.")
            else:
                gcutPrintf("\n[IMPORTXYZ] Uwaga: nie udalo sie zgrupowac punktow (%s)." % powod)
                gcutPrintf("\n            Punkty SA w rysunku — tylko trzeba je kasowac recznie.")
        except Exception as gerr:
            gcutPrintf("\n[IMPORTXYZ] Uwaga: grupowanie pominiete (%s: %s)." % (type(gerr).__name__, gerr))
            gcutPrintf("\n            Punkty SA w rysunku.")
        if pominiete:
            gcutPrintf("\n[IMPORTXYZ] Pominieto %d wierszy:" % len(pominiete))
            for nr, powod, tresc in pominiete[:5]:
                gcutPrintf("\n            linia %d: %s | %s" % (nr, powod, tresc))
            if len(pominiete) > 5:
                gcutPrintf("\n            ... i %d dalszych" % (len(pominiete) - 5))
        etyk = [p[0] for p in punkty]
        dubli = len(etyk) - len(set(etyk))
        if dubli:
            gcutPrintf("\n[IMPORTXYZ] Uwaga: %d powtorzonych numerow punktow (wstawione bez zmian)." % dubli)
        gcutPrintf("\n[IMPORTXYZ] Wpisz ZOOM, potem A (Wszystko), zeby zobaczyc wszystkie punkty.")

    except Exception as err:
        gcutPrintf("\n[IMPORTXYZ BLAD] %s: %s" % (type(err).__name__, str(err)))
