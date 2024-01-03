from eth_account import Account
from web3 import Web3
from tqdm import tqdm
from datetime import datetime
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
import os
import sys
import time

unknown_word1_number = 9
unknown_word2_number = 10

load_dotenv()
INCOMPLETE_PHRASE = os.getenv('INCOMPLETE_PHRASE')
ETH_NODE_KEYS = os.getenv('ETH_NODE_KEYS').split(', ')

node_keys = len(ETH_NODE_KEYS)

Account.enable_unaudited_hdwallet_features()

with open('bip39.txt', 'r') as f:
    word_list = [word.replace('\n', '') for word in f.readlines()]
    # word_list = word_list[::-1]

all_word_list = word_list

alternate_node_urls = [f"https://polygon-mainnet.infura.io/v3/{key}" for key in ETH_NODE_KEYS]


def process_phrase(args):
    thread_id, chunk, ethereum_node_url, pbar = args
    web3 = Web3(Web3.HTTPProvider(ethereum_node_url[1]))

    if not ethereum_node_url:
        return 0

    incomplete_phrase = INCOMPLETE_PHRASE.split(', ')

    start_time = datetime.now()
    break_flag = False
    for word in chunk:
        if break_flag:
            break
        while True:
            try:
                incomplete_phrase[unknown_word1_number-1] = word

                for word2 in all_word_list:
                    incomplete_phrase[unknown_word2_number-1] = word2
                    wallet_address = ''

                    balance = 0

                    try:
                        private_key = Account.from_mnemonic(" ".join(incomplete_phrase))._private_key
                        account = Account.from_key(private_key)
                        wallet_address = account.address
                    except:
                        continue

                    if wallet_address != '':
                        balance_wei = web3.eth.get_balance(wallet_address)
                        balance = web3.from_wei(balance_wei, 'ether')

                    if balance > 0:
                        break_flag = True
                        print(incomplete_phrase)
                        print(f"[{thread_id}] Wallet Address: {wallet_address} | Balance: {balance} MATIC | Time: {datetime.now() - start_time}")
                        with open('result.txt', 'a') as f:
                            f.write(f"[{datetime.now()}]\n[{datetime.now() - start_time}]\n{incomplete_phrase}\n{wallet_address} | {balance} MATIC\n" + '-' * 50 + '\n')


            except KeyboardInterrupt:
                print('Interrupted')
                try:
                    sys.exit(130)
                except SystemExit:
                    os._exit(130)
            except Exception as e:
                print(f"[{thread_id}] Error: {e}")
                continue
            break
        pbar.update(1)


chunk_size = len(word_list) // node_keys
chunks = [(i, word_list[i:i + chunk_size], node_url) for i, node_url in enumerate(zip(range(0, len(word_list), chunk_size), alternate_node_urls))]

with ThreadPoolExecutor(max_workers=node_keys) as executor:
    with tqdm(total=len(word_list), desc="Fetching data", unit='word') as pbar:
        futures = [executor.submit(process_phrase, (chunk_id, chunk, node_url, pbar)) for chunk_id, chunk, node_url in chunks]

        for future in as_completed(futures):
            future.result()

