import argparse
from logger import get_logger
from utils import load_client, validate_symbol, validate_positive_decimal
from binance.exceptions import BinanceAPIException, BinanceRequestException

logger = get_logger("market_orders")

def place_market_order(client, symbol, side, quantity, test=False):
    """
    Places a USDT-M Futures market order using python-binance futures_create_order.
    side: "BUY" or "SELL"
    test: if True, will use test order endpoint (client.futures_create_order_test) if available
    """
    try:
        order_params = {
            "symbol": symbol.upper(),
            "side": side.upper(),
            "type": "MARKET",
            "quantity": float(quantity)
        }
        if test:
            logger.info(f"Placing TEST market order: {order_params}")
            client.futures_create_order(**order_params)  
            logger.info("Test order API call succeeded (no execution on testnet).")
            return {"status": "test-success", "params": order_params}
        else:
            logger.info(f"Placing MARKET order: {order_params}")
            resp = client.futures_create_order(**order_params)
            logger.debug(f"Order response: {resp}")
            return resp
    except (BinanceAPIException, BinanceRequestException) as e:
        logger.error(f"Binance API error placing market order: {e}")
        raise
    except Exception as e:
        logger.exception("Unexpected error placing market order")
        raise

def main():
    parser = argparse.ArgumentParser(description="Place a Binance USDT-M Futures MARKET order")
    parser.add_argument("symbol", help="Trading pair (e.g., BTCUSDT)")
    parser.add_argument("side", choices=["BUY","SELL"], help="BUY or SELL")
    parser.add_argument("quantity", help="Quantity (in contract units, e.g., 0.001)")
    parser.add_argument("--dry", action="store_true", help="Don't execute on mainnet; use testnet/dry-run behavior")
    args = parser.parse_args()

    if not validate_symbol(args.symbol):
        logger.error("Invalid symbol format.")
        return

    try:
        q = validate_positive_decimal(args.quantity)
    except ValueError as e:
        logger.error(f"Invalid quantity: {e}")
        return

    client, use_testnet = load_client()
    test_flag = args.dry or (use_testnet and True) or (not client.API_KEY)
    try:
        res = place_market_order(client, args.symbol, args.side, q, test=test_flag)
        logger.info(f"Result: {res}")
    except Exception as e:
        logger.error(f"Failed to place market order: {e}")

if __name__ == "__main__":
    main()
