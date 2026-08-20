from datetime import timedelta

from rest_framework_simplejwt.tokens import AccessToken

MAGIC_LINK_LIFETIME = timedelta(minutes=15)
MAGIC_LINK_PURPOSE_CLAIM = "purpose"
MAGIC_LINK_PURPOSE_VALUE = "dashboard_magic_link"


class MagicLinkToken(AccessToken):
    """
    A short-lived, single-use, purpose-tagged access token used only to hand
    off from WhatsApp to the dashboard. It is NOT used to authenticate
    regular API calls - dashboard_bridge.services.verify_and_exchange trades
    it for a normal session AccessToken (SIMPLE_JWT's default lifetime) the
    first time it's presented, then marks it used.
    """

    lifetime = MAGIC_LINK_LIFETIME

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not args:  # only stamp the claim when minting a new token
            self[MAGIC_LINK_PURPOSE_CLAIM] = MAGIC_LINK_PURPOSE_VALUE
