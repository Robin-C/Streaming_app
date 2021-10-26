from time import time
import tweepy
import os
import json
import csv
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

# csv
field_names = ['created_at','tweet']
tweet = []

# timezone converter
paris_tz = timezone('Europe/Paris')
utc = timezone('UTC')
 
# kafka producer
producer = KafkaProducer(bootstrap_servers='kafka:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))
  
# helpers
 
def created_at(string_datetime):
  dt_object = datetime.strptime(string_datetime, '%a %b %d %H:%M:%S +0000 %Y')
  utc_created_at = utc.localize(dt_object)
  return str(utc_created_at.astimezone(paris_tz))

def isWestern(tweet):
    try:
        tweet.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

# parse and save to csv
def parse_json(json_object):
    parsed_object = {
      'created_at': created_at(json_object['created_at']),
      'tweet': re.findall(r"#(\w+)", json_object['text'].rstrip())
    }
    if len(parsed_object['tweet']) > 0 and isWestern(json_object['text'].rstrip()):
      tweet.append(parsed_object)
      producer.send('hashtags', parsed_object)
      a_file = open("tweets.csv", "w")
      dict_writer = csv.DictWriter(a_file, field_names)
      dict_writer.writeheader()
      dict_writer.writerows(tweet)
      a_file.close()


class IDPrinter(tweepy.Stream):

    def on_status(self, status):
        print(status.id)
    def on_data(self, data):
         json_obj = json.loads(data.decode('utf-8'))
         if 'text' in json_obj:
           parse_json(json_obj)
      


printer = IDPrinter(
  api_key, api_key_secret,
  access_token, access_token_secret
)
#printer.filter(locations=[-52,2,9,51]) # France

printer.sample()
