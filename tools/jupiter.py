import requests
from config import settings
from pool import pool
from log import logger
import time
import json


def swap_token(
    input_amount: float, input_mint: str, output_mint: str, user_id: str
) -> str:
    """
    Use this tool to swap tokens.
    Args:
        input_amount (float): Amount of input token to swap. > 0
        input_mint (str): Mint address of input token.
        output_mint (str): Mint address of output token.
        user_id (str): User ID to identify the user.'
    Returns:
        str: Transaction hash or error message.
    """
    logger.info(
        f"[TOOLS] Swapping {input_amount} {input_mint} to {output_mint} for user: {user_id}"
    )
    decimal_input_amount = input_amount * 10**6
    ### CALL JUPITER API
    with pool.connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM wallets WHERE user_id = %s",
            (user_id,),
        )
        wallet = cursor.fetchone()  # tuple
        private_key = wallet[4]
        retry = 0
        max_retry = 3
        while retry < max_retry:
            logger.info(
                f"[{retry+1}/{max_retry}]: Swapping {input_amount} {input_mint} to {output_mint} for user: {user_id}"
            )
            response = requests.post(
                f"{settings.SERVICE_JUPITER_BASE_URL}/jupiterSwap",
                json={
                    "inputAmount": decimal_input_amount,
                    "inputMint": input_mint,
                    "outputMint": output_mint,
                    "privateKey": private_key,
                },
            )
            logger.info(f"Response: {response}")
            try:
                res = response.json()
            except requests.exceptions.JSONDecodeError:
                # Handle empty or invalid JSON response
                logger.error(
                    f"Error: Invalid response received. Status code: {response.status_code}"
                )
                logger.error(f"Response text: {response.text}")
                return response.text
            if res["status"] is True:
                logger.info(
                    f"[TOOLS] Swapped {input_amount} {input_mint} to {output_mint} for user: {user_id}"
                )
                return res["data"]
            else:
                retry += 1
                logger.error(f"[FAILED] {response.text}")
                time.sleep(5)

        ## RETURN ERROR
        logger.error(
            f"[TOOLS] Failed to swap {input_amount} {input_mint} to {output_mint} for user: {user_id}"
        )
        return res["data"]


def limit_order(
    maker_amount: float,
    taker_amount: float,
    maker_mint: str,
    taker_mint: str,
    user_id: str,
) -> str:
    """
    Use this tool to create a limit order.
    Args:
        maker_amount (float): Amount of maker token to swap. > 0
        taker_amount (float): Amount of taker token to swap. > 0
        maker_mint (str): Mint address of maker token.
        taker_mint (str): Mint address of taker token.
        user_id (str): User ID to identify the user.
    Returns:
        str: status of the request
    """
    logger.info(f"[TOOLS] Creating limit order for user: {user_id}")
    decimal_maker_amount = maker_amount * 10**6
    decimal_taker_amount = taker_amount * 10**9
    with pool.connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM wallets WHERE user_id = %s",
            (user_id,),
        )
        wallet = cursor.fetchone()  # tuple
        private_key = wallet[4]
        retry = 0
        max_retry = 3
        while retry < max_retry:
            logger.info(
                f"[{retry+1}/{max_retry}]: Creating limit order for user: {user_id}"
            )
            response = requests.post(
                f"{settings.SERVICE_JUPITER_BASE_URL}/jupiterLimitOrder",
                json={
                    "makingAmount": decimal_maker_amount,
                    "takingAmount": decimal_taker_amount,
                    "inputMint": maker_mint,
                    "outputMint": taker_mint,
                    "privateKey": private_key,
                },
            )
            logger.info(f"Response: {response}")
            try:
                res = response.json()
            except requests.exceptions.JSONDecodeError:
                # Handle empty or invalid JSON response
                logger.error(
                    f"Error: Invalid response received. Status code: {response.status_code}"
                )
                logger.error(f"Response text: {response.text}")
                return response.text
            if res["status"] is True:
                logger.info(f"[TOOLS] Created limit order for user: {user_id}")
                return res["data"]
            else:
                retry += 1
                logger.error(f"[FAILED] {response.text}")
                time.sleep(5)
        ## RETURN ERROR
        logger.error(f"[TOOLS] Failed to create limit order for user: {user_id}")
        return res["data"]


def cancel_all_orders(user_id: str) -> str:
    """
    Use this tool to cancel all orders for a user.
    Args:
        user_id (str): User ID to identify the user.
    Returns:
        str: status of the request
    """
    logger.info(f"[TOOLS] Cancelling all orders for user: {user_id}")
    with pool.connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM wallets WHERE user_id = %s",
            (user_id,),
        )
        wallet = cursor.fetchone()  # tuple
        private_key = wallet[4]
        retry = 0
        max_retry = 3
        while retry < max_retry:
            logger.info(
                f"[{retry+1}/{max_retry}]: Creating limit order for user: {user_id}"
            )
            response = requests.post(
                f"{settings.SERVICE_JUPITER_BASE_URL}/cancelOrders",
                json={
                    "privateKey": private_key,
                },
            )
            logger.info(f"Response: {response}")
            try:
                res = response.json()
            except requests.exceptions.JSONDecodeError:
                # Handle empty or invalid JSON response
                logger.error(
                    f"Error: Invalid response received. Status code: {response.status_code}"
                )
                logger.error(f"Response text: {response.text}")
                return response.text
            if res["status"] is True:
                logger.info(f"[TOOLS] Cancelled all orders for user: {user_id}")
                return res["data"]
            else:
                retry += 1
                logger.error(f"[FAILED] {response.text}")
                time.sleep(5)
        ## RETURN ERROR
        logger.error(f"[TOOLS] Failed to cancel all orders for user: {user_id}")
        return res["data"]
