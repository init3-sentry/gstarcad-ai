# Opinie użytkowników na ai.gstarcad.pl — rozpoznanie (06.10.2026)

Stan strony sprawdzony na żywo 06.10 rano (przeglądarka, widok 1440 px). Wersji mobilnej nie oglądałem.
Zrzuty: `/private/tmp/claude-501/-Users-init3-pro/9c0080d5-0707-429f-b2e3-bfc659512ac9/scratchpad/opinie-zrzuty/` (01–11, nazwy mówią, co na nich jest). Katalog tymczasowy, zniknie z sesją.

## Trzy rzeczy, które zmieniają projekt

1. **Żaden kandydat na opinię nie ma dziś karty na stronie.** GSAI_WMS i GSAI_SKARPA (Szczepański) oraz GSAI_ORIENTACYJNY (Wiecan) stoją na liście dla Eryki w 🟡 „w testach — jeszcze NIE na stronę”. GSAI_RURA (Kujawski) jest w 🔧 „w budowie”. GSAI_ZAZNACZ (Natalia) jest ✅, ale karty jeszcze nie ma. `/biblioteka/gsai_wms/` zwraca 404, w katalogu (24 narzędzia) WMS nie występuje. Przy regule „na stronę idzie tylko ✅” opublikowanie zdania o GSAI_WMS promuje narzędzie spoza listy. **Najpierw decyzja Dawida: WMS na ✅ i karta u Eryki, albo opinia czeka.**
2. **Strona nie stoi na Elementorze.** To własny motyw WordPress `aigstarcad`. Karty narzędzi są wpisami typu `biblioteka` (filtr, sortowanie i „Pokaż więcej” idą przez admin-ajax). Wariant „ręcznie” oznacza więc pole albo blok w motywie Eryki, nie widżet Elementora.
3. **Changelog stoi w hero, nie w osobnej sekcji.** Iframe `https://upd.tmsys.pl/changelog/widget.html` (bez `?rynek`, wysokość 640 px, pokazuje 3 najnowsze wpisy) siedzi w prawej kolumnie pierwszego ekranu. Katalog i karty changelogu nie mają. Blok „Nowe w tym miesiącu” z naszej makiety katalogu nie został wdrożony.

Przy okazji: changelog pokazuje GSAI_WMS publicznie jako „wydane” od 09.09 (8 wpisów), a biblioteka WMS nie zna. To ta sama niespójność co w punkcie 1.

## (a) Mapa obecnej strony

**Strona główna** (kolejność z DOM, wysokości przy 1440 px):

| # | Sekcja | Rola | Uwagi |
|---|---|---|---|
| 1 | Hero „Polska biblioteka rozszerzeń / Od inżynierów dla inżynierów” | obietnica + 2 CTA („Pobierz bibliotekę”, „Zgłoś potrzebę”) | **nad zgięciem**; z prawej widżet „Co nowego” (changelog) |
| 2 | 3 kafle „Polecenie GSAI_DACH / SCHODY / PN ✓ …” | demo efektu w stylu konsoli | częściowo nad zgięciem |
| 3 | „Zaktualizuj GstarCAD do wersji 2027!” | upsell licencji, CTA do gstarcad.pl/aktualizacje | |
| 4 | „Jak to działa? / CAD, który dostosowuje się do Ciebie” | narracja „analizujemy zgłoszenia” + „Ponad 60 000 użytkowników GstarCAD w Polsce” | jedyny dziś „dowód społeczny” to ta liczba |
| 5 | „Od pomysłu do gotowego rozwiązania” | 4 kroki: Pomysł → Analiza → Decyzja → Gotowe narzędzie | proces bez przykładu z życia |
| 6 | Baner „Przejdź do biblioteki gotowych narzędzi” | ciemny granatowy blok, CTA do katalogu | |
| 7 | „Najpopularniejsze narzędzia z biblioteki” | uwaga o ARM + 4 karty (DACH, SCHODY, PN, POLA) + „Zobacz wszystkie” + wymagania + „Pobierz” | |
| 8 | „Nie znalazłeś/aś funkcji…” | CTA „Zgłoś potrzebę” + 4 punkty (darmowe, realne potrzeby, przetestowane, oszczędność) | |
| 9 | FAQ (12 pytań, akordeon) | obiekcje | |
| 10 | „Zgłoś swoją propozycję” + formularz (reCAPTCHA) | pętla zgłoszeń | |
| — | Stopka granatowa | opis, kontakt TMSys, polityka, podręcznik, instrukcja PDF, link do GstarCAD | |

Menu: Jak to działa? · Biblioteka gotowych narzędzi · FAQ · „Pobierz bibliotekę”.

**Katalog** `/biblioteka-narzedzi-do-gstarcad/`: nagłówek i opis, wymagania, „Pobierz” + podręcznik, „Instalacja krok po kroku” (4 kafle), „Lista dostępnych narzędzi (24)” z kategoriami, wyszukiwarką i sortowaniem (polecane / najpopularniejsze / najnowsze / A–Z), po 12 z „Pokaż więcej”. Changelogu brak.

**Karta narzędzia** (np. `/biblioteka/gsai_dach/`): „Cofnij”, ikona, H1 z nazwą komendy, jedno zdanie, film MP4 z prawej. Pod spodem „Szczegółowe informacje”: Kiedy użyć? / Co robi? / Jak użyć?. Na dole powtórzone „Najpopularniejsze narzędzia” i „Pobierz bibliotekę”. Bez daty, bez changelogu, bez opinii.

**Styl:** tło biało-szare (gradient do #F2F5F9). Granat tekstu #001E4D. Akcent niebieski #3F71FF, przyciski w pigułce (radius ~24 px). Karty białe, radius ~21 px, miękki niebieski cień. Nagłówki Poppins 500, tekst „indivisible”, nazwy komend monospace. Widżet changelogu ma własny krój (IBM Plex), czyli wizualnie odstaje od reszty strony.

**Opinie dziś:** nigdzie. W tekście strony nie ma słów opinia, referencja ani recenzja. Społeczny dowód to wyłącznie „60 000 użytkowników”.

## (b) Warianty miejsca

### A. Karta narzędzia: blok pod „Szczegółowe informacje”
Cytat, podpis i data jako czwarty element po „Jak użyć?”.
- **Plusy:** opinia stoi przy tym, czego dotyczy, czyli w momencie decyzji „pobrać czy nie”. Przy jednej opinii wygląda naturalnie: karta ma jeden cytat i nikt nie oczekuje więcej. Skaluje się samo, bo każde narzędzie ma swój głos.
- **Minusy:** dziś nie ma gdzie go postawić, bo żaden kandydat nie ma karty. Na kartach ruch jest mniejszy niż na stronie głównej. Większość kart przez długi czas opinii mieć nie będzie, więc blok musi się pokazywać tylko wtedy, gdy opinia istnieje.
- **Przy jednej opinii:** ryzyka pustej sekcji nie ma. Warunek brzmi: brak opinii oznacza brak bloku, bez placeholdera typu „bądź pierwszy”.

### B. Strona główna: jeden cytat między „Od pomysłu do gotowego rozwiązania” a banerem biblioteki
Jedno zdanie użytkownika domyka 4 kroki procesu: „Użytkownicy zgłaszają…”, a pod spodem prawdziwy głos z praktyki.
- **Plusy:** największy ruch. Wypełnia jedyną lukę w dowodzie społecznym (dziś tylko liczba 60 000). Wzmacnia główną tezę strony, że budujemy to, o co prosicie. Strona główna dostaje jeden stały slot i nie rośnie, co zgadza się z decyzją, że rośnie katalog.
- **Minusy:** cytat o narzędziu spoza katalogu (dziś WMS) linkuje donikąd. Sekcja z nagłówkiem „Opinie użytkowników” i jednym cytatem pod nim wygląda biednie.
- **Przy jednej opinii:** projektować pod **jeden** cytat jako pełnoszeroki „głos z praktyki”: duży cudzysłów, zdanie, podpis, chip narzędzia. Bez nagłówka w liczbie mnogiej. Bez siatki 3 kolumn i bez karuzeli z kropkami (karuzela z 1 slajdem zdradza, że jest jeden). Przy 2–3 opiniach ten sam slot pokazuje jedną naraz, wybraną albo najnowszą, z rotacją bez kontrolek. Przy zerze sekcja znika.

### C. Przy changelogu / procesie: historia „zgłosił → dostał → mówi”
Opinia jako dowód pętli zgłoszeń: „Przemek z branży mostowej poprosił o X. Wydane 09.09. Jego słowa: …”. Miejsce to krok 5 procesu albo znacznik „na prośbę użytkownika” przy wpisie w widżecie „Co nowego”.
- **Plusy:** najmocniejsza historia, jaką mamy. Spina się z silnikiem powrotów (changelog plus pętla zgłoszeń) i odpowiada wprost na „czy moje zgłoszenie coś da?”.
- **Minusy:** wymaga, żeby cytat dotyczył **tego samego** narzędzia, które autor zgłosił. U Szczepańskiego się to rozjeżdża: zgłaszał SKARPA, chwali WMS. Sklejenie jego cytatu z historią SKARPA to wkładanie mu słów w usta. Widżet ma stałą wysokość i 3 wiersze, więc nie ma w nim miejsca na cytat. Do tego dochodzi nowe pole w changelogu (powiązanie wpisu ze zgłoszeniem).
- **Przy jednej opinii:** działa jako „przykład”, nie „opinie”, więc jedna wystarczy. Ale nie z tym cytatem.

## (c) Źródło danych: feed jak changelog czy ręcznie u Eryki

| | Feed z repo (rejestr → `opinie.json` na upd → strona) | Ręcznie w WordPress (pole/blok w motywie) |
|---|---|---|
| Jedno źródło prawdy | rejestr-opinii.json; zgoda, podpis i skrót w jednym miejscu | treść żyje u Eryki, zgoda u nas, więc łatwo o rozjazd |
| Bramka zgody | twarda w generatorze: bez zgody nic nie wychodzi | zależy od tego, co dostanie Eryka i czy ktoś później coś poprawi |
| Wycofanie zgody | jedna zmiana w rejestrze, strona czysta po deployu | trzeba pamiętać i prosić Erykę |
| PL / DE / RO | pole `rynek`, ten sam mechanizm co `feed-DE/RO` i `?rynek=` | każda strona osobno (DE prowadzi Kateryna) |
| Wygląd | iframe ma własne style i stałą wysokość (widżet changelogu odstaje krojem) | natywnie w stylu strony |
| SEO / dostępność | treść w iframe nie należy do strony | tekst na stronie |
| Koszt | generator + plik + osadzenie (raz) | zero kodu u nas, ręczna robota przy każdej opinii |
| Skala | opinii będzie kilka rocznie, nie 130 jak w changelogu | przy tej skali ręczna robota jest mała |

**Ochrona danych:** rejestr ma nazwiska i adresy e-mail. Feed może zawierać **wyłącznie** pola publiczne (cytat, podpis, narzędzie, link, data, rynek). Nigdy `osoba`, `adres`, `uwagi`. To argument za generatorem z białą listą pól, nie za kopiowaniem pliku.

**Wniosek:** źródłem ma być rejestr i generowany plik `opinie.json` na upd, publikowany razem z feedami changelogu. Eryka nie dostaje iframe'u, tylko JSON, i rysuje blok w motywie (pobranie po stronie serwera z cache'em). Dzięki temu jest natywny wygląd, tekst w HTML i żadnej stałej wysokości. Gdyby to było dla niej za dużo, zapasem jest nasz mały widżet iframe jak przy changelogu, ze stylami dopasowanymi do strony (Poppins/indivisible, #3F71FF), nie IBM Plex. Wpis ręczny bez feedu odradzam ze względu na zgodę i wycofanie.

## (d) Rekomendacja

**Wariant B (jeden cytat na stronie głównej, pod procesem „Od pomysłu do gotowego rozwiązania”), zasilany z feedu. Ten sam komponent w drugim kroku wchodzi warunkowo na karty (wariant A), bez nowego projektu.**

Dlaczego:
- Na start jest jedna opinia. B to jedyne miejsce, gdzie jeden cytat robi robotę, bo uzupełnia jedyną lukę w dowodzie społecznym. A dziś nie ma gdzie stanąć.
- Cytat pod czterema krokami procesu zamienia „Użytkownicy zgłaszają…” z deklaracji w fakt. To ta sama logika co przy changelogu: dowód z przeszłości zamiast przymiotnika.
- C jest najmocniejsze fabularnie, ale wymaga opinii o narzędziu, które autor sam zgłosił. Wraca, gdy taka będzie (Kujawski z RURA, Natalia z ZAZNACZ, Wiecan z ORIENTACYJNY to dokładnie ten typ).

**Warunek startu (decyzja Dawida, przed projektem):** GSAI_WMS przechodzi na ✅ i Eryka stawia jego kartę. Inaczej cytat o WMS łamie regułę „na stronę tylko ✅” i linkuje w 404. Druga możliwość: opinia czeka na pierwszego kandydata z narzędziem ✅.

**Do zaprojektowania (makieta jak przy changelogu, wersja jasna):**
- **Komponent „Głos z praktyki”** (jeden cytat):
  - **cytat**: wersja na stronę, czyli dosłowna albo skrót zaakceptowany przez autora; typograficzny cudzysłów; bez ozdobników i bez gwiazdek
  - **podpis**: dokładnie jak autor wybrał („Przemek, branża mostowa”); bez zdjęcia i logo firmy (na to zgody nie ma)
  - **narzędzie**: chip z nazwą komendy (monospace, jak w kartach), link do karty
  - **link do karty**: osobne pole w danych, bo z nazwy komendy adresu nie da się wyliczyć (GSAI_PN → `gsai_strzalka_polnocy`, GSAI_XYZ → `gsai_importxyz`). Bez karty nie ma linku albo nie ma publikacji.
  - **data**: miesiąc i rok opinii, tylko przeszła (spójne z changelogiem)
  - **rynek**: PL / DE / RO. Strona DE i RO pokazuje tylko opinie ze swojego rynku; polskich cytatów nie tłumaczymy, bo to też byłoby wkładanie słów w usta
- **Stany:** 0 opinii oznacza brak sekcji. 1 opinia to jeden cytat bez nagłówka w liczbie mnogiej. 2+ opinii to nadal jeden slot (wybrana albo najnowsza, ewentualnie spokojna rotacja bez kropek).
- **Wersja na kartę (krok 2):** ten sam komponent, węższy, pod „Jak użyć?”, wyłącznie gdy narzędzie ma opinię.
- **Plik danych:** `opinie.json` (i `-DE`/`-RO`) obok feedów changelogu, z białą listą pól publicznych.
- **Rejestr, braki:** brakuje pól `rynek`, `cytat_publiczny` (wersja na stronę), `skrot_zaakceptowany` (data akceptacji skrótu przez autora) i `karta_url`. Opis stanów w `_opis` nie zna `zgoda`, `czeka_na_klienta` ani `odbior_u_zamawiajacego`, więc generator powinien patrzeć na pola (zgoda, podpis, data), nie na nazwę stanu.

## (e) Zasady z README opinii, które projekt musi uszanować

- **Bez wyraźnej zgody nic nie wychodzi.** Generator publikuje tylko wpis z `zgoda_publikacja` i `podpis_publiczny`. Szczepański: zgoda z 02.10 08:10 jest.
- **Podpis wybiera autor.** Projekt przyjmuje podpis dosłownie z rejestru. Nie skracamy go, nie dopisujemy firmy, nie dodajemy zdjęcia.
- **Skrót akceptuje autor.** W rejestrze opinia leży dosłownie. Jeśli na stronę idzie skrót, musi być `skrot_zaakceptowany`. U Szczepańskiego zdanie jest krótkie i idzie w całości. Uwaga: „warto **tą** funkcjonalność” (potocznie zamiast „tę”). Poprawka gramatyki to też zmiana jego słów: albo publikujemy dosłownie, albo pytamy go o akceptację „tę”. Decyzja Dawida.
- **`opublikowane` = gdzie i kiedy.** Po wdrożeniu wpisujemy miejsce (strona główna / karta X) i datę, tak żeby wycofanie zgody wiedziało, co zdjąć.
- **Nie nachodzimy ludzi.** Projekt nie może wymuszać zbierania opinii pod sekcję. Pusta sekcja się chowa, więc nie ma presji, żeby ją zapełniać.
- **Pochwała, która już padła, to prośba tylko o zgodę i podpis.** Dotyczy Kujawskiego („petarda”, „miód na moje oczy”): kandydat do wariantu C po zgodzie, ale RURA najpierw musi trafić na stronę.
