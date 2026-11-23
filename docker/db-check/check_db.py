"""One-shot PostgreSQL connection check; exit 0 on success and 1 on failure."""
import os
import time

import psycopg2


def main():
    for attempt in range(1, 11):
        try:
            with psycopg2.connect(
                host=os.getenv("DB_HOST", "db"),
                port=int(os.getenv("DB_PORT", "5432")),
                dbname=os.getenv("DB_NAME", "shoe_store"),
                user=os.getenv("DB_USER", "shoe_user"),
                password=os.environ["DB_PASSWORD"],
                connect_timeout=3,
            ) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT current_database()")
                    name = cursor.fetchone()[0]
                    cursor.execute("""
                        SELECT COUNT(*) FROM information_schema.tables
                        WHERE table_schema='public' AND table_type='BASE TABLE'
                    """)
                    count = cursor.fetchone()[0]
            print(f"OK: база={name}; таблиц={count}", flush=True)
            return 0
        except psycopg2.OperationalError:
            # Never print credentials or a connection string in shared logs.
            print(f"Попытка {attempt}/10: PostgreSQL недоступен; проверьте DNS, порт и параметры доступа.", flush=True)
            if attempt < 10:
                time.sleep(3)
    print("Ошибка: подключение к PostgreSQL не установлено", flush=True)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
