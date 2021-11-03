# Flask Stripe Connect Onboarding

This is a pip package which makes integrating Stripe connect easier between projects.

It will automatically register some routes, needed to complete [Stripe connect](https://stripe.com/en-gb/connect) onboarding.

## Example installation

To use `flask_saas` in your flask project, install this package within your existing flask project

Clone this repo to outside of your flask project directory.

Then install `flask_saas` to your existing flask project.

```
cd <path/to/your flask/project>
# Activate your venv
. venv/bin/activate

# Install `flask_saas`

pip install -e /path/to/where/you/cloned/this/repo
```

## Assumptions

- You have a [Stripe account](https://dashboard.stripe.com/register)
- In your existing flask appliction, you can/are storiing the following information somwhere/somehow in your app (e.g. in your config, database, 
environment settings, a mix of either)
    - stripe_secret_key
    - stripe_business_profile
    - stripe connect account id
    - stripe_livemode (true/false, 1/0)
    - stripe_connect_completed_status (true/false, 1/0) - a boolean to track if stripe connect onboarding has completed or not

## Example usage


### 1. 
In your main flask app, inside create_app

```
from flask import Flask
import os 

from flask_saas import Flask_SaaS

def create_app(test_config=None):
    app = Flask(__name__)

    app.config.update(os.environ)


    # Initialize flask_saas
    Flask_SaaS(
        app,
        get_stripe_secret_key=get_stripe_secret_key,
        get_stripe_business_profile=get_stripe_business_profile,
        get_stripe_connect_account=get_stripe_connect_account,
        get_stripe_livemode=get_stripe_livemode,
        set_stripe_livemode=set_stripe_livemode,
        get_stripe_connect_account_id=get_stripe_connect_account_id,
        set_stripe_connect_account_id=set_stripe_connect_account_id,
        get_stripe_connect_completed_status=get_stripe_connect_completed_status,
        set_stripe_connect_completed_status=set_stripe_connect_completed_status,
    )

    @app.route("/")
    def hello_world():
        return "<p>Hello, World!</p>"

    return app
```

Start your app as normal `flask run`, then navigate to `/stripe-connect` and you will see the Stripe onboarding process.


> Note, you have to write the functions above to tell `flask_saas` *how* to connect to 
your existing flask application. This makes `flask_saas` flexibily and (hopefully) 
eaiser to integrate with your existing application/database or object store.

For example, to implement `get_stripe_secret_key`, if your flask application stores
your Stripe key as an environment variable called `STRIPE_SECRET_KEY`, then you might write (before `Flask_Saas` instantiation):

```
def get_stripe_secret_key():
    return os.getenv("STRIPE_SECRET_KEY")
```

### 2. Create link to Stripe connect onboarding


In your flask application, create a link to the route `stripe-connect.index` to start the Stripe onboarding process.

For example: create a template called `stripe-connect.html`, and write:
```
{% extends "layout.html" %}
{% block body %}
  <h2>Connect to Stripe</h2>
  <a href="{{ url_for('stripe_connect.index') }}">Connect to Stripe</a>
{% endblock %}

```
Reload your application, and you should see a link to stripe-connect.

## Building / Development

```
python3 -m pip install --upgrade build
python3 -m build
```
See https://packaging.python.org/tutorials/packaging-projects/
