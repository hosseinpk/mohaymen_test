## for checking does kafka working correctly or not

```
docker exec -it city_kafka /opt/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server kafka:9092 \
  --topic app_logs \
  --from-beginning
```

## for show topic lists

```
docker compose exec kafka sh -lc   "cd /opt/kafka/bin && ./kafka-topics.sh --bootstrap-server kafka:9092 --list"
```
