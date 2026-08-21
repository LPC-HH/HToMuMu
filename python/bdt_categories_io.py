import json
from pathlib import Path

BDT_CATEGORIES_PATH = Path(__file__).resolve().parent.parent / "root_io" / "bdt_categories.json"


def load_bdt_categories(path=BDT_CATEGORIES_PATH):
    if not Path(path).exists():
        return {}
    with open(path) as f:
        return json.load(f)


def save_bdt_category(channel, era, subset_title, mass_variable, boundaries, path=BDT_CATEGORIES_PATH):
    data = load_bdt_categories(path)
    data.setdefault(channel, {}).setdefault(era, {}).setdefault(subset_title, {})[mass_variable] = boundaries
    with open(path, "w") as f:
        json.dump(data, f, indent=2, sort_keys=True)


def get_bdt_cuts(data, channel, era, subset_title, mass_variable):
    try:
        return data[channel][era][subset_title][mass_variable]
    except KeyError:
        raise KeyError(
            f"No BDT category boundaries found for channel={channel!r}, era={era!r}, "
            f"subset_title={subset_title!r}, mass_variable={mass_variable!r}. "
            "Run plot_macros/plot_BDT_Categories.py for this combination first."
        )
