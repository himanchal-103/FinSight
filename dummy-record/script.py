"""
seed_sqlite.py
--------------
Inserts 200 dummy Transaction records directly into a SQLite database.

Usage:
    python seed_sqlite.py                    # uses db.sqlite3 in current dir
    python seed_sqlite.py --db /path/to/db   # custom path

Requirements:
    pip install faker
"""

import argparse
import random
import sqlite3
from datetime import datetime, timedelta

try:
    from faker import Faker
except ImportError:
    raise SystemExit("Faker is not installed. Run: pip install faker")

# ── Config ────────────────────────────────────────────────────────────────────
TRANSACTION_TYPES = ["deposit", "withdrawn"]
TRANSACTION_CATEGORIES = [
    "payroll",
    "parts_purchase",
    "shop_expense",
    "service_charge",
]

DESCRIPTIONS = {
    "payroll": [
        "Monthly payroll for shop staff",
        "Weekly wages for technicians",
        "Overtime pay for mechanics",
        "Bonus payment for senior staff",
        "Part-time worker salary",
    ],
    "parts_purchase": [
        "Brake pads and rotors purchase",
        "Engine oil and filters bulk order",
        "Transmission parts from supplier",
        "Suspension components restock",
        "Exhaust system parts purchase",
        "Battery and electrical components",
        "Tyre purchase for customer order",
    ],
    "shop_expense": [
        "Monthly electricity bill",
        "Water and utilities payment",
        "Shop rent payment",
        "Equipment maintenance fee",
        "Cleaning supplies purchase",
        "Internet and phone bill",
        "Office stationery restock",
    ],
    "service_charge": [
        "Full service charge - sedan",
        "Oil change service fee",
        "Tyre rotation and alignment charge",
        "Brake inspection service",
        "AC recharge service charge",
        "Engine diagnostic fee",
        "Annual vehicle inspection charge",
    ],
}

faker = Faker()
# ── Helpers ───────────────────────────────────────────────────────────────────

def random_datetime(days_back: int = 365) -> str:
    """Return a random ISO datetime string within the past `days_back` days."""
    delta = timedelta(
        days=random.randint(0, days_back),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59),
    )
    dt = datetime.now() - delta
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def random_amount() -> str:
    """Return a realistic decimal amount as a string."""
    return f"{random.uniform(50, 25000):.2f}"


def make_record() -> tuple:
    """Build one dummy transaction row."""
    t_type = random.choice(TRANSACTION_TYPES)
    category = random.choice(TRANSACTION_CATEGORIES)
    description = random.choice(DESCRIPTIONS[category])
    amount = random_amount()
    transaction_at = random_datetime()
    return (transaction_at, amount, t_type, category, description)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Seed SQLite with 200 Transaction records")
    parser.add_argument("--db", default="db.sqlite3", help="Path to SQLite database file")
    parser.add_argument("--count", type=int, default=200, help="Number of records to insert")
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    cursor = conn.cursor()

    # Create table if it doesn't exist (mirrors the Django model)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions_transaction (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_at  DATETIME NOT NULL,
            amount          DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
            transaction_type VARCHAR(10) NOT NULL,
            category        VARCHAR(20) NOT NULL,
            description     VARCHAR(255) NOT NULL
        )
    """)

    records = [make_record() for _ in range(args.count)]

    cursor.executemany(
        """
        INSERT INTO transactions_transaction
            (transaction_at, amount, transaction_type, category, description)
        VALUES (?, ?, ?, ?, ?)
        """,
        records,
    )

    conn.commit()
    total = cursor.execute("SELECT COUNT(*) FROM transactions_transaction").fetchone()[0]
    conn.close()

    print(f"✅  Inserted {args.count} records into '{args.db}'")
    print(f"   Total rows in table: {total}")


if __name__ == "__main__":
    main()