# pygcad — Verified API Signatures (reference)

Referencja sygnatur API pygcad wyprowadzona z oficjalnych stubów `pygrx.pyi` (443 klasy,
~19 tys. sygnatur) z instalacji GstarCAD 2027. **Wydzielona z `przewodnik-systemowy.md`
przy konsolidacji SoT (2026-07-12):** operacyjny system prompt = `poc-plugin-askai/backend/system-prompt.md`;
ta referencja to materiał głębszy dla RAG / ludzi — celowo NIE leci w prompcie przy każdym żądaniu
(zbyt ciężki), ale karmi kolekcję OWUI `gstarcad-ai-knowledge` przez zwykły sync repo.

Metoda i liczba argumentów są wiążące; adnotacje typów zwrotnych są C++-generowane (traktuj luźno).

---

## Verified API signatures (from the official pygcad type stubs)

**Source and how to read this.** These signatures come from the official pygcad type stubs (`pygrx.pyi`, 443 classes, ~19,000 method signatures) shipped **inside the GstarCAD 2027 install** (`plugins/pygrx.bundle/…`). They are the authoritative statement of *which methods exist and how many arguments they take*. Two honesty caveats: (1) the stubs are auto-generated from the C++ SDK, so some return-type annotations are C++ types (`double`, `void`, `handle`, `buffer`) and some methods appear twice as overloads — trust the **method name** and **argument count**, treat the annotation loosely; (2) existence in the stub is not the same as a runtime pass here, so these are tagged 🟡 (official material, not yet exercised end-to-end on our LC). Where a stub signature contradicts what your ObjectARX training data suggests, **follow the stub** — it describes *this* API.

The point of this section: the workhorse operations (batch text edits, attribute extraction, renumbering) all hinge on reading/writing strings on text and attribute entities. The exact method names differ per class, and guessing wrong is the #1 source of broken generated code. Use the tables below verbatim.

### Reading and writing text strings — per class

`GcDbAttribute` inherits from `GcDbText` (confirmed: `class GcDbAttribute(GcDbText)`), so an attribute's **value** uses the *text* API, while its **tag** uses the attribute API. `GcDbMText` is a different class with its own method names.

| Class | Read the string (getter) | Write the string (setter) |
|---|---|---|
| `GcDbText` | `textString()` → str  (also `textStringConst()` → str) | `setTextString(str)` |
| `GcDbAttribute` *(is-a GcDbText)* | `textString()` / `textStringConst()` — the attribute's **value** | `setTextString(str)` |
| `GcDbMText` | `contents()` → str  (also `text()` → str) | `setContents(str)` |

Attribute **tag** (which slot it is, e.g. `NUMER`, `OPIS`): `tag()` → str (also `tagConst()`), set with `setTag(str)`. The tag is *not* the value — read/change the value with the text getters/setters above.

```python
# Uniwersalny odczyt stringa z encji tekstowej — WYBIERZ metodę wg klasy, nie zgaduj:
cls = ent.isA().name()
if "MText" in cls:
    s = ent.contents()          # GcDbMText
else:
    s = ent.textString()        # GcDbText oraz GcDbAttribute (dziedziczy z GcDbText)

# Zapis analogicznie:
if "MText" in cls:
    ent.setContents(nowy)       # GcDbMText
else:
    ent.setTextString(nowy)     # GcDbText / GcDbAttribute
```

(A defensive "try several getter names" helper is acceptable as a fallback, but prefer the class-directed form above — it is confirmed and self-documenting.)

### Block-reference attributes — iterate and open

Confirmed signatures on `GcDbBlockReference` (is-a `GcDbEntity`) and the iterator it returns:

- `attributeIterator()` → `GcDbObjectIterator`
- `openAttribute(id: GcDbObjectId, openMode, openErasedOne=False)` → `(status, GcDbAttribute)` — returns a tuple, unpack it
- `GcDbObjectIterator`: `start(atEnd=False)`, `done()` → bool, `step(backwards=False, skipDeleted=False)`, `objectId()` → `GcDbObjectId`

```python
it = blockRef.attributeIterator()
it.start()
while not it.done():
    attrId = it.objectId()
    status, attr = blockRef.openAttribute(attrId, GcDb.kForRead)
    if status == Gcad.eOk and attr is not None:
        tag = attr.tag()                # który to atrybut
        value = attr.textString()       # jego wartość (API tekstu — dziedziczy z GcDbText)
        attr.close()
    it.step()
```

**Block name** — there is **no** `GcDbBlockReference.blockName()`. Get the name through the block-table record the reference points to:

```python
recId = blockRef.blockTableRecord()               # GcDbObjectId definicji bloku
status, rec = gcdbOpenObject(recId, GcDb.kForRead)
if status == Gcad.eOk:
    status, name = rec.getName()                  # (status, nazwa) — getName zwraca krotkę
    rec.close()
```

### Object handle (stable per-entity identifier)

A handle is the persistent hex id you use to match an entity across an export/import round-trip. On any `GcDbObject`:

- `handle()` → `GcDbHandle` (alias `getGcDbHandle()`)
- `GcDbHandle.getIntoAsciiBuffer()` → `(bool, str)` — the hex string. There is **no** `.ascii()` method.
- `GcDbHandle.isNull()` → bool

```python
ok, hex_id = ent.handle().getIntoAsciiBuffer()    # np. (True, "2F3")
if not ok:
    hex_id = ""                                    # brak handle — nie dopasowuj po nim
```

### Input / selection free functions — exact shapes

Confirmed from the stubs. Note the **asymmetry**: some return a `(status, value)` tuple, others return only a status and write the result into a buffer you pass in. Getting this wrong (unpacking a non-tuple, or ignoring the out-parameter) is a common failure.

| Function | Signature | Returns |
|---|---|---|
| `gcedGetInt` | `gcedGetInt(prompt)` | `(status, int)` |
| `gcedGetString` | `gcedGetString(cronly, prompt)` | `(status, str)` — `cronly=1` allows spaces |
| `gcedGetKword` | `gcedGetKword(prompt)` | `(status, str)` |
| `gcedGetReal` | `gcedGetReal(prompt, result)` | `status` — **writes into `result`** |
| `gcedGetPoint` | `gcedGetPoint(pt, prompt, result)` | `status` — **writes into `result`** |
| `gcedGetDist` | `gcedGetDist(pt, prompt)` | `(status, float)` |
| `gcedGetAngle` | `gcedGetAngle(pt, prompt)` | `(status, float)` |
| `gcedGetCorner` | `gcedGetCorner(pt, prompt, result)` | `status` — writes into `result` |
| `gcedSSGet` | `gcedSSGet(str, pt1, pt2, filter, ss)` | `status` — fills selection set `ss` |
| `gcedSSLength` | `gcedSSLength(ss)` | `(status, int)` |
| `gcedSSName` | `gcedSSName(ss, i, entres)` | `status` — writes name into `entres` |
| `gcdbOpenObject` | `gcdbOpenObject(id, mode, openErased=False)` | `(status, GcDbObject)` |
| `gcdbOpenGcDbEntity` | `gcdbOpenGcDbEntity(id, mode, openErasedEntity=False)` | `(status, GcDbEntity)` |
| `gcdbWorkingDatabase` | `gcdbWorkingDatabase()` | `GcDbDatabase` |

Compare against `RTNORM` for the input functions and `Gcad.eOk` for the `gcdb*` object openers (see the status-codes section — they are different families).

### Methods that do NOT exist (common ObjectARX-style guesses to avoid)

The stubs confirm these are absent in pygcad — do not generate them:

- `GcDbBlockReference.blockName()` → use `blockTableRecord()` + record `getName()` (above).
- `GcDbHandle.ascii()` → use `getIntoAsciiBuffer()`.
- `GcDbLayerTableRecord.setColorIndex()` / `.colorIndex()` → go through `GcCmColor` (pitfalls 1 & 5).

---

## Warstwa ZWERYFIKOWANA NA ŻYWO (🟢) — generatywne rysowanie

> **Ta sekcja rośnie z każdym narzędziem.** Reguła żywej bazy: gdy skrypt przejdzie test **na LC / w GstarCAD** (nie tylko walidator), jego zweryfikowane kształty wywołań lądują tu z 🟢 i datą. Stub (`pygrx.pyi`) mówi *„metoda istnieje"* — NIE mówi *„tak się ją woła i to działa"* (patrz BUG-06/07/10 niżej). Ta warstwa to jedyne, czemu można ufać w 100%.
>
> **Legenda źródła:** 🟢 uruchomione na żywo w GstarCAD · 🟡 w stubie, nie odpalone end-to-end · ⛔ zakazane (truje sesję / nieużywalne z Pythona).

### 🟢 Konstruktory encji (geometria) — potwierdzone na LC

Źródło: `GSAI_SCHODY` (RZUT/ŁUK/PRZEKRÓJ) — 3/3 tryby narysowane na żywo, GstarCAD 2027, 2026-07-29.

| Encja | Konstruktor (działa) | Uwagi |
|---|---|---|
| `GcDbLine` | `GcDbLine(GcGePoint3d, GcGePoint3d)` | dwa punkty świata |
| `GcDbPolyline` | `GcDbPolyline()` + `addVertexAt(i, GcGePoint2d, bulge, startW, endW)` | wierzchołki 2D; `bulge=0` = prosto; domknij powtarzając pierwszy punkt |
| `GcDbArc` | `GcDbArc(center: GcGePoint3d, radius: float, startAngle: float, endAngle: float)` | rysuje **CCW** od start do end; kąty w radianach |
| `GcDbText` | `GcDbText(GcGePoint3d, str)` + `setHeight(float)` | tekst upright; wysokość osobnym setterem |

Wspólny finał każdej encji (potwierdzony):

```python
ent.setLayer("NAZWA_WARSTWY")            # 🟢 str, nie ObjectId
st, _id = ms.appendGcDbEntity(ent)       # 🟢 zwraca (status, GcDbObjectId) — rozpakuj
# ... a potem ZAWSZE:
ent.close()                              # w finally
```

### 🟢 Warstwa i przestrzeń modelu — BEZ castu

Źródło: `GSAI_SCHODY` live. To jest wzorzec „utwórz warstwę, otwórz model space" który nie truje sesji (kontra BUG-07).

```python
# Warstwa (idempotentnie) — GcDbLayerTableRecord przez add(), zero .cast():
st, tabela = db.getLayerTable(GcDb.kForWrite)      # 🟢
if not tabela.has(nazwa):
    rec = GcDbLayerTableRecord()                   # 🟢
    rec.setName(nazwa)
    kolor = GcCmColor(); kolor.setColorIndex(idx)  # 🟢 kolor przez GcCmColor, NIE przez rekord
    rec.setColor(kolor)
    tabela.add(rec); rec.close()
tabela.close()                                     # w finally

# Model space — getAt zwraca od razu typowaną podklasę, cast zbędny:
st, bt = db.getBlockTable(GcDb.kForRead)           # 🟢
st, ms = bt.getAt(GCDB_MODEL_SPACE, GcDb.kForWrite)# 🟢 typowane, bez .cast()
bt.close()
```

### 🟢 Wejście użytkownika — potwierdzone kształty (live)

```python
st, txt = gcedGetString(0, "\nPytanie <domyślne>: ")   # 🟢 (st, str). cronly=1 pozwala spacje
pt = GcGePoint3d()
st = gcedGetPoint(None, "\nWskaż punkt:", pt)           # 🟢 param WYJŚCIOWY pt, status w return
if st == RTNORM: ...                                    # input funkcje -> RTNORM (nie Gcad.eOk!)
```

> **Liczby: NIE `gcedGetReal`.** Pytaj `gcedGetString` i parsuj `float`/`int` sam (obsłuż `,`→`.` i Enter→domyślna). Powód niżej (BUG-06).

### 🟡 Gotowe do promocji (w stubie, wejdą z najbliższym narzędziem)

Zgrepane w `pygrx.pyi` 2026-07-29, jeszcze nie odpalone — pierwszy skrypt, który ich użyje, przenosi je do 🟢:

| Encja | Konstruktor (stub) |
|---|---|
| `GcDbCircle` | `GcDbCircle(cntr: GcGePoint3d, nrm: GcGeVector3d, radius: float)` — normalna zwykle `GcGeVector3d(0,0,1)` |
| `GcDbEllipse` | `GcDbEllipse(center, unitNormal: GcGeVector3d, majorAxis: GcGeVector3d, radiusRatio: float[, startAngle, endAngle])` |

> **Kształty okrągłe — idiom 🟢 (potwierdzony na LC 2026-07-29, `GSAI_MEBLE` stół okrągły):** rysuj koło dwoma pół-łukami `GcDbArc(c, r, 0, π)` + `GcDbArc(c, r, π, 2π)` (prymityw `GcDbArc` już 🟢). Renderuje pełny okrąg, przetrwa obrót (dodaj `rot` do obu kątów). Pełny okrąg jednym `GcDbArc(c,r,0,2π)` bywa zerowej długości — nie używać. `GcDbCircle`/`GcDbEllipse` (niżej) nadal 🟡 — wejdą, gdy jakiś skrypt będzie potrzebował prawdziwej elipsy.

### ⛔ ZAKAZANE — z bezpieczną alternatywą (rejestr bólu)

| API | Dlaczego ⛔ | Zamiast tego |
|---|---|---|
| `.cast()` (np. `GcDbLayerTableRecord.cast(rec)`) | **BUG-07** — nie crashuje od razu, **truje sesję**: następny dostęp do bazy / akcja usera wywala GstarCAD | otwórz rekord typowany wprost: `getAt(nazwa, mode)` zwraca podklasę |
| `gcedGetReal(prompt, result)` | **BUG-06** — parametr wyjściowy typu prostego, z Pythona nieużywalny | `gcedGetString` + parsowanie float |
| czytanie geometrii **wczytanych** encji (`getArea`, `getDistAtParam`, `length` na encji z DWG) | **BUG-10** — pygcad nie robi downcastu, encja otwiera się jako bazowy `GcDbEntity`, metody pochodne niedostępne → pada na plikach po ponownym otwarciu | narzędzia **generatywne** (twórz geometrię, nie czytaj cudzej). `getGeomExtents`/`layer()` = metody bazowe, bezpieczne |

> **Reguła projektowa, którą to wymusza:** domyślny kształt narzędzia GSAI = **generatywny** (rysuje nową geometrię). To automatycznie omija BUG-10 i większość pułapek odczytu. Odczyt cudzych encji tylko gdy narzędzie naprawdę o to jest, i wtedy tylko metodami bazowymi.

---


## GcDbSolid — wypełnienie (zweryfikowane na LC 2026-08-01, GstarCAD 2027 Premium)

🟢 **Wypełniony TROJKAT przez `GcDbSolid`: `setPointAt(0..3)` w kolejnosci `[A,B,C,A]` renderuje sie CZYSTO** (empirycznie, GSAI_SOLIDPROBE na LC). Testowano tez `[A,B,A,C]` (0-1-3-2) — tez czysty. Wniosek: dla trojkata (4. punkt = powtorzony wierzcholek) **kolejnosc nie tworzy „muszki"**; klasyczna pulapka bowtie 0-1-2-3 vs 0-1-3-2 dotyczy tylko prawdziwych **czworokatow** (4 rozne punkty). Wzorzec dzialajacy: `s=GcDbSolid(); for i,(x,y) in enumerate([A,B,C,A]): s.setPointAt(i, GcGePoint3d(x,y,0)); s.setLayer(...); ms.appendGcDbEntity(s)`. Uzywane w filled-strzalkach polnocy (polowa = trojkat solid).
