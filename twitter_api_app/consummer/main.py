from kafka import KafkaConsumer
import json
import psycopg2

# set up postgres connection
connection = psycopg2.connect(host='postgres', user='root', password='root', dbname='tweets')
cursor = connection.cursor()



consumer = KafkaConsumer('fact_tweets', bootstrap_servers='kafka:9092')
for tweet in consumer:
  deserialized = json.loads(tweet.value)
  print(deserialized['created_at'])
  # insert occurence into postgres
  cursor.execute("INSERT INTO fact_tweets (created_at, tweet) VALUES(%s, %s)", (deserialized['created_at'], deserialized['tweet']))
  # delete records older than 30 minutes
  cursor.execute("delete from fact_tweets where NOW() at time zone 'Europe/Paris' - interval '30 minutes' > created_at")
  connection.commit()



