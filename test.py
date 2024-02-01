import time
import hashlib
import hmac
import base64
import json
import requests

api_key = "os.getenv('KUCOIN_API_KEY')"
api_secret = "os.getenv('KUCOIN_SECRET_KEY')"
api_passphrase = "@SuperSanta1995"
api_key_version = "2"  # Версия вашего API-ключа
#url_balance = 'https://api.kucoin.com/api/v1/accounts'

# Указываем параметры запроса
url_deposit_addresses = 'https://api.kucoin.com/api/v2/deposit-addresses'
currency = "BTC"  # Замените на нужную валюту

# Создаем подпись для запроса
now_deposit_addresses = int(time.time() * 1000)
str_to_sign_deposit_addresses = str(now_deposit_addresses) + 'GET' + '/api/v2/deposit-addresses?currency=' + currency
print(str_to_sign_deposit_addresses)
signature_deposit_addresses = base64.b64encode(
    hmac.new(api_secret.encode('utf-8'), str_to_sign_deposit_addresses.encode('utf-8'), hashlib.sha256).digest())
passphrase_deposit_addresses = base64.b64encode(
    hmac.new(api_secret.encode('utf-8'), api_passphrase.encode('utf-8'), hashlib.sha256).digest())

# Формируем заголовки запроса
headers_deposit_addresses = {
    "KC-API-SIGN": signature_deposit_addresses,
    "KC-API-TIMESTAMP": str(now_deposit_addresses),
    "KC-API-KEY": api_key,
    "KC-API-PASSPHRASE": passphrase_deposit_addresses,
    "KC-API-KEY-VERSION": api_key_version
}

# Отправляем GET-запрос
response_deposit_addresses = requests.get(url_deposit_addresses, headers=headers_deposit_addresses, params={"currency": currency})

# Выводим результат
print(response_deposit_addresses.status_code)
print(response_deposit_addresses.json())

# now_balance = int(time.time() * 1000)
# str_to_sign_balance = str(now_balance) + 'GET' + '/api/v1/accounts'
# signature_balance = base64.b64encode(
#     hmac.new(api_secret.encode('utf-8'), str_to_sign_balance.encode('utf-8'), hashlib.sha256).digest())
#
# passphrase_balance = base64.b64encode(hmac.new(api_secret.encode('utf-8'), api_passphrase.encode('utf-8'), hashlib.sha256).digest())
#
# headers_balance = {
#     "KC-API-SIGN": signature_balance,
#     "KC-API-TIMESTAMP": str(now_balance),
#     "KC-API-KEY": api_key,
#     "KC-API-PASSPHRASE": passphrase_balance,
#     "KC-API-KEY-VERSION": api_key_version
# }
#
# response_balance = requests.request('get', url_balance, headers=headers_balance)
# print(response_balance.status_code)
# print(response_balance.json())

# url_deposit_address = 'https://api.kucoin.com/api/v1/deposit-addresses'
# now_deposit_address = int(time.time() * 1000)
# data_deposit_address = {"currency": "BTC"}
# data_json_deposit_address = json.dumps(data_deposit_address)
# str_to_sign_deposit_address = str(now_deposit_address) + 'POST' + '/api/v1/deposit-addresses' + data_json_deposit_address
# signature_deposit_address = base64.b64encode(
#     hmac.new(api_secret.encode('utf-8'), str_to_sign_deposit_address.encode('utf-8'), hashlib.sha256).digest())
# passphrase_deposit_address = base64.b64encode(
#     hmac.new(api_secret.encode('utf-8'), api_passphrase.encode('utf-8'), hashlib.sha256).digest())
#
# headers_deposit_address = {
#     "KC-API-SIGN": signature_deposit_address,
#     "KC-API-TIMESTAMP": str(now_deposit_address),
#     "KC-API-KEY": api_key,
#     "KC-API-PASSPHRASE": passphrase_deposit_address,
#     "KC-API-KEY-VERSION": api_key_version,
#     "Content-Type": "application/json"
# }
#
# response_deposit_address = requests.request('post', url_deposit_address, headers=headers_deposit_address, data=data_json_deposit_address)
# print(response_deposit_address.status_code)
# print(response_deposit_address.json())

