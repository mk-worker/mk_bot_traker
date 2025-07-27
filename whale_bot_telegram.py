### crypto_whale_sniper_bot
# ربات مانیتور تراکنش‌های نهنگ‌ها (خرید/فروش توکن ERC20) و اعلان به تلگرام

import requests
from web3 import Web3
import json
import time

# ---------- تنظیمات ----------
INFURA_URL = 'https://mainnet.infura.io/v3/2df49cef14254995952868ba26475e75'  # اینجا کلید واقعی Infura خودتو بذار
web3 = Web3(Web3.HTTPProvider(INFURA_URL))

TELEGRAM_BOT_TOKEN = '8441460025:AAEEpvny7lwgCh1gJKQGNvawHHNxETDj3ng'
TELEGRAM_CHAT_ID = '8069794293'

WHALE_ADDRESSES = [
    '0x28C6c06298d514Db089934071355E5743bf21d60',  # Binance 14
    '0x742d35Cc6634C0532925a3b844Bc454e4438f44e',  # Bitfinex
    '0xDC76CD25977E0a5Ae17155770273aD58648900D3',  # Whale Wallet
    '0xBE0eB53F46cd790Cd13851d5EFF43D12404d33E8',  # Binance 7
    '0x742d35Cc6634C0532925A3b844Bc454e4438f44e',  # Bitfinex 2
    '0x40B38765696e3D5D8d9D834d8aaD4bB6e418E489',  # Robinhood
    '0xC02aaA39b223FE8D0a0e5C4F27eAD9083C756Cc2',  # Wrapped ETH contract
    '0x00000000219ab540356cBB839CBe05303d7705Fa',  # Beacon Deposit Contract    '0x8315177aB297ba92a06054CE80a67eD4DBd7ed3a',  # Arbitrum Bridge (~1.02M ETH) :contentReference[oaicite:1]{index=1}
    '0x49048044d57e1C92a77f79988D21fa8Faf74E97e',  # Base Portal (~1.84M ETH) :contentReference[oaicite:2]{index=2}
    '0x0e58e8993100f1cbe45376c410f97f4893d9bfcd',  # Upbit Exchange (~768K ETH) :contentReference[oaicite:3]{index=3}
       '0x61EDCDF1E9AA6E8AF11f1A56EEA',  # Gemini Custody (~309K ETH) :contentReference[oaicite:5]{index=5}
    '0x8315177ab297ba92a06054ce80a67ed4dbd7ed3a',
    '0x49048044d57e1c92a77f79988d21fa8faf74e97e',
    '0x0e58e8993100f1cbe45376c410f97f4893d9bfcd',

]

ERC20_TRANSFER_TOPIC = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'

# ---------- ارسال پیام تلگرام ----------
def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"[!] Telegram Error: {e}")

# ---------- بررسی لاگ های تراکنش ----------
def monitor_wallets():
    print('[*] Monitoring wallets for buy/sell transactions...')
    latest_block = web3.eth.block_number
    whale_set = set([a.lower() for a in WHALE_ADDRESSES])

    while True:
        try:
            current_block = web3.eth.block_number
            if current_block > latest_block:
                for block_num in range(latest_block + 1, current_block + 1):
                    block = web3.eth.get_block(block_num, full_transactions=True)
                    for tx in block.transactions:
                        from_addr = tx['from'].lower()
                        to_addr = str(tx['to']).lower() if tx['to'] else ''

                        if from_addr in whale_set or to_addr in whale_set:
                            receipt = web3.eth.get_transaction_receipt(tx.hash)
                            for log in receipt['logs']:
                                if log['topics'][0].hex() == ERC20_TRANSFER_TOPIC:
                                    from_wallet = '0x' + log['topics'][1].hex()[-40:]
                                    to_wallet = '0x' + log['topics'][2].hex()[-40:]
                                    value = int(log['data'], 16) / (10 ** 18)

                                    action = ''
                                    if to_wallet.lower() in whale_set:
                                        action = '🟢 Buy'
                                    elif from_wallet.lower() in whale_set:
                                        action = '🔴 Sell'

                                    token_address = log['address']
                                    message = f"{action} detected\nToken Address: {token_address}\nFrom: {from_wallet}\nTo: {to_wallet}\nAmount: {value:.6f}"
                                    print(message)
                                    send_telegram_message(message)
                latest_block = current_block
            time.sleep(5)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == '__main__':
    monitor_wallets()
