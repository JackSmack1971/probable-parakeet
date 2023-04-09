import pytest
from unittest import mock
from frontrunning_bot import calculate_gas_price, create_new_tx, broadcast_tx

def test_calculate_gas_price(w3, contract):
    tx = {
        'from_address': '0x1234...',
        'to': contract.address,
        'value': 1000000000000000000,
        'gas': 100000,
        'gasPrice': 20000000000,
        'nonce': 0,
        'input': contract.functions.transfer('0x5678...', 100000000000000000).buildTransaction({'from': '0x1234...'})['data']
    }

    def mock_calculate_expected_profit(w3, tx, gas_price):
        return tx['value'] - gas_price * tx['gas']

    with mock.patch('frontrunning_bot.calculate_expected_profit', side_effect=mock_calculate_expected_profit):
        gas_price = calculate_gas_price(w3, tx)
        assert gas_price > tx['gasPrice']

    tx['value'] = 10000000000000000  # 0.01 ETH
    with mock.patch('frontrunning_bot.calculate_expected_profit', side_effect=mock_calculate_expected_profit):
        with pytest.raises(ValueError):
            calculate_gas_price(w3, tx)

def test_create_new_tx(w3, contract, YOUR_PRIVATE_KEY):
    tx = {
        'from': '0x1234...',
        'to': contract.address,
        'value': 1000000000000000000,
        'gas': 100000,
        'gasPrice': 20000000000,
        'nonce': 0,
        'input': contract.functions.transfer('0x5678...', 100000000000000000).buildTransaction({'from': '0x1234...'})['data']
    }

    def mock_encode_abi(types, values):
        return b'\x00\x01'

    with mock.patch('eth_abi.encode_abi', side_effect=mock_encode_abi):
        new_tx = create_new_tx(w3, tx, 22000000000, YOUR_PRIVATE_KEY)
        assert new_tx['gasPrice'] == 22000000000
        assert new_tx['nonce'] == 0

def test_broadcast_tx(w3):
    new_tx = w3.eth.account.sign_transaction({
        'from': '0x1234...',
        'to': CONTRACT_ADDRESS,
        'value': 1000000000000000000,
        'gas': 100000,
        'gasPrice': 22000000000,
        'nonce': 0,
        'data': b'\x00\x01',
    }, private_key=YOUR_PRIVATE_KEY)

    def mock_send_raw_transaction(raw_transaction):
        return b'\x00' * 32

    with mock.patch('web3.eth.Eth.send_raw_transaction', side_effect=mock_send_raw_transaction):
        with mock.patch('logging.info') as log_info_mock:
            broadcast_tx(w3, new_tx)
            log_info_mock.assert_called_with('Broadcasting transaction: %s', '0x' + '00' * 32)
