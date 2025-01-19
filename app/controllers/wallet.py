from app.services.wallet import WalletService


class WalletController:
    @staticmethod
    def generate_wallet():
        return WalletService().generate_wallet()
