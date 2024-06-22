from requests import Session

supported_coins = [1, 1027, 11419, 74, 2]

url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
parameters = {
    'id': ','.join(map(str, supported_coins)),
}
headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': '07a3a2f6-f0f5-4be5-8824-8f397b3519fd',
}

session = Session()
session.headers.update(headers)

