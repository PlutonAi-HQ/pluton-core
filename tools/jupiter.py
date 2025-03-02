import requests
from config import settings
from pool import pool
import time
import json
from phi.agent import Agent
from phi.tools import Toolkit
from phi.utils.log import logger
from app.utils.requests import retry_request
from pydantic import BaseModel


class Wallet(BaseModel):
    public_key: str
    private_key: str


class JupiterTool(Toolkit):
    def __init__(self):
        super().__init__(name="jupiter_tools")
        self.register(self.check_balance)
        self.register(self.swap_token)
        self.register(self.limit_order)
        self.register(self.cancel_all_orders)
        self.register(self.check_all_tokens)
        self.register(self.get_token_address)
        self.register(self.get_pool_info)
        self.register(self.pre_swap_info)
        self.register(self.create_dca)

    def _get_wallet(self, agent: Agent) -> Wallet | None:
        user_id = agent.context["user_id"]
        with pool.connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM wallets WHERE user_id = %s", (user_id,))
            wallet = cursor.fetchone()  # tuple
            if wallet is None:
                logger.error(f"[TOOLS] User {user_id} does not have a wallet")
                return None

        return Wallet(
            public_key=wallet[3],
            private_key=wallet[4],
        )

    def check_balance(self, agent: Agent, token_address: str) -> str:
        """
        Use this tool to check the balance of a user in a token.
        Args:
            token_address (str): Mint address of the token. Default is SOL. with address "So11111111111111111111111111111111111111112"
        Returns:
            str: Balance of the user in the token.
        """
        wallet = self._get_wallet(agent)
        if wallet is None:
            logger.error(
                f"[TOOLS] User {agent.context['user_id']} does not have a wallet"
            )
            return "User does not have a wallet"
        public_key = wallet.public_key

        def get_balance(public_key: str, token_address: str) -> str:
            res = requests.get(
                f"{settings.SERVICE_JUPITER_BASE_URL}/balance",
                params={"address": public_key, "tokenAddress": token_address},
            )
            res.raise_for_status()
            return str(res.json().get("balance", None))  # Return balance as string

        balance = retry_request(get_balance, retries=3, delay=5)(
            public_key, token_address
        )
        return balance

    def check_all_tokens(self, agent: Agent) -> str:
        """
        Use this tool to check the balance of all tokens for a user.
        Returns:
            str: Balance of all tokens for a user.
        """
        user_id = agent.context["user_id"]
        wallet = self._get_wallet(agent)
        if wallet is None:
            logger.error(f"[TOOLS] User {user_id} does not have a wallet")
            return "User does not have a wallet"
        public_key = wallet.public_key

        def _check_all_tokens(public_key: str) -> str:
            res = requests.get(
                f"{settings.SERVICE_JUPITER_BASE_URL}/allTokens",
                params={"address": public_key},
            )
            res.raise_for_status()
            return str(res.json().get("data", None))

        return retry_request(_check_all_tokens, retries=3, delay=5)(public_key)

    def get_token_address(self, token_name: str) -> str:
        """
        Use this tool to get the address of a token.
        Args:
            token_name (str): Name of the token.
        Returns:
            str: Address of the token.
        """

        def _get_token_address(token_name: str) -> str:
            res = requests.get(
                f"{settings.SERVICE_JUPITER_BASE_URL}/searchToken",
                params={"name": token_name},
            )
            res.raise_for_status()
            return str(res.json().get("data", None))

        return retry_request(_get_token_address, retries=3, delay=5)(token_name)

    def get_pool_info(self, token_A: str, token_B: str) -> str:
        """
        Use this tool to get the pool info of two tokens.
        Args:
            token_A (str): Name of the first token.
            token_B (str): Name of the second token.
        Returns:
            str: Pool info of the two tokens.
        """

        def _get_pool_info(token_A: str, token_B: str) -> str:
            res = requests.get(
                f"{settings.SERVICE_JUPITER_BASE_URL}/getPoolInfo",
                params={"tokenAName": token_A, "tokenBName": token_B},
            )
            res.raise_for_status()
            return str(res.json())

        return retry_request(_get_pool_info, retries=3, delay=5)(token_A, token_B)

    def pre_swap_info(
        self,
        input_amount: float,
        input_token_name: str,
        output_token_name: str,
        is_buy: bool,
        slippage: float = 0.5,
    ):
        """
        Retrieves pre-swap information for a token exchange on Jupiter, including token addresses and estimated output amount.

        This tool must be called before executing swap_token to obtain the necessary mint addresses and validate
        the potential swap outcome with slippage consideration.

        Args:
            input_amount (float): The amount of tokens to swap from. Must be greater than 0.
            input_token_name (str): The name of the token you're swapping from (e.g., "SOL", "USDC").
            output_token_name (str): The name of the token you're swapping to (e.g., "USDC", "SOL").
            is_buy (bool): Transaction direction indicator:
                          - True: Buying output_token with input_token
                          - False: Selling input_token for output_token
            slippage (float): Maximum acceptable price impact as a percentage.
                             Range: 0.1% to 10%. Default: 0.5%

        Returns:
            str: A JSON string containing:
                - input_mint_address: The SPL token address for the input token
                - output_mint_address: The SPL token address for the output token
                - output_amount: Estimated amount of output tokens to receive
                - price_impact: Expected price impact of the swap
                - minimum_received: Minimum output amount accounting for slippage
        """
        if is_buy:
            input_token_name, output_token_name = (
                output_token_name,
                input_token_name,
            )

        def _before_swap_info(
            input_amount: float,
            input_token_name: str,
            output_token_name: str,
            slippage: float = 0.5,
        ) -> str:
            res = requests.get(
                f"{settings.SERVICE_JUPITER_BASE_URL}/searchTokenPair",
                params={
                    "amount": input_amount,
                    "tokenNameA": input_token_name,
                    "tokenNameB": output_token_name,
                    "slippage": slippage,
                },
            )
            res.raise_for_status()
            return str(res.json())

        return retry_request(_before_swap_info, retries=3, delay=5)(
            input_amount,
            input_token_name,
            output_token_name,
            slippage,
        )

    def swap_token(
        self,
        agent: Agent,
        input_amount: float,
        input_mint_address: str,
        output_mint_address: str,
        is_buy: bool,
        slippage: float = 0.5,
    ) -> str:
        """
        Use this tool to swap tokens. Always notify the user about the addresses of tokens.
        Args:
            input_amount (float): Amount of input token to swap. > 0
            input_mint_address (str): Mint address of input token. It must be a valid mint address. Example: "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
            output_mint_address (str): Mint address of output token. It must be a valid mint address. Example: "So11111111111111111111111111111111111111112"
            is_buy (bool): True if the user is buying, False if the user is selling.
            slippage (float): Slippage tolerance in percentage. Default is 0.5, value must be between 0.1 and 10. Always ask the user for the slippage.
        Returns:
            str: Transaction hash or error message.
        """
        user_id = agent.context["user_id"]
        # If buy, swap input_mint_address to output_mint_address
        if is_buy:
            input_mint_address, output_mint_address = (
                output_mint_address,
                input_mint_address,
            )

        logger.info(
            f"[TOOLS] Swapping {input_amount} {input_mint_address} to {output_mint_address} for user: {user_id}"
        )
        ## CALL JUPITER API
        wallet = self._get_wallet(agent)
        if wallet is None:
            logger.error(f"[TOOLS] User {user_id} does not have a wallet")
            return "User does not have a wallet"
        private_key = wallet.private_key

        balance = float(self.check_balance(agent, input_mint_address))
        if balance < input_amount:
            logger.error(f"[TOOLS] Insufficient balance for user: {user_id}")
            return "Insufficient balance"

        def _swap(
            private_key: str,
            input_amount: float,
            input_mint_address: str,
            output_mint_address: str,
            slippage: float = 0.5,
        ) -> str:
            body = {
                "inputAmount": input_amount,
                "inputMint": input_mint_address,
                "outputMint": output_mint_address,
                "privateKey": private_key,
                "slippage": slippage,
            }
            response = requests.post(
                f"{settings.SERVICE_JUPITER_BASE_URL}/jupiterSwap",
                json=body,
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
                    f"[TOOLS] Swapped {input_amount} {input_mint_address} to {output_mint_address} for user: {user_id}"
                )
                return str(res["data"])
            else:
                raise Exception(f"Something went wrong: {res}")

        try:
            return retry_request(_swap, retries=3, delay=5)(
                private_key,
                input_amount,
                input_mint_address,
                output_mint_address,
                slippage,
            )
        except Exception as e:
            logger.error(f"[TOOLS] Something went wrong: {e}")
            return str(e)

    def limit_order(
        self,
        agent: Agent,
        maker_amount: float,
        taker_amount: float,
        maker_mint: str,
        taker_mint: str,
    ) -> str:
        """
        Use this tool to create a limit order. Always notify the user about the addresses of tokens.
        Args:
            maker_amount (float): Amount of maker token to swap. > 0
            taker_amount (float): Amount of taker token to swap. > 0
            maker_mint (str): Mint address of maker token. It must be a valid mint address. Example: "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
            taker_mint (str): Mint address of taker token. It must be a valid mint address. Example: "So11111111111111111111111111111111111111112"
        Returns:
            str: Transaction hash or error message.
        """
        # if maker_amount < 5:
        #     return "Maker amount must be greater than 5"
        user_id = agent.context["user_id"]
        logger.info(f"[TOOLS] Creating limit order for user: {user_id}")
        wallet = self._get_wallet(agent)
        if wallet is None:
            logger.error(f"[TOOLS] User {user_id} does not have a wallet")
            return "User does not have a wallet"
        private_key = wallet.private_key

        balance = float(self.check_balance(agent, maker_mint))
        if balance < maker_amount:
            logger.error(f"[TOOLS] Insufficient balance for user: {user_id}")
            return "Insufficient balance"

        def _limit_order(
            private_key: str,
            maker_amount: float,
            taker_amount: float,
            maker_mint: str,
            taker_mint: str,
        ) -> str:
            body = {
                "makingAmount": maker_amount,
                "takingAmount": taker_amount,
                "inputMint": maker_mint,
                "outputMint": taker_mint,
                "privateKey": private_key,
            }
            response = requests.post(
                f"{settings.SERVICE_JUPITER_BASE_URL}/jupiterLimitOrder",
                json=body,
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
                return str(res["data"])
            else:
                raise Exception(f"Something went wrong: {res}")

        try:
            return retry_request(_limit_order, retries=3, delay=5)(
                private_key,
                maker_amount,
                taker_amount,
                maker_mint,
                taker_mint,
            )
        except Exception as e:
            logger.error(f"[TOOLS] Something went wrong: {e}")
            return str(e)

    def cancel_all_orders(self, agent: Agent) -> str:
        """
        Use this tool to cancel all orders for a user.
        Args:

        Returns:
            str: status of the request
        """
        user_id = agent.context["user_id"]
        logger.info(f"[TOOLS] Cancelling all orders for user: {user_id}")
        wallet = self._get_wallet(agent)
        if wallet is None:
            logger.error(f"[TOOLS] User {user_id} does not have a wallet")
            return "User does not have a wallet"
        private_key = wallet.private_key

        def _cancel_all_orders(private_key: str) -> str:
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
                return str(res["data"])
            else:
                raise Exception(f"[TOOLS] Something went wrong: {res}")

        try:
            return retry_request(_cancel_all_orders, retries=3, delay=5)(private_key)
        except Exception as e:
            logger.error(f"[TOOLS] Something went wrong: {e}")
            return str(e)

    def create_dca(
        self,
        agent: Agent,
        input_token: str,
        output_token: str,
        total_amount: float,
        interval: float,
        amount_per_interval: float,
    ) -> str:
        """
        Use this tool to create a DCA for a user.
        Args:
            input_token (str): Name of input token. Example: "SOL", "USDC"
            output_token (str): Name of output token. Example: "USDC", "SOL"
            total_amount (float): Total amount of input token to swap. > 0
            interval (float): Interval in hours between each swap. > 0. It could be a float number. If 0.5, it means 30 minutes, 1.5 means 90 minutes, etc.
            amount_per_interval (float): Amount of input token to swap per interval. > 0
        Returns:
            str: Transaction hash or error message.
        """
        user_id = agent.context["user_id"]
        logger.info(f"[TOOLS] Creating DCA for user: {user_id}")
        wallet = self._get_wallet(agent)
        if wallet is None:
            logger.error(f"[TOOLS] User {user_id} does not have a wallet")
            return "User does not have a wallet"
        private_key = wallet.private_key

        def _create_dca(
            private_key: str,
            input_token: str,
            output_token: str,
            total_amount: float,
            interval: float,
            amount_per_interval: float,
        ) -> str:
            body = {
                "privateKey": private_key,
                "inputMint": input_token,
                "outputMint": output_token,
                "inputAmount": total_amount,
                "timeHoursCircle": interval,
                "amountPerCircle": amount_per_interval,
            }
            response = requests.post(
                f"{settings.SERVICE_JUPITER_BASE_URL}/dca",
                json=body,
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
                logger.info(f"[TOOLS] Created DCA for user: {user_id}")
                return str(res["data"])
            else:
                raise Exception(f"Something went wrong: {res}")

        try:
            return retry_request(_create_dca, retries=3, delay=5)(
                private_key,
                input_token,
                output_token,
                total_amount,
                interval,
                amount_per_interval,
            )
        except Exception as e:
            logger.error(f"[TOOLS] Something went wrong: {e}")
            return str(e)

    def cancel_dca(self, agent: Agent, dca_public_key: str) -> str:
        """
        Use this tool to cancel a DCA for a user.
        Args:
            dca_public_key (str): Public key of the DCA.
        Returns:
            str: Transaction hash or error message.
        """
        user_id = agent.context["user_id"]
        logger.info(f"[TOOLS] Cancelling DCA for user: {user_id}")
        wallet = self._get_wallet(agent)
        if wallet is None:
            logger.error(f"[TOOLS] User {user_id} does not have a wallet")
            return "User does not have a wallet"
        private_key = wallet.private_key

        def _cancel_dca(private_key: str, dca_public_key: str) -> str:
            body = {
                "privateKey": private_key,
                "dcaPublickey": dca_public_key,
            }
            response = requests.post(
                f"{settings.SERVICE_JUPITER_BASE_URL}/dca/close",
                json=body,
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
                logger.info(f"[TOOLS] Cancelled DCA for user: {user_id}")
                return str(res["data"])
            else:
                raise Exception(f"Something went wrong: {res}")

        try:
            return retry_request(_cancel_dca, retries=3, delay=5)(
                private_key, dca_public_key
            )
        except Exception as e:
            logger.error(f"[TOOLS] Something went wrong: {e}")
            return str(e)
