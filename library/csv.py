# standard library
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


def create_csv():
    """
    Docstring for create_csv
    """
    print("Creating CSV")
    data = load_purchase_data()
    with open("data/steam_purchase_history.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["name", "date", "type", "desc", "total"])
        for entry in data:
            games = entry.get("games", [])
            date = entry.get("date")
            total = entry.get("total", 0)
            entry_type = entry.get("type", "Unknown")

            # TODO allow for removal of refunded games entirely as an option
            rows = []
            if len(games) == 1:
                rows.append([games[0], date, entry_type, "", total])
            elif entry_type == "In-Game Purchase":
                rows.append([games[0], date, entry_type, games[1], total])
            else:
                first = True
                for game in games:
                    grouped_total = total if first else 0
                    first = False
                    rows.append(
                        [game, date, entry_type, "grouped purchase", grouped_total]
                    )
            for row in rows:
                writer.writerow(row)
    print("CSV Creation Complete")


def load_csv(recreate_csv=False):
    csv = Path("data/steam_purchase_history.csv")
    if recreate_csv or not csv.exists():
        create_csv()
    df = pd.read_csv(csv, na_values="?")
    return df


if __name__ == "__main__":
    create_csv()
