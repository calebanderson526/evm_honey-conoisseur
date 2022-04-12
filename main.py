from web3 import Web3
import asyncio
import HoneyPotTest
import json
from web3.middleware import local_filter_middleware

network_config = json.load(open('network_config.json'))
test_interval = 1  # program runs honeypot test every 1 tokens


def handle_event(event):
    if Web3.toJSON(event)[21:25] != "0xbb":
        print('Token spotted: ' + Web3.toJSON(event)[21:63])
        # write to new token txt file
        address = Web3.toJSON(event)[21:63]
        with open('newtokens.txt', 'a') as f:
            f.write(address + '\n')
    else:
        print('Token spotted: ' + Web3.toJSON(event)[77:119])
        # write to new token txt file
        address = Web3.toJSON(event)[77:119]
        with open('newtokens.txt', 'a') as f:
            f.write(address + '\n')


async def look_for_pairs(exchange, network):
    print('Creating task for: ' + network["name"] + ', Using Exchange: ' + exchange['name'])
    # blockchain connection information
    rpc_url = network["rpc_url"]
    if network["rpc_key"] != "":
        network_url = rpc_url + network["rpc_key"]
    else:
        network_url = rpc_url

    web3 = Web3(Web3.HTTPProvider(network_url))
    web3.middleware_onion.add(local_filter_middleware)

    # factory address and abi
    factory_address = exchange["factory"]
    factory_abi = open('evm_factory_abi', 'r').read().replace('\n', '')
    contract = web3.eth.contract(address=factory_address, abi=factory_abi)
    event_filter = contract.events.PairCreated.createFilter(fromBlock='latest')
    count = 0
    while True:
        try:
            for PairCreated in event_filter.get_new_entries():
                print('Found token in Network: ' + network["name"] + ', Using Exchange: ' + exchange['name'])
                handle_event(PairCreated)
                count = count + 1
                if count >= test_interval:
                    print('Forking blockchain and running tests')
                    new_hp_test = HoneyPotTest
                    new_hp_test.loop_tokens(exchange, network)
                    count = 0
            await asyncio.sleep(network["block_time"] * 0.8)
        except Exception as inst:
            event_filter = contract.events.PairCreated.createFilter(fromBlock='latest')


async def main():
    print('Searching for tokens')
    for network in network_config["networks"]:
        for exchange in network["exchanges"]:
            task = asyncio.create_task(look_for_pairs(exchange, network))
    await task


if __name__ == "__main__":
    asyncio.run(main())
else:
    pass
