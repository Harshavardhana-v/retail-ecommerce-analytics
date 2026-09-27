# 🛒 Retail & E-Commerce Analytics – Real-Time Purchase Trend Dashboard

A real-time retail analytics system that streams purchase events using
Apache Kafka, stores transaction data in Hadoop HDFS, processes sales
using Hadoop MapReduce, and visualizes the top 20 products in a
60-minute sliding window through a live dashboard.

docker start bda-lab2-namenode-1
docker start bda-lab2-datanode-1
docker start retail-kafka

docker ps

delete old topic:
docker exec retail-kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --delete --topic purchase_events

recreate topic:
docker exec retail-kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --topic purchase_events --partitions 3 --replication-factor 1

verify topic:
docker exec retail-kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list
  should see purchase_events

optional
Remove-Item .\data\top20_realtime.json -ErrorAction SilentlyContinue

in termial 2
python realtime_consumer.py

in terminal 3
python producer.py

in terminal 4
python app.py
 check http://localhost:5000/api/top-products

in terminal 5
python -m http.server 8000

http://localhost:8000


TERMINAL 1                    TERMINAL 2
CONSUMER                      PRODUCER

Event #1 RECEIVED  ←────────  Event #1 SENT
Event #2 RECEIVED  ←────────  Event #2 SENT
Event #3 RECEIVED  ←────────  Event #3 SENT
Event #4 RECEIVED  ←────────  Event #4 SENT
       ↓                              ↓
       └────────── Kafka ─────────────┘
                       ↓
                 60-min Window
                       ↓
                  Top 20 Products
                       ↓
                  Flask API
                       ↓
                  DASHBOARD