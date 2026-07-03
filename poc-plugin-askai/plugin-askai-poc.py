# Plugin ASKAI dla GstarCAD 2026 — Proof of Concept
# Wersja 0.1 — 1 lipca 2026
#
# Etap zerowy projektu gstarcad-ai. Realizuje dni 1-4 planu PoC opisanego
# w poc-plugin-askai/README.md:
#   - Dzień 1: minimalny plugin z komendą ASKAI otwierający okno tkinter
#   - Dzień 2: wywołanie HTTPS do backendu i odbiór odpowiedzi
#   - Dzień 3: strumieniowanie odpowiedzi z aktualizacją okna linia po linii
#   - Dzień 4: przycisk "Wykonaj tutaj" — uruchomienie wygenerowanego kodu
#             bezpośrednio w kontekście bieżącego rysunku
#
# Dzień 5 (podpięcie realnego modelu Anthropic zamiast stubu) realizowany
# jest po stronie backendu — patrz poc-plugin-askai/backend/.
#
# Sposób użycia w GstarCAD 2026:
#   1. Uruchom GstarCAD 2026
#   2. Wpisz w wierszu poleceń: APPLOAD
#   3. Wybierz ten plik i wciśnij Load
#   4. Wpisz w wierszu poleceń: ASKAI
#   5. Wpisz polecenie w polu (np. "narysuj okrąg o promieniu 5")
#   6. Wciśnij "Generuj kod" — kod pojawi się linia po linii
#   7. Wciśnij "Wykonaj tutaj" — kod uruchamia się w bieżącym rysunku

import json
import queue
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from urllib import request as urlrequest
from urllib.error import URLError, HTTPError

from pygcad.core.runtime import *
from pygcad.pygrx import *


BACKEND_URL = "https://gs-ai.init3.pro/api/generate"
BACKEND_TIMEOUT_SECS = 30
STREAM_CHUNK_BYTES = 64
UI_POLL_MS = 50


class AskaiDialog:
    # Modalne okno dialogowe pluginu ASKAI. Pobiera polecenie od użytkownika,
    # wysyła do backendu, wyświetla strumieniowo wygenerowany kod i pozwala
    # go wykonać w kontekście bieżącego rysunku.

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ASKAI — plugin dla GstarCAD (PoC 0.1)")
        self.root.geometry("760x560")
        self.root.minsize(600, 400)
        self.stream_queue = queue.Queue()
        self.stream_thread = None
        self._build_ui()

    def _build_ui(self):
        # Sekcja z poleceniem użytkownika
        prompt_frame = ttk.LabelFrame(self.root, text="Polecenie do wygenerowania", padding=8)
        prompt_frame.pack(fill=tk.X, padx=10, pady=(10, 4))
        self.prompt_entry = ttk.Entry(prompt_frame, font=("Segoe UI", 11))
        self.prompt_entry.pack(fill=tk.X, expand=True)
        self.prompt_entry.insert(0, "Narysuj okrąg o promieniu 5 w punkcie (0, 0)")
        self.prompt_entry.bind("<Return>", lambda e: self.on_generate())
        self.prompt_entry.focus_set()

        # Sekcja przycisków
        btn_frame = ttk.Frame(self.root, padding=(10, 4))
        btn_frame.pack(fill=tk.X)
        self.gen_btn = ttk.Button(btn_frame, text="Generuj kod", command=self.on_generate)
        self.gen_btn.pack(side=tk.LEFT, padx=(0, 6))
        self.exec_btn = ttk.Button(
            btn_frame, text="Wykonaj tutaj", command=self.on_execute, state=tk.DISABLED
        )
        self.exec_btn.pack(side=tk.LEFT, padx=6)
        self.clear_btn = ttk.Button(btn_frame, text="Wyczyść", command=self.on_clear)
        self.clear_btn.pack(side=tk.LEFT, padx=6)
        self.close_btn = ttk.Button(btn_frame, text="Zamknij", command=self.root.destroy)
        self.close_btn.pack(side=tk.RIGHT)

        # Sekcja wygenerowanego kodu
        code_frame = ttk.LabelFrame(self.root, text="Wygenerowany kod Pythona", padding=8)
        code_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=4)
        self.code_text = scrolledtext.ScrolledText(
            code_frame, font=("Consolas", 10), wrap=tk.NONE, height=18
        )
        self.code_text.pack(fill=tk.BOTH, expand=True)

        # Pasek statusu
        self.status_var = tk.StringVar(
            value="Gotowy. Wpisz polecenie i wciśnij Enter lub Generuj kod."
        )
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=4,
        )
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def on_generate(self):
        prompt = self.prompt_entry.get().strip()
        if not prompt:
            self.status_var.set("Wpisz polecenie zanim wciśniesz Generuj.")
            return

        # Reset UI przed nowym generowaniem
        self.code_text.delete("1.0", tk.END)
        self.exec_btn.config(state=tk.DISABLED)
        self.gen_btn.config(state=tk.DISABLED)
        self.status_var.set(f"Łączę z {BACKEND_URL}...")

        # Uruchom osobny wątek do pobierania — inaczej tkinter zamarza
        self.stream_thread = threading.Thread(
            target=self._fetch_stream, args=(prompt,), daemon=True
        )
        self.stream_thread.start()
        self.root.after(UI_POLL_MS, self._poll_queue)

    def _fetch_stream(self, prompt):
        # Uruchamiane w osobnym wątku — pobiera strumień odpowiedzi z backendu
        # i wrzuca chunki do kolejki dla wątku tkinter.
        try:
            body = json.dumps({"prompt": prompt}).encode("utf-8")
            req = urlrequest.Request(
                BACKEND_URL,
                data=body,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "gs-ai-plugin/0.1 (GstarCAD 2026)",
                    "Accept": "text/plain",
                },
                method="POST",
            )
            with urlrequest.urlopen(req, timeout=BACKEND_TIMEOUT_SECS) as response:
                while True:
                    chunk = response.read(STREAM_CHUNK_BYTES)
                    if not chunk:
                        break
                    self.stream_queue.put(("chunk", chunk.decode("utf-8", errors="replace")))
                self.stream_queue.put(("done", None))
        except HTTPError as e:
            self.stream_queue.put(("error", f"Błąd HTTP {e.code}: {e.reason}"))
        except URLError as e:
            self.stream_queue.put(("error", f"Brak połączenia z backendem: {e.reason}"))
        except Exception as e:
            self.stream_queue.put(("error", f"Nieoczekiwany błąd: {type(e).__name__}: {e}"))

    def _poll_queue(self):
        # Uruchamiane w wątku tkinter co UI_POLL_MS — pobiera chunki z kolejki
        # i aktualizuje pole tekstowe. Nie blokuje UI bo kolejka jest nieblokująca.
        try:
            while True:
                kind, payload = self.stream_queue.get_nowait()
                if kind == "chunk":
                    self.code_text.insert(tk.END, payload)
                    self.code_text.see(tk.END)
                elif kind == "done":
                    self.status_var.set(
                        "Kod wygenerowany. Zweryfikuj i wciśnij Wykonaj tutaj."
                    )
                    self.gen_btn.config(state=tk.NORMAL)
                    self.exec_btn.config(state=tk.NORMAL)
                    return
                elif kind == "error":
                    self.status_var.set(payload)
                    self.gen_btn.config(state=tk.NORMAL)
                    return
        except queue.Empty:
            pass
        # Zaplanuj kolejny odczyt kolejki
        self.root.after(UI_POLL_MS, self._poll_queue)

    def on_execute(self):
        code = self.code_text.get("1.0", tk.END).strip()
        if not code:
            self.status_var.set("Brak kodu do wykonania.")
            return

        # Przygotuj przestrzeń nazw dla exec — udostępnij pełne API pygcad.
        # Kod wygenerowany przez backend zakłada import z pygcad, ale wykonuje
        # się w izolowanym namespace — musimy podać referencje ręcznie.
        exec_namespace = dict(globals())
        exec_namespace["__name__"] = "askai_generated"

        try:
            exec(code, exec_namespace)
            self.status_var.set("Kod wykonany pomyślnie w bieżącym rysunku.")
            gcedPrompt("[ASKAI] Kod wykonany pomyślnie.")
        except Exception as e:
            error_msg = f"Błąd wykonania: {type(e).__name__}: {e}"
            self.status_var.set(error_msg)
            gcedPrompt(f"[ASKAI] {error_msg}")
            messagebox.showerror(
                "ASKAI — błąd wykonania kodu",
                f"{type(e).__name__}: {e}\n\nSprawdź kod w oknie ASKAI "
                "i zweryfikuj go przed ponownym wykonaniem.",
            )

    def on_clear(self):
        self.code_text.delete("1.0", tk.END)
        self.prompt_entry.delete(0, tk.END)
        self.exec_btn.config(state=tk.DISABLED)
        self.status_var.set("Wyczyszczone. Wpisz nowe polecenie.")
        self.prompt_entry.focus_set()

    def show(self):
        self.root.mainloop()


@command(local_name='ASKAI')
def openAskaiDialog():
    """Otwiera okno pluginu ASKAI — asystent AI do generowania komend GstarCAD."""
    try:
        gcedPrompt("[ASKAI] Otwieram okno pluginu...")
        dialog = AskaiDialog()
        dialog.show()
        gcedPrompt("[ASKAI] Okno zamknięte.")
    except Exception as err:
        gcedPrompt(f"---- [BŁĄD ASKAI]: {err}")
