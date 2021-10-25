from flask import Blueprint
from flask import current_app, url_for, render_template, request, redirect
from flask.json import jsonify


import stripe
import logging

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask_saas import Flask_SaaS
    from flask_saas.flask_saas import StripeBusinessProfile

log = logging.getLogger(__name__)

stripe_connect = Blueprint(
    "stripe_connect", __name__, template_folder="templates"
)  # noqa: E501


def modify_stripe_account_capability(account_id):
    """Request (again) card_payments capability after kyc onboarding
    is complete"""
    log.debug("Called modify_stripe_account_capability")
    stripe.Account.modify_capability(account_id, "card_payments", requested=True)


def _generate_account_link(account_id):
    """
    From the Stripe Docs:
    A user that is redirected to your return_url might not have completed the
    onboarding process. Use the /v1/accounts endpoint to retrieve the user’s
    account and check for charges_enabled. If the account is not fully onboarded,
    provide UI prompts to allow the user to continue onboarding later. The user
    can complete their account activation through a new account link (generated
    by your integration). You can check the state of the details_submitted
    parameter on their account to see if they’ve completed the onboarding process.
    """
    log.debug("Called _generate_account_link")
    account_link = stripe.AccountLink.create(
        type="account_onboarding",
        account=account_id,
        refresh_url=url_for("stripe_connect.index", refresh="refresh", _external=True),
        return_url=url_for("stripe_connect.index", success="success", _external=True),
    )
    return account_link.url


@stripe_connect.route("/stripe-set-livemode", methods=["POST"])
def set_stripe_livemode():
    log.debug("Called set_stripe_livemode")
    breakpoint()
    flask_saas: Flask_SaaS = current_app.config["flask_saas"]
    livemode = request.data.decode("utf-8")
    if livemode == "0" or livemode == "1":
        flask_saas.set_stripe_livemode(int(livemode))

        return redirect(url_for("stripe_connect.index"))

    return jsonify("Invalid request, valid values: 'live' or 'test'"), 500


@stripe_connect.route("/stripe-connect", methods=["GET"])
def index() -> str:
    log.debug("Called stripe_connect index route")

    flask_saas: Flask_SaaS = current_app.config["flask_saas"]

    account = None
    stripe_express_dashboard_url = None
    stripe.api_key = flask_saas.get_stripe_secret_key()

    try:
        account = flask_saas.get_stripe_connect_account()
        if account is not None and account.charges_enabled and account.payouts_enabled:
            flask_saas.set_stripe_connect_completed_status(status=True)
        else:
            flask_saas.set_stripe_connect_completed_status(status=False)
    except (
        stripe.error.PermissionError,
        stripe.error.InvalidRequestError,
        AttributeError,
    ) as e:
        log.error(e)
        account = None

    # Setup Stripe webhook endpoint if it dosent already exist
    if account:
        # Attempt to Updates an existing Account Capability to accept card payments
        try:
            account = flask_saas.get_stripe_connect_account()
            modify_stripe_account_capability(account.id)
        except Exception as e:
            log.error(f"Could not update card_payments capability for account. {e}")

        try:
            stripe_express_dashboard_url = stripe.Account.create_login_link(
                account.id
            ).url
        except stripe.error.InvalidRequestError:
            stripe_express_dashboard_url = None

    return render_template(
        "stripe/stripe_connect.html",
        stripe_onboard_path=url_for("stripe_connect.stripe_onboarding"),
        account=account,
        stripe_livemode=flask_saas.get_stripe_livemode(),
        stripe_express_dashboard_url=stripe_express_dashboard_url,
    )


@stripe_connect.route("/stripe-onboard", methods=["POST"])
def stripe_onboarding() -> jsonify:
    log.debug("called stripe_onboarding")

    flask_saas: Flask_SaaS = current_app.config["flask_saas"]
    stripe.api_key = flask_saas.get_stripe_secret_key()

    # Use existing stripe_connect_account_id, otherwise create stripe connect account
    try:
        log.info("Trying if there's an existing stripe account")
        account = flask_saas.get_stripe_connect_account()
        log.info(f"Stripe account found, account id: {account.id}")
    except (
        stripe.error.PermissionError,
        stripe.error.InvalidRequestError,
        AttributeError,
    ):
        log.info("Could not find a stripe account, Creating stripe account")
        account = flask_saas.create_stripe_connect_account()
        flask_saas.set_stripe_connect_account_id(account.id)

    account_link_url = _generate_account_link(account.id)
    try:
        return jsonify({"url": account_link_url})
    except Exception as e:
        return jsonify(error=str(e)), 403
