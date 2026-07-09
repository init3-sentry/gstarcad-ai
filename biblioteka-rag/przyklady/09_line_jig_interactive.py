# Wzorcowa komenda 09 — Interakcyjne rysowanie linii z podglądem (jig).
#
# Demonstruje mechanizm "jig" — interakcyjne rysowanie z podglądem w czasie
# rzeczywistym, gdy użytkownik porusza kursorem. Klasyczny wzorzec CAD-owy:
# linia elastyczna od punktu startowego do bieżącej pozycji kursora, dopóki
# użytkownik nie kliknie punktu końcowego.
#
# Wzorzec kanoniczny z oficjalnego samples linejig.py.
#
# Sposób użycia: APPLOAD w GstarCAD 2026/2027, następnie wpisz
# RYSUJ_LINIE_INTERAKTYWNIE. Komenda poprosi o punkt startowy — po jego wskazaniu
# do kursora "przyklei się" linia, którą można umieścić klikiem w drugim punkcie.
#
# Konwencje (v2 przewodnika-systemowego + linejig.py):
#   - Dziedziczymy z GcEdJig i nadpisujemy 4 metody:
#       sampler()  — pobiera nowy input, zwraca status
#       update()   — aktualizuje encję na podstawie inputu
#       entity()   — zwraca encję renderowaną podczas draggingu
#       doIt()     — orchestrator: prompt + drag() + append()
#   - drag() renderuje encję w pętli aż użytkownik kliknie
#   - append() dodaje encję do rysunku po zaakceptowaniu

from pygcad.core.runtime import *
from pygcad.pygrx import *


class LineJig(GcEdJig):
    """Jig rysujący linię — start punkt fiksowany, koniec śledzi kursor."""

    def __init__(self, startPt: GcGePoint3d):
        GcEdJig.__init__(self)
        self.startPt = startPt
        # Startowy koniec: mały offset od start, żeby linia miała jakąś długość
        self.endPt = startPt + GcGeVector3d(1.0, 1.0, 0.0)
        self.line = GcDbLine(self.startPt, self.endPt)

    def sampler(self):
        """Pobiera aktualną pozycję kursora. Zwraca status jig-a."""
        pt = GcGePoint3d(self.endPt.x, self.endPt.y, self.endPt.z)
        status = self.acquirePoint(pt, self.startPt)
        if status != GcEdJig.kNormal:
            return status
        if self.endPt == pt:
            return GcEdJig.kNoChange
        self.endPt = pt
        return status

    def update(self):
        """Odświeża geometrię encji na podstawie aktualnego endPt."""
        self.line.setEndPoint(self.endPt)
        return True

    def entity(self):
        """Zwraca encję renderowaną w trakcie draggingu."""
        return self.line

    def doIt(self):
        """Orchestrator: prompt do usera + drag loop + append do rysunku."""
        self.setDispPrompt("\nWskaż punkt końcowy: ")
        self.drag()
        self.append(self.line)


@command(local_name='RYSUJ_LINIE_INTERAKTYWNIE')
def drawLineByJig():
    """Interakcyjne rysowanie linii z podglądem — jig od punktu startowego."""
    try:
        # Punkt startowy — zwykły gcedGetPoint (bez jig-a, bo nie ma czego draggować)
        startPt = GcGePoint3d()
        status = gcedGetPoint(None, "\nWskaż punkt startowy: ", startPt)
        if status != RTNORM:
            gcutPrintf("\nAnulowano.")
            return

        # Uruchom jig — od tego momentu do kursora przyklejona jest linia
        jig = LineJig(startPt)
        jig.doIt()

        gcutPrintf("\nLinia interakcyjna narysowana.")

    except Exception as err:
        gcutPrintf(f"\n[BŁĄD] przy interakcyjnym rysowaniu linii: {err}")
