import requests
import json
import time
import hmac
import hashlib
import base64

if __name__ == "__main__":
    api_key = "657ede20be4887000156b83f"
    api_secret = "94cc5784-73a6-4b10-87b6-ec1e9982f5dc"
    api_passphrase = "@SuperSanta1995"

    url = 'https://api.kucoin.com/api/v1/deposit-addresses'

    currency = "TRX"  # Ваша целевая валюта
    chain = "BEP20"  # Наименование цепочки валюты (в данном случае, для BTC)

    now = int(time.time() * 1000)
    method = 'POST'
    endpoint = '/api/v1/deposit-addresses'
    data = {
        "currency": currency,
        "chain": chain
    }
    data_json = json.dumps(data)

    str_to_sign = str(now) + method + endpoint + data_json
    signature = base64.b64encode(
        hmac.new(api_secret.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest()).decode('utf-8')

    passphrase = base64.b64encode(
        hmac.new(api_secret.encode('utf-8'), api_passphrase.encode('utf-8'), hashlib.sha256).digest()).decode('utf-8')

    headers = {
        "KC-API-SIGN": signature,
        "KC-API-TIMESTAMP": str(now),
        "KC-API-KEY": api_key,
        "KC-API-PASSPHRASE": passphrase,
        "KC-API-KEY-VERSION": "2",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, data=data_json)
    print(response.status_code)
    print(response.json())
