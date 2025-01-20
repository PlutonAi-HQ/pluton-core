from config import settings
import requests
from app.dto import WalletRequestDTO, WalletResponseDTO
from app.models.wallet import Wallet
from sqlalchemy.orm import Session


class WalletService:
    def __init__(self, db: Session):
        self.db = db
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

    def create_wallet(self, wallet: WalletRequestDTO) -> Wallet:
        wallet_model = Wallet(**wallet.model_dump())
        self.db.add(wallet_model)
        self.db.commit()
        return wallet_model
