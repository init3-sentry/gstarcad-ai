# Narzędzia na stronę — aktualna lista dla Eryki

> Stan **2026-08-06**. Źródło prawdy: `NARZEDZIA.md` + wyniki testów zespołu. Zastępuje wcześniejszą listę.
> **Legenda statusu:** ✅ zwalidowane na realnych rysunkach (można pisać jako pewne) · 🟡 w testach (jeszcze **nie** obiecywać na stronie) · 🔧 w budowie (poza stroną).
> Reguła z briefu, sekcja 6: **na stronę idą tylko ✅.** 🟡 i 🔧 zostawiamy do rozmowy handlowej.

## Poprawki względem Twojej propozycji (to samo, tylko na faktach)
1. `GSAI_RZUTOWANIE` → **`GSAI_SYMBOL_RZUTOWANIA`** (zmieniona nazwa — stara myliła, że rzutuje obiekty).
2. `GSAI_CUI` — zostaje, dobra i prosta nazwa (miałaś rację).
3. **Słońce** — usuń „zacieniania". To wykres **pozycji słońca / ścieżki słońca**, nie mapa cienia działki. Właściwie: „diagram nasłonecznienia — ścieżka słońca dla daty i lokalizacji".
4. **Ornament / „Generator AI"** — **zdejmij ze strony.** Dwa powody: praktyk (Robert) ocenił „nie widzę zastosowania", a nazwa „Generator AI" łamie ramę z briefu (AI jest po naszej stronie, klient nie dostaje „przycisku AI").
5. **Dodane: `GSAI_SPADEK`** — gotowe, dziś potwierdzone przez zespół. Pominęłaś je.

---

## [Architektura]
- ✅ **Generator schodów** (`GSAI_SCHODY`) — rysuje bieg schodów w rzucie i przekroju jednym poleceniem. *(dziś: cm zamiast mm, wynik jako blok, auto-opis)*
- ✅ **Koty wysokościowe** (`GSAI_RZEDNE`) — stawia rzędne od poziomu ±0.00 z automatycznym odczytem wysokości.
- ✅ **Ścieżka słońca** (`GSAI_SLONCE`) — diagram nasłonecznienia dla daty i szerokości geograficznej (przydatne przy warunkach zabudowy). *Nie „mapa cienia".*
- ✅ **Strzałka spadku** (`GSAI_SPADEK`) — oznaczenie spadku dachu, tarasu, odwodnienia (%/‰/° albo z różnicy wysokości).

## [Konstrukcje i mechanika]
- 🟡 **Symbole chropowatości** (`GSAI_CHROPOWATOSC`) — znaki obróbki powierzchni wg PN-EN ISO 21920-1. *W testach zespołu — na stronę dopiero po zaliczeniu.*
- 🟡 **Symbol rzutowania** (`GSAI_SYMBOL_RZUTOWANIA`) — tabliczkowy znak metody 1. i 3. kąta (europejska/amerykańska), ISO 5456-2. *Świeżo przemianowane, do testu.*

## [Geodezja]
- ✅ **Import współrzędnych** (`GSAI_IMPORTXYZ`) — punkty X,Y,Z z pliku TXT/Excel prosto do rysunku, z numerami. Koniec wstawiania punkt po punkcie.
- ✅ **Strzałka północy** (`GSAI_STRZALKA_POLNOCY`) — estetyczny symbol orientacji, 6 stylów, wstawiany jako blok. *(dziś: potwierdzone przez zespół)*
- ✅ **Audyt osi Z** (`GSAI_AUDYTZ`) — wykrywa obiekty „uciekające" w trzeci wymiar (Z≠0), które fałszują płaskie pomiary.
- 🟡 **Linie urbanistyczne** (zasób `planninglines`) — znormalizowane linie zabudowy, tory, ogrodzenia, granice. *Świeżo wciągnięte, do testu + instalator musi dowozić czcionkę shape.*

## [Automatyzacja i porządkowanie]
- ✅ **Standard warstw** (`GSAI_WARSTWY_STANDARD`) — pełne drzewo warstw jednym kliknięciem przy starcie projektu. *(dziś: v2 po uwagach Roberta — do potwierdzenia w teście)* 🟡
- ✅ **Zmiana nazw warstw** (`GSAI_RENAME_WARSTWY`) — hurtowa podmiana nazw wzorcem, sprzątanie plików po podwykonawcach. *(lukę potwierdził na piśmie QA Manager Autodesku)*
- 🟡 **Numeracja arkuszy** (`GSAI_NUMERACJA`) — automatyczne wstawianie i inkrementacja numerów rysunków. *Status do potwierdzenia testem.*
- 🟡 **Reset interfejsu** (`GSAI_CUI`) — natychmiastowe przywracanie znikających pasków i wstążek. *Status do potwierdzenia.*
- 🟡 **Raport warstw** (`GSAI_DUMP_WARSTW`) — pokazuje puste/„używane" warstwy, których PURGE nie sprząta, i kolizje nazw. Nic nie zmienia.

## 🔧 W budowie — NIE na stronę
- **Formatka rysunkowa** (`GSAI_FORMATKA`) — czeka na wzorzec Roberta + testy.
- **Przedmiar / suma długości** (`GSAI_PRZEDMIAR`, `GSAI_DLUGOSC`) — zablokowane bugiem wiązania na plikach klienta (zgłoszone do R&D). Nie promować.

---

## Drugie pytanie Eryki — pobieranie ze strony
**Tak, self-service — bez kontaktu.** Klient pobiera instalator, uruchamia, i narzędzia same wgrywają się do GstarCAD (razem z Pythonem, o który nie musi dbać). Instalator jest **dziś testowany przez zespół na czystych maszynach i przechodzi.** Finalny link na stronie uruchamiamy na premierę. Do tego czasu: „pobierzesz bezpośrednio ze strony" jest prawdą, którą wolno zapowiadać — bez daty (brief §6).
