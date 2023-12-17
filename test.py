import httpx

domain = 'https://api.kucoin.com'

def gett():

    #url = 'https://api.kucoin.com/api/v1/market/allTickers'
    url = domain + "/api/v1/market/allTickers"#/api/v2/symbols"
    with httpx.Client() as client:
        client.get(url)
        response = client.get(url)
        data = response.json()
        print(data)


# def get_deposit_addresses(api_key, currency):
#     endpoint = 'https://api.kucoin.com/api/v2/deposit-addresses'
#     headers = {
#         'Content-Type': 'application/json',
#         'KC-API-KEY': api_key
#     }
#     params = {
#         'currency': currency
#     }
#
#     response = requests.get(endpoint, headers=headers, params=params)
#
#     if response.status_code == 200:
#         return response.json()
#     else:
#         return f"Request failed with status code {response.status_code}"


if __name__ == "__main__":
    gett()