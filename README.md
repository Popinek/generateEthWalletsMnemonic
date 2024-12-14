## Generate Ethereum wallets with mnemonic phrases and check balances

This repository contains Python scripts to create Ethereum wallets in bulk efficiently. It includes functionalities to generate thousands Ethereum wallets with mnemonic phrases, save them to files, and check the balance of addresses stored in `address.txt`.

### Features:

1. **Wallet Generation:** Utilizes `eth_account` library to generate Ethereum wallets with mnemonic phrases. The script [`main.py`](main.py) allows users to specify the number of wallets to create and saves the mnemonic phrases and addresses to separate files.

2. **Balance Checking:** The `check_balance_and_save` function in [`main.py`](main.py) checks the balance of Ethereum addresses listed in `address.txt`. If an address has a non-zero balance, it saves it to `balance.txt`. This feature utilizes the `web3.py` library for interacting with the Ethereum blockchain.

3. **Check up to 200k wallets for free:** Newly added Etherscan api allows to check up additional 100k wallets for free. You can also use the old Infura api that also allows 100k wallets check up. I recommend to use Infura because it works faster and isnt capped to check only 5 addresses per second as Etherscan api.

   
### Setup:

1. Install dependencies:

```bash
pip install eth-account web3
```

2. Obtain an Infura project ID and replace
   'https://mainnet.infura.io/v3/xxxxxYOURinfuraKEYxxxxxxx' with your Infura project ID in the script.

3. Run the scripts:

+ To generate Ethereum wallets, run main.py.
+ To check balances from address.txt, uncomment the call to check_balance_and_save at the end of main.py and run it.

### Note:
+ Experimental Feature Warning: The wallet generation functionality utilizes experimental features of eth_account library.
+ Use Infura or Own Ethereum Node: The balance checking feature requires access to an Ethereum node. You can use Infura or run your own Ethereum node.
