# Skrypty pomocnicze projektu gstarcad-ai

Folder zawiera narzędzia pomocnicze do nadzorowania i obsługi technicznej projektu.

## Skrypty

| Plik | Co robi | Uruchamiany przez |
|---|---|---|
| `przeglad-tygodniowy.sh` | Cotygodniowy raport nadzorczy stanu projektu | procedurę `launchd` (piątek 8:00) |
| `pro.init3.tygodniowy-przeglad-gstarcad.plist` | Konfiguracja procedury `launchd` | jednorazowo, przez chezmoi |

## Mechanizm cotygodniowego nadzoru

Skrypt `przeglad-tygodniowy.sh` jest sercem mechanizmu nadzoru projektu. Uruchamiany automatycznie w każdy piątek o godzinie ósmej rano lokalnego czasu, robi następujące rzeczy:

1. **Pobiera świeży stan repozytorium** — wykonuje `git pull origin main`, żeby ostatnie zatwierdzenia wszystkich osób były lokalne.
2. **Czyta wszystkie pliki zadań** w folderze `tasks/` i klasyfikuje je po statusie (oczekuje, w trakcie, zakończone).
3. **Czyta zatwierdzenia z ostatnich siedmiu dni** z `git log` — żeby zobaczyć, kto co robił przez tydzień.
4. **Generuje raport** w folderze `przeglady/` o nazwie `RRRR-MM-DD-przeglad.md`. Raport zawiera trzy akapity: co się stało, ocena tempa, rekomendacja działania.
5. **Wypycha raport** z powrotem do publicznego repozytorium, dla zachowania jawności.
6. **Wysyła powiadomienie push** do Dawida przez `ntfy.init3.pro` z jednolinijkowym werdyktem — żeby Dawid wiedział, czy musi otworzyć raport, czy może odłożyć na pożniejszą porę.

Werdykt może być jedną z trzech kategorii:

| Symbol | Kategoria | Kiedy |
|---|---|---|
| 🟢 | dobry | Co najmniej cztery zatwierdzenia w tygodniu, zadania się posuwają |
| 🟡 | średni | Jedno do trzech zatwierdzeń, ostrzeżenie |
| 🔴 | mizerny | Zero zatwierdzeń, projekt utknął — czas na interwencję |

## Instalacja mechanizmu

Per stała reguła `decision_mbp_default_actions`, instalacja procedury `launchd` na MBP wymaga przejścia przez chezmoi i wpisania do `MBP-Runbook`. Pełen przepis:

### Krok pierwszy — skopiuj plik konfiguracyjny do chezmoi

```bash
cp ~/Code/gstarcad-ai/skrypty/pro.init3.tygodniowy-przeglad-gstarcad.plist \
   ~/.local/share/chezmoi/private_Library/LaunchAgents/
```

### Krok drugi — zatwierdź zmianę chezmoi

```bash
cd ~/Code/init3-dotfiles
git add -A
git commit -m "Dodaj procedurę pro.init3.tygodniowy-przeglad-gstarcad"
git push
```

### Krok trzeci — zastosuj chezmoi do bieżącej maszyny

```bash
chezmoi apply
```

### Krok czwarty — załaduj procedurę do `launchd`

```bash
launchctl load ~/Library/LaunchAgents/pro.init3.tygodniowy-przeglad-gstarcad.plist
```

### Krok piąty — zweryfikuj, że działa

```bash
launchctl list | grep tygodniowy-przeglad
```

Powinien się pokazać wpis z PID -1 (nie uruchomiony jeszcze, ale gotowy do uruchomienia w najbliższy piątek).

### Krok szósty — wpis do MBP-Runbook

Otwórz `~/Code/init3-runbooks/MBP-Runbook.md`, sekcja „LaunchAgents", dodaj wpis o nowej procedurze. Następnie zatwierdź zmiany w `init3-runbooks`.

## Test ręczny

Przed pozostawieniem mechanizmu do automatycznego uruchamiania warto raz odpalić go ręcznie i sprawdzić, że wszystko działa.

```bash
~/Code/gstarcad-ai/skrypty/przeglad-tygodniowy.sh
```

Po wykonaniu sprawdź:

- Czy w folderze `~/Code/gstarcad-ai/przeglady/` pojawił się plik z dzisiejszą datą?
- Czy nowy plik został zatwierdzony i wypchnięty do repozytorium GitHub?
- Czy w aplikacji powiadomień (lub na telefonie Dawida) pojawiło się powiadomienie push?
- Czy dziennik `~/Library/Logs/pro.init3.tygodniowy-przeglad-gstarcad.log` zawiera kompletną historię uruchomienia bez błędów?

Jeśli wszystkie cztery odpowiedzi to „tak" — mechanizm jest gotowy. Może być pozostawiony do automatycznego uruchamiania.

## Co jeśli coś nie działa

Najczęstsze problemy:

**Brak NTFY_TOKEN.** Skrypt szuka pliku `~/.config/init3/load-env.sh`. Jeśli go nie ma — pominie powiadomienie push i wpisze do dziennika informację. Wszystko inne (raport, zatwierdzenie, wypchnięcie) działa.

**Brak uprawnień do `git push`.** Sprawdź, czy `gh auth status` pokazuje login. Skrypt zakłada, że jesteś zalogowany jako `init3-sentry` z prawem do zapisu.

**Procedura nie uruchamia się o czasie.** Sprawdź `launchctl list | grep tygodniowy-przeglad`. Jeśli wpis nie istnieje — uruchom `launchctl load`. Jeśli istnieje, ale PID jest `-1` cały tydzień — sprawdź, czy plik plist ma poprawnie sformatowany `StartCalendarInterval`.

**Skrypt wywala się przy pierwszym uruchomieniu.** Sprawdź dziennik błędów `~/Library/Logs/pro.init3.tygodniowy-przeglad-gstarcad.err.log`.

---

*Wersja: 1.0 — 30 czerwca 2026*
