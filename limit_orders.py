import argparse
from decimal import Decimal
from logger import get_logger
from utils import load_client, validate_symbol, validate_positive_decimal
from binance.exceptions import BinanceAPIException, BinanceRequestException

logger = get_logger("limit_orders")

def place_limit_order(client, symbol, side, quantity, price, time_in_force="GTC", test=False):
    order_params = {
        "symbol": symbol.upper(),
        "side": side.upper(),
        "type": "LIMIT",
        "quantity": float(quantity),
        "price": str(price),
        "timeInForce": time_in_force
    }
    try:
        if test:
            logger.info(f"Placing TEST limit order: {order_params}")
            client.futures_create_order(**order_params)
            return {"status": "test-success", "params": order_params}
        else:
            logger.info(f"Placing LIMIT order: {order_params}")
            resp = client.futures_create_order(**order_params)
            logger.debug(f"Order response: {resp}")
            return resp
    except (BinanceAPIException, BinanceRequestException) as e:
        logger.error(f"Binance API error placing limit order: {e}")
        raise
    except Exception:
        logger.exception("Unexpected error placing limit order")
        raise

def main():
    parser = argparse.ArgumentParser(description="Place a Binance USDT-M Futures LIMIT order")
    parser.add_argument("symbol", help="Trading pair (e.g., BTCUSDT)")
    parser.add_argument("side", choices=["BUY","SELL"], help="BUY or SELL")
    parser.add_argument("quantity", help="Quantity (in contract units)")
    parser.add_argument("price", help="Limit price")
    parser.add_argument("--time-in-force", default="GTC", choices=["GTC","IOC","FOK"], help="Time in force")
    parser.add_argument("--dry", action="store_true", help="Dry run / testnet")
    args = parser.parse_args()

    if not validate_symbol(args.symbol):
        logger.error("Invalid symbol format.")
        return

    try:
        q = validate_positive_decimal(args.quantity)
        p = validate_positive_decimal(args.price)
    except ValueError as e:
        logger.error(f"Invalid numeric input: {e}")
        return

    client, use_testnet = load_client()
    test_flag = args.dry or (use_testnet and True) or (not client.API_KEY)
    try:
        res = place_limit_order(client, args.symbol, args.side, q, p, time_in_force=args.time_in_force, test=test_flag)
        logger.info(f"Result: {res}")
    except Exception as e:
        logger.error(f"Failed to place limit order: {e}")

if __name__ == "__main__":
    main()
