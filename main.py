# standard library
from pathlib import Path

# local imports
from library.csv import load_csv

# third-party imports
import pandas as pd
import matplotlib.pyplot as plt
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def game_summary(df: pd.DataFrame):
    # market profit
    # TODO remove market data
    total_paid = df["total"].sum()
    avg_paid = df["total"].mean()

    now = pd.Timestamp.now().normalize()
    last_7 = df[df["date"] >= now - pd.Timedelta(days=7)]
    last_30 = df[df["date"] >= now - pd.Timedelta(days=30)]
    last_365 = df[df["date"] >= now - pd.Timedelta(days=365)]

    prev_7 = df[
        (df["date"] >= now - pd.Timedelta(days=14))
        & (df["date"] <= now - pd.Timedelta(days=7))
    ]

    prev_30 = df[
        (df["date"] >= now - pd.Timedelta(days=60))
        & (df["date"] <= now - pd.Timedelta(days=30))
    ]

    prev_365 = df[
        (df["date"] >= now - pd.Timedelta(days=730))
        & (df["date"] <= now - pd.Timedelta(days=365))
    ]

    summary = Panel(
        f"""
    [bold cyan]Last 7:[/]   ${last_7["total"].sum():,.2f}
    [bold cyan]Last 30:[/]  ${last_30["total"].sum():,.2f}
    [bold cyan]Last 365:[/]   ${last_365["total"].sum():,.2f}

    [bold cyan]Previous 7:[/]  ${prev_7["total"].sum():,.2f}
    [bold cyan]Previous 30:[/] ${prev_30["total"].sum():,.2f}
    [bold cyan]Previous 365:[/]  ${prev_365["total"].sum():,.2f}

    [bold cyan]Avg Price:[/] ${avg_paid:,.2f}
    [bold cyan]Total Payed:[/] ${total_paid:,.2f}
        """,
        title="Game Summary",
        border_style="green",
        expand=False,
    )
    console.print(summary)


def market_summary(df: pd.DataFrame):
    df = df[df["market"]]
    total_profit = df["total"].sum()
    total_revenue = df["total"].sum()
    total_bought = df["total"].sum()

    summary = Panel(
        f"""
    [bold cyan]Total Profit:[/] ${total_profit:.2f}
    [bold cyan]Total Revenue:[/] ${total_revenue:.2f}
    [bold cyan]Total Bought:[/] ${total_bought:.2f}
        """,
        title="Market Summary",
        border_style="green",
        expand=False,
    )
    console.print(summary)


def purchases_by_month(df: pd.DataFrame):
    df = df[~df["not_games"]]
    plt.figure(figsize=(20, 10))
    plt.plot(df["date"], df["total"], marker="o")
    plt.xlabel("Date")
    plt.ylabel("Amount Spent ($)")
    plt.title("Steam Purchases Over Time")
    plt.grid(True)
    plt.show()


def cumulative(df: pd.DataFrame):
    # cumulative total by month
    # b.index = pd.to_datetime(b['date'],format='%m/%d/%y %I:%M%p')
    # b.groupby(by=[b.index.month, b.index.year])
    # or
    # I think the more pandonic ways are to either use resample
    # (when it provides the functionality you need) or use a TimeGrouper: df.groupby(pd.TimeGrouper(freq='M'))

    # df = df.set_index("date")
    # df = df.resample("M").sum()

    df = df[~df["not_games"]]
    df["cumulative_total"] = df["total"].cumsum()
    plt.figure(figsize=(20, 10))
    plt.plot(df["date"], df["cumulative_total"], marker="o")
    plt.xlabel("Date")
    plt.ylabel("Total Spent ($)")
    plt.title("Cumulative Steam Spending")
    plt.grid(True)
    plt.show()

    # WIP finish monthly
    # monthly = df.set_index("date").resample("M")["total"].sum()
    # plt.figure(figsize=(20, 10))
    # monthly.plot(kind="bar")
    # plt.xlabel("Month")
    # plt.ylabel("Total Spent ($)")
    # plt.title("Monthly Steam Spending")
    # plt.tight_layout()
    # plt.show()


def price_f(price):
    polarity = "-" if price < 0 else ""
    return f"{polarity}${abs(price):.2f}"


def in_game_purchases(df: pd.DataFrame):
    # ensure numeric
    df["total"] = pd.to_numeric(df["total"], errors="coerce")
    in_game = df[df["type"] == "In-Game Purchase"]
    sums = in_game.groupby("name", as_index=False)["total"].sum()
    sorted_sums = sums.sort_values(by="total", ascending=False)  # type: ignore

    TABLE_TITLE = "In-Game Purchase Totals"
    table = Table(
        title=TABLE_TITLE,
        show_lines=True,
        title_style="bold",
        style="green3",
    )
    table.add_column("Name", justify="left")
    table.add_column("Total", justify="right")

    ignore = ["STAR WARS&trade;: Squadrons Pre-order Edition"]

    all_total = 0
    for _, row in sorted_sums.iterrows():
        name, total = row["name"], row["total"]
        # games to ignore
        if name in ignore:
            print("yay")
            continue
        if name == "Uninitialized":
            continue
        all_total += total
        row = [name, f"${total:.2f}"]
        table.add_row(*row)

    # total summary
    summary = Panel(
        f"""
    [bold cyan]Purchase Total:[/] ${all_total:.2f}
        """,
        title="In-Game Purchase Summary",
        border_style="green",
        expand=False,
    )
    console.print(summary)
    console.print(table, new_line_start=True)


def purchase_history_stats(df: pd.DataFrame):
    # parses dates
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    # non game mask
    ignore_keywords = ["Market", "Valve Index", "Steam Deck"]
    df["not_games"] = df["name"].str.contains(
        "|".join(ignore_keywords), case=False, na=False
    )
    # market mask
    df["market"] = df["type"].str.contains("Market", case=False, na=False)

    game_summary(df)
    market_summary(df)
    in_game_purchases(df)
    # purchases_by_month(df)
    # cumulative(df)


def recent_purchases(df: pd.DataFrame, n=14):
    TABLE_TITLE = f"Recent Purchases ({n} Days)"
    table = Table(
        title=TABLE_TITLE,
        show_lines=True,
        title_style="bold",
        style="green3",
    )
    table.add_column("Name", justify="left")
    table.add_column("Type", justify="left")
    table.add_column("Total", justify="right")
    table.add_column("Date", justify="right")

    # TODO remove anything that was refunded

    for _, row in df.iterrows():
        if not n:
            break
        name = row["name"]
        type = row["type"]
        total = row["total"]
        date = row["date"]
        if name == "Uninitialized":
            continue
        row = [
            name,
            type,  # TODO change color by type
            price_f(total),  # TODO change color by price
            date.strftime("%b %d, %Y"),  # TODO change color by current month
        ]
        table.add_row(*row)
        n -= 1

    console.print(table, new_line_start=True)


def main():
    dataframe = load_csv()
    purchase_history_stats(dataframe)
    recent_purchases(dataframe)


if __name__ == "__main__":
    main()
