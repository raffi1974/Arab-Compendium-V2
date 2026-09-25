# Compendium data quality

- Part of the same repository as the pipeline, which lives one level up in
  `../`. One notebook, `Compendium_Data_Quality.ipynb`.
- Nothing here changes the data — both parts only measure and report; a
  correction Part 1 finds is made directly, by a person, in the source
  questionnaire, `translation dict_V2.xlsx`, or `value corrections.xlsx`.
- **Part 1 is the pipeline's first step, not a side notebook.** A "run the
  pipeline" request runs this first, every time, and stops here: notebook 1
  does not run until a person has reviewed what Part 1 found, made whatever
  corrections it calls for, and told Claude to resume. See `../CLAUDE.md`'s
  pipeline order.

| File | What it does |
|---|---|
| `Compendium_Data_Quality.ipynb` | Part 1 reads the **raw questionnaires**, writes one `Data quality issues before pipeline execution_<Chapter>.txt` per chapter, and gates the rest of the pipeline. Part 2 reads the **final long files** and writes `data_gaps_report.xlsx` |

- Two parts of one notebook, sharing nothing but a file — Part 1 never reads
  a final file, Part 2 never reads a raw one — so either can be run alone.

## Part 1 — before the pipeline runs

- Reads every raw questionnaire — the same files notebook 1 reads:
  1. **Labels not in the dictionary, exactly** — a column name or value with
     no exact match, in either language. Below `FUZZY_MATCH_CUTOFF` is
     deliberate: a label the real pipeline would fix on its own needs no
     review.
  2. **Values that are not plain numbers, and that `clean_one_value()`
     could not make sense of on its own** — a unit phrase, a placeholder, a
     sum are all handled automatically and need no review either; this is
     only the residue.
  3. **Structural problems** — reporting only: a duplicate column header, a
     stray space in a merge key, a sheet with no `index` row that is not a
     recognized cover tab. Fixed in the source Excel file, not here.
- **`Data quality issues before pipeline execution_<Chapter>.txt`**, one per
  chapter, is Part 1's only output — `write_chapter_reports()`.
  - Every outstanding issue lives here, and only here — there is no separate
    action file to edit and apply. A person reads it and corrects whatever
    it calls for directly: the source questionnaire or `value
    corrections.xlsx` (in `DATA COLLECTOR\`), or `translation dict_V2.xlsx`
    (in the `COMPENDIUM ARAB SOCIETY - V2\` root) — then tells Claude to
    resume.
  - Not aggregated across chapters — the same mistyped header found in both
    Housing and Poverty gets its own line in each chapter's file, not one
    merged entry.
  - Each finding is one line: `Country | Sheet | Indicator | Year | reason`.
  - Label and structural findings are about a column, a citation, or a
    whole sheet rather than one row, so Country/Indicator/Year print as `-`
    for those; only a value finding has a row to point at.
- **`CHAPTERS = None` picks up every folder `discover_chapters()` finds**,
  which currently includes two that are not real chapters:
  - `datacollector_received_quest_AR\yemen\` (Yemen's five questionnaires,
    one folder level too shallow).
  - `country excel sheets` (two unsorted files).
  - Both get scanned and reported on as if they were chapters, which is why
    a full run's structural-problem count looks alarming — most of it is
    `yemen`. See Known issues in `../CLAUDE.md`.
  - Set `CHAPTERS` to the real chapter list explicitly to skip both.

## Part 2 — the final files: completeness and contradictions

- Reads every `<Chapter>_EN.xlsx` in `longfiles\` and, per chapter,
  in one pass:
- **Completeness.**
  - For every indicator × country, how many of the expected years
    (`FIRST_YEAR` to the current edition, taken from the calendar rather than
    typed in) carry a value at all, and separately how many carry a
    *headline* value with every breakdown at its total — and which
    breakdowns a country actually supplies for an indicator.
  - Only 9–18% of rows in the long files carry a value, and that number is
    **not** a completeness figure and must never be reported as one: the
    questionnaire grid is every age group × marital status × nationality ×
    year, whether or not the combination was ever intended to be filled.
  - Series are banded instead — `none` / `sparse` (1-6 points) / `partial`
    (7-12) / `strong` (13-16) / `complete` (every expected year) — never
    averaged into one number, because a one-point series and a full one must
    never be allowed to cancel out into something that reads as "half
    full".
- **Contradictions**, six kinds, all through `measure_chapter()`'s `issues`:
  - a reported total that does not match the sum of its own parts
    (`total mismatch`)
  - a year-on-year change of more than `SPIKE_FACTOR` (`spike`)
  - a percentage indicator that also holds absolute counts (`units`)
  - a percentage breakdown that does not add to 100 within
    `PERCENT_TOLERANCE` (`percentages do not sum to 100`)
  - a negative value or a percentage outside 0-100 (`implausible value`)
  - the same row reported twice with two different values (`conflicting
    duplicate rows`)
  - Nothing here suggests a correction the way Part 1 does — a
    contradiction in the FINISHED data is a finding about the SOURCE, and
    fixing it means going back to the questionnaire.
## Things that look wrong but are deliberate

- **Seven dimensions have no total category** — causes of death, economic
  activity, employment status, main occupation, institutional sector,
  reasons for inactivity, the ICD list.
  - An indicator broken down that way has no meaningful aggregate row, so
    its headline coverage is blank *by design*, not as a gap.
  - `TOTAL_LABELS` in Part 2's config lists only the dimensions that do
    have one.
- **The expected range ends at the current year, and is not typed in.**
  - `LAST_YEAR = date.today().year`, so this cannot quietly go on measuring
    last year's range.
  - The template's projection columns run past it and are excluded by
    construction; counting them would make every country look incomplete.
  - Pin `LAST_YEAR` to an integer to re-measure an older edition.
- **Spikes are compared after collapsing to one value per series per
  year.**
  - The same dimensions and year can appear twice in these files, and
    without that step the comparison pits two rows from the *same* year
    against each other.
- **`Value` is parsed with `to_number()` in Part 2, `clean_one_value()` in
  Part 1 — not `float()` in either.**
  - Only 337 of 33,968 population cells are numeric; the rest are text
    like `' 701 956 '` using spaces as thousand separators.
  - `to_number()` only needs a float-or-None for measuring tens of
    thousands of already-processed rows; `clean_one_value()` also has to
    explain, per cell, what it changed and why.

## Conventions

- `pandas` with `openpyxl`, `pathlib.Path` for every path — the paths
  contain spaces.
- Read-only, fully — neither part writes anything back to the dictionary,
  the value corrections file, or a questionnaire. If a change to the data is
  ever needed, it belongs in the pipeline project, or is made by a person
  directly in the source file Part 1 pointed at.
