from web3 import Web3
import json
import time

config = json.load(open('config.json'))
my_wallet = Web3.toChecksumAddress(config['public_key'])
evm_routerV2_abi = open('evm_routerV2_abi', 'r').read().replace('\n', '')
private = config['private_key']


def buy(shit_coin, exchange, network):
    node_url = network["rpc_url"]
    web3 = Web3(Web3.HTTPProvider(node_url))

    # v2router
    router_address = web3.toChecksumAddress(exchange["router"])
    spend = web3.toChecksumAddress(network["native_token"])

    # v2router contract and tx nonce
    contract_id = web3.toChecksumAddress(shit_coin)
    contract = web3.eth.contract(address=router_address, abi=evm_routerV2_abi)
    nonce = web3.eth.get_transaction_count(my_wallet)

    # create, sign, send first tx
    print('BUYING TOKEN')
    v2router_buy = contract.functions.swapExactETHForTokensSupportingFeeOnTransferTokens(
        0,
        [spend, contract_id],
        my_wallet,
        (int(time.time()) + 1000000)
    ).buildTransaction({
        'from': my_wallet,
        'value': web3.toWei(.00023, 'ether'),  # This is the Token(BNB) amount you want to Swap from
        'gas': 250000,
        'gasPrice': web3.toWei('5', 'gwei'),
        'nonce': nonce,
    })
    signed_txn = web3.eth.account.sign_transaction(v2router_buy, private_key=private)
    web3.eth.send_raw_transaction(signed_txn.rawTransaction)
