import requests
from rich import print
from database import PostgresDAO


def faucet(chat_id: int, amount: int = 5):
    """
    Use this function to get tokens from a faucet.
    Args:
        chat_id: The chat ID of the user
        amount: The amount of tokens to get
    Returns:
        str: The transaction hash of the faucet or the error message
    """
    try:
        print(f"Requesting tokens for chat_id: {chat_id} with amount: {amount}")
        # Check if the user has a wallet
        dao = PostgresDAO()
        user = dao.get_user_by_chat_id(chat_id)
        if not user.seed_phrase:
            return "You need to create a wallet first"

        url = "http://localhost:3000/solana/faucet"
        body = {
            "chat_id": str(chat_id),
            "amount": amount,
        }
        response = requests.post(url, json=body)
        print(response.json())
        if response.ok:
            response_json = response.json()
            signature = response_json.get("signature", "Unknown signature")
            success = response_json.get("success", False)
            if success:
                return "Tokens received successfully with transaction hash: {}".format(
                    signature
                )
            else:
                return "Failed to receive tokens with error: {} {}".format(
                    response_json.get("error", "Unknown error"),
                    response_json.get("details", "Unknown message"),
                )
        else:
            return "Failed to receive tokens with error: {} {}".format(
                response.json().get("error", "Unknown error"),
                response.json().get("details", "Unknown message"),
            )
    except Exception as e:
        return f"Failed to receive tokens: {e}"


def swap(chat_id: int):
    """
    Use this function to swap tokens.
    """
    pass
