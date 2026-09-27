import json
import time
from pathlib import Path
from collections import deque, defaultdict
from datetime import datetime, timedelta

from kafka import KafkaConsumer


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

KAFKA_SERVER = "localhost:9092"
TOPIC = "purchase_events"

# Trailing window
WINDOW_MINUTES = 60

# Dashboard result file
OUTPUT_FILE = PROJECT_ROOT / "data" / "top20_realtime.json"

# Print dashboard result every 5 seconds
DISPLAY_INTERVAL = 5


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# KAFKA CONSUMER
# ============================================================

print("=" * 60)
print("RETAIL E-COMMERCE ANALYTICS")
print("REAL-TIME 60-MINUTE CONSUMER")
print("=" * 60)

print("\nConnecting to Kafka...")

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=[KAFKA_SERVER],

    group_id=f"realtime-dashboard-demo-{int(time.time())}",

    auto_offset_reset="earliest",

    enable_auto_commit=True,

    value_deserializer=lambda value:
        json.loads(value.decode("utf-8"))
)

print("Connected to Kafka.")
print(f"Topic: {TOPIC}")
print(f"Window: {WINDOW_MINUTES} minutes")


# ============================================================
# SLIDING WINDOW
# ============================================================

# Each item:
# (event_time, product_id, product_name, quantity)

events = deque()


# ============================================================
# VARIABLES
# ============================================================

last_display_time = time.time()

event_count = 0


# ============================================================
# FUNCTION: REMOVE OLD EVENTS
# ============================================================

def remove_old_events(current_time):

    window_start = (
        current_time
        - timedelta(minutes=WINDOW_MINUTES)
    )

    while events:

        oldest_event_time = events[0][0]

        if oldest_event_time < window_start:
            events.popleft()
        else:
            break


# ============================================================
# FUNCTION: CALCULATE TOP 20
# ============================================================

def calculate_top20():

    product_totals = defaultdict(int)

    product_names = {}

    for (
        event_time,
        product_id,
        product_name,
        quantity
    ) in events:

        product_totals[product_id] += quantity

        product_names[product_id] = product_name

    # Sort by quantity descending
    sorted_products = sorted(
        product_totals.items(),
        key=lambda item: item[1],
        reverse=True
    )

    top20 = []

    for product_id, units_sold in sorted_products[:20]:

        top20.append({
            "product_id": product_id,
            "product_name": product_names[product_id],
            "units_sold": units_sold
        })

    return top20


# ============================================================
# FUNCTION: SAVE RESULT
# ============================================================

def save_result(
    current_time,
    top20
):

    result = {

        "window_start": (
            current_time
            - timedelta(minutes=WINDOW_MINUTES)
        ).strftime("%Y-%m-%d %H:%M:%S"),

        "window_end": current_time.strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "window_minutes": WINDOW_MINUTES,

        "generated_at": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "total_events_in_window": len(events),

        "total_events_received": event_count,

        "latest_event":{
            "product_id": product_id,
            "product_name": product_name,
            "event_time": event_time.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "quantity": quantity
        },

        "top_products": top20
    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            result,
            file,
            indent=4
        )


# ============================================================
# MAIN CONSUMER LOOP
# ============================================================

try:

    for message in consumer:

        event = message.value

        # ----------------------------------------------------
        # Read event
        # ----------------------------------------------------

        event_time = datetime.strptime(
            event["event_time"],
            "%Y-%m-%d %H:%M:%S"
        )

        product_id = int(
            event["product_id"]
        )

        product_name = event[
            "product_name"
        ]

        quantity = int(
            event["quantity"]
        )

        # ----------------------------------------------------
        # Add event to sliding window
        # ----------------------------------------------------

        events.append(
            (
                event_time,
                product_id,
                product_name,
                quantity
            )
        )

        event_count += 1


        if event_count <=20 or event_count % 100 == 0:
            print(
                f"[CONSUMER] Event #{event_count} RECEIVED -"
                f"{product_name} |"
                f"Product ID: {product_id} |"
                f"Event Time: {event_time}"
            )

        # ----------------------------------------------------
        # Remove events older than 60 minutes
        # ----------------------------------------------------

        remove_old_events(event_time)

        # ----------------------------------------------------
        # Display periodically
        # ----------------------------------------------------

        if (
            time.time() - last_display_time
            >= DISPLAY_INTERVAL
        ):

            top20 = calculate_top20()

            save_result(
                event_time,
                top20
            )

            print("\n" + "=" * 60)

            print(
                f"Events received: {event_count}"
            )

            print(
                f"Window: "
                f"{event_time - timedelta(minutes=60)}"
                f" → "
                f"{event_time}"
            )

            print(
                f"Events in window: "
                f"{len(events)}"
            )

            print("\nTOP 20 PRODUCTS")

            print(
                "-" * 60
            )

            for index, product in enumerate(
                top20,
                start=1
            ):

                print(
                    f"{index:2}. "
                    f"{product['product_name'][:35]:35} "
                    f"{product['units_sold']:4}"
                )

            print(
                f"\nSaved to: {OUTPUT_FILE}"
            )

            last_display_time = time.time()


except KeyboardInterrupt:

    print(
        "\n\nConsumer stopped by user."
    )


finally:

    consumer.close()

    print(
        "\nReal-time consumer closed."
    )