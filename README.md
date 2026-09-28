# 🛒 Retail & E-Commerce Analytics – Real-Time Purchase Trend Dashboard

A big-data pipeline that streams retail purchase events through **Apache Kafka**, archives transactions in **Hadoop HDFS**, runs batch aggregation with **Hadoop MapReduce**, and shows the **Top 20 products in a 60-minute sliding window** on a live web dashboard served by a **Flask** API.

---

## 📌 Overview

Retail teams need to know what is selling *right now*, not just what sold last month. This project simulates that scenario end to end:

1. Historical order data (Instacart-style) is cleaned and turned into a transaction file.
2. A **producer** replays those transactions into Kafka as a live purchase stream.
3. A **real-time consumer** keeps a 60-minute sliding window and continuously computes the Top 20 products.
4. A **Flask API** exposes the latest result, and a **dashboard** polls it and renders it.
5. In parallel, transaction batches are stored in **HDFS** and processed with **MapReduce** for batch (offline) analytics.

---

## 🏗️ Architecture

```
 dataset/*.csv
      │
      ▼
 preprocessing/  ──►  data/prepared_transactions.csv
                              │
                              ▼
                    kafka/producer.py
                              │  purchase_events (3 partitions)
                              ▼
                        Apache Kafka
                        │           │
                        ▼           ▼
        kafka/realtime_consumer.py   kafka/consumer.py
        (60-min sliding window)      (batches → HDFS)
                │                            │
                ▼                            ▼
     data/top20_realtime.json        data/hdfs_batches/ ──► HDFS
                │                            │
                ▼                            ▼
       backend/app.py (Flask)          mapreduce/ jobs
                │                            │
                ▼                            ▼
     dashboard/ (HTML/CSS/JS)        data/top20_products.csv
```

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|-----------|
| Streaming | Apache Kafka (Docker) |
| Batch storage | Hadoop HDFS (Docker – NameNode + DataNode) |
| Batch processing | Hadoop MapReduce |
| Language | Python |
| API | Flask |
| Frontend | HTML, CSS, JavaScript |
| Containerisation | Docker, Docker Compose |

---

## 📁 Project Structure

```
retail-ecommerce-analytics/
├── backend/
│   └── app.py                    # Flask API – serves top-products data
├── dashboard/
│   ├── index.html                # Dashboard page
│   ├── script.js                 # Fetches the API and renders the chart/table
│   └── style.css                 # Styling
├── data/
│   ├── hdfs_batches/             # Transaction batches staged for HDFS
│   ├── prepared_transactions.csv # Cleaned transactions used by the producer
│   ├── top20_products.csv        # Batch (MapReduce) Top 20 result
│   └── top20_realtime.json       # Live Top 20 result written by the consumer
├── dataset/                      # Raw dataset (NOT included in the repo)
│   ├── aisles.csv
│   ├── departments.csv
│   ├── order_products__prior.csv
│   ├── order_products__train.csv
│   ├── orders.csv
│   └── products.csv
├── kafka/
│   ├── docker-compose.yml        # Kafka container setup
│   ├── producer.py               # Streams purchase events to Kafka
│   ├── consumer.py               # Basic consumer
│   └── realtime_consumer.py      # Sliding-window Top 20 consumer
├── mapreduce/                    # Hadoop MapReduce mapper/reducer jobs
├── preprocessing/                # Scripts that build prepared_transactions.csv
├── .gitignore
└── README.md
```

---

## 📦 Dataset

This project uses the **Instacart Market Basket Analysis** dataset. The raw CSVs are large, so they are **not committed** to this repo (see `.gitignore`).

Download the dataset from [Kaggle – Instacart Market Basket Analysis](https://www.kaggle.com/c/instacart-market-basket-analysis/data) and place these files in a `dataset/` folder at the project root:

| File | Description |
|------|-------------|
| `orders.csv` | One row per order (user, order number, day/hour of order) |
| `products.csv` | Product ID, name, aisle ID, department ID |
| `aisles.csv` | Aisle ID → aisle name |
| `departments.csv` | Department ID → department name |
| `order_products__prior.csv` | Products in each prior order |
| `order_products__train.csv` | Products in each training-set order |

---

## ✅ Prerequisites

- Python 3.9+
- Docker Desktop
- Running containers for **HDFS** (`bda-lab2-namenode-1`, `bda-lab2-datanode-1`) and **Kafka** (`retail-kafka`)
- Python packages (install what your scripts import, typically):

```bash
pip install kafka-python flask flask-cors pandas
```

---

## 🚀 How to Run

Open **5 terminals** from the project root.

### 0. Start the infrastructure

```bash
docker start bda-lab2-namenode-1
docker start bda-lab2-datanode-1
docker start retail-kafka

docker ps        # confirm all three are running
```

### 1. Prepare the Kafka topic

Delete the old topic (if any):

```bash
docker exec retail-kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --delete --topic purchase_events
```

Recreate it:

```bash
docker exec retail-kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --topic purchase_events --partitions 3 --replication-factor 1
```

Verify (you should see `purchase_events`):

```bash
docker exec retail-kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list
```

*(Optional)* Clear stale real-time output (PowerShell):

```powershell
Remove-Item .\data\top20_realtime.json -ErrorAction SilentlyContinue
```

### 2. Terminal 1 – Real-time consumer

```bash
cd kafka
python realtime_consumer.py
```

### 3. Terminal 2 – Producer

```bash
cd kafka
python producer.py
```

### 4. Terminal 3 – Flask API

```bash
cd backend
python app.py
```

Check the API: <http://localhost:5000/api/top-products>

### 5. Terminal 4 – Dashboard

```bash
cd dashboard
python -m http.server 8000
```

Open the dashboard: <http://localhost:8000>

---

## 🔄 How the Real-Time Flow Works

```
   CONSUMER  ◄──────── event received ◄──────── event sent ────────  PRODUCER
                                │
                                ▼
                              Kafka
                                │
                                ▼
                      60-minute sliding window
                                │
                                ▼
                        Top 20 products
                                │
                                ▼
                            Flask API
                                │
                                ▼
                            Dashboard
```

- Each purchase event sent by the producer is received by the consumer almost instantly.
- The consumer keeps only events from the **last 60 minutes**; older events expire from the window.
- After every update, the Top 20 products by purchase count are written to `data/top20_realtime.json`.
- The Flask API reads that file, and the dashboard refreshes from the API to stay live.

---

## 📊 Batch Analytics (HDFS + MapReduce)

- Transaction batches (`data/hdfs_batches/`) are uploaded to HDFS.
- MapReduce jobs in `mapreduce/` count product purchases across the full dataset.
- The batch Top 20 result is saved to `data/top20_products.csv`, which you can compare against the live results.

---

## 🌐 API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/top-products` | GET | Returns the current Top 20 products as JSON |

---

## 🔮 Future Improvements

- Add Docker Compose services for the full stack (HDFS + Flask + dashboard) in one command
- Replace polling with WebSockets / Server-Sent Events for push updates
- Add category-level (aisle/department) trend views
- Add tests and CI (GitHub Actions)

---

## 👤 Author

**Harshavardhana** – Computer Science Engineering, Dayananda Sagar College of Engineering, Bengaluru
GitHub: [@Harshavardhana-v](https://github.com/Harshavardhana-v)