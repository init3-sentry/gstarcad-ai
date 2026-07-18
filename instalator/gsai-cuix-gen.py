# -*- coding: utf-8 -*-
"""
Generator gsai.cuix — interfejs naszych narzedzi w GstarCAD.

Robi jedna rzecz: czyta komendy.json i sklada z niego plik gsai.cuix.
Ten plik wnosi do GstarCAD zakladke na wstazce, menu klasyczne i pasek narzedzi
— te same trzy miejsca naraz, z tych samych danych.

    python3 gsai-cuix-gen.py                    # -> gsai.cuix obok tego skryptu
    python3 gsai-cuix-gen.py --wypakuj podglad  # dodatkowo rozpakowany XML do obejrzenia

Zeby dodac narzedzie do interfejsu: dopisz pozycje w komendy.json. Nic tutaj.

--------------------------------------------------------------------------------
SKAD TO WIEMY (2026-07-17)

Wzorcem jest express.cuix producenta — ich wlasny Express Tools:
  /Applications/gstarcad.app/Contents/Resources/UserDataCache/Support/pl-PL/express.cuix
Rozebrany i odtworzony element po elemencie. Pelny opis formatu:
  gstarcad-ai-wewnetrzne/referencje/cuix-anatomia.md

Trzy fakty, na ktorych stoi ten generator:

1. .cuix to ZIP z plikami XML. Schemat jest Autodeskowy (atrybut Id="AcRibbonCommandButton",
   prefiks "Ac" = AutoCAD). Komentarze w srodku strasza po chinsku "nie edytuj recznie,
   uzyj CUI" — ignorujemy. To XML w ZIP-ie, generujemy go skryptem, bo wtedy mamy
   repozytorium, wersjonowanie i diff zamiast klikania w oknie.

2. Przycisk nie zna ani komendy, ani ikony. Wskazuje MenuMacroID -> MenuMacro w MenuGroup.cui.
   Dopiero makro zna jedno i drugie. Dlatego jedno makro obsluguje wstazke, menu i pasek naraz.

3. Ikona wiaze sie PRZEZ NAZWE PLIKU, nie przez sciezke:
       <SmallImage Name="X"/>  ->  RibbonIcon/{light,dark}/RCDATA_16_X.svg
       <LargeImage Name="X"/>  ->  RibbonIcon/{light,dark}/RCDATA_32_X.svg
   Zweryfikowane w obie strony: LAYISO/TCOUNT/BURST maja ikony i maja wpisy;
   LMAN nie ma ikony i NIE MA wpisu SmallImage.

--------------------------------------------------------------------------------
CZEGO NIE WIEMY — trzy rzeczy do sprawdzenia na Windows (Z-13, Issue #36)

a) Czy nasz .cuix moze wniesc WLASNE ikony, czy trzeba je dolozyc do katalogu
   RibbonIcon/ producenta. Jesli to drugie — instalator kopiuje SVG tam, a nie do siebie.

b) Czy ^C^C_ dziala przed NASZA komenda. Podkreslnik wymusza angielska nazwe komendy
   wbudowanej. Nasze komendy sa rejestrowane przez @command i zadnej nazwy przetlumaczonej
   nie maja. Dlatego PREFIKS_MAKRA nizej jest stala do przelaczenia jednym znakiem,
   a nie wpisana w kod na sztywno.

c) Czy Windows ma identyczna strukture .cuix. Rozebrany plik jest z macOS.

DOPOKI (a) i (b) nie wroca z maszyny, ten plik generuje sie poprawnie, ale NIE JEST
POTWIERDZONY W BOJU. Nie wolno go wysylac klientowi na podstawie samego "skrypt nie
wywalil sie".

--------------------------------------------------------------------------------
⚠️ KONWENCJA NAZW IKON ROZNI SIE MIEDZY PLATFORMAMI — sprawdzone 2026-07-18 na LC

Policzone w `MenuGroup.cui` producenta, obie platformy:

    platforma   <SmallImage Name="LAYISO">   <SmallImage Name="RCDATA_16_LAYISO">
    macOS                 280                            22
    Windows                 0                           149     <-- WYLACZNIE ta

**Windows uzywa TYLKO konwencji z pelnym prefiksem.** Krotkiej nie ma tam ani razu.
Dlatego generator sklada nazwe jako `RCDATA_16_<ikona>` / `RCDATA_32_<ikona>`.

Skad blad, ktory tu byl: rozbieralem `express.cuix` z **macOS** (bo tam mialem dostep do
plikow), zobaczylem 280 do 22 i poszedlem za wiekszoscia. Na Windows to jest 0 do 149 —
czyli dokladnie odwrotnie. **Produkt jest windowsowy, wiec liczy sie kolumna Windows.**

Gdyby to przeszlo: zakladka na wstazce owszem by sie pojawila, ale przyciski **bez ikon**
— i wygladaloby to jak „grafiki jeszcze nie ma", a nie jak blad. Wykrylibysmy dopiero,
gdy graficy oddadza pliki i nadal nic by sie nie pokazalo.

🔴 GDZIE FIZYCZNIE SA IKONY NA WINDOWS — NIEROZSTRZYGNIETE:
Katalog RibbonIcon (z plikami SVG) **na Windows nie istnieje**. `RCDATA` to typ zasobu
wkompilowanego w pliki binarne Windows, a w `express.bundle` leza `express.dll` (5,3 MB)
i `expressTheme.dll` (5,3 MB). Wszystko wskazuje, ze ikony sa **zasobami w .dll**, nie
plikami. Jesli tak, sam plik SVG od grafika NIE WYSTARCZY — trzeba go czyms zapakowac.
To trzeba sprawdzic PRZED zamowieniem grafiki.
"""

import argparse
import hashlib
import io
import json
import os
import shutil
import sys
import zipfile
from xml.sax.saxutils import escape, quoteattr

KATALOG = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(KATALOG, "komendy.json")
IKONY = os.path.join(KATALOG, "ikony")

# Patrz (b) wyzej. "^C^C" = dwa razy Esc, czyli przerwij to, co user akurat robi.
# Podkreslnik na koncu = wymus nazwe angielska. Jesli Z-13 pokaze, ze przy naszych
# komendach przeszkadza — skasuj sam podkreslnik, reszta zostaje.
PREFIKS_MAKRA = "^C^C_"

# ZIP z data na sztywno. Bez tego kazde uruchomienie daje inne bajty i git pokazuje
# zmiane pliku, w ktorym nic sie nie zmienilo.
DATA_ZIP = (2026, 1, 1, 0, 0, 0)

NS = ('xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
      'xmlns:xsd="http://www.w3.org/2001/XMLSchema"')
REV = '<ModifiedRev MajorVersion="19" MinorVersion="0" UserVersion="1" />'

# Puste szkielety. Producent trzyma je w kazdym .cuix, wiec my tez — nieobecnosc
# ktoregos z nich to ryzyko, ktorego nie ma sensu podejmowac dla 570 bajtow.
PUSTE = [
    "AcceleratorRoot", "DigitizerButtonRoot", "DoubleClickRoot", "ImageMenuRoot",
    "LSPFiles", "MouseButtonRoot", "OverrideRoot", "QuickAccessToolbarRoot",
    "QuickPropertiesRoot", "RolloverTooltipRoot", "ScreenMenuRoot", "TabletMenuRoot",
    "ToolPanelRoot",
]

CONTENT_TYPES = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="bmp" ContentType="image/bmp" />'
    '<Default Extension="cui" ContentType="text/xml" />'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml" />'
    '<Default Extension="xml" ContentType="text/xml" />'
    '</Types>'
)


def uid(rodzaj, klucz):
    """Identyfikator stabilny i unikalny w obrebie pliku.

    Z nazwy komendy, nie z licznika i nie z losu: ta sama komenda dostaje ten sam UID
    przy kazdym generowaniu. Dzieki temu diff pokazuje realna zmiane, a nie przetasowanie.
    Wzorzec producenta to MMU_190_F3FF1 (grupa + skrot); nasz prefiks GSAI_ nie ma prawa
    zderzyc sie z niczym ich.
    """
    h = hashlib.sha1(("GSAI:" + rodzaj + ":" + klucz).encode("utf-8")).hexdigest()[:6].upper()
    return "%s_GSAI_%s" % (rodzaj, h)


def naglowek(korzen, tresc=""):
    return ('<?xml version="1.0"?>\n<%s %s>%s</%s>' % (korzen, NS, tresc, korzen)
            if tresc else '<?xml version="1.0"?>\n<%s %s />' % (korzen, NS))


def wczytaj():
    with io.open(MANIFEST, encoding="utf-8") as f:
        d = json.load(f)
    kom = [k for k in d["komendy"] if k.get("wlaczone")]
    if not kom:
        sys.exit("BLAD: komendy.json nie ma ani jednej pozycji z wlaczone=true.")
    widziane = set()
    for k in kom:
        n = k["komenda"]
        if n in widziane:
            sys.exit("BLAD: komenda %s wystepuje dwa razy." % n)
        widziane.add(n)
        k.setdefault("ikona", n)
    return d, kom


def panele(kom):
    """Kolejnosc paneli = kolejnosc pierwszego wystapienia w manifescie."""
    out = []
    for k in kom:
        for nazwa, lista in out:
            if nazwa == k["panel"]:
                lista.append(k)
                break
        else:
            out.append((k["panel"], [k]))
    return out


def menu_group(d, kom):
    czesci = []
    for k in kom:
        czesci.append(
            '    <MenuMacro UID=%s>\n'
            '      <Macro type="Any">\n'
            '        <Revision MajorVersion="19" MinorVersion="0" UserVersion="1" />\n'
            '        %s\n'
            '        <Name xlate="true" UID=%s>%s</Name>\n'
            '        <Command>%s%s</Command>\n'
            '        <HelpString xlate="true" UID=%s>%s</HelpString>\n'
            '        <SmallImage Name=%s />\n'
            '        <LargeImage Name=%s />\n'
            '      </Macro>\n'
            '    </MenuMacro>' % (
                quoteattr(uid("MMU", k["komenda"])), REV,
                quoteattr(uid("XLS", k["komenda"] + ":nazwa")), escape(k["nazwa"]),
                PREFIKS_MAKRA, escape(k["komenda"]),
                quoteattr(uid("XLS", k["komenda"] + ":opis")), escape(k["opis"]),
                quoteattr(k["ikona"] + "_16.bmp"), quoteattr(k["ikona"] + "_32.bmp"),
            ))
    return ('<?xml version="1.0"?>\n'
            '<MenuGroup %s Name=%s DisplayName=%s>\n'
            '  <MacroGroup Name="GsaiMacros" Citizen="A">\n%s\n  </MacroGroup>\n'
            '</MenuGroup>' % (NS, quoteattr(d["grupa"]), quoteattr(d["nazwa_grupy"]),
                              "\n".join(czesci)))


def ribbon_root(d, kom):
    grupy = panele(kom)

    src = []
    for nazwa, lista in grupy:
        btn = []
        for k in lista:
            btn.append(
                '        <RibbonCommandButton UID=%s Id="AcRibbonCommandButton" Text=%s '
                'ButtonStyle="LargeWithText" MenuMacroID=%s KeyTip="">\n'
                '          <TooltipTitle xlate="true" UID=%s>%s</TooltipTitle>\n'
                '          %s\n'
                '        </RibbonCommandButton>' % (
                    quoteattr(uid("RBNU", "btn:" + k["komenda"])), quoteattr(k["nazwa"]),
                    quoteattr(uid("MMU", k["komenda"])),
                    quoteattr(uid("XLS", k["komenda"] + ":dymek")), escape(k["opis"]), REV))
        src.append(
            '    <RibbonPanelSource UID=%s Text=%s HiddenInEditor="false" KeyTip="">\n'
            '      %s\n'
            '      <Name xlate="true" UID=%s>%s</Name>\n'
            '      <RibbonRow UID=%s>\n'
            '        %s\n%s\n'
            '      </RibbonRow>\n'
            '    </RibbonPanelSource>' % (
                quoteattr(uid("RBNU", "panel:" + nazwa)), quoteattr(nazwa), REV,
                quoteattr(uid("XLS", "panel:" + nazwa)), escape(nazwa),
                quoteattr(uid("RBNU", "row:" + nazwa)), REV, "\n".join(btn)))

    ref = []
    for nazwa, _ in grupy:
        ref.append(
            '      <RibbonPanelSourceReference UID=%s PanelId=%s ResizeStyle="Default">\n'
            '        %s\n'
            '      </RibbonPanelSourceReference>' % (
                quoteattr(uid("RBNU", "ref:" + nazwa)),
                quoteattr(uid("RBNU", "panel:" + nazwa)), REV))

    # WorkspaceBehavior="AddTabOnly" — dokladnie to, czego uzywa ich zakladka Express.
    # Znaczy: dolóz zakladke do przestrzeni roboczych, nie ruszaj niczego innego.
    return ('<?xml version="1.0"?>\n'
            '<RibbonRoot %s>\n'
            '  <RibbonPanelSourceCollection>\n%s\n  </RibbonPanelSourceCollection>\n'
            '  <RibbonTabSourceCollection>\n'
            '    <RibbonTabSource Text=%s UID=%s KeyTip="" WorkspaceBehavior="AddTabOnly">\n'
            '      %s\n'
            '      <Name xlate="true" UID=%s>%s</Name>\n%s\n'
            '    </RibbonTabSource>\n'
            '  </RibbonTabSourceCollection>\n'
            '</RibbonRoot>' % (
                NS, "\n".join(src),
                quoteattr(d["zakladka"]), quoteattr(uid("RBNU", "tab")), REV,
                quoteattr(uid("XLS", "tab")), escape(d["zakladka"]), "\n".join(ref)))


def pop_menu_root(d, kom):
    """Menu klasyczne. Plaskie — jedna pozycja na komende.

    Producent robi tu podmenu (PopMenuRef -> osobny PopMenu). Przy siedmiu narzedziach
    podmenu to samo klikania wiecej i nic w zamian. Wrocic, gdy pozycji bedzie ~15.
    """
    poz = []
    for k in kom:
        poz.append(
            '    <PopMenuItem UID=%s>\n'
            '      %s\n'
            '      <Name xlate="true" UID=%s>%s</Name>\n'
            '      <MenuItem>\n'
            '        <MacroRef MenuMacroID=%s />\n'
            '      </MenuItem>\n'
            '    </PopMenuItem>' % (
                quoteattr(uid("PMU", k["komenda"])), REV,
                quoteattr(uid("XLS", k["komenda"] + ":menu")), escape(k["nazwa"]),
                quoteattr(uid("MMU", k["komenda"]))))
    return ('<?xml version="1.0"?>\n'
            '<PopMenuRoot %s>\n'
            '  <PopMenu hasDiesel="false" UID=%s>\n'
            '    %s\n'
            '    <Alias>POP12</Alias>\n'
            '    <Name xlate="true" UID=%s>%s</Name>\n%s\n'
            '  </PopMenu>\n'
            '</PopMenuRoot>' % (
                NS, quoteattr("ID_MN" + d["grupa"]), REV,
                quoteattr(uid("XLS", "popmenu")), escape(d["nazwa_grupy"]), "\n".join(poz)))


def toolbar_root(d, kom):
    """Pasek narzedzi — to jest odpowiedz na interfejs klasyczny.

    ToolbarVisible="hide": pasek istnieje, ale nie wyskakuje sam na srodek ekranu
    przy pierwszym uruchomieniu. User wlacza go z listy paskow. Tak robi producent
    i tak jest grzeczniej.
    """
    btn = []
    for k in kom:
        btn.append(
            '    <ToolbarButton IsSeparator="false" UID=%s>\n'
            '      %s\n'
            '      <Name xlate="true" UID=%s>%s</Name>\n'
            '      <MenuItem>\n'
            '        <MacroRef MenuMacroID=%s />\n'
            '      </MenuItem>\n'
            '    </ToolbarButton>' % (
                quoteattr(uid("TBBU", k["komenda"])), REV,
                quoteattr(uid("XLS", k["komenda"] + ":pasek")), escape(k["nazwa"]),
                quoteattr(uid("MMU", k["komenda"]))))
    return ('<?xml version="1.0"?>\n'
            '<ToolbarRoot %s>\n'
            '  <Toolbar ToolbarOrient="floating" ToolbarVisible="hide" xval="200" yval="150" '
            'rows="1" UID=%s>\n'
            '    %s\n'
            '    <Alias>%s</Alias>\n'
            '    <Name xlate="true" UID=%s>%s</Name>\n%s\n'
            '    <Description xlate="true" UID=%s>%s</Description>\n'
            '  </Toolbar>\n'
            '</ToolbarRoot>' % (
                NS, quoteattr(uid("TBU", "pasek")), REV, escape(d["grupa"]),
                quoteattr(uid("XLS", "pasek")), escape(d["nazwa_grupy"]), "\n".join(btn),
                quoteattr(uid("XLS", "pasek:opis")), escape(d["nazwa_grupy"])))


def package_info(pliki):
    p = ['  <PartData PartData_Name="/%s" PartData_Modified="2026-01-01T00:00:00.0000000+01:00" />' % f
         for f in pliki]
    return ('<?xml version="1.0" encoding="utf-8"?>\n<MenuPackageParts>\n%s\n</MenuPackageParts>'
            % "\n".join(p))


def sprawdz_ikony(kom):
    """Brak ikony nie jest bledem — grafiki jeszcze nie ma, a plik ma sie zbudowac.

    Ale przycisk bez ikony to przycisk, ktorego nikt nie znajdzie. Wiec ma byc glosno.
    """
    brak = []
    for k in kom:
        for rozmiar in (16, 32):
            p = os.path.join(IKONY, "%s_%d.bmp" % (k["ikona"], rozmiar))
            if not os.path.exists(p):
                brak.append(os.path.relpath(p, KATALOG))
    return brak


def main():
    ap = argparse.ArgumentParser(description="Generuje gsai.cuix z komendy.json")
    ap.add_argument("--wyjscie", default=os.path.join(KATALOG, "gsai.cuix"))
    ap.add_argument("--wypakuj", metavar="KATALOG",
                    help="zapisz tez rozpakowany XML do obejrzenia")
    a = ap.parse_args()

    d, kom = wczytaj()

    czesci = {
        "Header.cui": ('<?xml version="1.0"?>\n<CustSection %s>\n'
                       '  <FileVersion MajorVersion="0" MinorVersion="6" '
                       'IncrementalVersion="1" UserVersion="0" />\n'
                       '  <Header>\n    <CommonConfiguration>\n      <CommonItems>\n'
                       '        %s\n'
                       '      </CommonItems>\n    </CommonConfiguration>\n  </Header>\n'
                       '</CustSection>' % (NS, REV)),
        "MenuGroup.cui": menu_group(d, kom),
        "RibbonRoot.cui": ribbon_root(d, kom),
        "PopMenuRoot.cui": pop_menu_root(d, kom),
        "ToolbarRoot.cui": toolbar_root(d, kom),
        "WorkspaceRoot.cui": naglowek("WorkspaceRoot", "\n  <WorkspaceConfigRoot />\n"),
        "PanelSetRoot.cui": naglowek(
            "PanelSetRoot", '\n  <PanelSet UID=%s />\n' % quoteattr(uid("PSTU", "panelset"))),
    }
    for p in PUSTE:
        czesci[p + ".cui"] = naglowek(p)
    czesci["Menu_Package_Info.xml"] = package_info(sorted(czesci.keys()) + ["Menu_Package_Info.xml"])
    czesci["[Content_Types].xml"] = CONTENT_TYPES

    # Ikony wchodza DO paczki. Bierzemy te, ktore istnieja — brak nie jest bledem,
    # GstarCAD wstawi wtedy swoje logo, co jest widoczne od razu.
    spakowane = []
    for k in kom:
        for rozmiar in (16, 32):
            plik = os.path.join(IKONY, "%s_%d.bmp" % (k["ikona"], rozmiar))
            if os.path.exists(plik):
                spakowane.append(plik)

    with zipfile.ZipFile(a.wyjscie, "w", zipfile.ZIP_DEFLATED) as z:
        for nazwa in sorted(czesci):
            zi = zipfile.ZipInfo(nazwa, DATA_ZIP)
            zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, czesci[nazwa].encode("utf-8"))
        # Ikony ida do KORZENIA paczki — podkatalog nie dziala (sprawdzone 2026-07-18).
        for plik in sorted(spakowane):
            zi = zipfile.ZipInfo(os.path.basename(plik), DATA_ZIP)
            zi.compress_type = zipfile.ZIP_DEFLATED
            with open(plik, "rb") as f:
                z.writestr(zi, f.read())

    if a.wypakuj:
        if os.path.isdir(a.wypakuj):
            shutil.rmtree(a.wypakuj)
        os.makedirs(a.wypakuj)
        for nazwa, tresc in czesci.items():
            with io.open(os.path.join(a.wypakuj, nazwa), "w", encoding="utf-8") as f:
                f.write(tresc)

    print("Zbudowany: %s (%d B)" % (a.wyjscie, os.path.getsize(a.wyjscie)))
    print("Komend: %d, paneli: %d" % (len(kom), len(panele(kom))))

    brak = sprawdz_ikony(kom)
    if brak:
        print("\nUWAGA: brakuje %d plikow ikon. Przyciski beda, ikon nie." % len(brak))
        for p in brak[:6]:
            print("  - " + p)
        if len(brak) > 6:
            print("  ... i %d dalszych" % (len(brak) - 6))
        print("Nazwa pliku JEST mechanizmem wiazania — musi zgadzac sie co do znaku (z rozszerzeniem .bmp).")


if __name__ == "__main__":
    main()
