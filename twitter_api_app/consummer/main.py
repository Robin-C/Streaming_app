from kafka import KafkaConsumer
from pymongo import MongoClient
import json

# set up mongo instance
client = MongoClient('mongo', 27017, username='root', password='pwd')
db = client.tweets
collection = db.tweet_list


consumer = KafkaConsumer('hashtags', bootstrap_servers='kafka:9092')
for tweet in consumer:
 
  deserialized = json.loads(tweet.value)

  collection.insert_one(deserialized)
  

