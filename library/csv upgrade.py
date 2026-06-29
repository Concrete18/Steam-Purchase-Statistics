# standard library
from dataclasses import dataclass
from pathlib import Path
import json, csv

# third-party imports
import pandas as pd


def load_purchase_data() -> list[dict]:
    """
    Loads purchase history from config folder.
    """
    path = Path("data/steam_purchase_history.json")
    if path.exists():
        with open(path) as file:
            return json.load(file)
    return []


@dataclass
class Game:
    name: str
    date: str
    entry_type: str
    total: float
    refunded: bool

    @property
    def row(self) -> list:
        return [
            self.name,
            self.date,
            self.entry_type,
            "",
            self.total,
        ]


def create_csv(ignore_refunded=False):
    """
    Docstring for create_csv
    """
    print("Creating CSV")
    data = load_purchase_data()
    with open("data/steam_purchase_history.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["name", "date", "type", "desc", "total"])
        refunded = []
        for entry in data:
            names = entry.get("names", [])
            date = entry.get("date", "")
            total = entry.get("total", 0)
            entry_type = entry.get("type", "Unknown")
            rows = []
            if len(names) == 1:
                name = names[0]
                # if not isinstance(name, str):
                #     continue
                game = Game(
                    name=name,
                    date=date,
                    entry_type=entry_type,
                    total=total,
                    refunded=False,
                )
                rows.append([names[0], date, entry_type, "", total])
            elif entry_type == "In-Game Purchase":
                rows.append([names[0], date, entry_type, names[1], total])
            else:
                first = True
                for game in names:
                    if ignore_refunded:
                        if game.refunded:
                            continue
                    grouped_total = total if first else 0
                    first = False
                    rows.append(
                        [game, date, entry_type, "grouped purchase", grouped_total]
                    )
            for row in rows:
                writer.writerow(row)
    print("CSV Creation Complete")
    if refunded:
        print(f"{len(refunded)} Refunded game(s) missing purchase(s)")


def load_csv(recreate_csv=False):
    csv = Path("data/steam_purchase_history.csv")
    if recreate_csv or not csv.exists():
        create_csv(ignore_refunded=True)
    df = pd.read_csv(csv, na_values="?")
    return df


if __name__ == "__main__":
    create_csv()
