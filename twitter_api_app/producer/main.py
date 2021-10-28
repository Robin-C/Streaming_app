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
 
# kafka producer
producer = KafkaProducer(bootstrap_servers='kafka:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))
  
# helpers
def created_at(string_datetime):
  dt_object = datetime.strptime(string_datetime, '%a %b %d %H:%M:%S +0000 %Y')
  utc_created_at = utc.localize(dt_object)
 # print(str(utc_created_at.astimezone(paris_tz)))
  return str(utc_created_at.astimezone(paris_tz))

# parse and save to csv
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
         if 'text' in json_obj and json_obj['text'].find('macron') != -1:
           parse_json(json_obj['created_at'], 'macron')
         if 'text' in json_obj and json_obj['text'].find('zemmour') != -1:
           parse_json(json_obj['created_at'], 'zemmour')
         if 'text' in json_obj and json_obj['text'].find('le pen') != -1:
           parse_json(json_obj['created_at'], 'le pen')
         if 'text' in json_obj and json_obj['text'].find('melenchon') != -1:
           parse_json(json_obj['created_at'], 'melenchon')
         if 'text' in json_obj and json_obj['text'].find('asselineau') != -1:
           parse_json(json_obj['created_at'], 'asselineau')   

printer = IDPrinter(
  api_key, api_key_secret,
  access_token, access_token_secret
)
#printer.filter(locations=[-52,2,9,51]) # France

printer.filter(track=['macron', 'zemmour', 'le pen', 'melenchon', 'asselineau'])
