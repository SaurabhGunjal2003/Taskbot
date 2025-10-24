import os
import re
from decimal import Decimal, InvalidOperation
from binance.client import Client
from logger import get_logger

logger = get_logger("utils")

def load_client():
    """
    Loads Binance Client for USDT-M Futures.
    Requires environment variables: BINANCE_API_KEY, BINANCE_API_SECRET
    Optional: USE_TESTNET=1 to use testnet endpoints (futures testnet).
    """
    api_key = os.getenv("BINANCE_API_KEY", "")
    api_secret = os.getenv("BINANCE_API_SECRET", "")
    use_testnet = os.getenv("USE_TESTNET", "0") == "1"

    if not api_key or not api_secret:
        logger.warning("API key/secret not found in environment - running in dry-run mode.")

    client = Client(api_key, api_secret)

    if use_testnet:
        
        client.FUTURES_URL = "https://testnet.binancefuture.com"
        logger.info("Using FUTURES testnet endpoint")

    return client, use_testnet

def validate_symbol(symbol: str) -> bool:
    return bool(re.fullmatch(r'[A-Za-z0-9]{3,12}', symbol))

def validate_positive_decimal(value: str) -> Decimal:
    try:
        d = Decimal(value)
    except InvalidOperation:
        raise ValueError("Invalid decimal number")
    if d <= 0:
        raise ValueError("Value must be positive")
    return d
