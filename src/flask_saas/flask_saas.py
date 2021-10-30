from typing import Callable, TypedDict
import logging
from flask import Flask, request
from .blueprints import stripe_connect
import stripe

log = logging.getLogger(__name__)


class StripeBusinessProfile(TypedDict):
    name: str
    url: str
    email: str


class Flask_SaaS:
    """Flask SaaS routes for Stripe Connect

    :param app: The current flask app
    :param get_stripe_secret_key: A callable which returns the Stripe
        secret api key
    :param get_stripe_business_profile: A callable with returns a dict
        describing the business profile according to
        https://stripe.com/docs/api/accounts/object#account_object-business_profile
    :param  get_stripe_connect_account: A callable which returns a Stripe
        connect Account object. Note, upon creation Stripe Account objects
        do not have to be associated with an account/person.
    :param get_stripe_connect_completed: A callable with gets stripe connect
        completed status (true or false)
    :param set_stripe_connect_completed: A callable with sets stripe connect
        completed to true or false
    """

    def __init__(
        self,
        app: Flask,
        get_stripe_secret_key: Callable[..., str],
        get_stripe_business_profile: Callable[..., str],
        get_stripe_connect_account: Callable[..., stripe.Account],
        get_stripe_livemode: Callable[..., bool],
        set_stripe_livemode: Callable[..., bool],
        get_stripe_connect_account_id: Callable[..., bool],
        set_stripe_connect_account_id: Callable[..., bool],
        get_stripe_connect_completed_status: Callable[..., bool],
        set_stripe_connect_completed_status: Callable[..., bool],
    ) -> None:
        log.debug("Called Flask_SaaS")
        app.config["flask_saas"] = self
        self.app = app
        self.get_stripe_secret_key = get_stripe_secret_key
        self.get_stripe_business_profile: StripeBusinessProfile = (
            get_stripe_business_profile
        )
        self.get_stripe_connect_account = get_stripe_connect_account
        self.get_stripe_livemode = get_stripe_livemode
        self.set_stripe_livemode = set_stripe_livemode
        self.get_stripe_connect_account_id = get_stripe_connect_account_id
        self.set_stripe_connect_account_id = set_stripe_connect_account_id
        self.get_stripe_connect_completed_status = get_stripe_connect_completed_status
        self.set_stripe_connect_completed_status = set_stripe_connect_completed_status

        self.app.register_blueprint(stripe_connect)

    def create_stripe_connect_account(self) -> stripe.Account:
        log.debug("Called create_stripe_connect_account")

        stripe.api_key = self.get_stripe_secret_key()

        # Get business name from business profile, otherwise use request.host_url
        if "url" not in self.get_stripe_business_profile():
            if "127.0.0.1" in request.host_url:
                url = "blackhole-1.iana.org"
            else:
                url = request.host_url

        account = stripe.Account.create(
            type="express",
            email=self.get_stripe_business_profile()["email"],
            default_currency="gbp",
            business_profile={
                "url": url,
                "name": self.get_stripe_business_profile()["name"],
            },
            capabilities={
                "card_payments": {"requested": True},
                "transfers": {"requested": True},
            },
        )

        return account

    def create_stripe_account_link(
        self, account_id: stripe.Account, refresh_url: str, return_url: str
    ) -> str:
        """
        From the Stripe Docs: https://stripe.com/docs/api/account_links/create
        A user that is redirected to your return_url might not have completed the
        onboarding process. Use the /v1/accounts endpoint to retrieve the user’s
        account and check for charges_enabled. If the account is not fully onboarded,
        provide UI prompts to allow the user to continue onboarding later. The user
        can complete their account activation through a new account link (generated
        by your integration). You can check the state of the details_submitted
        parameter on their account to see if they’ve completed the onboarding process.
        """
        account_link = stripe.AccountLink.create(
            type="account_onboarding",
            account=account_id,
            refresh_url=refresh_url,
            return_url=return_url,
        )
        return account_link.url

    def modify_stripe_account_capability(self, account_id: str) -> None:
        """Request (again) card_payments capability after kyc onboarding
        is complete"""
        log.debug("Called modify_stripe_account_capability")
        stripe.Account.modify_capability(account_id, "card_payments", requested=True)
