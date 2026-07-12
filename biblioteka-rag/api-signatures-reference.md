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

