import requests
from constants import MARKET_CAP
from phi.tools import Toolkit
from phi.utils.log import logger

def rename_keys(data):
    # Định nghĩa từ điển ánh xạ các key cũ sang key mới
    key_mapping = {
        'h24': 'last_24_hours',
        'h6': 'last_6_hours',
        'h1': 'last_1_hour',
        'm5': 'last_5_minutes',
        'txns': 'transactions'
    }
    
    # Thay đổi key trong 'txns'
     # Kiểm tra sự tồn tại của key 'txns' và đổi tên thành 'transactions'
    if 'txns' in data:
        data['transactions'] = {key_mapping.get(k, k): v for k, v in data['txns'].items()}
        del data['txns']  # Xóa key 'txns' cũ

    # Thay đổi key trong 'volume'
    if 'volume' in data:
        data['volume'] = {key_mapping.get(k, k): v for k, v in data['volume'].items()}
    
    # Thay đổi key trong 'priceChange'
    if 'priceChange' in data:
        data['priceChange'] = {key_mapping.get(k, k): v for k, v in data['priceChange'].items()}
    
    return data

def fetcher( url: str):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return {"status": "success", "data": response.json()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def fetch_token_boosts():
    try:
        url = "https://api.dexscreener.com/token-boosts/top/v1"
        res = fetcher(url)
        if res["status"] == "success":
            boosts = res.get("data", {})
            return boosts

        else:
            return {"status": "error", "message": res["message"]}
    except Exception as e:
        return {"status": "error", "message": str(e)}


    
def fetch_token_rankings():
    try:
        url = "https://gmgn.ai/defi/quotation/v1/rank/sol/wallets/30d?orderby=pnl_30d&direction=desc"
        res = fetcher(url)
        if res["status"] == "success":
            data = res.get("data", {})
            data = data.get("data", {})
            rankings = data.get("rank", {})
            return rankings
        else:
            return {"status": "error", "message": res["message"]}
    except Exception as e:
        return {"status": "error", "message": str(e)}
def get_tokens_information(chainId: str):
        """
        This tool is designed to provide a comprehensive list of information about tokens and coins.

        Args:
            chainId(str): The id of chain. Default is "solana"

        Returns:
            A list of dictionaries containing information about tokens with market capitalization over 300k.
        """
        logger.info("Tool: Suggest")
        tokens_address = []
        tokens = fetch_token_boosts()
        for token in tokens:
            tokens_address.append(token['tokenAddress'])
        tokens_address_string = ",".join(tokens_address)
        chainId = "solana"
        try:
            url = f"https://api.dexscreener.com/tokens/v1/{chainId}/{tokens_address_string}"
            res = fetcher(url)
            if res["status"] == "success":
                tokens_information = res.get("data", {})
                tokens_infor_over_300k = [rename_keys(item) for item in tokens_information if item['marketCap'] >= MARKET_CAP ]
                return"Below are a few trending tokens today:\n" +  str(tokens_infor_over_300k[:10])

            else:
                return {"status": "error", "message": res["message"]}
        except Exception as e:
            return {"status": "error", "message": str(e)}