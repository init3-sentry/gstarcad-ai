#!/usr/bin/env python3
# Generator pliku dla Eryki (copywriter). Zero zaleznosci (stdlib json).
#
# JAK DZIALA:
#   - SoT statusu = narzedzia-status.json (edytuj TYLKO "status" i "na_premiere").
#   - Ten skrypt czyta JSON i generuje NARZEDZIA-DLA-ERYKI-AKTUALNE.md.
#   - Snapshot poprzedniego stanu (.narzedzia-status.prev.json) -> sekcja "Co sie zmienilo".
#   - Uruchamiaj po kazdej zmianie statusu (albo z crona/LaunchAgenta raz dziennie).
#
# status: gotowe = wolno na strone | w_tescie = jeszcze nie | w_budowie = poza strona
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOT  = os.path.join(HERE, "narzedzia-status.json")
PREV = os.path.join(HERE, ".narzedzia-status.prev.json")
OUT  = os.path.join(HERE, "NARZEDZIA-DLA-ERYKI-AKTUALNE.md")

SEED = {
  "kategorie": [
    {"id":"architektura","nazwa":"Architektura i rysunek","narzedzia":[
      {"cmd":"GSAI_SCHODY","nazwa":"Generator schodow","status":"gotowe","na_premiere":True,"korzysc":"Rysuje bieg schodow w rzucie i przekroju jednym poleceniem."},
      {"cmd":"GSAI_RZEDNE","nazwa":"Rzedne wysokosciowe","status":"gotowe","na_premiere":True,"korzysc":"Stawia rzedne od poziomu +-0.00 z automatycznym odczytem wysokosci."},
      {"cmd":"GSAI_SLONCE","nazwa":"Sciezka slonca","status":"gotowe","na_premiere":True,"korzysc":"Diagram naslonecznienia dla daty i lokalizacji - przy warunkach zabudowy."},
      {"cmd":"GSAI_SPADEK","nazwa":"Strzalka spadku","status":"gotowe","na_premiere":True,"korzysc":"Oznaczenie spadku dachu, tarasu, odwodnienia."},
      {"cmd":"GSAI_STRZALKA_POLNOCY","nazwa":"Strzalka polnocy","status":"gotowe","na_premiere":True,"korzysc":"Estetyczny symbol orientacji, 6 stylow, jako blok."},
      {"cmd":"GSAI_FORMATKA","nazwa":"Formatka rysunkowa","status":"w_tescie","na_premiere":True,"korzysc":"Ramka i tabliczka rysunkowa wg formatu, jednym poleceniem."}]},
    {"id":"mechanika","nazwa":"Konstrukcje i mechanika","narzedzia":[
      {"cmd":"GSAI_CHROPOWATOSC","nazwa":"Symbole chropowatosci","status":"w_tescie","na_premiere":True,"korzysc":"Znaki obrobki powierzchni wg PN-EN ISO 21920-1."},
      {"cmd":"GSAI_SYMBOL_RZUTOWANIA","nazwa":"Symbol rzutowania","status":"w_tescie","na_premiere":True,"korzysc":"Tabliczkowy znak metody 1. i 3. kata (ISO 5456-2)."}]},
    {"id":"geodezja","nazwa":"Geodezja","narzedzia":[
      {"cmd":"GSAI_IMPORTXYZ","nazwa":"Import wspolrzednych","status":"gotowe","na_premiere":True,"korzysc":"Punkty X,Y,Z z pliku TXT/Excel prosto do rysunku, z numerami."},
      {"cmd":"GSAI_AUDYTZ","nazwa":"Audyt osi Z","status":"gotowe","na_premiere":True,"korzysc":"Wykrywa obiekty z Z!=0, ktore falszuja plaskie pomiary."},
      {"cmd":"PLANNINGLINES","nazwa":"Linie urbanistyczne","status":"w_tescie","na_premiere":True,"korzysc":"Znormalizowane linie zabudowy, granice, ogrodzenia."}]},
    {"id":"pomiary","nazwa":"Pomiary i zestawienia","narzedzia":[
      {"cmd":"GSAI_POMIAR","nazwa":"Pomiar z opisem","status":"w_tescie","na_premiere":True,"korzysc":"Dlugosci obiektow i odleglosci z trwalym opisem na rysunku."},
      {"cmd":"GSAI_DLUGOSC_OPIS","nazwa":"Suma dlugosci","status":"w_tescie","na_premiere":True,"korzysc":"Sumuje dlugosc wskazanych obiektow i podpisuje na rysunku."},
      {"cmd":"GSAI_PRZEDMIAR","nazwa":"Przedmiar do Excela","status":"w_tescie","na_premiere":True,"korzysc":"Zaznacz zamkniete obiekty -> pole i obwod + suma, otwiera sie w Excelu."},
      {"cmd":"GSAI_ZESTAWIENIE","nazwa":"Zestawienie pol","status":"w_tescie","na_premiere":True,"korzysc":"Pole, obwod i tabela dla zaznaczonych obiektow."},
      {"cmd":"GSAI_POLA","nazwa":"Pola i pomieszczenia","status":"w_tescie","na_premiere":True,"korzysc":"Pole i obwod pol - zaznacz oknem albo kliknij w pomieszczenie, opis + tabela."}]},
    {"id":"porzadek","nazwa":"Automatyzacja i porzadkowanie","narzedzia":[
      {"cmd":"GSAI_WARSTWY_STANDARD","nazwa":"Standard warstw","status":"w_tescie","na_premiere":True,"korzysc":"Pelne drzewo warstw jednym klknieciem przy starcie projektu."},
      {"cmd":"GSAI_RENAME_WARSTWY","nazwa":"Zmiana nazw warstw","status":"gotowe","na_premiere":True,"korzysc":"Hurtowa podmiana nazw wzorcem - sprzatanie plikow po podwykonawcach."},
      {"cmd":"GSAI_ZLICZ","nazwa":"Zliczanie obiektow","status":"w_tescie","na_premiere":True,"korzysc":"Liczy obiekty wg warstwy/typu/bloku i wstawia tabele."},
      {"cmd":"GSAI_KOLEJNOSC","nazwa":"Kolejnosc rysowania","status":"w_tescie","na_premiere":True,"korzysc":"Warstwa na wierzch/spod - dziala tam, gdzie natywne LAYDRAWORDER zawodzi."},
      {"cmd":"GSAI_NUMERACJA","nazwa":"Numeracja arkuszy","status":"w_tescie","na_premiere":True,"korzysc":"Automatyczne wstawianie i inkrementacja numerow rysunkow."},
      {"cmd":"GSAI_CUI","nazwa":"Reset interfejsu","status":"w_tescie","na_premiere":True,"korzysc":"Natychmiastowe przywracanie znikajacych paskow i wstazek."},
      {"cmd":"GSAI_DUMP_WARSTW","nazwa":"Raport warstw","status":"w_tescie","na_premiere":True,"korzysc":"Pokazuje puste/kolizyjne warstwy, ktorych PURGE nie sprzata."}]}
  ]
}

STMAP = {"gotowe":"✅ NA STRONE", "w_tescie":"🟡 w testach (jeszcze nie)", "w_budowie":"🔧 poza strona"}

def load():
    if not os.path.exists(SOT):
        with open(SOT,"w",encoding="utf-8") as f: json.dump(SEED,f,ensure_ascii=False,indent=2)
    with open(SOT,encoding="utf-8") as f: return json.load(f)

def flat(d):
    return {t["cmd"]:t["status"] for k in d["kategorie"] for t in k["narzedzia"]}

def diff(cur):
    if not os.path.exists(PREV): return []
    with open(PREV,encoding="utf-8") as f: prev = json.load(f)
    ch=[]
    for cmd,st in cur.items():
        if cmd not in prev: ch.append("+ NOWE: %s (%s)"%(cmd,STMAP.get(st,st)))
        elif prev[cmd]!=st: ch.append("~ %s: %s -> %s"%(cmd,STMAP.get(prev[cmd],prev[cmd]),STMAP.get(st,st)))
    for cmd in prev:
        if cmd not in cur: ch.append("- USUNIETE: %s"%cmd)
    return ch

def gen(d, stamp):
    cur = flat(d)
    changes = diff(cur)
    L=[]
    L.append("# Narzedzia na strone - LISTA AUTOMATYCZNA (dla Eryki)")
    L.append("")
    L.append("> **Aktualizowane automatycznie.** Zerkaj tu **raz dziennie**. Ostatnia aktualizacja: **%s**." % stamp)
    L.append("> Regula z briefu: **na strone idzie tylko ✅.** 🟡 = jeszcze nie obiecuj (moze sie zmienic). NIE edytuj tego pliku recznie.")
    L.append("")
    if changes:
        L.append("## 🔔 Co sie zmienilo od ostatniego razu")
        for c in changes: L.append("- "+c)
        L.append("")
    gotowe = sum(1 for s in cur.values() if s=="gotowe")
    L.append("Gotowych na strone: **%d** | w testach: **%d** | razem przewidzianych na premiere: **%d**"
             % (gotowe, sum(1 for s in cur.values() if s=="w_tescie"),
                sum(1 for k in d["kategorie"] for t in k["narzedzia"] if t.get("na_premiere"))))
    L.append("")
    for k in d["kategorie"]:
        L.append("## %s"%k["nazwa"])
        for t in k["narzedzia"]:
            L.append("- %s **%s** (`%s`) - %s" % (STMAP.get(t["status"],t["status"]).split()[0], t["nazwa"], t["cmd"], t["korzysc"]))
        L.append("")
    with open(OUT,"w",encoding="utf-8") as f: f.write("\n".join(L))
    with open(PREV,"w",encoding="utf-8") as f: json.dump(cur,f,ensure_ascii=False,indent=2)
    return len(changes), gotowe

if __name__=="__main__":
    stamp = sys.argv[1] if len(sys.argv)>1 else "(brak daty)"
    d = load()
    nch, ng = gen(d, stamp)
    print("OK: %s | zmian: %d | gotowych: %d" % (os.path.basename(OUT), nch, ng))
