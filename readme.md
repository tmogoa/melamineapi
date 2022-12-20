# Activating the python virtual environment

    $ . venv/bin/activate

# Running the flask app

    $ cd api
    $ flask --app api.py --debug run --host=0.0.0.0

# Installing dependencies

    $ pip install -r requirements.txt

# Running in production

    waitress-serve --host 127.0.0.1 --call api:create_app
