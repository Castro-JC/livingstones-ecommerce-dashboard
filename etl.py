import sqlite3
from pathlib import Path
import numpy as np
import pandas as pd

BASE = Path(__file__).parent
CSV_PATH = BASE / "data" / "stg_orders.csv"
DB_PATH = BASE / "data" / "livingstones.db"

def extract():
    return pd.read_csv(CSV_PATH, sep=";")

def transform(df):
    df = df.copy()
    df["order_date"] = pd.to_datetime(df["order_date"], format="%d/%m/%Y")
    df = df.drop_duplicates(subset="order_id")
    df["order_date"] = df["order_date"].dt.strftime("%Y-%m-%d")
    return df

def load(df):
    with sqlite3.connect(DB_PATH) as con:
        df.to_sql("orders", con, if_exists="replace", index=False)
        con.executescript("""
            CREATE INDEX IF NOT EXISTS ix_orders_date ON orders(order_date);
            CREATE INDEX IF NOT EXISTS ix_orders_cust ON orders(customer_id);
            DROP VIEW IF EXISTS v_orders;
            CREATE VIEW v_orders AS
            SELECT o.*,
                CAST(strftime('%Y', order_date) AS INTEGER) AS anio,
                CAST(strftime('%m', order_date) AS INTEGER) AS mes,
                CASE
                    WHEN CAST(ROUND(discount * 100) AS INTEGER) = 0 THEN '0% Sin Descuento'
                    WHEN CAST(ROUND(discount * 100) AS INTEGER) <= 10 THEN '1% - 10% Bajo'
                    WHEN CAST(ROUND(discount * 100) AS INTEGER) <= 20 THEN '11% - 20% Medio'
                    ELSE 'Más de 20% Alto'
                END AS banda_descuento
            FROM orders o;
        """)

if __name__ == "__main__":
    data = transform(extract())
    load(data)
    print(f"OK -> {DB_PATH} ({len(data):,} filas)")
