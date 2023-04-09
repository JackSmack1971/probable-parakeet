# conftest.py

import pytest
from web3 import Web3
from web3.middleware import geth_poa_middleware
from solc import compile_standard
import json

@pytest.fixture(scope='module')
def w3():
    # Replace with the address of your local Ethereum node or Infura endpoint
    provider_url = 'http://localhost:8545'
    w3 = Web3(Web3.HTTPProvider(provider_url))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    return w3

@pytest.fixture(scope='module')
def contract(w3):
    # Replace with the path to your Solidity contract
    contract_path = 'path/to/your/contract.sol'
    
    # Replace with the name of your contract
    contract_name = 'YourContractName'

    # Read the contract file
    with open(contract_path, 'r') as file:
        contract_source_code = file.read()

    # Compile the contract
    compiled_sol = compile_standard({
        'language': 'Solidity',
        'sources': {
            contract_path: {
                'content': contract_source_code
            }
        },
        'settings': {
            'outputSelection': {
                '*': {
                    '*': ['metadata', 'evm.bytecode', 'evm.bytecode.sourceMap']
                }
            }
        }
    })

    # Get the contract ABI and bytecode
    contract_interface = json.loads(compiled_sol['contracts'][contract_path][contract_name]['metadata'])['output']['abi']
    contract_bytecode = compiled_sol['contracts'][contract_path][contract_name]['evm']['bytecode']['object']

    # Deploy the contract
    contract = w3.eth.contract(abi=contract_interface, bytecode=contract_bytecode)
    estimated_gas = contract.constructor().estimateGas()
    account = w3.eth.accounts[0]
    transaction = contract.constructor().buildTransaction({'from': account, 'gas': estimated_gas, 'nonce': w3.eth.getTransactionCount(account)})
    signed_txn = w3.eth.account.signTransaction(transaction, w3.eth.account.privateKeyToAccount(account).privateKey)
    transaction_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

    # Get the contract address
    transaction_receipt = w3.eth.waitForTransactionReceipt(transaction_hash)
    contract_address = transaction_receipt['contractAddress']

    # Instantiate the contract
    contract_instance = w3.eth.contract(address=contract_address, abi=contract_interface)

    return contract_instance
