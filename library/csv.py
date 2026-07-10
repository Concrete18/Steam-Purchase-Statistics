# standard library
from pathlib import Path
import json, csv

# third-party imports
import pandas as pd


def load_purchase_data() -> list[dict]:
    """
    Loads purchase history from config folder.
    """
    path = Path("data/purchase_history.json")
    if path.exists():
        with open(path) as file:
            return json.load(file)
    return []


def create_csv():
    """
    Docstring for create_csv
    """
    print("Creating CSV")
    market = []
    purchases = []
    data = load_purchase_data()
    for entry in data:
        games = entry.get("games", [])
        date = entry.get("date")
        total = entry.get("total", 0)
        entry_type = entry.get("type", "Unknown")

        # TODO allow for removal of refunded games entirely as an option
        # market data
        if "market" in entry_type.lower():
            count = entry_type.split(" ")
            if len(count) == 3:
                count = entry_type.split(" ")[0]
            else:
                count = 1
            market.append([date, total, count])
            continue
        # purchase data
        if len(games) == 1:
            purchases.append([games[0], date, entry_type, "", total])
        elif entry_type == "In-Game Purchase":
            purchases.append([games[0], date, entry_type, games[1], total])
        else:
            first = True
            for game in games:
                grouped_total = total if first else 0
                first = False
                purchases.append(
                    [
                        game,
                        date,
                        entry_type,
                        "grouped purchase",
                        grouped_total,
                    ]
                )
    print("Created Rows")

    with open("data/purchase_history.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["name", "date", "type", "desc", "total"])
        for row in purchases:
            writer.writerow(row)

    with open("data/market_history.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["date", "total", "count"])
        for row in market:
            writer.writerow(row)

    print("CSV Creation Complete")


def load_csv(recreate_csv=False):
    csv = Path("data/purchase_history_final.csv")
    if recreate_csv or not csv.exists():
        create_csv()
    df = pd.read_csv(csv, na_values="?")
    return df


if __name__ == "__main__":
    create_csv()
