"""
One-time OAuth2 authorization for sending application emails from
Sahawat.nil@outlook.com (auth-code flow, no Azure account needed).

Microsoft has permanently disabled Basic Authentication for SMTP AUTH on
Outlook.com — the old OUTLOOK_APP_PASSWORD login in email_sender.py has been
failing on every application email (535, 5.7.139). This grants SMTP.Send via
Modern Auth instead. One-time action; the token silently refreshes after.

Step 1: python3 authorize_outlook_smtp.py
        → prints a sign-in URL. Open it, sign in with Sahawat.nil@outlook.com.
        The browser will land on https://localhost/?code=... and show a
        "can't connect" error — that's expected. Copy the FULL URL from
        the address bar.

Step 2: python3 authorize_outlook_smtp.py "<pasted-url>"
        → exchanges the code for tokens and saves outlook_token_send.json
        (gitignored, matches the outlook_token*.json pattern).
"""
import argparse
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def main() -> int:
    from outlook_oauth import OutlookOAuthSender

    parser = argparse.ArgumentParser(description="Authorize Outlook SMTP sending for the job agent")
    parser.add_argument(
        "redirect_url",
        nargs="?",
        help="The https://localhost/?code=... URL copied from the browser",
    )
    args = parser.parse_args()

    client = OutlookOAuthSender()

    if not args.redirect_url:
        logger.info("Open this URL and sign in with Sahawat.nil@outlook.com:")
        logger.info("")
        logger.info(client.get_authorization_url())
        logger.info("")
        logger.info(
            "After sign-in the browser shows a 'can't connect to localhost' "
            "error — that's expected."
        )
        logger.info(
            'Copy the full URL from the address bar, then run:\n'
            '  python3 authorize_outlook_smtp.py "<pasted-url>"'
        )
        return 0

    result = client.redeem_authorization_code(args.redirect_url)
    username = (result.get("id_token_claims") or {}).get("preferred_username")
    logger.info(f"SUCCESS! Token saved to: {client.token_file}")
    logger.info(f"Authorized account: {username}")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
