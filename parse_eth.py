from eth_account import Account
from web3 import Web3
from tqdm import tqdm
from datetime import datetime

from dotenv import load_dotenv
import os

load_dotenv()
ETH_NODE_KEY = os.getenv('ETH_NODE_KEY')
INCOMPLETE_PHRASE = os.getenv('INCOMPLETE_PHRASE')

Account.enable_unaudited_hdwallet_features()

ethereum_node_url = f"https://polygon-mainnet.infura.io/v3/{ETH_NODE_KEY}"
web3 = Web3(Web3.HTTPProvider(ethereum_node_url))

def get_wallet_address(phrase):
    private_key = Account.from_mnemonic(" ".join(phrase))._private_key
    account = Account.from_key(private_key)
    address = account.address
    return address

def check_balance(address):
    balance_wei = web3.eth.get_balance(address)
    balance_eth = web3.from_wei(balance_wei, 'ether')
    return balance_eth

with open('bip39.txt', 'r') as f:
    word_list = [word.replace('\n', '') for word in f.readlines()]

incomplete_phrase = INCOMPLETE_PHRASE.split(', ')
if len(incomplete_phrase) == 11:
    incomplete_phrase.append("")

for word in tqdm(word_list):
    incomplete_phrase[11] = word

    wallet_address = ''

    try:
        wallet_address = get_wallet_address(incomplete_phrase)
    except:
        continue

    balance = check_balance(wallet_address)
    if balance > 0:
        print(incomplete_phrase)
        print(f"Wallet Address: {wallet_address} | Balance: {balance} MATIC")
        with open('result.txt', 'a') as f:
            f.write(f"[{datetime.now()}]\n{incomplete_phrase}\n{wallet_address} | {balance} MATIC\n" + '-' * 50 + '\n')
        break

