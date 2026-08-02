# Katalog narzędzi — co mamy, co działa, skąd pobrać

> _Stan na 2026-08-01._ **To jest jedyny obowiązujący katalog narzędzi.** Wszystkie repozytoria projektu linkują tutaj. Zmiana statusu, nazwy komendy albo nowe narzędzie — **zmienia się tylko ten plik**.
>
> Jak uruchomić którekolwiek z nich: **[JAK-URUCHOMIC.md](JAK-URUCHOMIC.md)**.

**Komendy mają przedrostek `GSAI_`** (zmiana z 14.07.2026). Wpisuje się np. `GSAI_IMPORTXYZ`. Stare nazwy bez przedrostka już nie działają — po pobraniu nowej wersji trzeba zrobić `APPLOAD` jeszcze raz.

**Jak pobrać:** kliknąć nazwę pliku → na stronie pliku przycisk **„Download raw file"** (prawy górny róg). Pilnować, żeby zapisało się jako `.py`, nie `.txt`. Wszystko naraz: zielony **Code → Download ZIP**.

---

## ✅ Działają — zwalidowane na prawdziwych rysunkach (kandydaci na premierę)

Sprawdzone na prawdziwych rysunkach projektowych — tych ciężkich, z bałaganem po poprzednim projektancie. **To najlepsze źródło problemów, jakie mamy** — narzędzie, które działa tylko na sztucznie wygenerowanym pliku, jest do niczego.

| Komenda | Co robi | Plik | Zwalidował |
|---|---|---|---|
| **`GSAI_RENAME_WARSTWY`** 🦸 | Hurtowa zmiana nazw warstw wzorcem (find→replace w środku nazwy) z obsługą kolizji. Natywnie GstarCAD tego nie ma — **lukę potwierdził na piśmie QA Manager Autodesku** (ADR 08). Wartość = hurt/wzorzec, nie pojedyncza warstwa. | [31_rename_warstw_wzorcem.py](biblioteka-rag/przyklady/31_rename_warstw_wzorcem.py) | Tomasz 29.07 (hurt) |
| **`GSAI_IMPORTXYZ`** | Plik z Excela/Notatnika ze współrzędnymi → punkty z numerami. Natywnie brak (płatne nakładki = dowód popytu). | [25_import_coordinates.py](biblioteka-rag/przyklady/25_import_coordinates.py) | Robert |
| **`GSAI_AUDYTZ`** | Znajduje i zaznacza obiekty, które „uciekły" w Z≠0 (z góry niewidoczne, psują pomiary w płaskim rysunku). Prostowanie natywnym `FLATTEN`. | [26_audit_z_axis.py](biblioteka-rag/przyklady/26_audit_z_axis.py) | Jakub 29.07 |
| **`GSAI_SCHODY`** 🎁 | Generator schodów (rzut / przekrój; tryby biegu) — „wow": schody w GstarCAD za darmo. **Rysuje też po ponownym otwarciu pliku** (generatywne → odporne na BUG-10). | kod w repo *powertools*, dostawa: release `skrypty-test` | Tomasz 31.07 |
| **`GSAI_STRZALKA_POLNOCY`** 🧭 | Ozdobna strzałka północy — **6 stylów dwutonowych** (prosta/strzałka/romb/róża wiatrów/kompas geodezyjny/iglica), panel wyboru z podglądem + wysokość + klik. Natywnie brak (GstarCAD ma tylko `COMPASS`/`NORTHDIRECTION`). Generatywne → BUG-10-safe. `GSAI_STRZALKA_GALERIA` = wszystkie naraz. | kod w *powertools*, release `skrypty-test` | **LC (GUI) 01.08** → zespół [#65](https://github.com/init3-sentry/gstarcad-ai-zespol/issues/65) |
| **`GSAI_SLONCE`** ☀️ | Diagram nasłonecznienia / ścieżka słońca (biegunowy wykres): szerokość geo + data → horyzont, pierścienie wysokości, azymuty N/E/S/W, ścieżka słońca + przesilenia/równonoc. Okno z **dropdownem 18 miast wojewódzkich** + ręczna szerokość. Generatywne → BUG-10-safe. Spina z **Linijką Słońca**. `GSAI_SUNPATH` = alias. | kod w *powertools*, release `skrypty-test` | **LC 02.08** → zespół [#66](https://github.com/init3-sentry/gstarcad-ai-zespol/issues/66) |

> **Bramka przed premierą (nie pomijać):** te narzędzia zespół ma jeszcze przejść **na pliku ZAPISANYM → otwartym ponownie** (bo BUG-10 — patrz niżej — ujawnił różnicę „świeży rysunek" vs „plik klienta"). RENAME/IMPORTXYZ/AUDYTZ/SCHODY są konstrukcyjnie BUG-10-safe, ale gate potwierdza to na realnym workflow.

## 🟡 Warunkowe / w testach

| Komenda | Co robi | Plik | Stan |
|---|---|---|---|
| **`GSAI_PRZEDMIAR`** | Pole + obwód wskazanych obiektów → CSV (Excel). | [30_przedmiar.py](biblioteka-rag/przyklady/30_przedmiar.py) | 🔴 **Blokada BUG-10** — na ZAPISANYM pliku encje wracają jako bazowe, `getArea` pada → działa na świeżym rysunku, **nie na plikach klienta**. Region: `BOUNDARY` (zdecydowane, [robert#7](https://github.com/init3-sentry/gstarcad-ai-robert/issues/7)). Eskalowane R&D (Jira **162444**). |
| **`GSAI_DLUGOSC`** / **`GSAI_DLUGOSC_OPIS`** | Suma długości; `_OPIS` dokłada etykietę na rysunku. | [GSAI_DLUGOSC.py](biblioteka-rag/przyklady/GSAI_DLUGOSC.py) · [29_dlugosc_opis.py](biblioteka-rag/przyklady/29_dlugosc_opis.py) | Zwalidowane na **ŚWIEŻYM** rysunku (Jakub 29.07), ale 🔴 **BUG-10 na zapisanych** (`length` pada). Do przepisania na `entget` albo fix R&D. |
| **`GSAI_FORMATKA`** 📐 | Formatka rysunkowa: ramka **ISO 5457** + tabliczka **ISO 7200** (PL) + pas właściciela (logo + Biuro), blok **ATTDEF**, formaty A4/A3/A2 (A4 też poziomo), guard „tylko Arkusz". Natywnie brak w bazie Professional (Mechanical ma). Generatywne → BUG-10-safe. Styl **TTF `GSAI_PL`** dla polskich znaków. | kod w *powertools*, release `skrypty-test` | 🟡 **Do testów zespołu ([zespol#64](https://github.com/init3-sentry/gstarcad-ai-zespol/issues/64))** — działa na LC (rama/tabliczka/PL/TTF, Dawid 02.08); czeka: realne rysunki + formaty poziome + **szablon `.dwt` A4 pion** (auto-orientacja niemożliwa ze skryptu — [BUG-11](../gstarcad-ai-wewnetrzne/produkt-i-badania/sdk-bugs/pygcad-bug-ledger.md)). ⚠️ testerzy: klawiatura **Polski (Programisty)**, nie 214. |
| **`GSAI_WEKTORYZUJ`** *(prototyp)* | Skan rastrowy → polilinie, lokalnie. | [wektoryzacja.py](biblioteka-rag/przyklady/wektoryzacja.py) | Prototyp; oddzielanie tekstu do walidacji u Jakuba. OCR = v2.0 (ADR 05). |
| **`GSAI_CHROPOWATOSC`** | Symbol chropowatości wg normy. | [27_surface_roughness.py](biblioteka-rag/przyklady/27_surface_roughness.py) | Czeka na **PN-EN ISO 21920-1** (zastąpiła ISO 1302) — nie zgadujemy geometrii. |

> **⚠️ BUG-10 (bug wiązania pygcad, nie nasz):** encje wczytane z ZAPISANEGO pliku DWG wracają jako bazowe `GcDbEntity` → typowane metody geometryczne (`getArea`/`length`) na nich padają. Narzędzia CZYTAJĄCE geometrię z plików klienta (PRZEDMIAR, DLUGOSC) są tym zablokowane; narzędzia GENERUJĄCE (SCHODY, ORNAMENT, IMPORTXYZ) i tabelowe (RENAME_WARSTWY, AUDYTZ) są odporne. Zgłoszone R&D jako top-issue **162444**.

## ⛔ Wycofane — bo GstarCAD ma to natywnie

Zbudowaliśmy je, po czym **sami skasowaliśmy**. Sprawdziliśmy uczciwie i okazało się, że GstarCAD ma te funkcje od lat — tylko mało kto o tym wie.

| Nasze (wycofane) | GstarCAD ma natywnie |
|---|---|
| `GSAI_ZAMIEN_TEKST` | **`FIND`** — i jest bogatszy od naszego |
| `GSAI_EKSPORT_ATRYBUTOW` | **`ATTOUT`** (Express Tools) |
| `GSAI_IMPORT_ATRYBUTOW` | **`ATTIN`** (Express Tools) |
| `GSAI_RENUMERUJ` | **`ATTINC`** — trzyma nawet zera wiodące (P-002) |

Warto też znać: **`FLATTEN`** (prostowanie do płaszczyzny), **`TCOUNT`** (numerowanie), **`DATAEXTRACTION`** (dane → tabela/Excel), **`MEASUREGEOM`** (pomiary długości i pól).

**Zasada projektu: nie budujemy tego, co jest już w pudełku.** Dublowanie natywnej funkcji to strata naszego czasu i wprowadzanie klienta w błąd.

## 🧪 Biblioteka wzorców

W [`biblioteka-rag/przyklady/`](biblioteka-rag/przyklady/) leży ~30 plików. Numerowane **01–24** to **przykłady wzorcowe** — materiał uczący sztuczną inteligencję, jak poprawnie pisać kod dla GstarCAD; **działają** i bywają przydatne, ale to pomoce warsztatowe, nie produkty (dlatego bez przedrostka `GSAI_`). Pliki od **25 wzwyż** oraz `GSAI_*.py` to **implementacje narzędzi** skatalogowane w sekcjach wyżej (✅/🟡). `GSAI_CASTPROBE.py` to skrypt diagnostyczny SDK.

Kilka użytecznych z brzegu:

| Komenda | Co robi | Plik |
|---|---|---|
| `ZAKRESKUJ` | Wypełnia wskazaną zamkniętą polilinię kreskowaniem pod skos. | [24_hatch_selected_object.py](biblioteka-rag/przyklady/24_hatch_selected_object.py) |
| `AUDYT_WARSTW` | Zestawienie warstw rysunku — kolory, co włączone/zamrożone. | [04_layer_audit_report.py](biblioteka-rag/przyklady/04_layer_audit_report.py) |
| `ZLICZ_OBIEKTY` | Ile czego jest w rysunku (linie, bloki, teksty…). | [12_count_entities_by_type.py](biblioteka-rag/przyklady/12_count_entities_by_type.py) |

## 🔧 W budowie

| Narzędzie | Co ma robić |
|---|---|
| **Dane z Geoportalu** | Numer i obrys działki, rzędna terenu, zdjęcie lotnicze — z ewidencji GUGiK prosto do rysunku, po wskazaniu punktu. |
| **Podkład rastrowy z georeferencją** | Wstawiony raster sam siada we właściwym miejscu (GstarCAD nie czyta georeferencji z pliku). |
| **Opis współrzędnych punktu** | Opisywanie bez nachodzenia tekstu na siebie. |
| **Formuły w zestawieniach** | Kolumny wyliczane (SUMA = ilość × cena). |
| **Kolejność rysowania wg warstw** | Działająca wersja tego, co w GstarCAD bywa kapryśne. |
| **Szyk „jak w SketchUpie"** | Kopiuj + obróć raz, podaj ×5 — mnoży w danym kierunku. |

---

## Gdzie zgłaszać problemy

- **Zespół wsparcia** (Jakub, Tomasz, Rafał) → komentarz pod właściwym zadaniem w [`gstarcad-ai-zespol`](https://github.com/init3-sentry/gstarcad-ai-zespol).
- **Robert** → panel w [`gstarcad-ai-robert`](https://github.com/init3-sentry/gstarcad-ai-robert).
- **Rysunek, na którym coś się sypie** — to najcenniejszy materiał, jaki możemy dostać. Zawsze **na kopii**, nigdy na oryginale klienta.
