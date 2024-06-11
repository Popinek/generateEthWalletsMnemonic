import requests
import time
from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv
import winsound
import os
from multiprocessing import Pool, cpu_count

# Load environment variables from .env file
load_dotenv()

# Control panel configuration
CONFIG = {
    'use_infura': True,
    'use_etherscan': False,
    'check_transactions_only': False,
    'num_wallets_to_generate': 1000,
    'infura_url': os.getenv('INFURA_URL'),
    'etherscan_api_url': 'https://api.etherscan.io/api',
    'etherscan_api_key': os.getenv('ETHERSCAN_API_KEY'),
    'wallet_max_workers': 4,  # Number of processes for generating wallets
    'check_max_workers': 4  # Number of processes for checking balances or transactions. Use max 3 for Infura, 2 for Etherscan
}

# Initialize web3 provider
web3_infura = Web3(Web3.HTTPProvider(CONFIG['infura_url']))


def check_eth_balance_infura(address):
    while True:
        try:
            return web3_infura.eth.get_balance(address)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Too Many Requests
                print("Too many requests. Retrying in 5 seconds...")
                time.sleep(5)
            else:
                raise  # Re-raise the exception if it's not a 429 error


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


def check_address(address):
    if CONFIG['check_transactions_only']:
        has_transactions = check_transactions(address)
        if has_transactions:
            return address, "Has transactions"
    else:
        balance = check_eth_balance(address)
        if balance > 0:
            return address, balance
    return None


def check_balances_and_save(accounts_file, output_file, wallets):
    # Read addresses from address.txt
    with open(accounts_file, 'r') as f:
        addresses = f.readlines()
    addresses = [address.strip() for address in addresses]

    num_addresses_checked = 0
    num_addresses_with_balance = 0

    # Check balances or transactions for each address using parallel processing
    addresses_with_balance = []

    with Pool(processes=CONFIG['check_max_workers']) as pool:
        results = pool.map(check_address, addresses)

    for result in results:
        if result:
            addresses_with_balance.append(result)
            num_addresses_with_balance += 1
        num_addresses_checked += 1

    # Write addresses with non-zero balance or transactions to balance.txt
    with open(output_file, 'a') as f:
        for address, balance in addresses_with_balance:
            mnemonic = next(wallet["mnemonic_phrase"] for wallet in wallets if wallet["address"] == address)
            f.write(f"Address: {address}, Balance: {balance}, Mnemonic: {mnemonic}\n")

    print(f"Checked {num_addresses_checked} addresses.")
    print(f"Found {num_addresses_with_balance} addresses with non-zero balance or transactions.")


def create_wallet(_):
    # Enable Mnemonic features
    Account.enable_unaudited_hdwallet_features()
    # Create a new private key and related mnemonic with 12 words
    acct, mnemonic_phrase = Account.create_with_mnemonic(num_words=12)
    # Get the address corresponding to the mnemonic phrase
    address = acct.address
    return {
        "mnemonic_phrase": mnemonic_phrase,
        "address": address
    }


def generate_eth_wallets(num_wallets):
    start_wallet_generation = time.time()  # Start timing the wallet generation
    print(f"Generating {num_wallets} wallets using {CONFIG['wallet_max_workers']} workers...")

    with Pool(processes=CONFIG['wallet_max_workers']) as pool:
        wallets = pool.map(create_wallet, range(num_wallets))

    end_wallet_generation = time.time()  # End timing the wallet generation
    wallet_generation_time = end_wallet_generation - start_wallet_generation
    print(f"Wallet generation took {wallet_generation_time:.2f} seconds.")

    return wallets


if __name__ == '__main__':
    # Start timer
    start_time = time.time()

    wallets = generate_eth_wallets(CONFIG['num_wallets_to_generate'])

    # Write mnemonic phrases to mnemonic.txt
    with open('mnemonic.txt', 'w') as f:
        for wallet in wallets:
            f.write(wallet["mnemonic_phrase"] + '\n')

    # Write addresses to address.txt
    with open('address.txt', 'w') as f:
        for wallet in wallets:
            f.write(wallet["address"] + '\n')

    print(
        "\nEthereum Wallets Generated. Mnemonic phrases saved in 'mnemonic.txt' and addresses saved in 'address.txt'.")

    accounts_file = 'address.txt'
    output_file = 'balance.txt'

    # Check if we need to perform balance or transaction checks
    if CONFIG['use_infura'] or CONFIG['use_etherscan'] or CONFIG['check_transactions_only']:
        # Check balances or transactions from address.txt
        check_balances_and_save(accounts_file, output_file, wallets)

    # End timer
    end_time = time.time()
    elapsed_time = end_time - start_time
    elapsed_minutes = elapsed_time / 60

    # Calculate addresses checked per minute
    addresses_per_minute = (CONFIG['num_wallets_to_generate'] / elapsed_time) * 60

    print(f"Total Elapsed time: {elapsed_time:.2f} seconds ({elapsed_minutes:.2f} minutes).")
    print(f"Addresses checked per minute: {addresses_per_minute:.2f}.")
    # Play system sound to inform the task is done
    winsound.MessageBeep(winsound.MB_ICONHAND)
