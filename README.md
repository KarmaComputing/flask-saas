# Flask Stripe Connect Onboarding

This is a pip package which makes integrating Stripe connect easier between projects.

It will automatically register some routes, needed to complete Stripe connect onboarding.

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

## Example usage

In your main flask app, inside create_app

```
from flask Flask

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
```

Start your app as normal `flask run`, then navigate to `/stripe-connect` and you will see the Stripe onboarding process.


> Note, you have to write the functions above to tell `flask_saas` *how* to connect to 
your existing flask application. This makes `flask_saas` flexibily and (hopefully) 
eaiser to integrate with your existing application/database or object store.

For example, to implement `get_stripe_secret_key`, if your flask application stores
your Stripe key as an envrionment variable called `STRIPE_SECRET_KEY`, then you might write:

```
def get_stripe_secret_key():
    return os.getenv("STRIPE_SECRET_KEY")
```