import csv
import json
import time
from pathlib import Path
from datetime import datetime, timedelta

from kafka import KafkaProducer


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = PROJECT_ROOT / "data" / "prepared_transactions.csv"

KAFKA_SERVER = "localhost:9092"

TOPIC = "purchase_events"

# Number of records for testing
MAX_RECORDS = 300

# Real delay between Kafka messages
MESSAGE_DELAY = 0.5

# Each Kafka event represents 1 simulated minute
SIMULATED_MINUTES_PER_EVENT = 0.1


# ============================================================
# CHECK DATA FILE
# ============================================================

print("=" * 60)
print("RETAIL E-COMMERCE ANALYTICS")
print("KAFKA REAL-TIME PRODUCER")
print("=" * 60)

print("\nData file:")
print(DATA_FILE)

if not DATA_FILE.exists():
    print("\nERROR: prepared_transactions.csv not found!")
    print(DATA_FILE)
    exit(1)

print("\nData file found.")


# ============================================================
# CREATE SIMULATED START TIME
# ============================================================

simulation_start = datetime.now().replace(microsecond=0)

print("\nSimulation start time:")
print(simulation_start)


# ============================================================
# CREATE KAFKA PRODUCER
# ============================================================

print("\nConnecting to Kafka...")

producer = KafkaProducer(
    bootstrap_servers=[KAFKA_SERVER],
    value_serializer=lambda value:
        json.dumps(value).encode("utf-8"),
    acks="all"
)

print("Connected to Kafka.")
print(f"Kafka topic: {TOPIC}")


# ============================================================
# STREAM DATA
# ============================================================

count = 0

try:

    with open(
        DATA_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            # ------------------------------------------------
            # Generate simulated event time
            # ------------------------------------------------

            simulated_time = (
                simulation_start
                + timedelta(
                    minutes=count * SIMULATED_MINUTES_PER_EVENT
                )
            )

            # ------------------------------------------------
            # Create Kafka event
            # ------------------------------------------------

            event = {
                "event_time": simulated_time.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

                "order_id": int(row["order_id"]),

                "product_id": int(row["product_id"]),

                "product_name": row["product_name"],

                "quantity": int(row["quantity"])
            }

            # ------------------------------------------------
            # Send event to Kafka
            # ------------------------------------------------

            producer.send(
                TOPIC,
                value=event
            )

            count += 1

            # ------------------------------------------------
            # Display progress
            # ------------------------------------------------

            if count <= 100 or count % 100 == 0:

                print(
                    f"[PRODUCER] Event #{count} SENT - "
                    f"{event['product_name']} | "
                    f"Product ID: {event['product_id']} | "
                    f"Event Time: {event['event_time']}"
                )

            # ------------------------------------------------
            # Control streaming speed
            # ------------------------------------------------

            time.sleep(MESSAGE_DELAY)

            # ------------------------------------------------
            # Stop after test records
            # ------------------------------------------------

            if count >= MAX_RECORDS:
                break


except KeyboardInterrupt:

    print("\nProducer stopped by user.")


finally:

    producer.flush()

    producer.close()

    print("\n" + "=" * 60)
    print("PRODUCER FINISHED")
    print("=" * 60)

    print(f"Total records sent: {count}")

    print(f"Kafka topic: {TOPIC}")