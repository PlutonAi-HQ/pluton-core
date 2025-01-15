import requests


class TokenTrending:
    def __init__(self):
        pass

    def _fetcher(self, url: str):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def fetch_token_boosts(self):
        try:
            url = "https://api.dexscreener.com/token-boosts/top/v1"
            res = self._fetcher(url)
            if res["status"] == "success":
                boosts = res.get("data", {})
                return boosts

            else:
                return {"status": "error", "message": res["message"]}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def fetch_token_rankings(self):
        try:
            url = "https://gmgn.ai/defi/quotation/v1/rank/sol/wallets/30d?orderby=pnl_30d&direction=desc"
            res = self._fetcher(url)
            if res["status"] == "success":
                data = res.get("data", {})
                data = data.get("data", {})
                rankings = data.get("rank", {})
                return rankings
            else:
                return {"status": "error", "message": res["message"]}
        except Exception as e:
            return {"status": "error", "message": str(e)}
