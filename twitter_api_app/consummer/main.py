from kafka import KafkaConsumer
import json
import psycopg2

# set up postgres connection
connection = psycopg2.connect(host='postgres', user='root', password='root', dbname='tweets')
cursor = connection.cursor()



consumer = KafkaConsumer('hashtags', bootstrap_servers='kafka:9092')
for tweet in consumer:
  deserialized = json.loads(tweet.value)
  # insert a new row for each occurence of a hashtag (delimited by a space)
  for i in deserialized['tweet']:
    cursor.execute("INSERT INTO fact_hashtags (created_at, hashtag) VALUES(%s, %s)", (deserialized['created_at'], i))
  # delete records older than 30 minutes
  cursor.execute("delete from fact_hashtags where NOW() at time zone 'Europe/Paris' - interval '30 minutes' > created_at")
  connection.commit()
  

