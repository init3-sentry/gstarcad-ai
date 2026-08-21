# Narzedzia na strone - LISTA AUTOMATYCZNA (dla Eryki)

> **Aktualizowane automatycznie.** Zerkaj tu **raz dziennie**. Ostatnia aktualizacja: **2026-08-21**.
> Regula z briefu: **na strone idzie tylko ✅.** 🟡 = jeszcze nie obiecuj (moze sie zmienic). NIE edytuj tego pliku recznie.

Gotowych na strone: **12** | w testach: **14** | razem przewidzianych na premiere: **26**

## Architektura i rysunek
- ✅ **Generator schodow** (`GSAI_SCHODY`) - Rysuje bieg schodow w rzucie i przekroju jednym poleceniem.
- ✅ **Rzedne wysokosciowe** (`GSAI_RZEDNE`) - Stawia rzedne od poziomu +-0.00 z automatycznym odczytem wysokosci.
- ✅ **Sciezka slonca** (`GSAI_SLONCE`) - Diagram naslonecznienia dla daty i lokalizacji - przy warunkach zabudowy.
- ✅ **Strzalka spadku** (`GSAI_SPADEK`) - Oznaczenie spadku dachu, tarasu, odwodnienia.
- ✅ **Strzalka polnocy** (`GSAI_STRZALKA_POLNOCY`) - Estetyczny symbol orientacji, 6 stylow, jako blok.
- 🟡 **Formatka rysunkowa** (`GSAI_FORMATKA`) - Ramka i tabliczka rysunkowa wg formatu, jednym poleceniem.
- 🟡 **Podzialka liniowa** (`GSAI_PODZIALKA`) - Graficzna podzialka liniowa (scale bar) do map i rzutow.
- 🟡 **Meble** (`GSAI_MEBLE`) - Biblioteka mebli + auto-rozmieszczanie: wstaw, szyk, stol z krzeslami.
- 🟡 **Tabliczka rysunkowa** (`GSAI_TABELKA`) - Tabliczka ISO 7200 jako blok z polami; punkt wstawienia = prawy dolny rog.

## Konstrukcje i mechanika
- 🟡 **Symbole chropowatosci** (`GSAI_CHROPOWATOSC`) - Znaki obrobki powierzchni wg PN-EN ISO 21920-1.
- 🟡 **Symbol rzutowania** (`GSAI_SYMBOL_RZUTOWANIA`) - Tabliczkowy znak metody 1. i 3. kata (ISO 5456-2).

## Geodezja
- ✅ **Import wspolrzednych** (`GSAI_IMPORTXYZ`) - Punkty X,Y,Z z pliku TXT/Excel prosto do rysunku, z numerami.
- ✅ **Audyt osi Z** (`GSAI_AUDYTZ`) - Wykrywa obiekty z Z!=0, ktore falszuja plaskie pomiary.
- 🟡 **Biblioteka linii urbanistycznych** (`PLANNINGLINES`) - Gotowe znormalizowane linie: zabudowa i nieprzekraczalna zabudowa, tory kolejowe i tramwajowe, ogrodzenie, skarpa, granice. Biblioteka linii (wczytywana do rysunku), nie komenda.

## Pomiary i zestawienia
- ✅ **Pomiar z opisem** (`GSAI_POMIAR`) - Dlugosci obiektow i odleglosci z trwalym opisem na rysunku.
- 🟡 **Suma dlugosci** (`GSAI_DLUGOSC_OPIS`) - Sumuje dlugosc wskazanych obiektow i podpisuje na rysunku.
- ✅ **Przedmiar do Excela** (`GSAI_PRZEDMIAR`) - Zaznacz zamkniete obiekty -> pole i obwod + suma, otwiera sie w Excelu.
- ✅ **Zestawienie pol** (`GSAI_ZESTAWIENIE`) - Pole, obwod i tabela dla zaznaczonych obiektow.
- ✅ **Pola i pomieszczenia** (`GSAI_POLA`) - Pole i obwod pol - zaznacz oknem albo kliknij w pomieszczenie, opis + tabela.

## Automatyzacja i porzadkowanie
- 🟡 **Standard warstw** (`GSAI_WARSTWY_STANDARD`) - Pelne drzewo warstw jednym klknieciem przy starcie projektu.
- ✅ **Zmiana nazw warstw** (`GSAI_RENAME_WARSTWY`) - Hurtowa podmiana nazw wzorcem - sprzatanie plikow po podwykonawcach.
- 🟡 **Zliczanie obiektow** (`GSAI_ZLICZ`) - Liczy obiekty wg warstwy/typu/bloku i wstawia tabele.
- 🟡 **Kolejnosc rysowania** (`GSAI_KOLEJNOSC`) - Warstwa na wierzch/spod - dziala tam, gdzie natywne LAYDRAWORDER zawodzi.
- 🟡 **Numeracja arkuszy** (`GSAI_NUMERACJA`) - Automatyczne wstawianie i inkrementacja numerow rysunkow.
- 🟡 **Reset interfejsu** (`GSAI_CUI`) - Natychmiastowe przywracanie znikajacych paskow i wstazek.
- 🟡 **Rodzaj linii z opisem** (`GSAI_LINIA`) - Wlasny rodzaj linii z wtopionym tekstem (GAZ/KABEL) do sieci uzbrojenia.
