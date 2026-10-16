# Charts — how they are built and why

Everything behind `Compendium_6_Charts.ipynb`. Read this before changing how a
chart looks: it records what was measured and what was chosen, so none of it has
to be worked out twice.

```
Merged_long_files\<Chapter>_merged_long_files\<Chapter>_EN.xlsx   ->   Charts\<Chapter>_charts\
```

Run it after notebook 4. It reads the same long files notebook 5 does, so it
picks up the merged questionnaire rows and the calculated indicators. It is
independent of notebook 5 — neither needs the other.

**The long file is the source of truth.** Charts read
`Merged_long_files\<Chapter>_merged_long_files\<Chapter>_EN.xlsx` exactly as
saved and never rebuild it
from the questionnaires, so rows added or corrected there by hand (data that
never went through a questionnaire) are charted as they stand. `load_chapter()`
logs the file path and when it was last saved on every run, so a stale copy or
an unsaved edit shows up in the log. Edits made in a copy of the file elsewhere
are not seen. Re-running notebooks 1-4 rewrites the long file from the
questionnaires and would overwrite hand edits, so make those corrections at the
source or re-apply them after such a run.

`CHAPTERS` at the top of the config cell picks what runs. It is `None`, which
charts every chapter with a long file; set an explicit list to restrict one run.

## What is being copied

The compendium's own figures, exported from the old plotly workbook, are the
reference for every chart here:

```
COMPENDIUM-ARAB SOCIETY\old files\population old charts\
    population\  housing\  health\  education\  labor\  poverty\
```

They live in the original compendium folder, beside this V2 one, which has no
copy of them.

`OLD_CHARTS_PATH` in the config cell records that path. Nothing reads the folder
at run time — every chapter set was read out of those SVGs by hand (the shape of
each numbered figure, the countries on it, its unit and its axis range) and the
path is kept so a figure drawn here can be checked against the one it replaces.
The SVGs still carry their text as text, so `grep` finds a legend or an axis
label without opening anything.

Two of them were decoded from the bar geometry rather than from a label, and it
is worth not redoing that: `2.6_early_marriage` runs Mauritania 36.6 per cent
down to Tunisia 1.5, which identifies it as the UNICEF child-marriage series
(women aged 20-24 married before 18), and `2.7_early_childbearing` is its
companion. **Neither is a questionnaire indicator**, so neither is drawn today —
`find_indicator()` reports the gap and the figure is skipped. The functions are
written and will produce the figures the moment such an indicator reaches a long
file. Filling them with the nearest thing to hand — a marital-status share of
the whole female population — would print as the published figure and mean
something else.

## What comes out

`<Chapter>_charts.xlsx` is the deliverable: one sheet per chart, each holding
that chart's picture with exactly the rows that produced it underneath, plus an
`Index` sheet linking to them all. Every chart's SVG and PNG sit in the same
folder, next to `charts_index.csv` and `chart_data_findings.txt`.

**Excel cannot hold an SVG.** openpyxl places images through Pillow, which does
not rasterise SVG, so the picture *inside* a sheet is the PNG. The SVG beside it
is the vector copy and the one to use anywhere that wants live text. There is no
way around this from Python — don't spend time trying again.

**Every chapter now gets the numbered set the compendium prints**, and the
filenames are the published figure numbers, so a folder lines up with the report.

| chapter | figures | shapes used |
|---|---|---|
| Population | `1.1`–`1.13`, `2.1`–`2.7`, a pyramid per country | all six |
| Housing | `3.1`–`3.7` | stacked shares, grouped bars, lines |
| Health | `4.1`–`4.28` (4.9 retired, 4.15–4.28 have no published number — see **Health 4.15-4.24**, **Health 4.25-4.26** and **Health 4.27-4.28** below) | lines, small multiples, grouped bars |
| Education | `5.1`–`5.7` | small multiples, lines |
| Labor | `6.1`–`6.8` | small multiples |
| Poverty | `7.1`–`7.5` | lines, small multiples, grouped bars |

**Population's numbering keeps its gaps on purpose**: no 1.4 or 1.5 was supplied
to copy, so those numbers are left free and the files still line up with the
figure numbers in the report. Don't close the gap.

**Only Population and Labor have long files.** The Housing, Health, Education and
Poverty sets are written from the published figures and from the indicator names
in `old files\indicators.txt`, and are **unverified against real data** until
those chapters are run. A mismatch surfaces as an `indicator missing` or
`breakdown missing` line in that chapter's `chart_data_findings.txt` — read that
first, then widen the pattern rather than pinning a new exact string.

**Indicators are resolved by pattern, not by an exact name.** `find_indicator()`
takes the report's wording and matches it against the chapter's own indicator
names; `breakdown_column()` and `matching_values()` do the same for a column and
for one slice of it. The questionnaires spell the same measure differently
between chapters — and sometimes between two editions of one chapter — so a
pinned string breaks on a stray double space and a pattern does not. Patterns are
tried in order, exact wording first and a looser fallback behind it, and a
pattern that matches nothing is reported and that one figure skipped.

**The data-driven builder is now the fallback**, for a chapter with no published
set. `ALSO_CHART_UNUSED_INDICATORS = True` in the config cell also runs it over
whatever a published set never touched — useful while a chapter is being
explored, noise in a deliverable. It works out what was touched from the source
note each figure registers, so a chapter set that leaves its `source_note` blank
will see its indicators charted twice.

Three classifications in the Housing set are **judgements, not facts in the
file**: `IMPROVED_WATER`, `IMPROVED_SANITATION` and `HAS_ELECTRICITY` decide
which of a questionnaire's categories count towards 3.3, 3.4 and 3.5. Every
category a list does not recognise is reported by name, so the first Housing run
says exactly what it left out of the numerator. Check that finding against the
questionnaire before those three figures are published.

## The theme

Light, and not a matter of taste — every value was read back out of the published
SVGs in `OLD_CHARTS_PATH\population\` (see **What is being copied** above).

| | value | |
|---|---|---|
| surface | `#FFFFFF` | figure and plot ground |
| ink | `#000000` | titles, ticks, values |
| muted ink | `#5A5A5A` | subtitles and units |
| axis line | `#444444` | exactly as the originals draw it |
| grid | `#E4E7EB` | **not in the originals** — see below |
| font | Times New Roman | the originals use 17px body, 20px title |
| sizes | 16 tick / 16 legend / 16 panel / 21 title | |
| line | `LINE_WIDTH = 1.45` | 2px at 100 dpi, as published |
| marker | `MARKER_SIZE = 5.0` | |
| bar gap | 0.9px in the surface colour | reads as space, not as a drawn keyline |

`dpi = 100`, so one figure inch is 100 px and every pixel calculation below is
literal. `svg.fonttype = "none"` keeps text as text — editable, and a smaller
file.

**The one deliberate deviation: the originals have no gridlines at all.** Their
`gridlayer` is empty. A faint grid was added because a value in the middle of a
tall panel is otherwise unreadable. Set `GRID_COLOR = SURFACE` to switch it off
and match the published figures exactly.

### Colours

The categorical triad, read out of 1.3, 1.7 and the pyramids:

- `#003F5C` navy · `#BC5090` pink · `#FFA600` amber

It separates well — Male/Female ΔE 42.8 colour-blind and 50.9 normal; the three
age bands 16.2 and 30.1. The amber sits at **1.96:1 against white**, which the
validator flags as needing relief (a visible label or a table view) rather than
as a free choice. **That relief is already drawn** and must stay: `stacked_shares`
prints the number inside every segment wide enough to hold one, and the workbook
puts the whole table on the sheet beneath the picture.

The published life-expectancy chart used blue and red instead, but those are
plotly's defaults showing through the label-lookup miss described below — not a
house choice — so the triad is used for every sex encoding.

Single-series bars use `#19516C`, from 1.11.

### The country palette, and the bug in the published charts

The 22 country colours are the published ones. **They are keyed on the name as it
appears in the long file, not on the printed label** — this is the one fix kept
from the originals. The published charts keyed theirs by label, so wherever a
legend wrote a country without spaces — `SaudiArabia`, `SyrianArabRepublic`,
`UnitedArabEmirates`, `StateofPalestine` — the lookup missed and plotly's default
sequence took over. That is why Saudi Arabia is olive on one published figure and
blue on the next. You can still see both values in the old SVGs.

**What the house palette costs, measured:** United Arab Emirates `#999999` has
zero chroma (it is grey, not a hue) and sits at ΔE 1.0 from Tunisia under a
deutan simulation; Iraq and Egypt are 7.8 apart under normal vision against a
floor of 15; ten of the twenty-two fall below 3:1 contrast on white. They are
kept because they are what the compendium prints.

`HOUSE_ALTERNATIVE` in the config cell is a measured replacement if the set is
ever allowed to change — worst pair anywhere 5.9 instead of 1.0, worst legend
neighbours 15.4, every colour at or above 3.11:1 and 0.106 chroma. Switch with
one line: `COUNTRY_COLORS = HOUSE_ALTERNATIVE`.

**5.9 is a ceiling, not a shortfall.** Twenty-two colours that must each clear
3:1 on white cannot do better on their worst pair; the search was exhaustive
enough to be confident of that. It is below the validator's target of 8, which is
exactly why **these charts never identify a line by colour alone**: the legend is
always drawn, and where one country's own path matters more than the ranking,
`small_multiples` is the shape to reach for.

Run the validator rather than reasoning about any of this:

```
node <dataviz skill>/scripts/validate_palette.js "<hex,hex,...>" --mode light --surface "#FFFFFF"
```

Add `--pairs all` for anything where any two series can end up side by side —
lines, scatter, small multiples. Adjacent-only is for stacks and bars. The CLI
guard requires the script to be invoked at a path ending in `validate_palette.js`,
and it is an ES module, so it needs a `package.json` holding `{"type":"module"}`
beside it.

## Sizes are measured, never guessed

This is the part most worth keeping. Nothing uses a character-count estimate; the
figure is sized from the rendered width of the text that has to fit, which is why
no label clips at any length.

- `widest_label_px(fig, labels, size)` measures real text through the renderer's
  `get_window_extent`.
- `label_margin()` turns that into a left margin, clamped to 0.12–0.55.
- `head_px()` / `draw_head()` reserve the title and subtitle band and return the
  fraction consumed, so a two-line title cannot land on a panel title.
- `stacked_shares` sets its own height from measured content:
  `head + panel titles + 46 px per row + 44 px + 32 px per legend row`, with the
  legend column count derived from the widest category label.
- `country_lines` measures the legend and widens the *figure* to hold it, keeping
  the plot itself a fixed `PLOT_WIDTH_PX = 700`. It used to fix the plot at 0.52
  of an 800 px figure, which gave a 19-country legend nearly 40% of the width and
  left twenty-one lines of data sharing 416 px. Sizing this way also keeps
  `Syrian Arab Republic` whole — the published SVGs cut it off.
- `small_multiples` lays out from a pixel budget, not from `subplots_adjust`
  fractions: head, legend band, then per row a `PANEL_TITLE_PX` and a `PANEL_PX`,
  `ROW_GAP_PX` between rows, and `FLOOR_PX` for the year labels. The fractions had
  `hspace = 0.75` — three quarters of a panel's height spent on the gap — which
  left every panel **180×90 px** on an 800 px figure. At that size a series reads
  as a flat line whatever it does, and the year labels only fit turned on their
  side. A panel is now a fixed **320×150 px** whatever the country count, the
  years sit upright, and the y axis gets `MaxNLocator(4)` instead of just a floor
  and a ceiling.
- **The year labels stay upright because a panel is wide enough to hold them,
  not because the tick count is thinned to fit.** A column of sideways years
  was the hardest thing to read on the old figures; the fixed 320 px panel
  width is what fixed it. An earlier version of the fixed-grid ticks (see
  **Chart titles, axes, legends and sort order** below) tried to additionally
  thin the grid itself when a panel seemed too narrow, using `widest_label_px`
  to measure how many fit — that thinning is what silently dropped the latest
  year's tick on some charts, and was removed rather than fixed, since the
  grid is short enough (4-5 entries through the 2030s) that a 320 px panel
  never actually needed thinning in the first place.

Three fixes worth not re-breaking:

- **Shared axes invert once, not per axis.** Calling `invert_yaxis()` on each
  panel of a shared-y figure cancels itself on the second. `stacked_shares` uses
  a single `set_ylim`.
- **Shared x hides tick labels on every panel but the bottom row, and the bottom
  row is usually part empty.** `small_multiples` turns labels back on for the
  lowest *occupied* panel in each column.
- **The shared legend is collected from every panel, not from the first one.**
  Reading `get_legend_handles_labels()` off `axes[0][0]` drops a series from the
  legend whenever the first country alphabetically does not happen to report it —
  Iraq reports only one sex on several Labor indicators. The handles are gathered
  across all panels and ordered by the `series_colors` dict, so the legend reads
  Male, Female in house order rather than alphabetically.

`readable_on()` picks the text colour for a number sitting on a fill **by
measuring contrast**, not by a fixed lightness rule. A fixed rule is only correct
for one theme and silently inverts on the other — it did, when the theme moved
from dark to light, and every number inside a stacked bar went invisible.

## The six shapes

Every chart is one of these, in `cell_primitives`:

| | used by |
|---|---|
| `country_lines` | 1.1, 1.2, 1.6, 2.1–2.4, 3.6, 4.1–4.4, 4.11a/4.11b, 7.1–7.3 — one line per country, legend right (or left — see `mirror=`, below) |
| `small_multiples` | 1.8–1.10, 2.5, 4.5, 4.15–4.24, 5.1–5.6, all of 6, 7.4 — a panel per country, **one shared y scale** |
| `stacked_shares` | 1.3, 1.7, 3.1, 3.2 — percentages that sum to 100 |
| `ranked_bars` | 1.11, 2.6 — one bar per country, longest on top, no legend |
| `grouped_bars` | 3.3–3.5, 4.6–4.8, 4.25–4.28, 7.5 — two to five bars per country |
| `pyramid` | the country pyramids — male left, female right, one shared scale |

`grouped_bars` is the newest and the only one that prints no figure on the bar:
`ranked_bars` can, because it draws one series, and here two to five bars share a
row and the numbers would collide at any width worth printing. The legend names
the series and the exact figures go on the workbook sheet beneath the picture. It
sizes itself the same measured way as everything else — `len(series) × 20 px` per
country plus a 16 px gap, so a five-bar row gets two and a half times the height
of a pair instead of both being squeezed into one fixed figure.

Rows are ordered by `sort_by` where a caller names a series and by the row's mean
otherwise, largest at the top. That ordering is the whole readability of the
shape: there are no gridlines to count along, so a ranking is what lets a reader
place a country without measuring.

`run_jobs(chapter, jobs)` draws a set with every figure isolated — one missing
indicator, or one breakdown not shaped the way the published figure assumed, must
not take the other thirteen with it. Every chapter builder returns through it.

`small_multiples` shares its y scale deliberately: on separate scales a country
whose fertility moved 2.0 → 2.2 looks identical to one that moved 2 → 6.

The pyramid plots **percent of total population**, not percent of that sex —
verified against the published Bahrain figure (male 20-24: published 4.50%,
computed 4.48%) and the sheets sum to 100.00% across both halves.

## Chart titles, axes, legends and sort order

Approved from a colleague's review of the Health chapter's chart output,
2026-10-06, and implemented the same day. These are content rules, sitting
above the drawing mechanics in **The six shapes** and the sizing rules in
**Sizes are measured, never guessed** — where a bullet here reads
differently from an earlier one in this file, this section is the one to
follow.

### General rules, every chart

- **X-axis end is the latest year any country has data for**, not a year
  typed into the chart — a chapter whose newest figure is 2025 ends its axis
  at 2025, one whose newest is 2023 ends at 2023. `year_ticks()` in
  `cell_primitives` reads this off the data itself (`years[-1]`) rather than
  from a constant.
- **Time-series x-axis ticks are 2010, 2015, 2020, 2025** — every five years
  since 2010, whatever the end year turns out to be. `AXIS_START_YEAR = 2010`
  and `TICK_STEP_YEARS = 5` in `cell_primitives` fix the grid; `year_ticks()`
  builds `range(AXIS_START_YEAR, end_year + 1, TICK_STEP_YEARS)` instead of
  thinning whatever years a chart's own data happened to carry. The old
  thinning meant two charts covering the same period landed ticks on
  different years and could not be read side by side.
  - A first version of this fix kept a second, separate thinning step for a
    `small_multiples` panel judged too narrow for the full grid — removed,
    not kept: `ticks[::step]` could drop the *last* tick (the latest year
    with data, the one a reader most needs) whenever the grid length did not
    divide evenly by the stride, which is exactly what happened to some
    Health and Education charts the first time this ran. The fixed grid
    never has more than 4-5 entries through the 2030s and every
    `small_multiples` panel is a constant 320 px wide regardless of country
    count, so no chart actually needed thinning — `year_ticks()` now takes
    no `max_ticks` argument at all.
- **A bounded `(percent)` indicator's y-axis (or value axis, for a
  horizontal-bar shape) is labelled up to 100, with a little headroom past
  it so a value sitting at exactly 100 is not drawn flattened against the
  axis frame itself.** `country_lines`, `small_multiples` and `grouped_bars`
  each take a `percent=False` kwarg; where a caller sets it `True` the axis
  runs to `PERCENT_AXIS_MAX = 110` with `PERCENT_TICKS = [0, 20, 40, 60, 80,
  100]` as the only labelled ticks — the 100-110 band exists so a point or
  line sitting on the true ceiling is still visible, not so a reader sees a
  "110" tick that means nothing. This is an axis-range rule, distinct from
  `drop_impossible_percentages()` in **The data guards** below, which drops
  a value *above* 100 rather than setting where the axis stops.
  - A first version pinned the axis to exactly `(0, 100)` with no headroom:
    a country's line sitting at 100 across most years rode the top spine for
    its whole length and was nearly invisible, which is the opposite of what
    capping the axis at a knowable ceiling was supposed to buy.
  - Set only where the indicator is a genuine share of a whole — Health 4.1,
    4.2, 4.3, 4.5, 4.6–4.8, 4.10; Education 5.1–5.4; Housing 3.3–3.5 (via
    `improved_share_by_area`).
  - Deliberately **not** set on a ratio-type "percent of X" with no natural
    ceiling near 100 — GDP share (4.11), per-capita spending (4.12),
    expenditure-of-budget (5.7), pupil-teacher ratios (5.5/5.6) — capping
    those at 100 would flatten a series that never leaves single digits.
  - `stacked_shares` (1.3, 1.7, 3.1, 3.2) is deliberately **not** given this
    kwarg: it already has its own, more specific axis-widening behaviour for
    a country whose reported shares sum past 100 (see **The data guards**),
    and this rule does not override that.
- **Chart titles are bold; the subtitle beneath them (unit and period) is a
  smaller font.** `draw_head()`'s title loop now passes
  `fontweight="bold"` to `fig.text()`; the subtitle loop is unchanged
  (`PANEL_SIZE`, `INK_MUTED`).
- **A fixed gap between the title/subtitle block and the chart body under
  it, the same everywhere** — country_lines, small_multiples, stacked_shares,
  ranked_bars, grouped_bars and pyramid all reserve it through
  `head_px()`/`draw_head()`. `HEAD_GAP_PX = 36` in `cell_primitives` replaces
  two numbers that were standing in for the same gap without agreeing with
  each other: `head_px()` (sizes the figure before it exists) used a flat
  `12` px, `draw_head()` (draws the text and reports what it used, after the
  figure exists) used a flat `0.02` *figure-fraction* — a different unit
  entirely, and one that shrinks in real pixels on a short figure. On the
  fixed-height 800 px `country_lines` figure that 0.02 worked out to 16 px,
  barely past the subtitle's own descender, which is why a subtitle like
  "United States Dollars per person, 2010-2023" sat almost on top of the
  first y-axis tick. Both functions now add `HEAD_GAP_PX` in the same pixel
  unit, `draw_head()` converting it to a fraction of its own actual height
  (`HEAD_GAP_PX / height_px`) rather than using an unrelated constant.
- **One fixed offset between the legend and the axis labels it sits next
  to, the same number everywhere** — legend-to-country-labels on a time
  series, legend-to-x-axis on a sex-disaggregated chart.
  `LEGEND_GAP_PX = 50` in `cell_primitives` replaces the three different
  hardcoded numbers (52, 46, 44) that `country_lines`, `small_multiples`,
  `stacked_shares` and `grouped_bars` each used to size this gap with
  separately.
  - **In `small_multiples`, the gap and the legend's own rendered height have
    to be two separate numbers, not one.** A first version set
    `legend_px = LEGEND_GAP_PX` alone, which gave the legend's own text just
    enough room to fit and nothing left over as an actual gap before the
    panel title below it — visibly touching, not offset. `legend_px` is now
    `LEGEND_GAP_PX + 32`, the `32` being one legend row's own height (the
    same constant `stacked_shares`/`grouped_bars` already use), so the gap
    survives as real whitespace on top of whatever room the legend itself
    needs. Measured in the rendered SVGs at 47.6 px.
  - **`grouped_bars` and `stacked_shares` sized their legend's column count
    from the wrong width.** Both anchor the legend at `bbox_to_anchor=(left,
    0.008)` — `left` being the fraction already reserved for the row labels
    (country names) down the left edge — so the legend starts partway across
    the figure, not at x=0. `legend_cols` was computed as
    `(width_px - 40) // slot_px`, sized against the *whole* figure width as
    if the legend started at the left edge, so a legend wide enough to need
    every column it was given ran its last column off the figure's own right
    edge — first caught on 4.25/4.26 (the first `grouped_bars` chart with 4
    series instead of 2: legend_cols computed as 3, actual rightmost edge
    897 px on an 860 px figure). Both now compute
    `available_px = width_px - left * width_px - 20` and fit `legend_cols`
    to that instead — re-checked against 4.25's own numbers: legend_cols
    drops to 2, rightmost edge 654 px, comfortably inside the figure.
  - **`stacked_shares` had a second, separate overflow the `legend_cols` fix
    alone couldn't reach: a single category name wider than the whole legend
    budget.** Housing's tenure categories include "Provided by the employer,
    local or central government and/or by nonprofit organizations" — 786 px
    alone, on an 800 px figure whose width never grew to fit its legend the
    way `country_lines()`'s already does (only the figure's *height* grew,
    to fit extra legend rows). Forcing `legend_cols=1` doesn't help when the
    one column itself doesn't fit. Fixed by widening the figure when
    `slot_px > available_px`: `width_px = left * width_px + slot_px + 20`,
    then `label_margin()` is re-measured against the new, wider figure
    (its fraction shrinks once the figure grows) before `available_px` is
    recomputed. Verified against 3.1's real category list before touching
    matplotlib: figure widens 800 → 1084.5 px, `legend_cols` resolves to 1,
    rightmost edge 1064.5 px inside the new canvas.
- **A latest-year bar chart sorts its countries high to low.**
  `ranked_bars` and `grouped_bars` already did this ("largest at the top" —
  see **The six shapes**); `stacked_shares` read alphabetically by
  `country_label` until this review, and now ranks rows by the first listed
  category's value, descending, the same way `grouped_bars`' `sort_by`
  stands in for "size" when a row is several numbers rather than one.
  Affects Housing 3.1 (tenure) and 3.2 (living quarters).
- **No axis label may be cut off.** The review caught "Yemen" clipped on
  4.11's country axis — crowded out by having to share one legend with all
  twenty-two countries plus two group-average lines. Splitting 4.11 (below)
  removes that crowding directly; `widest_label_px()`/`label_margin()` still
  do the actual measuring everywhere else, as before.

### Health chapter, per-figure titles and subtitles

The title is the chart's name as it appears in `build_health_charts`
(`cell_primitives` → Health section); the subtitle sits beneath it, smaller
and in `INK_MUTED`:

| figure | title | subtitle | `percent=` |
|---|---|---|---|
| 4.1 | Contraceptive prevalence | Per cent of women currently using any method of contraception, 2010-2025 | `True` |
| 4.2 | Prenatal care | Per cent of women receiving at least 4 visits, 2010-2025 | `True` |
| 4.3 | Births attended by a skilled health professional | Per cent, 2010-2025 | `True` |
| 4.4 | Maternal mortality ratio | Maternal deaths per 100,000 livebirths, 2010-2025 | `False` — not a percent indicator, no 100 cap |
| 4.5 | Immunization coverage | Per cent of children aged 12-23 months, immunized, 2010-2025 | `True` |
| 4.6 | Stunting among children under five | Per cent, latest available year | `True`, sorted high to low |
| 4.7 | Wasting among children under five | Per cent, latest available year | `True`, sorted high to low |
| 4.8 | Underweight among children under five | Per cent, latest available year | `True`, sorted high to low |
| 4.10 | Obese adults, 18 years and over | Per cent, by sex, 2010-2024 | `True` |
| 4.11a | Government expenditure on health, GCC countries | Government expenditure on health as % of Gross Domestic Product (GDP), 2010-2023 | `False` — ratio of GDP, not bounded; `y_max` shared with 4.11b (see 2026-10-13) |
| 4.11b | Government expenditure on health, non-GCC countries | Government expenditure on health as % of Gross Domestic Product (GDP), 2010-2023 | `False` — ratio of GDP, not bounded; `y_max` shared with 4.11a |
| 4.12 | Government expenditure on health per capita | United States Dollars per person, 2010-2023 | `False` — USD, not a percent |
| 4.13 | Density of health care personnel | Per 10,000 population, 2010-2024 | `False` — rate per 10,000, not bounded |
| 4.14 | Number of hospitals | 2010-2025 | `False` — a count |

**4.11 is now two figures, not one.** `chart_health_expenditure_gdp()` no
longer appends `"GCC countries"`/`"Non-GCC countries"` average lines into the
series it hands to `country_lines` — it splits the country dict instead and
draws two charts, `4.11a_health_expenditure_gdp_gcc` and
`4.11b_health_expenditure_gdp_non_gcc`, each `country_lines` with no
averages on it. `GROUP_COLORS` in the config cell and `country_color()`'s
fallback to it are now dead code kept only because the two are harmless and
untangling them was not part of this review; nothing produces a
`"GCC countries"`/`"Non-GCC countries"` key for `country_color()` to resolve
any more.

**4.11's pair is mirrored, not identical.** `country_lines()` now takes a
`mirror=False` kwarg — `True` moves the y-axis tick labels to the right
(`ax.yaxis.tick_right()`) and the legend to the left (`bbox_to_anchor=(-0.03,
1.0)`, `loc="upper right"`), reserving the figure's left edge for the legend
and its right edge for the tick-label margin instead of the usual way round.
4.11a (GCC) is drawn with `mirror=True`, 4.11b (non-GCC) with the default
`mirror=False` — the review's own framing ("1st chart: y-axis right, legend
left; 2nd chart: y-axis left, legend right") is two charts meant to face each
other when placed side by side, not two independently-styled figures.

**4.11's title casing was a real bug, not a style choice.** The first version
built the title as `f"...{name.lower()}"`, where `name` was `"GCC countries"`
/ `"Non-GCC countries"` — `.lower()` silently lowercased the acronym too,
printing "gcc countries" / "non-gcc countries" where the review's own titles
read "GCC countries" / "non-GCC countries". Fixed by spelling the two title
suffixes out explicitly (`"GCC countries"`, `"non-GCC countries"`) rather
than deriving either from the grouping label.

**4.11a (GCC) has a stated y-axis ceiling; 4.11b (non-GCC) does not.**
`country_lines()` takes a `y_max=None` kwarg — when given (and `percent` is
`False`), the axis is pinned to `(0, y_max)` instead of autoscaling.
4.11a is drawn with `y_max=6`: GCC's own data tops out at 5.41 (Kuwait), so
6 gives a little headroom without a 0-100 percent cap. 4.11b keeps `y_max`
unset — the review only asked for a scale on the GCC chart.

**4.13's subtitle now reads 2010-2024, matching the capped axis.** 2025 is
reported by only a handful of countries for either a health profession's own
count or the Population chapter's denominator `chart_health_personnel_
density()` divides by, and the review asked for the chart capped at 2024
rather than stretching the shared panel axis for a thin, partial final year —
every panel's data is filtered to `year != 2025` before `small_multiples()`
ever sees it. An earlier round left the subtitle saying 2010-2025 (as it was
literally specified that round); the 2026-10-08 review corrected the
subtitle text itself to 2010-2024 to match.

**2026-10-06, round two — a few more deltas, same review thread:**

- `year_ticks()` now always adds the real end year as an extra tick when the
  fixed 5-year grid would undershoot it — a chart whose data stops at 2024
  used to tick 2010/2015/2020 only, with 2024 implied only by where the line
  stopped; it now reads 2010/2015/2020/2024. This is a general change (every
  time-series chart gets it), not scoped to 4.10/4.13 alone, though both are
  what surfaced it.
- **Stunting/wasting/underweight (4.6-4.8): the review's "Yemen (2023) should
  be ranked 1st" note holds for two of three, checked against the real,
  `to_number()`-cleaned data, not eyeballed.** Underweight: Yemen 39.7
  (2023) is already highest. Stunting: Yemen is also already highest, but at
  45.4 from **2013** — Yemen's own most recent stunting report, not 2023;
  `latest_breakdown()` takes each country's own latest year, and Yemen's
  latest for this one indicator predates the others'. Wasting: Sudan's 15.7
  (2014) genuinely outranks Yemen's 14.6 (2023) — sorting is correct and
  numeric (`sort_by="Female"`, descending), the two values just don't put
  Yemen first. Nothing was changed here: forcing Yemen to the top of 4.7
  would mean no longer sorting by the reported value, which the general
  "sort high to low" rule exists to do. Worth the reviewer re-checking
  against the source figures rather than this chart being quietly
  overridden.

### Health 4.15-4.24 — two indicators with no published figure number

Car-accident deaths and smoking prevalence are real indicators in Health's
long file (`Percentage of deaths from car accidents`, `Number of deaths from
car accidents`, `Smoking prevalence rate (percent)`) but were never part of
the compendium's own numbered figure set — `OLD_CHARTS_PATH` has nothing to
copy for them. Ten figures, continuing the chapter's own numbering since
4.9 is permanently retired (see **What is being copied**):

| figure | title | subtitle | shape |
|---|---|---|---|
| 4.15 | Percentage of deaths from car accidents | Per cent of total, by sex, 2010-2024 | by sex, Age Total |
| 4.16 | Percentage of deaths from car accidents | Per cent of age group (15-24 yrs), by sex, 2010-2024 | by sex, 15-24 years |
| 4.17 | Percentage of deaths from car accidents | Per cent, by age groups (total vs 15-24 yrs), 2010-2024 | by age, Both sexes |
| 4.18 | Percentage of deaths from car accidents | Per cent, by age groups, by sex, 2010-2024 | by age and sex, 4 series |
| 4.19 | Number of deaths from car accidents | Number of total, by sex, 2010-2024 | by sex, Age Total |
| 4.20 | Number of deaths from car accidents | Number of age group (15-24 yrs), by sex, 2010-2024 | by sex, 15-24 years |
| 4.21 | Number of deaths from car accidents | Number, by age groups (total vs 15-24 yrs), 2010-2024 | by age, Both sexes |
| 4.22 | Number of deaths from car accidents | Number, by age groups, by sex, 2010-2024 | by age and sex, 4 series |
| 4.23 | Smoking prevalence rate | Per cent, for total, by sex, 2010-2024 | by sex, Age Total |
| 4.24 | Smoking prevalence rate | Per cent, for age group 15-24 yrs, by sex, 2010-2024 | by sex, 15-24 years |

All ten are `small_multiples` — one panel per country, built by three new
helpers in the Health section rather than reusing `sex_panel_figure()`
directly, because "by age groups" and "by age groups, by sex" are shapes
nothing else in the chapter draws:

- `chart_by_sex_for_age()` — Male/Female panels at one fixed `Age Group`
  (4.15/4.16/4.19/4.20/4.23/4.24). Filters to the age slice, then reuses the
  existing `panels_by_sex()`.
- `chart_by_age()` — `Age Total` vs `15-24 years` panels, `Both sexes` only
  (4.17/4.21). New `panels_by_age()` helper, coloured navy/amber
  (`AGE_COMPARISON_COLORS`) — the same two-tone pairing `AREA_COLORS` and
  `QUINTILE_COLORS` already use for a two-way split.
- `chart_by_age_and_sex()` — all four `Sex` × `Age Group` combinations in one
  panel (4.18/4.22). New `panels_by_age_and_sex()` helper, series named
  `"Male, Age Total"` etc., coloured from the first four slots of the
  already-validated `CATEGORY_COLORS` (`AGE_SEX_COLORS`).

**Percentage (4.15-4.18) is `percent=True`; the head-count (4.19-4.22) and
smoking (4.23-4.24, itself a percent indicator) follow the same rule as
everywhere else** — smoking is `percent=True` too, a genuine 0-100 share.

**Two country-years are dropped before any of the eight car-accident charts
draw, per the review:** Jordan's 2025 percentage figure (4.27%) and Oman's
2025 head-count (595 total deaths) — the only two 2025 values either
indicator carries anywhere, confirmed against the long file rather than
assumed. `car_accident_frame()` drops the named country-year and logs it as
`value excluded by review` in `chart_data_findings.txt`. Dropping them is
also what the "2010-2024" subtitle comes from: with those two points gone,
no country has a 2025 value left in either indicator, so `year_ticks()`'s own
"latest year with data" rule lands on 2024 without a separate axis override.
Smoking needed no exclusion — checked, and it carries no 2025 values at all.

### Health 4.25-4.26 — two more, latest-year bars instead of a time series

2026-10-08 review, added alongside the per-chart country drops below. Both
are `grouped_bars`, one bar per `Sex, Age Group` combination, at each
country's own latest reported year — the same four-way split 4.18/4.22
already draw as a time series, drawn here instead as a single snapshot:

| figure | title | subtitle |
|---|---|---|
| 4.25 | Percentage of deaths from car accidents | Per cent, age groups (total vs 15-24 yrs), by sex, latest available year |
| 4.26 | Number of deaths from car accidents | Number, age groups (total vs 15-24 yrs), by sex, latest available year |

`chart_by_age_and_sex_latest()` reuses `latest_breakdown()` and
`grouped_bars()` rather than writing a new latest-year mechanic — a
synthetic `"Sex, Age Group"` column (`"Male, Age Total"`, `"Female, 15-24
years"`, …) stands in for the single breakdown column those two already
expect, built from the real `Sex`/`Age Group` columns rather than kept as a
separate category list that could drift from them. Both still go through
`car_accident_frame()` first, so 4.25 drops Jordan 2025 and 4.26 drops Oman
2025 the same as the time-series versions — the bad point does not become
any country's "latest year" just because the chart changed shape. 4.25 also
drops Morocco entirely — see **Country exclusions, 2026-10-08 review**
below, added in a follow-up pass once this chart's real output showed
Morocco's bar at essentially zero.

**No `sort_by` — `grouped_bars()`'s mean-of-all-columns fallback, not a named
category.** A first version passed `sort_by="Female, Age Total"`, matching
the `sort_by="Female"` convention 4.6-4.8 already use. It read as unsorted:
Female values run far smaller than Male's for both indicators here, so
ranking by Female alone ordered rows by whichever bar happens to be
*smallest*, not by the ones a reader's eye actually follows — Morocco, the
single largest Male value in the set, landed 4th instead of near the top.
Leaving `sort_by` unset falls through to `grouped_bars()`'s own
`frame.mean(axis=1)`, which tracks each row's overall bar length and reads
as "high to low" the way the general rule intends. 4.6-4.8's `sort_by`
stays as it was — Female is a reasonably-sized, comparable figure for those
three, and the convention holds there.

The review's source document also described a new smoking-prevalence bar
chart, but the relevant section contained two contradictory drafts — a
"CHART 11" and a second, differently-worded block mislabelled "CHART 10"
(reusing the number of an already-existing, different chart), with two
different subtitles under one chart and a "2010-2024" subtitle on a declared
`BAR` type that has no time axis to carry a date range on. Asked which to
build, skipped the first time rather than guess; asked again and resolved —
see **Health 4.27-4.28** below.

### Health 4.27-4.28 — smoking, earliest year against latest, by sex

Resolved from the same ambiguous "CHART 11"/duplicate "CHART 10" block
above: two bar charts, Male/Female, each country's own earliest reported
year against its own latest, one for `Age Total` and one for `15-24 years`:

| figure | title | subtitle |
|---|---|---|
| 4.27 | Smoking prevalence rate | Per cent, for total, by sex, 2010-2024 |
| 4.28 | Smoking prevalence rate | Per cent, for age group 15-24 yrs, by sex, 2010-2024 |

**Same title and subtitle as 4.23/4.24, on purpose.** 4.23/4.24 are the time
series over the same slice; 4.27/4.28 are the same data, same stated span,
read as two points instead of the whole line — confirmed explicitly rather
than assumed: "2010-2024" stays because that genuinely is the range the data
spans, even though the chart itself draws only the two ends of it.

**No `sort_by` here either, for the same reason as 4.25/4.26 above** —
`sort_by="Female, latest"` ranked rows by whichever bar was smallest, not by
overall bar length, with the same Morocco-ranked-4th symptom. Left unset,
falling through to `grouped_bars()`'s `frame.mean(axis=1)`.

`earliest_latest_by_sex()` is new, not a reuse of `latest_breakdown()` —
that picks one year per country, and this chart needs two, whichever year a
country's own series happens to start and end on (different country to
country, same as everywhere else in this chapter). Builds a country ×
`{"Male, earliest", "Male, latest", "Female, earliest", "Female, latest"}`
table directly rather than routing through `latest_breakdown()`'s single-year
pivot. The row label carries no year the way `latest_breakdown()`'s does,
since one row here spans two different years, one per bar, and the workbook
sheet itself carries no year column either — just the four values per
country. The actual years are recoverable from the long file (each is that
country's own min/max reported year for the indicator), not read directly
off anything this chart writes; a year column on the sheet would be worth
adding if that's ever needed without going back to the source. Colours are
the first four `CATEGORY_COLORS` slots
again (`EARLIEST_LATEST_COLORS`), the same reuse `AGE_SEX_COLORS` already
established for a new four-way split in this chapter. No country exclusion —
the review named none for smoking.

### Review of 2026-10-13 — three changes (written, not yet re-run)

1. **4.27/4.28 (earliest vs latest) show the years and need two data points.**
   Each row label now reads `Country (earliest year, latest year)`, taken from
   that country's own series. A country is drawn only if both Male and Female
   have at least 2 reported years — one data point would draw "earliest" and
   "latest" as the same bar. Countries left off are logged as
   `country excluded` in `chart_data_findings.txt`.
2. **New 4.29 — Smoking prevalence rate, BAR.** Subtitle: "Per cent, for age
   groups (total and 15-24 yrs), by sex, latest available year". Same shape as
   4.25 (`chart_by_age_and_sex_latest()`: Male/Female x Age Total/15-24 years,
   each country's own latest year in its label), `percent=True`.
3. **4.11a and 4.11b share one y axis.** `chart_health_expenditure_gdp()` takes
   the higher of the two groups' peaks, rounded up to a whole per cent, and
   passes it as `y_max` to both. This replaces 4.11a's fixed `y_max=6` (and
   4.11b's unset one): non-GCC's Libya reaches about 6.3, so a fixed 6 would
   clip it and the pair would not line up.

### Country exclusions, 2026-10-08 review

Four of the percentage car-accident charts (4.15, 4.16, 4.18, 4.25) drop
Morocco entirely — every year, not one country-year — and 4.17 drops
Morocco, Palestine and the United Arab Emirates. 4.25's own Morocco row is
effectively zero (mean 0.003 across its four bars, 2026-10-08 Health
re-run) — not wrong in the sense the other guards catch, but a bar with
nothing visible on it next to countries in the double digits, so the
2026-10-08 follow-up review asked for it to be dropped the same way the
other three percentage charts already drop Morocco. `exclude_countries(frame,
chapter, what, *countries)` is the general-purpose version of the
single-country-year drop `car_accident_frame()` already did: it removes the
named countries outright and logs `country excluded by review` once per
chart that drops something, so the two kinds of exclusion — one bad
country-year across every chart an indicator feeds, versus a whole country
dropped from one specific chart — stay visibly distinct in
`chart_data_findings.txt` rather than reading as the same kind of problem.
Applied per chart, not blanket: 4.19-4.22 (the head-count charts), 4.26 (the
head-count latest-year chart) and 4.23-4.24/4.27-4.28 (smoking) keep every
country the review didn't name.

## The data guards

The charts refuse a figure rather than draw a wrong one, and every refusal is
written to `chart_data_findings.txt`. These are findings about the
questionnaires, not the code, so they outlive the run and can go back to the
country that reported them.

- `to_number()` — the same parser as notebook 4. Only 337 of 33,968 population
  cells are numeric; the rest are text like `' 701 956 '` with spaces as
  thousand separators.
- `total_or_derived()` — where a country has no `Area Total` row, the total is
  summed from an exhaustive partition (Urban + Rural, or Nationals +
  Non-nationals) and the fact is recorded. Egypt has no total rows at all.
- `drop_scale_outliers(factor=20)` — a point more than 20× off its own country's
  median is a unit or typing error, not a fact. Catches Lebanon's 2022 population
  filed as `100`. A figure filed in thousands never reaches it: notebook 1 reads
  a `الاعداد بالالف` note on the column and scales it at source, so the figure
  arrives correct instead of being dropped.
- `drop_impossible_percentages()` — a share cannot be more than all of it, so a
  value above 100 in an indicator whose own name says `(percent)` is dropped.
  Only that name is trusted: a rate per 1,000 women runs past 100 legitimately
  and a growth rate goes negative legitimately, so neither is bounded. This
  matters more than one wrong dot because `small_multiples` shares **one** y
  scale across every panel: Egypt's single 110% occupation share stretched the
  axis to 0–110 and flattened all fourteen countries onto the baseline. Algeria
  trips it too, for a different reason — it files head-counts (1,744 … 8,250)
  under a percent indicator, the same fault as the two Population `(%)`
  indicators in CLAUDE.md's known issues. Reported one line per indicator and
  country, not per point: per point it was 781 lines for Labor alone.
- `drop_contradictory_sexes()` — where Male + Female misses its own reported
  total by more than `SEX_TOTAL_TOLERANCE = 2.0`%, **the whole country-year is
  dropped**. Nothing in the file says which of the two figures is sound, so
  guessing would be worse than refusing. Catches Kuwait 2020 (total missing its
  leading digit) and Tunisia 2015 (male figure with an extra digit).
- **Population totals take only the `Total` slice of one indicator.** The
  by-nationality and by-area indicators describe the same people; summing them,
  or their parts, double-counts.
- `WHOLE_LABELS` holds *ordered fallbacks* per column, and **Age Group is
  deliberately excluded from `BREAKDOWN_COLUMNS`**. Labor's rates carry
  overlapping bands (15+, 15-24, 15-64, 25+) with no `Age Total`, so stacking
  them was meaningless; excluding the column took Labor from 19 charts to 29.
- `total_slice()` treats a blank breakdown column as its own total, not only
  an explicit label like `Nationality Total`. Different countries use
  different conventions for the same thing — Bahrain is the only country
  that writes `Nationality Total` on its pupil-teacher ratio, every other
  country just leaves Nationality blank — and recognising only the explicit
  label meant that the moment any country used it, every country using the
  other convention was silently dropped: Bahrain was the sole survivor on
  both pupil-teacher charts. Checked across all six chapters' current data
  first: no country reports a figure both ways at once, so this creates no
  double-counted total today, but the explicit label wins over a blank
  duplicate if that ever changes.
- `latest_breakdown()` never excludes a country for an incomplete report or a
  total that does not sum to 100 — it charts exactly what was reported, for
  that country's own latest year, and logs the rest as a finding instead.
  Requiring every category before charting a country used to drop nearly
  everyone: most countries only report the categories they have any of at
  all, leaving the rest a silent zero rather than an explicit one — Bahrain's
  housing-type report is two categories summing to exactly 100, the other
  six never written down. `stacked_shares()`'s x-axis widens to fit rather
  than clipping a country whose reported categories sum past 100 at the 100
  line — Qatar's housing-type report sums to 200 (looks like doubled rows)
  and now draws as a bar running to 200, visibly wrong, rather than being cut
  off invisibly at 100.

## The chart data on each sheet

Captured **inside the drawing primitives**, not in the chart functions. The
primitive is the last place that still holds exactly what was drawn, after every
filter and guard has run, so a sheet cannot drift away from the picture above it.
`record_data(stem, frame)` stores it; `CHART_DATA` holds it until the workbook is
written.

If you add a primitive, add a `record_data` call before its `save()` or its
charts will render but get no sheet — the run reports that rather than failing.

## Environment

- **plotly cannot be installed here** (no package index), and the originals were
  plotly exports. Everything is reproduced in matplotlib with the `Agg` backend.
  Don't try to install it again.
- Excel locks files it has open. If a write fails, check `<Chapter>_*.xlsx` and
  the output workbook are closed.
- **The source files can still change mid-session.**
  `Population_EN.xlsx` was once observed going 0 bytes → 2 KB → 17.6 MB while a
  pipeline run finished in another window. Before charting, confirm the source is
  a valid zip and its size has stopped changing; treat the live file as
  authoritative over any earlier snapshot.
- Verify writes explicitly rather than assuming they landed — the notebook's last
  cell re-opens every file, checks it is a real SVG carrying drawn marks, and
  re-opens the workbook to confirm each sheet has both a picture and a table.
- Run the notebook by executing its cells from a script (`py -u`), not through a
  subagent.
