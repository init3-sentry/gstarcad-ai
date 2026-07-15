# Katalog narzędzi — co mamy, co działa, skąd pobrać

> **To jest jedyny obowiązujący katalog narzędzi.** Wszystkie repozytoria projektu linkują tutaj. Zmiana statusu, nazwy komendy albo nowe narzędzie — **zmienia się tylko ten plik**.
>
> Jak uruchomić którekolwiek z nich: **[JAK-URUCHOMIC.md](JAK-URUCHOMIC.md)**.

**Komendy mają przedrostek `GSAI_`** (zmiana z 14.07.2026). Wpisuje się np. `GSAI_IMPORTXYZ`. Stare nazwy bez przedrostka już nie działają — po pobraniu nowej wersji trzeba zrobić `APPLOAD` jeszcze raz.

**Jak pobrać:** kliknąć nazwę pliku → na stronie pliku przycisk **„Download raw file"** (prawy górny róg). Pilnować, żeby zapisało się jako `.py`, nie `.txt`. Wszystko naraz: zielony **Code → Download ZIP**.

---

## ✅ Działają — sprawdzone na prawdziwych rysunkach

Sprawdzone na prawdziwych rysunkach klientów — tych ciężkich, z bałaganem po poprzednim projektancie. **To najlepsze źródło problemów, jakie mamy** — narzędzie, które działa tylko na sztucznie wygenerowanym pliku, jest do niczego.

| Komenda | Co robi | Plik |
|---|---|---|
| **`GSAI_IMPORTXYZ`** | Plik z Excela albo Notatnika ze współrzędnymi → punkty z numerami w rysunku. Natywnie GstarCAD tego nie ma (tylko płatna nakładka). | [25_import_coordinates.py](biblioteka-rag/przyklady/25_import_coordinates.py) |
| **`GSAI_AUDYTZ`** | Znajduje i zaznacza obiekty, które „uciekły" w trzeci wymiar (Z≠0) i psują pomiary w płaskim rysunku — z góry są niewidoczne, więc inaczej nie sposób ich znaleźć. Potem prostuje się je natywnym `FLATTEN`. | [26_audit_z_axis.py](biblioteka-rag/przyklady/26_audit_z_axis.py) |

## 🟡 W testach — jeszcze nie zwalidowane

| Komenda | Co robi | Plik | Stan |
|---|---|---|---|
| **`GSAI_CHROPOWATOSC`** | Symbol struktury geometrycznej powierzchni (chropowatość) wg ISO 1302. | [27_surface_roughness.py](biblioteka-rag/przyklady/27_surface_roughness.py) | Czeka na normę **PN-EN ISO 21920-1** (zastąpiła ISO 1302) — nie zgadujemy geometrii. |

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

W [`biblioteka-rag/przyklady/`](biblioteka-rag/przyklady/) leży **27 przykładów wzorcowych**. Powstały jako materiał uczący sztuczną inteligencję, jak poprawnie pisać kod dla GstarCAD. **Działają** i bywają przydatne, ale to pomoce warsztatowe, nie produkty — dlatego **nie mają przedrostka `GSAI_`**.

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
