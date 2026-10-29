"""Single source of truth for the Zernio API key.

Reads ZERNIO_API_KEY from .env so a rotated key only has to change in one place.
Import the key, never hardcode it:

    from zernio_key import ZERNIO_API_KEY as API_KEY
"""
import os
from dotenv import load_dotenv

load_dotenv()

ZERNIO_API_KEY = os.getenv("ZERNIO_API_KEY")
if not ZERNIO_API_KEY:
    raise RuntimeError(
        "ZERNIO_API_KEY not set in .env — add it from the Zernio dashboard "
        "(Settings -> API)."
    )
