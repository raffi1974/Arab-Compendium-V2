# Arab Society Compendium — pipeline (V2)

- Six notebooks make the deliverables. `data quality/`'s Part 1 runs first
  and gates them; its Part 2 checks the finished result afterward. Nothing
  in `data quality/` changes data on its own.
- Every output lands in the V2 root, `C:\RAFFI\DSS-local\COMPENDIUM ARAB
  SOCIETY - V2\`, in **one folder per chapter** under each kind of output —
  `Merged_long_files\Population_merged_long_files\`,
  `Tabulations\Population_tabulations\`, `Charts\Population_charts\`.

| # | Notebook | Reads | Writes |
|---|---|---|---|
| 1 | `Compendium_1_Long_Files.ipynb` | `DATA COLLECTOR\datacollector_received_quest\<Chapter>\*.xlsx` | `<Chapter>_EN.xlsx` (every questionnaire, in English) and `<Chapter>_AR.xlsx` (the Arabic ones, as they arrived) |
| 2 | `Compendium_2_New_Indicators.ipynb` | `<Chapter>_AR.xlsx` | the calculated rows, in Arabic, appended to it |
| 3 | `Compendium_3_External_Data.ipynb` | `DATA COLLECTOR\external data\<Chapter>\*.xlsx` | `<Chapter>_EN_external.xlsx`, plus a `*_reshaped.xlsx` questionnaire-layout copy of each source file |
| 4 | `Compendium_4_Translation.ipynb` | `<Chapter>_AR.xlsx` + `<Chapter>_EN_external.xlsx` | the calculated rows, translated, into `<Chapter>_EN.xlsx`; external data appended to it, and its Arabic form to `<Chapter>_AR.xlsx` |
| 5 | `Compendium_5_Tabulations.ipynb` | `<Chapter>_EN.xlsx`, `<Chapter>_AR.xlsx` | `Tabulations\<Chapter>_tabulations\<Chapter>_tabulations_<LANG>.xlsx` |
| 6 | `Compendium_6_Charts.ipynb` | `<Chapter>_EN.xlsx` | `Charts\<Chapter>_charts\` — an SVG and a PNG per figure, `<Chapter>_charts.xlsx`, `charts_index.csv`, `chart_data_findings.txt` |

- Notebooks 1–4 read and write `Merged_long_files\<Chapter>_merged_long_files\`
  — every long file of a chapter, in both languages, and notebook 3's output,
  sits in that one folder.
- `<Chapter>_charts.xlsx` lives only in `Charts\<Chapter>_charts\`, beside the
  SVGs and PNGs it indexes — never copied into `Merged_long_files\`, which is
  the long files' own; a copy there would just be one more place for the two
  to drift apart.
- **`data quality/Compendium_Data_Quality.ipynb`'s Part 1 runs before all
  six, and gates them.** It checks the raw questionnaires and
  `external data\<Chapter>\`, writes its findings to text files, and the
  pipeline stops there — notebook 1 does not run — until a person has
  reviewed those findings, made whatever corrections they call for, and
  told Claude to resume.
  - Not row 0 in the table above — it lives in `data quality/`, keeps its
    own name, and is documented in full in `data quality/CLAUDE.md` — but it
    is the first thing that runs, every time, including for a "run the
    pipeline" request with no other qualifier.
  - **Do not run notebook 1 to satisfy a pipeline request until this gate
    has cleared.** If it is unclear whether it already has, ask rather than
    assume.
- **1 → 2 → 3 → 4 in order**, after the quality gate; each reads what the
  previous wrote.
  - 3 only has anything to do when a chapter has an
    `external data\<Chapter>\` folder, but always sits between 2 and 4 so 4
    can fold in whatever 3 found.
  - **5 and 6 are independent siblings** — both read the finished long
    files, neither needs the other, either can be re-run alone — and both
    come after 4 to pick up calculated indicators and anything external.

## Notebook 1 — one folder in, one English file out

- **Every questionnaire, Arabic or English, comes from one folder**,
  `DATA COLLECTOR\datacollector_received_quest\`, with a subfolder per
  chapter (Education, Health, Housing, Labor, Population, Poverty). Every
  chapter folder holding at least one `.xlsx` is read; `CHAPTERS` in the
  `config` cell restricts a run.
- **Each file's language is decided by one simple rule — the script its
  column headers are written in** (`detect_language()`).
  - The headers are the ones on each sheet's `index` row: `المؤشر`,
    `الدولة`, `الجنس`, … in an Arabic file; `Indicator`, `Country`, `Sex`, …
    in an English one. Year columns are digits and are not counted.
  - A header "is Arabic" if it holds at least one letter from the Arabic
    Unicode block, U+0600–U+06FF. **If at least one of a file's headers,
    across all of its data sheets together, is Arabic, the file is Arabic**;
    only a file with no Arabic header at all is English. A file with no
    usable header falls back to `DEFAULT_LANGUAGE`, Arabic.
  - Headers, not cell values, because values include numbers, codes and
    citations that can be in either script — an Arabic questionnaire often
    cites its source in English.
  - Every sheet is processed in its file's language. Each sheet is also
    checked on its own, and one whose headers disagree with its file is
    reported as `sheet in a different language from its file`.
- **An Arabic file is corrected, cleaned and translated to English; an
  English file is corrected, cleaned and kept as it is.** Then:
  - everything, in English, is appended into `<Chapter>_EN.xlsx`;
  - the Arabic files are also saved together, untranslated, as
    `<Chapter>_AR.xlsx` — notebook 2 calculates on it, and notebook 5 builds
    the Arabic tabulations from it. A country whose questionnaire came in
    English is therefore in the English deliverables only.
  - Both files are rebuilt from scratch on every run, which drops whatever
    notebooks 2 and 4 added — re-run 2 and 4 after 1.
- **Anything the dictionary cannot translate passes through as it is** and
  is logged as `no English translation`, with the country, indicator and
  year it appears in, and left in `GAPS` in the notebook's namespace — the
  shape `update_dictionary()` takes. See **Filling dictionary gaps** below.

## How the rest fits around it

- **Notebook 3 reads published indicator tables that never went through a
  questionnaire**, one folder per chapter under
  `DATA COLLECTOR\external data\<Chapter>\`.
  - Every sheet carries two blocks, each under its own `index` header row —
    `index = 1` the data, `index = 2` its citation — the same convention
    notebook 1 reads a questionnaire with.
  - A sheet whose shape it does not recognize is **refused whole and
    reported**; there is no partial column to salvage, because there is no
    shape left to be partially sure of.
  - Follows the `reshape-external-data-questionnaire-layout` skill: besides
    the rows written to `<Chapter>_EN_external.xlsx`, it saves a reshaped,
    questionnaire-layout copy of each source file into the chapter's long
    files folder, for a person to check against the original.
  - **It does no translation** — only extraction and reshaping; notebook 4
    gives the result its Arabic form.
  - Read notebook 3's own intro cell before changing it — most of what
    looks arbitrary there is a finding from the real file, not a guess.
- **Notebook 4 translates only what notebook 1 could not.** The
  questionnaires are already English by the time it runs; what is left is:
  - notebook 2's calculated rows, in `<Chapter>_AR.xlsx` only — translated
    and put into `<Chapter>_EN.xlsx`;
  - notebook 3's external rows, in English only — appended to
    `<Chapter>_EN.xlsx`, and given an Arabic form for `<Chapter>_AR.xlsx`
    once the dictionary has one (`apply_external_gaps()`).
- **Notebook 4 strips before it appends, so it can be re-run on its own.**
  - It edits `<Chapter>_EN.xlsx` in place, the file notebook 1 wrote. It
    first removes every row an earlier run of itself added — calculated rows
    by their titles (`CALCULATED_TITLES`), external rows by `Data Origin` —
    and only then appends this run's.
  - Without that, a second run would append its own rows a second time.
  - The Arabic side uses the same idea: notebook 2 strips its own
    previously-added rows before appending, and notebook 4 strips its
    previous external rows from `<Chapter>_AR.xlsx` by `Data Origin`.
  - `CALCULATED_TITLES` repeats notebook 2's `SEX_RATIO_TITLE` and
    `AGE_SHARE_TITLE`; change one, change the other.
- **Calculations run before their rows are translated, on the Arabic file.**
  - Doing the arithmetic in Arabic means the calculated rows are created in
    Arabic and go one way, once — never translated *back*, through an
    inverted dictionary that is lossy wherever several Arabic spellings share
    one English term.
  - **Never reintroduce a back-translation.**
- Notebook 2's code uses English names — `"Male"`, `"Age Total"`,
  `"Population size by nationality"` — and `term()` resolves each into what
  the Arabic file says.
  - An unresolved name is reported, not silently passed through, since a
    calculation built on it matches nothing and quietly produces no rows.

## What the notebooks record

- **Notebooks 1–5 record what they find wrong with the source data**, split
  by what happened to it into two files per chapter, in the V2 root:
  `pipeline_changes_<Chapter>.txt` for everything a run fixed, inferred, or
  added to the dictionary on its own, and
  `need manual intervention_<Chapter>.txt` for everything it left alone and
  why — plus a `_general` pair for a dictionary-level finding with no
  chapter of its own.
  - Which file a finding lands in is decided once, by its own `kind`, in
    `save_inconsistencies()`'s `CHANGE_KINDS` set — not worked out by each
    notebook. A `kind` nobody has classified as a change yet defaults to
    manual intervention, on purpose, so a new one surfaces for a person to
    see rather than silently reading as "already handled".
  - Notebook 1 logs every column/value match against the dictionary — a fix
    to `pipeline_changes_<Chapter>.txt`, a miss to
    `need manual intervention_<Chapter>.txt` — every Value it corrected, and
    every Arabic value it could not translate.
  - Notebook 2 logs contradictions in the calculated figures.
  - Notebook 3 logs sheets it refused.
  - Notebook 4 logs values with no translation — `4. TRANSLATION` for the
    calculated rows, `4b. EXTERNAL DATA` for external data's own
    English → Arabic gaps.
  - Notebook 5 logs tabulations that came out wrong.
  - Every row `update_dictionary()` actually adds is logged as
    `dictionary entry added` — in `1b. DICTIONARY` or `4c. DICTIONARY`,
    whichever notebook's copy of the function was called.
  - Every record carries the country, indicator and year, so a finding
    traces back to the cell.
  - These are findings about the questionnaires, not the code — they outlive
    the run and can go back to the country that reported them.
- Each notebook owns one named section (`### 1. LONG FILES ###`, and so on)
  and rewrites only that section **within its own chapter's pair of
  files**.
  - `save_inconsistencies()` takes `chapters=` explicitly, so even a clean
    chapter gets both files' sections replaced with "Nothing found" instead
    of left stale — and a run scoped to one chapter never touches another
    chapter's findings.
- **Every dictionary correction is logged, not only the ones the fuzzy
  matcher gives up on.** `correct_with_dictionary()` logs `column name
  corrected` / `value corrected` for fixes (into
  `pipeline_changes_<Chapter>.txt`), `column name not in the dictionary` /
  `value not in the dictionary` for misses (into
  `need manual intervention_<Chapter>.txt`).
- Notebook 6 keeps its own `chart_data_findings.txt` per chart folder rather
  than a shared-log section, because it refuses figures the other five pass
  through — a value orders of magnitude off its own series, or sexes that
  don't sum to their reported total.

## Cleaning the Value column

- **Notebook 1 cleans the Value column and reports every change.**
  - A number wrapped in a recognized unit phrase is scaled to match:
    `بالالف` and the typo `بالاف` both mean "thousands", so
    `7845(الاعداد بالالف)` → `7845000`.
  - A placeholder like `-` becomes blank, and so does a cell holding only
    spaces — not an empty cell, and otherwise it passes every "is it blank"
    test through to an unplottable chart value.
  - `51.2+1.2` is read as a sum.
  - An unrecognized wrapping phrase is just dropped, keeping the bare number
    — reported every time, since an unfamiliar phrase could carry a
    multiplier too, and only the reporting country can say for sure.
- **A unit note describes the whole column it sits in, not the one cell it's
  written on.**
  - A country can file `1444`, `1745`, `1815`, … with `الاعداد بالالف` typed
    into only the first cell.
  - Scaling just that cell would leave it 1,000× larger than its neighbours,
    so the multiplier is applied to every figure sharing that
    indicator/country/year, and the block is reported with the count moved.
  - Scope is the year, because the same file can have earlier years in whole
    units and only the latest in thousands.

## Data quality and charts

- **Checking the data lives in `data quality/`**, its own `CLAUDE.md`. Two
  parts of one notebook, sharing nothing but a file:
  - **Part 1 is the pipeline's first step, and gates it** — see the bullet
    near the top of this file. It scans the raw questionnaires — each file
    read in the language `detect_language()` gives it, exactly as notebook 1
    reads it — and `external data\<Chapter>\`, and writes one read-only
    `Data quality issues before pipeline execution_<Chapter>.txt` per
    chapter: labels the dictionary can't match, Value cells
    `clean_one_value()` can't parse, structural problems, and any external
    sheet notebook 3 would refuse (found with notebook 3's own reader). This
    is Part 1's only output; a person corrects whatever it calls for
    directly, in the source file, and tells Claude to resume.
  - **Part 2** reads the finished `<Chapter>_EN.xlsx` files after notebook 4
    and writes `data_gaps_report.xlsx` plus the dashboard's `docs/data.js` —
    completeness and contradictions across the whole finished series.
  - Neither part changes data — both only measure and report.
- **How the charts look is settled in `charts_design.md`**, beside notebook
  6 — colours, fonts, layout rules, data guards, and the trade-offs each was
  chosen on.
  - Read it before changing anything visual; several of the odd-looking
    choices are load-bearing.
- **Every chapter's charts are copies of the figures the compendium
  prints.**
  - Originals: `COMPENDIUM-ARAB SOCIETY\old files\population old charts\<chapter>\`
    (plotly SVGs, `OLD_CHARTS_PATH` in the notebook) — in the original
    compendium folder, beside this V2 one. Nothing reads it at run time.
  - Notebook 6 has a hand-written set per chapter, numbered to match
    (`1.1`–`2.7` Population, `3.x` Housing, `4.x` Health, `5.x` Education,
    `6.x` Labor, `7.x` Poverty); a data-driven builder is the fallback for a
    chapter with no such set.
  - SVG text stays text, so a legend or axis label reads straight out with
    `grep`.

## Filling dictionary gaps — do this without being asked

- **When the user asks to run the pipeline, closing dictionary gaps is part
  of the job**, not a separate ask. All kinds must close before a run counts
  finished.
- This is the *during-and-after* loop — gaps found while running notebooks
  1, 2 and 4, closed by Claude's own judgement, during the **resumed** part
  of a run, after the quality gate has cleared.
  - The data quality notebook's Part 1 is the *before* loop, and the
    pipeline's literal first step — the same kinds, found by reading raw
    questionnaires and `external data\<Chapter>\` ahead of a run, closed by
    a person directly (editing the source questionnaire,
    `translation dict_V2.xlsx`, or `value corrections.xlsx` — there is no
    intermediate file to apply), with the run stopped until they do.
  - The two are meant to meet in the middle: the more the before-loop
    closes, the fewer the resumed run turns up.

### Kind 1 — a value the questionnaires used

- A country writes a survey name the dictionary hasn't seen.
- Notebook 1 finds these by comparing an Arabic file's table before and
  after translation — an untranslated value passed through is the gap.
- Always the English side, since every questionnaire travels Arabic →
  English.
- Mostly Source citations: `translation dict_V2.xlsx` started with none, so
  every statistical body and survey name is new to it the first time it is
  seen.

### Kind 2 — a label the pipeline invented

- The calculations invent indicator titles and age-group labels
  (`Sex ratio, 2010-2025 (per 100 females)`, `<15 years`, …) that appear in
  **no questionnaire**.
- Notebook 2 needs their Arabic to write the rows at all, so a missing one
  is caught immediately: `term()` reports it instead of falling back
  silently, listed as "term missing from the dictionary".

### Kind 3 — external data introduces a new English-origin value

- Notebook 3's `<Chapter>_EN_external.xlsx` output is genuinely new English
  content with no Arabic form anywhere yet.
- Notebook 4's external-data section finds these the same way
  (`find_external_gaps()`) but travelling English → Arabic, since this
  content started in English — giving it an Arabic form for the first time,
  never back-translating anything already correct.
- Closed the same way as the other kinds; see notebook 4's own intro cell
  for the two-part run this needs (append first, review `EXTERNAL_GAPS`,
  `update_dictionary()`, then `apply_external_gaps()`).

### The loop, any kind

1. Run the notebook — 1 for Kind 1, 2 for Kind 2, 4 for Kind 3 and for the
   calculated rows.
2. Read the gaps from that chapter's own `need manual intervention_<Chapter>.txt`
   — no spreadsheet is written. Each carries the country, indicator and year
   of an example row. Notebook 1 also leaves them in `GAPS`, notebook 4's
   external ones in `EXTERNAL_GAPS`.
3. Translate them yourself. Use the official English name of a statistical
   body where one exists — search `translation dict_V2.xlsx` first, so
   wording stays consistent with what is already there.
4. Call `update_dictionary(filled, chapter="<Chapter>")` — notebook 1 and
   notebook 4 each carry a copy. It backs the file up first, skips rows
   already present, marks what it adds with `status = "updated"` so machine
   translations can be told from hand-typed ones, and logs every row it
   actually adds to that chapter's own `pipeline_changes_<Chapter>.txt` as
   `dictionary entry added`.
5. Re-run the notebook and confirm the gap list in
   `need manual intervention_<Chapter>.txt` is empty.
6. Report what you added, and flag any translation involving real judgement.

- **Attach translations by position, never by retyping the Arabic or
  English keys** — a retyped string that differs by one invisible character
  (non-breaking space, different letter form) silently fails to match.
  - Assert a couple of anchor rows before writing.

## Running it

Two ways, and both are fine. Either way, a full run starts with
`data quality/Compendium_Data_Quality.ipynb`'s Part 1 and stops there —
review its findings, correct whatever they call for directly, then resume
with notebook 1.

### Running it yourself, in Jupyter or VS Code

- Open the notebook and run its cells top to bottom, same as any other
  notebook — nothing about these requires a special runner.
- To limit a run to one chapter, edit `CHAPTERS` in the cell whose id is
  `config`:

```python
CHAPTERS = ["Poverty"]      # instead of None
```

- `None` means every chapter found on disk.
- Nothing resets this for you, so set it back to `None` (or to the chapter
  you actually want) before the next full run.

### Running it through Claude

- Claude has no Jupyter kernel, so a notebook is run by reading its JSON and
  `exec`-ing each code cell's source into one namespace, in cell order —
  after the `config` cell has run, `CHAPTERS` is overridden in that
  namespace before the rest continue.
- `run_pipeline.py` is exactly that, generalised and committed so it is not
  retyped every session.

```bash
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 py -u run_pipeline.py 1 2 3 4 5 6 --only Population > run.log 2>&1
```

- Then **poll the log** — never wait blind on a long run.
  - `PYTHONUTF8=1` is not optional: the Arabic in the progress output kills
    the default Windows console encoding.
- `--only` overrides `CHAPTERS` the same way the manual edit above does.
  Repeat it for several chapters.
- `run_pipeline.py` covers notebooks 1–6, not the data quality notebook;
  run that one's Part 1 by executing its code cells up to Part 2's intro
  (the markdown cell whose id is `intro2`). Running Part 2 regenerates the
  committed `docs/data.js`.
- Measured on the 16 October 2026 test run — one questionnaire per chapter,
  about 35,000 rows in all: notebook 1 about 30 seconds, 2 about 12, 3
  about 2, 4 about 23, 5 about 35, 6 about 25. Most of it is Excel I/O.

## Where everything lives

Two roots, both under `C:\RAFFI\DSS-local\`, on the local disk:

```
DATA COLLECTOR\                          inputs only - V2 reads here, never writes
├── datacollector_received_quest\        every questionnaire, Arabic or English
│   └── Education\ Health\ Housing\ Labor\ Population\ Poverty\
├── external data\                       published tables with no questionnaire behind them
│   └── <Chapter>\                       read by notebook 3
└── value corrections.xlsx               confirmed readings for malformed Value cells (optional)

COMPENDIUM ARAB SOCIETY - V2\            the git repository's root; every output lands here
├── translation dict_V2.xlsx             the dictionary
├── Merged_long_files\
│   └── <Chapter>_merged_long_files\     <Chapter>_EN.xlsx, <Chapter>_AR.xlsx,
│                                        <Chapter>_EN_external.xlsx, *_reshaped.xlsx
├── Tabulations\
│   └── <Chapter>_tabulations\           <Chapter>_tabulations_EN.xlsx, <Chapter>_tabulations_AR.xlsx
├── Charts\
│   └── <Chapter>_charts\                the SVGs, PNGs, <Chapter>_charts.xlsx, index and findings
├── pipeline_changes_<Chapter>.txt            what a resumed run fixed, inferred, or added
├── pipeline_changes_general.txt              same, with no chapter of its own
├── need manual intervention_<Chapter>.txt    what a resumed run left alone, and why
├── need manual intervention_general.txt      same, with no chapter of its own
├── Data quality issues before pipeline execution_<Chapter>.txt   Part 1's only output, one per chapter
└── codes\                               the notebooks, this file, the runner
```

- Every notebook's `config` cell builds its paths from
  `Path("C:/RAFFI/DSS-local")`; change that one prefix to move the whole
  tree.
- The outputs sit inside the repository but are not tracked — the root
  `.gitignore` leaves out `Merged_long_files\`, `Tabulations\`, `Charts\`,
  the findings `.txt` files and dictionary backups. `translation
  dict_V2.xlsx` is tracked.
- `translation dict_V2.xlsx` has four columns — `col_ar`, `val_ar`, `col_en`,
  `val_en` — plus `status`, which marks the rows the pipeline added.
  - Read **Arabic → English only** everywhere except notebook 4's
    external-data section, which is not a back-translation of anything: it
    is giving a brand new English value, from a file with no Arabic form
    anywhere in it, an Arabic form for the first time.
  - Nothing should build a reverse map of the *existing*, already-correct
    English content.
  - A row may carry `val_ar`/`val_en` both blank on purpose — that teaches a
    **column** name rather than a value, e.g. a raw sheet's mistyped header.
  - `update_dictionary()` keeps both kinds; do not reintroduce a `dropna()`
    across all four columns, which silently discards the column-only rows.
  - **Edited directly by a person for a Part 1 finding** — there is no
    notebook-driven path from "Part 1 found a label" to a dictionary row;
    see `data quality/CLAUDE.md`.
- `value corrections.xlsx` has `chapter`, `raw_value`, `corrected_value`,
  plus `status` and `date` the same way.
  - Read by notebook 1's `clean_one_value()` — see **Things that look wrong
    but are deliberate** below. Edited directly by a person, the same as
    the dictionary — nothing writes it automatically. Does not exist yet;
    the notebooks run without it.

## Where the data stands

- **Test run, 16 October 2026** — data quality Part 1, then notebooks 1–6,
  on the six questionnaires in `datacollector_received_quest\`, one per
  chapter, every one of them Arabic: Oman (Education), Libya (Health),
  Tunisia (Housing, Labor), Jordan (Population), Qatar (Poverty).
  - Long files: Education 2,121 rows, Health 1,974 (+4,916 external, 22
    countries), Housing 2,667, Labor 8,883, Population 19,203 (+13
    calculated), Poverty 441.
  - Tabulations for every chapter in both languages; 52 charts.
  - **Dictionary gaps closed the same day**: 54 rows added to
    `translation dict_V2.xlsx` (361 → 415), each under its column
    (`المصدر` / `Source`, one `المواطنة` / `Nationality`) with
    `status = updated` — 49 Arabic values Claude translated to English
    through notebook 1's `update_dictionary()`, 48 of them Source
    citations, and the external file's 5 WHO Source URLs, whose Arabic form is the URL
    itself, through notebook 4's. `apply_external_gaps()` then wrote
    Health's 4,916 external rows into `Health_AR.xlsx`, and 1–6 were re-run.
  - Translations involving judgement: Jordan's Nationality `أردني`
    ("Jordanian") is filed as `Nationals`, the dictionary's own category;
    Libya's two documentation-centre citations may name the same body.
  - One gap is left open on purpose — the `Population_22` header below.

## Conventions

- `pandas` with `openpyxl`, `pathlib.Path` for every path — the paths contain
  spaces, never hardcode separators.
- Plain functions, no classes.
- One cell per step, each opening with a `"""` block saying what the cell
  does.
- `logging` for progress; `print()` only for the progress bar and per-row
  dictionary replacements, which are meant to be read inline.
- One `try`/`except` per sheet, with a `step` variable naming the stage.
  - A bad sheet is logged and skipped — one malformed file never ends a run.
- Comments explain *why*, not what.
  - Most of the odd-looking code here is load-bearing; see below.
- Test against copies in the scratchpad.
  - Never write to the user's folders to try something out.

## Things that look wrong but are deliberate

- **`Value` is parsed with `to_number()`, not `float()`.**
  - Most population cells are text like `' 701 956 '`, using spaces as
    thousand separators.
- **Source is translated but never fuzzy-matched.**
  - Two citations differing by one digit score high enough to overwrite each
    other.
- **Notebook 4's Indicator resolution for external data never fuzzy-matches
  either, for a related but distinct reason.**
  - A long, templated sentence carries its topic in a small fraction of the
    string: "Government expenditure on health as % of Gross Domestic Product
    (GDP)" scored 0.628 — over the 0.6 cutoff — against the dictionary's
    *education*-spending indicator, on shared wording alone.
  - Measured, not guessed; see `NEVER_FUZZY_MATCHED` in its own `extdict`
    cell.
  - Country and Sex keep fuzzy matching there — proven useful, not just
    harmless: it reuses "Comoros Islands" for a bare "Comoros" rather than
    filing a second, inconsistent country.
- **Missing dimension values render as `(not specified)`, never blank.**
  - The tabulation layout blanks a repeated label to mean "same as above",
    so a blank would silently absorb a row into the group above it.
- **Every populated breakdown column becomes a nested row level**, not just
  the first.
- **The sex ratio falls back to the sum of the age bands** when a
  country-year has bands but no `Age Total` row.
  - The population is there either way, and dropping the year for want of a
    total line would lose it for nothing.
  - It's not the same figure, though — a band sum misses whoever the
    country left outside its bands (`Age unknown` included) — so every one
    is logged as `sex ratio taken from the age bands`.
  - A year whose two sexes came by different routes is logged again as not
    quite comparable.
- **Population totals take only the `Total` slice of one indicator.**
  - The by-nationality and by-area indicators describe the same people;
    summing them, or their parts, double-counts.
- **Merge keys are trimmed on both sides before merging.**
  - `reshape_and_merge()` runs before `correct_with_dictionary()`, so an
    untrimmed key matched nothing and the row lost its citation silently.
- **`clean_one_value()` checks `value corrections.xlsx` before its own
  guesses, keyed on `(chapter, exact raw text)`.**
  - A person confirms a reading once and every occurrence of that same
    malformed text in that chapter is fixed the same way on every future
    run — not just the one cell that happened to be reviewed.
- **A share/breakdown chart (notebook 6) never excludes a country for an
  incomplete report or a total that doesn't sum to 100 — it charts exactly
  what was reported and logs the rest as a finding.**
  - Most countries only report the categories they have any of, leaving the
    rest a silent zero rather than an explicit one, so requiring every
    category before charting a country would drop nearly everyone.
  - `stacked_shares()`'s x-axis widens to fit a country whose reported
    categories sum past 100 rather than clipping it invisibly at 100.
  - Full reasoning is in `charts_design.md`'s "data guards" section.
- **`total_slice()` (notebook 6) treats a blank breakdown column as its own
  total, not only an explicit label like `Nationality Total`.**
  - Different countries use different conventions for the same thing — one
    writes `Nationality Total`, another just leaves Nationality blank — and
    recognising only the explicit label would silently drop every country
    using the blank convention the moment any country used the other one.
  - The explicit label wins over a blank duplicate if a country ever reports
    a figure both ways at once.
- **`chart_pupil_teacher()`'s primary figure (5.5) tries "Primary" before
  falling back to "Basic", per country — not a single, alphabetically-picked
  label.**
  - Some countries (Jordan, Egypt) file their primary-equivalent stage as
    "Basic" (grades 1–9/10); the rest use "Primary".
  - `matching_values()` sorts its matches alphabetically, so a single
    pattern `"primary|basic"` would pick "Basic" for *every* country.
  - `level_slice()` applies the same preferred/fallback rule
    `preferred_edition()` uses for by-nationality / by-area splits: the
    first pattern that covers a country wins, a later one only fills the
    gap.

## Known issues

- **Jordan's `Population_22` carries its indicator's name in the header cell
  where `المؤشر` belongs** (`عدد الوفيات والأشخاص المفقودين والأشخاص المتضررين
  من الكوارث لكل 100,000 شخص`), so its 63 rows reach `Population_EN.xlsx`
  under an Arabic column of their own instead of `Indicator`.
  - Not closed through the dictionary: mapping that header to `Indicator`
    would give the merged English table two `Indicator` columns. Correct
    the header in the source file to `المؤشر`.
  - Once it is, the dictionary's existing row for that indicator needs
    fixing too — its English reads "Number of victims of intentional
    homicide per 100,000 population", a different indicator.
- **Qatar's `Poverty_4` is a source-citation table with no response rows** —
  only one `index` row — so notebook 1 skips it at `extract` and logs it.
  A source-file fault; not fixed in code.
- **Notebook 6 crashes on a few Health figures instead of skipping them**,
  seen on the 16 October 2026 test run. Each is caught, logged as
  `chart failed`, and the run goes on.
  - 4.1–4.3: `preferred_edition()` keeps an indicator whose rows have no
    total slice, then indexes into the empty frame — `IndexError`.
  - 4.15–4.22, 4.25, 4.26: no car-accident indicator in the data at all,
    and the chart code reads `Country` / `Sex` / `Age Group` off the empty
    frame — `KeyError`.
- Questionnaire cover tabs (`العنوان`, `قائمة الجداول`, `كيفية الإستخدام`,
  `البيانات الوصفية`) have no `index` column and are skipped by design.

## Environment

- Excel locks files it has open.
  - Check `<Chapter>_*.xlsx` and `translation dict_V2.xlsx` are closed
    before a run, and say which to close if a write fails.
- Everything lives on the local disk, `C:\RAFFI\DSS-local\`. Nothing syncs or
  backs up automatically: copy hand-edited long files in by hand, and push
  the repo.
  - Still verify a write landed rather than assuming it did.
- `pandas`, `openpyxl`, and for notebook 6 `matplotlib` and `Pillow`.
  - `nbformat` is **not** installed — notebooks are edited as raw JSON, and
    any script that rewrites one must compile every code cell before
    saving.
- See **Running it** above for how to start a run either way.
  - Claude's own runs never go through Jupyter — that's about what Claude
    can do, not a rule for you.
  - A pipeline run can go through Claude directly or through the matching
    subagent in `.claude/agents/`, one per notebook.
