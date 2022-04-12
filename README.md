# evm_honey-conoisseur
This program will get all new tokens from any number of networks and exchanges that you specify (in network_config.json) to then test if the token is a honey pot and if the token is verified on the block explorer. It's currently set up to watch PancakeSwap and BiSwap on BSC, as well as Trisolaris on Aurora. There's an option to buy every token that passes the honey pot test, with the current configuration set up to buy tokens on the Aurora network. Use at your own risk, there's more ways to hide a scam on the blockchain than detect one algorithmically. Honey pots can also be turned on and off, so just because it's not a honey pot now doesn't mean it won't be soon.

Quickstart:
1. Update the config.json file with your evm crypto wallet private key, public key, as well as database connection info if you are planning on using the database functionality.

2. Add your block explorer (i.e: bscscan, etherscan, aurorascan) api key to the network_config.json file. If you are planning on using this on the ETH network or another network with a non-public rpc endpoint, add your rpc api key to the network_config.json file, otherwise leave it blank.

3. If you want to use this without a database, delete the DBQueries.py file and remove all lines that cause an error. Soon there should be an option to make doing this much easier, as well as utilizing text files instead.

Roadmap:
1. **WEBSITE**
2. More thorough testing of the tokens
3. Add option to use text files instead of database for simpler set-up
4. Suggestions?

This program uses a SQL server database, make sure to create the TokenTest database and Tokens table as well as add all the correct database connection info to the config.json file.
