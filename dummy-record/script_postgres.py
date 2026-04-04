"""
seed_postgresql.py
------------------
Inserts 200 dummy Transaction records directly into a PostgreSQL database.

Usage:
    python seed_postgresql.py
    python seed_postgresql.py --host localhost --port 5432 --db mydb --user postgres --password secret
    python seed_postgresql.py --count 500   # insert more records

    # Or set environment variables (recommended for production):
    DB_HOST=localhost DB_PORT=5432 DB_NAME=mydb DB_USER=postgres DB_PASSWORD=secret python seed_postgresql.py

Requirements:
    pip install psycopg2-binary faker
"""

import argparse
import os
import random
from datetime import datetime, timedelta

try:
    import psycopg2
    from psycopg2.extras import execute_values
except ImportError:
    raise SystemExit("psycopg2 is not installed. Run: pip install psycopg2-binary")

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

def random_datetime(days_back: int = 365) -> datetime:
    """Return a random datetime within the past `days_back` days."""
    delta = timedelta(
        days=random.randint(0, days_back),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59),
    )
    return datetime.now() - delta


def random_amount() -> float:
    """Return a realistic decimal amount."""
    return round(random.uniform(50, 25000), 2)


def make_record() -> tuple:
    """Build one dummy transaction row."""
    t_type    = random.choice(TRANSACTION_TYPES)
    category  = random.choice(TRANSACTION_CATEGORIES)
    desc      = random.choice(DESCRIPTIONS[category])
    amount    = random_amount()
    tx_at     = random_datetime()
    return (tx_at, amount, t_type, category, desc)


# ── DB helpers ────────────────────────────────────────────────────────────────

def get_connection(args) -> "psycopg2.connection":
    """Create and return a psycopg2 connection using args or env vars."""
    return psycopg2.connect(
        host=args.host,
        port=args.port,
        dbname=args.db,
        user=args.user,
        password=args.password,
    )


def ensure_table(cursor) -> None:
    """Create the transactions table if it doesn't already exist."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions_transaction (
            id               SERIAL PRIMARY KEY,
            transaction_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            amount           NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
            transaction_type VARCHAR(10)  NOT NULL,
            category         VARCHAR(20)  NOT NULL,
            description      VARCHAR(255) NOT NULL
        )
    """)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Seed PostgreSQL with dummy Transaction records")
    parser.add_argument("--host",     default=os.getenv("DB_HOST", "localhost"))
    parser.add_argument("--port",     default=int(os.getenv("DB_PORT", 5432)), type=int)
    parser.add_argument("--db",       default=os.getenv("DB_NAME", "finsight_db"))
    parser.add_argument("--user",     default=os.getenv("DB_USER", "admin"))
    parser.add_argument("--password", default=os.getenv("DB_PASSWORD", "admin123"))
    parser.add_argument("--count",    default=200, type=int, help="Number of records to insert")
    args = parser.parse_args()

    print(f"🔌  Connecting to PostgreSQL at {args.host}:{args.port}/{args.db} …")
    conn = get_connection(args)
    conn.autocommit = False
    cursor = conn.cursor()

    ensure_table(cursor)

    records = [make_record() for _ in range(args.count)]

    execute_values(
        cursor,
        """
        INSERT INTO transactions_transaction
            (transaction_at, amount, transaction_type, category, description)
        VALUES %s
        """,
        records,
    )

    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM transactions_transaction")
    total = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    print(f"✅  Inserted {args.count} records into 'transactions_transaction'")
    print(f"   Total rows in table: {total}")


if __name__ == "__main__":
    main()