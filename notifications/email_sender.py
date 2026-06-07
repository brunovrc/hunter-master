import logging

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from analysis.score_engine import ScoreReport
from config.settings import settings
from .formatter import format_opportunity_email_html

logger = logging.getLogger(__name__)


def send_opportunity_email(report: ScoreReport, listing_url: str):
    if not settings.sendgrid_api_key or not settings.sendgrid_from_email:
        return

    html = format_opportunity_email_html(report, listing_url)
    subject = f"[Hunter Master] {report.recommendation.value} — {report.title[:50]}"

    message = Mail(
        from_email=settings.sendgrid_from_email,
        to_emails=settings.sendgrid_to_email,
        subject=subject,
        html_content=html,
    )

    try:
        sg = SendGridAPIClient(settings.sendgrid_api_key)
        sg.send(message)
    except Exception as e:
        logger.error(f"SendGrid: {e}")
