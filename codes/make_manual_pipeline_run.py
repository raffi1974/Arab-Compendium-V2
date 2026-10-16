# -*- coding: utf-8 -*-
r"""Build "manual pipeline run\" - the notebooks to run by hand in VS Code or
Jupyter, one after another, each with Run All and nothing typed in:

    0_Data_Quality_Check.ipynb     data quality Part 1 - the issue reports
    1_Long_Files.ipynb ... 6_Charts.ipynb
    7_Data_Quality_Report.ipynb    data quality Part 2 - gaps report, dashboard

Every one is a copy of a notebook in codes\ - nothing is changed on the way,
only split (the data quality notebook's two parts become 0 and 7) and given a
first cell saying where it sits in the run. So never edit the copies: change
the notebook in codes\, then re-run this script and the copies follow.

    py make_manual_pipeline_run.py
"""
import json
from pathlib import Path

CODES = Path(__file__).resolve().parent
OUT = CODES / "manual pipeline run"
DATA_QUALITY = CODES / "data quality" / "Compendium_Data_Quality.ipynb"

# Part 2 of the data quality notebook starts at this cell. It reuses Part 1's
# imports and paths, so its copy carries those two cells ahead of it.
PART_2_FIRST_CELL = "intro2"
PART_2_NEEDS = ["imports", "config"]

# (copy's name, source notebook, which cells)
STEPS = [
    ("0_Data_Quality_Check.ipynb", DATA_QUALITY, "part 1"),
    ("1_Long_Files.ipynb", CODES / "Compendium_1_Long_Files.ipynb", "all"),
    ("2_New_Indicators.ipynb", CODES / "Compendium_2_New_Indicators.ipynb", "all"),
    ("3_External_Data.ipynb", CODES / "Compendium_3_External_Data.ipynb", "all"),
    ("4_Translation.ipynb", CODES / "Compendium_4_Translation.ipynb", "all"),
    ("5_Tabulations.ipynb", CODES / "Compendium_5_Tabulations.ipynb", "all"),
    ("6_Charts.ipynb", CODES / "Compendium_6_Charts.ipynb", "all"),
    ("7_Data_Quality_Report.ipynb", DATA_QUALITY, "part 2"),
]


def pick_cells(cells, which):
    if which == "all":
        return cells
    ids = [cell.get("id") for cell in cells]
    split = ids.index(PART_2_FIRST_CELL)
    if which == "part 1":
        return cells[:split]
    return [cell for cell in cells[:split] if cell.get("id") in PART_2_NEEDS] + cells[split:]


def header_cell(step, name, source):
    last = step == len(STEPS) - 1
    after = ("This is the last step." if last else
             f"When it finishes, open **`{STEPS[step + 1][0]}`**.")
    text = (f"**Manual pipeline run - step {step} of {len(STEPS) - 1}** (`{name}`)\n\n"
            f"Run All. {after} Nothing has to be typed in - every notebook in\n"
            f"this folder runs top to bottom on its own.\n\n"
            f"A copy of `codes\\{source.relative_to(CODES)}`, made by\n"
            f"`make_manual_pipeline_run.py`. Change that notebook, not this copy,\n"
            f"then re-run the script.")
    return {"cell_type": "markdown", "id": "manualrun", "metadata": {},
            "source": text.splitlines(keepends=True)}


def build():
    OUT.mkdir(exist_ok=True)
    for stale in OUT.glob("*.ipynb"):
        stale.unlink()                 # a renamed step must not leave its old copy behind

    for step, (name, source, which) in enumerate(STEPS):
        notebook = json.loads(source.read_text(encoding="utf-8"))
        cells = [dict(cell) for cell in pick_cells(notebook["cells"], which)]
        for cell in cells:
            if cell["cell_type"] == "code":
                cell["outputs"], cell["execution_count"] = [], None
                compile("".join(cell["source"]), f"{name}:{cell.get('id')}", "exec")
        notebook["cells"] = [header_cell(step, name, source)] + cells

        path = OUT / name
        path.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n",
                        encoding="utf-8")
        print(f"  {name:<30} {len(cells):>3} cells  <- {source.relative_to(CODES)}"
              + (f" ({which})" if which != "all" else ""))


if __name__ == "__main__":
    print(f"Writing {OUT}")
    build()
