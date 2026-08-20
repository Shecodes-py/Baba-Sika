"""'Show my dashboard' - mints a fresh magic link on demand."""

from conversations.services import send_message
from dashboard_bridge.models import MagicLinkRequestSource
from dashboard_bridge.services import issue_magic_link


def handle_show_dashboard(user, session):
    dashboard_url, _ = issue_magic_link(user, requested_via=MagicLinkRequestSource.ON_DEMAND)
    send_message(
        user=user,
        session=session,
        body=f"Here's your dashboard link (expires in 15 min): {dashboard_url}",
    )
