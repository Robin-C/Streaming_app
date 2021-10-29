# install the packages to run the python scripts
cd /streaming_app/dash_app
virtualenv env
. env/bin/activate
pip install --upgrade pip
pip install dash pandas

python app.py