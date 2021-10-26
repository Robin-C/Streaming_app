from kafka import KafkaConsumer


consumer = KafkaConsumer('hashtags', bootstrap_servers='kafka:9092')
for msg in consumer:
  print (msg)