from config import settings
import requests


class WalletService:
    def __init__(self):
        self.base_url = settings.WALLET_API_URL
        self.headers = {"Content-Type": "application/json"}

    def generate_wallet(self):
        """
        Generate a new wallet in Solana
        """
        response = requests.post(
            f"{self.base_url}/api/wallet/generate", headers=self.headers
        )
        return response.json()
