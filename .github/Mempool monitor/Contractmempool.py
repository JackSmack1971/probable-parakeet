from web3 import Web3

# Replace <INFURA_PROJECT_ID> with your Infura project ID
infura_url = 'https://mainnet.infura.io/v3/<INFURA_PROJECT_ID>'

# Define the contract ABI and address
abi = [...]  # ERC20 contract ABI
contract_address = '0x...'  # ERC20 contract address

# Define the event signature for the Transfer event
event_signature = Web3.sha3(text='Transfer(address,address,uint256)').hex()

# Connect to Infura's Ethereum node
w3 = Web3(Web3.HTTPProvider(infura_url))

# Check that you are connected to a node synced with the latest block
latest_block = w3.eth.blockNumber
print('Latest block number:', latest_block)

# Load the contract using Web3.py
contract = w3.eth.contract(address=contract_address, abi=abi)

# Create a filter for the mempool
event_filter = w3.eth.filter({
    'topics': [event_signature],
    'fromBlock': 'pending',
    'toBlock': 'latest',
})

# Get the matching transactions from the filter
tx_hashes = event_filter.get_all_entries()

# Get the full transaction objects
txs = [w3.eth.get_transaction(tx_hash) for tx_hash in tx_hashes]

# Print the transaction details
for tx in txs:
    print('Tx hash:', tx.hash.hex())
    print('From:', tx['from'])
    print('To:', tx['to'])
    print('Value:', tx['value'])
