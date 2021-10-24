# install the packages to run the python scripts

cd /streaming_app/twitter_api_app 
virtualenv env_twitter_api_app
. env_twitter_api_app/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

# keep container running
tail -f /dev/null