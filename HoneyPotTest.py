import json
from web3 import Web3
import time
import subprocess
import requests
import DBQueries
import buyandhold

config = json.load(open('config.json'))
my_wallet = Web3.toChecksumAddress(config['public_key'])
evm_routerV2_abi = open('evm_routerV2_abi', 'r').read().replace('\n', '')
private = config['private_key']


# use block explorer api to fetch token source code
def verified_contract_test(honeypot, token, network, exchange):
    db_queries = DBQueries
    r = requests.get(network["api_url"] + token + '&apikey=' + network["api_key"])
    source = r.json()
    print(source["result"][0]["ABI"])
    if source["result"][0]["ABI"] != 'Contract source code not verified':
        print("TOKEN PASSES VERIFIED CONTRACT REQUIREMENT")
        db_queries.add_token(token, 1, 1, honeypot, network["network_id"], exchange["name"])
    else:
        print("TOKEN FAILS VERIFIED CONTRACT REQUIREMENT")
        db_queries.add_token(token, 0, 0, honeypot, network["network_id"], exchange["name"])


def loop_tokens(exchange, network):
    try:
        print('Forking: ' + network["name"] + ', Using Exchange: ' + exchange['name'])
        rpc_url = network["rpc_url"]
        if network["rpc_key"] != "":
            network_url = rpc_url + network["rpc_key"]
        else:
            network_url = rpc_url
        print('open fork')
        subprocess.Popen(['./fork.sh', network_url, str(exchange["port"])])
        print('fork opened')
        time.sleep(4)
        with open('newtokens.txt') as f:
            tokens = f.read().splitlines()
        for token in tokens:
            buy_sell(token, exchange, network)
        open('newtokens.txt', 'w').close()
        print('HONEY POT TEST COMPLETE')
    except Exception as e:
        print(e)


def buy_sell(shit_coin, exchange, network):
    try:
        ganache_url = 'http://127.0.0.1:' + str(exchange["port"])
        web3 = Web3(Web3.HTTPProvider(ganache_url))

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
            'value': web3.toWei(.01, 'ether'),  # This is the Token(BNB) amount you want to Swap from
            'gas': 250000,
            'gasPrice': web3.toWei('5', 'gwei'),
            'nonce': nonce,
        })
        signed_txn = web3.eth.account.sign_transaction(v2router_buy, private_key=private)
        web3.eth.send_raw_transaction(signed_txn.rawTransaction)

        # getting balance of shitcoin and new tx nonce
        evm_token_abi = '[{"inputs":[{"internalType":"string","name":"_NAME","type":"string"},{"internalType":"string","name":"_SYMBOL","type":"string"},{"internalType":"uint256","name":"_DECIMALS","type":"uint256"},{"internalType":"uint256","name":"_supply","type":"uint256"},{"internalType":"uint256","name":"_txFee","type":"uint256"},{"internalType":"uint256","name":"_lpFee","type":"uint256"},{"internalType":"uint256","name":"_MAXAMOUNT","type":"uint256"},{"internalType":"uint256","name":"SELLMAXAMOUNT","type":"uint256"},{"internalType":"address","name":"routerAddress","type":"address"},{"internalType":"address","name":"tokenOwner","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"minTokensBeforeSwap","type":"uint256"}],"name":"MinTokensBeforeSwapUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"tokensSwapped","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"ethReceived","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"tokensIntoLiqudity","type":"uint256"}],"name":"SwapAndLiquify","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"bool","name":"enabled","type":"bool"}],"name":"SwapAndLiquifyEnabledUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[],"name":"_liquidityFee","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"_maxTxAmount","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"_owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"_taxFee","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"claimTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"subtractedValue","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"tAmount","type":"uint256"}],"name":"deliver","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"excludeFromFee","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"excludeFromReward","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"geUnlockTime","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"includeInFee","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"includeInReward","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"addedValue","type":"uint256"}],"name":"increaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"isExcludedFromFee","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"isExcludedFromReward","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"time","type":"uint256"}],"name":"lock","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"numTokensSellToAddToLiquidity","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tAmount","type":"uint256"},{"internalType":"bool","name":"deductTransferFee","type":"bool"}],"name":"reflectionFromToken","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"liquidityFee","type":"uint256"}],"name":"setLiquidityFeePercent","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"maxTxPercent","type":"uint256"}],"name":"setMaxTxPercent","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"swapNumber","type":"uint256"}],"name":"setNumTokensSellToAddToLiquidity","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bool","name":"_enabled","type":"bool"}],"name":"setSwapAndLiquifyEnabled","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"taxFee","type":"uint256"}],"name":"setTaxFeePercent","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"swapAndLiquifyEnabled","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"rAmount","type":"uint256"}],"name":"tokenFromReflection","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalFees","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"uniswapV2Pair","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"uniswapV2Router","outputs":[{"internalType":"contract IUniswapV2Router02","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"unlock","outputs":[],"stateMutability":"nonpayable","type":"function"},{"stateMutability":"payable","type":"receive"}]'
        token_contract = web3.eth.contract(abi=evm_token_abi, address=contract_id)
        balance = token_contract.functions.balanceOf(my_wallet).call()
        nonce = web3.eth.get_transaction_count(my_wallet)

        approve = token_contract.functions.approve(router_address, balance).buildTransaction({
            'from': my_wallet,
            'gasPrice': web3.toWei('5', 'gwei'),
            'nonce': nonce,
        })
        approve_tx = web3.eth.account.sign_transaction(approve, private_key=private)
        web3.eth.send_raw_transaction(approve_tx.rawTransaction)
        time.sleep(4)

        # create, sign, send second tx
        print('SELLING TOKEN')
        v2router_sell = contract.functions.swapExactTokensForETHSupportingFeeOnTransferTokens(
            (int(balance - (5 * 250000))),
            0,
            [contract_id, spend],
            my_wallet,
            (int(time.time()) + 1000000)
        ).buildTransaction({
            'from': my_wallet,
            'gasPrice': web3.toWei('5', 'gwei'),
            'nonce': web3.eth.get_transaction_count(my_wallet),
        })
        signed_txn2 = web3.eth.account.sign_transaction(v2router_sell, private_key=private)
        web3.eth.send_raw_transaction(signed_txn2.rawTransaction)

    except Exception as inst:
        # token is likely a honey pot
        print(inst)
        print("------")
        print("Error Occurred, skipping token " + shit_coin)
        if network["name"] == 'Aurora':
            new_buy_and_hold = buyandhold
            new_buy_and_hold.buy(shit_coin, exchange, network)
        verified_contract_test(1, shit_coin, network, exchange)
    else:
        # token is not a honeypot right now
        verified_contract_test(0, shit_coin, network, exchange)
        print("Transaction successfully sent to blockchain.")
        print("------")
