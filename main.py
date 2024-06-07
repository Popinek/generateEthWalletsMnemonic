import requests
import time
from web3 import Web3
from eth_account import Account
import winsound

import os

# Control panel configuration
CONFIG = {
    'use_infura': True,
    'use_etherscan': False,
    'check_transactions_only': False,
    'num_wallets_to_generate': 10,
    'infura_url': 'https://mainnet.infura.io/v3/xxxxxxxxx',
    'etherscan_api_url': 'https://api.etherscan.io/api',
    'etherscan_api_key': 'xxxxxxxxxx'
}

# Initialize web3 provider
web3_infura = Web3(Web3.HTTPProvider(CONFIG['infura_url']))

def check_eth_balance_infura(address):
    return web3_infura.eth.get_balance(address)

def check_eth_balance_etherscan(address):
    response = requests.get(CONFIG['etherscan_api_url'], params={
        'module': 'account',
        'action': 'balance',
        'address': address,
        'tag': 'latest',
        'apikey': CONFIG['etherscan_api_key']
    })
    return int(response.json().get('result', 0))

def check_eth_balance(address):
    if CONFIG['use_infura']:
        balance = check_eth_balance_infura(Web3.to_checksum_address(address))
    elif CONFIG['use_etherscan']:
        balance = check_eth_balance_etherscan(Web3.to_checksum_address(address))
    return balance

def check_transactions(address):
    response = requests.get(CONFIG['etherscan_api_url'], params={
        'module': 'account',
        'action': 'txlist',
        'address': address,
        'startblock': 0,
        'endblock': 99999999,
        'sort': 'asc',
        'apikey': CONFIG['etherscan_api_key']
    })
    transactions = response.json().get('result', [])
    return len(transactions) > 0

def check_balances_and_save(accounts_file, output_file):

    # Read addresses from address.txt
    with open(accounts_file, 'r') as f:
        addresses = f.readlines()
    addresses = [address.strip() for address in addresses]

    num_addresses_checked = 0
    num_addresses_with_balance = 0

    # Check balances or transactions for each address
    addresses_with_balance = []
    for address in addresses:
        if CONFIG['check_transactions_only']:
            has_transactions = check_transactions(address)
            if has_transactions:
                addresses_with_balance.append((address, "Has transactions"))
        else:
            balance = check_eth_balance(address)
            if balance > 0:
                addresses_with_balance.append((address, balance))
        num_addresses_checked += 1

    # Write addresses with non-zero balance to balance.txt
    with open(output_file, 'a') as f:
        for address, balance in addresses_with_balance:
            mnemonic = next(wallet["mnemonic_phrase"] for wallet in wallets if wallet["address"] == address)
            f.write(f"Address: {address}, Balance: {balance}, Mnemonic: {mnemonic}\n")

    print(f"Checked {num_addresses_checked} addresses.")
    print(f"Found {num_addresses_with_balance} addresses with non-zero balance or transactions.")

def generate_eth_wallets(num_wallets):
    wallets = []

    # Enable Mnemonic features
    Account.enable_unaudited_hdwallet_features()

    for _ in range(num_wallets):
        # Create a new private key and related mnemonic with 12 words
        acct, mnemonic_phrase = Account.create_with_mnemonic(num_words=12)

        # Get the address corresponding to the mnemonic phrase
        address = acct.address

        wallet_info = {
            "mnemonic_phrase": mnemonic_phrase,
            "address": address
        }
        wallets.append(wallet_info)

    return wallets

if __name__ == '__main__':
    wallets = generate_eth_wallets(CONFIG['num_wallets_to_generate'])

    # Write mnemonic phrases to mnemonic.txt
    with open('mnemonic.txt', 'w') as f:
        for wallet in wallets:
            f.write(wallet["mnemonic_phrase"] + '\n')

    # Write addresses to address.txt
    with open('address.txt', 'w') as f:
        for wallet in wallets:
            f.write(wallet["address"] + '\n')

    print("\nEthereum Wallets Generated. Mnemonic phrases saved in 'mnemonic.txt' and addresses saved in 'address.txt'.")

    accounts_file = 'address.txt'
    output_file = 'balance.txt'

    # Check balances or transactions from address.txt
    check_balances_and_save(accounts_file, output_file)

    # Play system sound to inform the task is done
    winsound.MessageBeep(winsound.MB_ICONHAND)

