from solcx import compile_standard
import json
from web3 import Wb3, HTTPProvider, TestRPCProvider
import os
from dotenv import load_dotenv

load_dotenv()


with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()
# compile our solidity
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solcx_version="0.6.0",
)
with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# to deploy to a chain, you need 2 things 1.BYTECODE 2.ABI


# get bytecode
# walk down the compiled json code
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]


# get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# connect to ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
chain_id = 1337
my_address = "0x9722961561cECa50E84EAcC35e6D025Dbb86a91D"
private_key = os.getenv("PRIVATE_KEY")

# create the contract in python
SimpleStorage = w3.eth.contract(eth=abi, bytecode=bytecode)

# get the latest transaction
nonce = w3.eth.getTransactionCount(my_address)


# 1.Build a transaction
# 2.Sign a transaction
# 3.Send a transaction
transaction = SimpleStorage.constructor().buildTransaction(
    ("chainId", chain_id, "from", my_address, "nonce", nonce)
)
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

# send this signed transaction
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

# working with the contract needs 2 stuff
# 1. Contract addess
# 2. Contract ABI
SimpleStorage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

# transactions in blockchain are either 1. call or 2.  transactions
# call --> simulate making the call but not maling a state change but getting areturn value
# transact--> making a state change

# initial value of favoriteNumber
print(SimpleStorage.functions.retrieve().call())

store_transaction = SimpleStorage.functions.store(15).buildTransaction(
    ("chainId", chain_id, "from", my_address, "nonce", nonce + 1)
)

signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)
send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
print(transaction)
