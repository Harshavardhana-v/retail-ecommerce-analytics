import json
import csv
from pathlib import Path

from kafka import KafkaConsumer


# ============================================================
# CONFIGURATION
# ============================================================

KAFKA_SERVER = "localhost:9092"
TOPIC = "purchase_events"
GROUP_ID = "hdfs-consumer-group"

PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUTPUT_DIR = PROJECT_ROOT / "data" / "hdfs_batches"
OUTPUT_FILE = OUTPUT_DIR / "purchase_batch.csv"

MAX_MESSAGES = 1000


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# CONNECT TO KAFKA
# ============================================================

print("=" * 60)
print("KAFKA → HDFS CONSUMER")
print("=" * 60)

print("\nConnecting to Kafka...")

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=[KAFKA_SERVER],
    group_id=GROUP_ID,
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    value_deserializer=lambda value:
        json.loads(value.decode("utf-8"))
)

print("Connected to Kafka.")
print("Topic:", TOPIC)


# ============================================================
# RECEIVE KAFKA MESSAGES
# ============================================================

count = 0

with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.writer(file)

    writer.writerow([
        "event_time",
        "order_id",
        "product_id",
        "product_name",
        "quantity"
    ])

    print("\nWaiting for messages...\n")

    try:

        for message in consumer:

            event = message.value

            writer.writerow([
                event["event_time"],
                event["order_id"],
                event["product_id"],
                event["product_name"],
                event["quantity"]
            ])

            count += 1

            if count <= 10 or count % 100 == 0:

                print(
                    f"Received {count}: "
                    f"{event['product_name']}"
                )

            if count >= MAX_MESSAGES:
                break

    except KeyboardInterrupt:

        print("\nConsumer stopped.")

    finally:

        consumer.close()


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("CONSUMER COMPLETE")
print("=" * 60)

print("Messages received:", count)
print("Batch file:", OUTPUT_FILE)