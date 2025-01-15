from database import PostgresDAO
import requests
import json
from rich.console import Console
from config import settings

console = Console()


def get_wallet_secret(chat_id: int):
    """
    Use this function to get information about a wallet. Such as:
    - Private key
    - Address (public key)
    - Seed phrase (mnemonic)

    Args:
        chat_id: The chat ID of the user

    Returns:
        str: JSON string with the wallet information
    """
    try:
        dao = PostgresDAO()
        user = dao.get_wallet_secret(chat_id)
        console.print("GET WALLET SECRET")
        console.print(user)
        if user is None:
            return json.dumps({"status": "error", "message": "No wallet found"})
        else:
            return json.dumps({"status": "success", "data": user.to_dict()})
    except Exception as e:
        console.print(e)
        return json.dumps({"status": "error", "message": str(e)})


def generate_wallet(chat_id: int):
    """
    Use this function to generate or create a new wallet

    Args:
        chat_id: The chat ID of the user
    Returns:
        str: JSON represent statement that the wallet has been generated or an error message
    """
    try:
        dao = PostgresDAO()
        console.print("GENERATE WALLET")
        # Check if the wallet has been generated
        user = dao.get_user_by_chat_id(chat_id)
        if user.seed_phrase is not None:
            return json.dumps(
                {"status": "error", "message": "Wallet already generated"}
            )

        url = f"{settings.BASE_URL}/api/wallet/generate"
        response = requests.post(url)
        if response.status_code == 200:
            response_data = response.json()
            data = response_data["data"]
            wallet_secret = {
                "private_key": data["privateKeyBase58"],
                "public_key": data["publicKey"],
                "seed_phrase": data["seedPhrase"],
            }

            dao.update_user(chat_id, **wallet_secret)
            return json.dumps({"status": "success", "message": "Wallet generated"})

        else:
            console.print(response.text)
            return json.dumps(
                {"status": "error", "message": "Failed to generate wallet"}
            )
    except Exception as e:
        console.print(e)
        return json.dumps({"status": "error", "message": str(e)})
