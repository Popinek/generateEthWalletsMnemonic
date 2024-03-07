from web3 import Web3
from eth_account import Account
import os

# Initialize web3 provider
web3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/xxxxxYOURinfuraKEYxxxxxxx'))

def check_balance_and_save(accounts_file, output_file):
    # Read addresses from address.txt
    with open(accounts_file, 'r') as f:
        addresses = f.readlines()
    addresses = [address.strip() for address in addresses]

    num_addresses_checked = 0
    num_addresses_with_balance = 0

    # Check balance for each address
    addresses_with_balance = []
    for address in addresses:
        balance = web3.eth.get_balance(address)
        num_addresses_checked += 1
        if balance > 0:
            addresses_with_balance.append(address)
            num_addresses_with_balance += 1

    # Write addresses with non-zero balance to balance.txt
    with open(output_file, 'w') as f:
        for address in addresses_with_balance:
            f.write(address + '\n')

    print(f"Checked {num_addresses_checked} addresses.")
    print(f"Found {num_addresses_with_balance} addresses with non-zero balance.")

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
    num_wallets_to_generate = 1000  # Specify the number of Ethereum wallets to generate
    wallets = generate_eth_wallets(num_wallets_to_generate)

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

    #   Uncomment to check balances from address.txt
    # check_balance_and_save(accounts_file, output_file)
