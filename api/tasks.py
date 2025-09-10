import logging

import httpx

from api.config import get_config

logger = logging.getLogger(__name__)

async def send_email(to: str, subject: str, body: str):
    logger.info(f"Sending email to {to[:4]}... with subject {subject[:20]}... and body {body[:20]}...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"https://api.mailgun.net/v3/{get_config().MAILGUN_DOMAIN}/messages",
                auth=("api", get_config().MAILGUN_API_KEY),
                data={"from": f"Max Petrov <mailgun@{get_config().MAILGUN_DOMAIN}>", "to": [to], "subject": subject, "text": body}
            )
            response.raise_for_status()
            logger.debug(response.content)
            return response
        except httpx.HTTPStatusError as e:
            raise Exception(f"Error sending email to {to}: {e}") from e
        
async def send_confirmation_email(to: str, confirmation_url: str):
    subject = "Confirm your email"
    body = f"Please click the link to confirm your email: {confirmation_url}"
    await send_email(to, subject, body)
        