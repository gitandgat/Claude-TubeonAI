"""
One-time Outlook/Hotmail authorization (auth-code flow, no Azure account needed).

Step 1: python3 authorize_outlook.py [--token-file outlook_token_NAME.json]
        → prints a sign-in URL. Open it, sign in with your Hotmail account.
        The browser will land on https://localhost/?code=... and show a
        "can't connect" error — that's expected. Copy the FULL URL from
        the address bar.

Step 2: python3 authorize_outlook.py [--token-file ...] "<pasted-url>"
        → exchanges the code for tokens, saves the token file,
        and runs a quick unread-mail smoke test.

For a second account, use a distinct token file, e.g.:
  python3 authorize_outlook.py --token-file outlook_token_work.json
"""
import argparse
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def main() -> int:
    from outlook_client import OutlookClient, TOKEN_FILE

    parser = argparse.ArgumentParser(description="Authorize an Outlook/Hotmail account")
    parser.add_argument(
        "redirect_url",
        nargs="?",
        help="The https://localhost/?code=... URL copied from the browser",
    )
    parser.add_argument(
        "--token-file",
        default=str(TOKEN_FILE),
        help="Token cache path (use a distinct file per account)",
    )
    args = parser.parse_args()

    client = OutlookClient(token_file=args.token_file)

    if not args.redirect_url:
        logger.info("Open this URL and sign in with your Hotmail/Outlook account:")
        logger.info("")
        logger.info(client.get_authorization_url())
        logger.info("")
        logger.info(
            "After sign-in the browser shows a 'can't connect to localhost' "
            "error — that's expected."
        )
        logger.info(
            'Copy the full URL from the address bar, then run:\n'
            f'  python3 authorize_outlook.py --token-file {args.token_file} "<pasted-url>"'
        )
        return 0

    result = client.redeem_authorization_code(args.redirect_url)
    username = (result.get("id_token_claims") or {}).get("preferred_username")
    client.email = username or client.email
    logger.info(f"Token saved to: {args.token_file}")

    logger.info("Running smoke test (list unread)...")
    unread = client.list_unread(max_results=5)
    logger.info(f"SUCCESS! Found {len(unread)} unread messages:")
    for m in unread:
        logger.info(f"  - {m['subject'][:60]}  (from {m['sender_email']})")
    client.close()
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
