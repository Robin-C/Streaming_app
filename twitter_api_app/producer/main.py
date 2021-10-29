from time import time
import tweepy
import os
import json
import re
from pytz import timezone
from datetime import datetime
from kafka import KafkaProducer

# tweeter API
api_key = os.getenv('CONSUMMER_TOKEN')
api_key_secret = os.getenv('CONSUMMER_TOKEN_SECRET')
access_token = os.getenv('ACCESS_TOKEN')
access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')
authenticator = tweepy.OAuthHandler(api_key, api_key_secret)
authenticator.set_access_token(access_token, access_token_secret)
api = tweepy.API(authenticator, wait_on_rate_limit=True)

# timezone converter
paris_tz = timezone('Europe/Paris')
utc = timezone('UTC')
 
# world leaders
macron = ['macron']
biden = ['biden', 'potus', 'Potus']
bolsonaro = ['bolsonaro']
merckel = ['merckel']
jinping = ['jinping', 'xi jinping', '习近平']
poutine = ['putin', 'poutine', 'Владимир Путин']
 
# tweeter topics
topics = ['macron', 'Macron', 'biden', 'Biden', 'bolsonaro', 'Bolsonaro', 'merkel', 'Merkel', 'jinping', 'Jinping', '习近平',
'poutine, Poutine', 'Putin', 'putin', 'Владимир Путин']

# kafka producer
producer = KafkaProducer(bootstrap_servers='kafka:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))
  
# helpers
def created_at(string_datetime):
  dt_object = datetime.strptime(string_datetime, '%a %b %d %H:%M:%S +0000 %Y')
  utc_created_at = utc.localize(dt_object)
  return str(utc_created_at.astimezone(paris_tz))

def find_leader(str_list, tweet):
    for string_to_test in str_list:
        if tweet.find(string_to_test) != -1:
            return True
    return False

# parse tweet and produce to kafka
def parse_json(timestamp, candidate):
    parsed_object = {
      'created_at': created_at(timestamp),
      'tweet': candidate
    }
    if len(parsed_object['tweet']) > 0:
      producer.send('fact_tweets', parsed_object)    

class IDPrinter(tweepy.Stream):
    def on_status(self, status):
        print(status.id)
    def on_data(self, data):
         json_obj = json.loads(data.decode('utf-8'))
         if 'text' in json_obj:
           if find_leader(macron, json_obj['text']):
              parse_json(json_obj['created_at'], 'Macron')
           if find_leader(biden, json_obj['text']):
              parse_json(json_obj['created_at'], 'Biden')
           if find_leader(bolsonaro, json_obj['text']):
              parse_json(json_obj['created_at'], 'Bolsonaro')                   
           if find_leader(merckel, json_obj['text']):
              parse_json(json_obj['created_at'], 'Merckel')
           if find_leader(jinping, json_obj['text']):
              parse_json(json_obj['created_at'], 'Jinping')
           if find_leader(poutine, json_obj['text']):
              parse_json(json_obj['created_at'], 'Putin')

printer = IDPrinter(
  api_key, api_key_secret,
  access_token, access_token_secret
)

printer.filter(track=topics)
