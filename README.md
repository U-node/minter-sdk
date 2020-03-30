<p align="center" background="black"><img src="UN_logo_on_white.svg" width="450"></p>

<p align="center">
</p>

Python SDK

Ported from official Minter's <a href="https://github.com/MinterTeam/minter-php-sdk">php SDK</a>

Created by <a href="https://www.u-node.net">https://www.u-node.net</a>'s masternode co-founder Roman Matusevich 

You can support our project by sending any Minter's coins to our wallet Mx6e0cd64694b1e143adaa7d4914080e748837aec9

Feel free to delegate to our 3% masternode Mp02bc3c3f77d5ab9732ef9fc3801a6d72dc18f88328c14dc735648abfe551f50f


# Installation
`pip install minter-sdk`



# Using API
```python
from mintersdk.minterapi import MinterAPI

node_url = 'https://minter-node-1.testnet.minter.network:8841'  # Example of a node url
api = MinterAPI(api_url=node_url)

# 'connect_timeout', 'read_timeout', 'headers' kwargs would be passed to request, if provided
api = MinterAPI(api_url=node_url, connect_timeout=1, read_timeout=3, headers={})
```
Numeric strings automatically are converted to integers in `response['result']` dict.

Some API methods accept `pip2bip (bool)` argument to convert coin values from PIP to BIP.  
Values are `Decimal` type after conversion.

## Methods
- `get_addresses(addresses, height=None, pip2bip=False)`  
  Returns addresses balances.
  
- `get_balance(address, height=None, pip2bip=False)`  
  Returns coins list, balance and transaction count (for nonce) of an address.

- `get_block(height, pip2bip=False)`
  Returns block data at given height.
  
- `get_candidate(public_key, height=None, pip2bip=False)`  
  Returns candidate’s info by provided public_key. It will respond with 404 code if candidate is not found.
  
- `get_candidates(height=None, include_stakes=False, pip2bip=False)`  
  Returns list of candidates.
  
- `get_coin_info(symbol, height=None, pip2bip=False)`  
  Returns information about coin. Note: this method does not return information about base coins (MNT and BIP).
  
- `get_events(height, pip2bip=False)`  
  Returns events at given height.
  
- `get_genesis(pip2bip=False)`  
  Return network genesis.
  
- `get_latest_block_height()`  
  Returns latest block height.
  
- `get_max_gas_price(height=None)`  
  Returns current max gas price.
  
- `get_min_gas_price()`  
  Returns current min gas price.
  
- `get_missed_blocks(public_key, height=None)`  
  Returns missed blocks by validator public key.
  
- `get_network_info()`  
  Return node network information.
  
- `get_nonce(address)`  
  Returns next transaction number (nonce) of an address.
  
- `get_status()`  
  Returns node status info.
  
- `get_transaction(tx_hash, pip2bip=False)`  
  Returns transaction info.
  
- `get_transactions(query, page=None, limit=None, pip2bip=False)`  
  Return transactions by query.
  
- `get_unconfirmed_transactions(limit=None)`  
  Returns unconfirmed transactions.
  
- `get_validators(height=None, page=None, limit=None)`  
  Returns list of active validators.
  
- `estimate_coin_buy(coin_to_sell, value_to_buy, coin_to_buy, height=None, pip2bip=False)`  
  Return estimate of buy coin transaction.  
  Provide value in PIP if `pip2bip is False` or in BIP if `pip2bip is True`
  
- `estimate_coin_sell(coin_to_sell, value_to_sell, coin_to_buy, height=None, pip2bip=False)`  
  Return estimate of sell coin transaction.  
  Provide value in PIP if `pip2bip is False` or in BIP if `pip2bip is True`
  
- `estimate_coin_sell_all(coin_to_sell, value_to_sell, coin_to_buy, height=None, pip2bip=False)`  
  Return estimate of sell all coin transaction.  
  Provide value in PIP if `pip2bip is False` or in BIP if `pip2bip is True`
  
- `estimate_tx_commission(tx, height=None, pip2bip=False)`  
  Return estimate of transaction.
  
- `send_transaction(tx)`  
  Returns the result of sending signed tx.



# SDK use
## Create transactions
Each Minter transaction requires `nonce, gas_coin` to be passed.  Also you can pass `payload, chain_id, gas_price`.

`MiterTx(nonce, gas_coin, payload='', service_data='', chain_id=1, gas_price=1, **kwargs)`

**To create Minter transaction you MUST use concrete transaction class.**

All transaction values should be passed in BIP, you shouldn't convert them to PIP.  
All coin symbols are case insensitive, e.g. you can pass `gas_coin='BIP'` or `gas_coin='bip'`

### Transactions
- MinterBuyCoinTx
  ```python
  from mintersdk.sdk.transactions import MinterBuyCoinTx
  tx = MinterBuyCoinTx(coin_to_buy='SYMBOL', value_to_buy=1, coin_to_sell='SYMBOL', max_value_to_sell=2, nonce=1, gas_coin='SYMBOL')
  ```
  
- MinterCreateCoinTx
  ```python
  from mintersdk.sdk.transactions import MinterCreateCoinTx
  tx = MinterCreateCoinTx(name='Coin description', symbol='SYMBOL', initial_amount=1.5, initial_reserve=10000, crr=50, max_supply=1000, nonce=1, gas_coin='SYMBOL')
  ```
  
- MinterDeclareCandidacyTx
  ```python
  from mintersdk.sdk.transactions import MinterDeclareCandidacyTx
  tx = MinterDeclareCandidacyTx(address='Mx...', pub_key='Mp...', commission=1, coin='SYMBOL', stake=100, nonce=1, gas_coin='SYMBOL')
  ```
  
- MinterDelegateTx
  ```python
  from mintersdk.sdk.transactions import MinterDelegateTx
  tx = MinterDelegateTx(pub_key='Mp...', coin='SYMBOL', stake=100, nonce=1, gas_coin='SYMBOL')
  ```
  
- MinterRedeemCheckTx
  ```python
  from mintersdk.sdk.transactions import MinterRedeemCheckTx
  tx = MinterRedeemCheckTx(check='check hash str', proof='proof hash str', nonce=1, gas_coin='SYMBOL')
  ```
  
- MinterSellAllCoinTx
  ```python
  from mintersdk.sdk.transactions import MinterSellAllCoinTx
  tx = MinterSellAllCoinTx(coin_to_sell='SYMBOL', coin_to_buy='SYMBOL', min_value_to_buy=100, nonce=1, gas_coin='SYMBOL')
  ```
  
- MinterSellCoinTx
  ```python
  from mintersdk.sdk.transactions import MinterSellCoinTx
  tx = MinterSellCoinTx(coin_to_sell='SYMBOL', value_to_sell=1, coin_to_buy='SYMBOL', min_value_to_buy=2, nonce=1, gas_coin='SYMBOL')
  ```
  
- MinterSendCoinTx
  ```python
  from mintersdk.sdk.transactions import MinterSendCoinTx
  tx = MinterSendCoinTx(coin='SYMBOL', to='Mx...', value=5, nonce=1, gas_coin='SYMBOL')
  ```
  
- MinterMultiSendCoinTx
  ```python
  from mintersdk.sdk.transactions import MinterMultiSendCoinTx
  
  txs = [
      {'coin': 'SYMBOL', 'to': 'Mx..1', 'value': 5},
      {'coin': 'SYMBOL', 'to': 'Mx..2', 'value': 1},
      {'coin': 'SYMBOL', 'to': 'Mx..3', 'value': 4}
  ]
  tx = MinterMultiSendCoinTx(txs=txs, nonce=1, gas_coin='SYMBOL')
  ```
  
- MinterSetCandidateOffTx
  ```python
  from mintersdk.sdk.transactions import MinterSetCandidateOffTx
  tx = MinterSetCandidateOffTx(pub_key='Mp...', nonce=1, gas_coin='SYMBOL')
  ```
  
- MinterSetCandidateOnTx
  ```python
  from mintersdk.sdk.transactions import MinterSetCandidateOnTx
  tx = MinterSetCandidateOnTx(pub_key='Mp...', nonce=1, gas_coin='SYMBOL')
  ```
  
- MinterUnbondTx
  ```python
  from mintersdk.sdk.transactions import MinterUnbondTx
  tx = MinterUnbondTx(pub_key='Mp...', coin='SYMBOL', value=100, nonce=1, gas_coin='SYMBOL')
  ```
  
- MinterEditCandidateTx
  ```python
  from mintersdk.sdk.transactions import MinterEditCandidateTx
  tx = MinterEditCandidateTx(pub_key='Mp...', reward_address='Mx...', owner_address='Mx...', nonce=1, gas_coin='SYMBOL')
  ```


## Sign transaction
When your transaction object is created, you can sign it.
Every transaction can be signed by private key or/and by signature.  
Keep in mind, we have some `tx = MinterSomeTx(...)` and API `api = MinterAPI(...)`

- Sign single signature type transaction
  ```python
  # Sign with private key
  tx.sign(private_key='PRIVATE_KEY')
  
  # Sign with signature
  tx.signature_type = tx.SIGNATURE_SINGLE_TYPE
  
  signature = tx.generate_signature(private_key='PRIVATE_KEY')
  
  tx.sign(signature=signature)
  ```
  
- Sign multi signature type transaction
  ```python
  # Sign with private keys
  tx.sign(private_key=['PRIVATE_KEY_1', 'PRIVATE_KEY_2', ...], ms_address='Multisig address Mx...')
  
  # Sign with signatures
  tx.signature_type = tx.SIGNATURE_MULTI_TYPE
  
  signature_1 = tx.generate_signature(private_key='PRIVATE_KEY_1')
  signature_2 = tx.generate_signature(private_key='PRIVATE_KEY_2')
  
  tx.sign(signature=[signature_1, signature_2], ms_address='Multisig address Mx...')
  
  # Sign with both private keys and signatures
  tx.signature_type = tx.SIGNATURE_MULTI_TYPE
  
  private_key_1 = 'PRIVATE_KEY_1'
  private_key_2 = 'PRIVATE_KEY_2'

  signature_1 = tx.generate_signature(private_key='PRIVATE_KEY_3')
  signature_2 = tx.generate_signature(private_key='PRIVATE_KEY_4')
  
  tx.sign(private_key=[private_key_1, private_key_2], signature=[signature_1, signature_2], ms_address='Multisig address Mx...'))
  ```
  
As you see above, to generate signature we must set transaction `signature_type` before generating signature.  

You can set this argument while creating transaction.  
`tx = MinterSomeTx(..., signature_type=MinterTx.SIGNATURE_MULTI_TYPE)`  
`tx = MinterSomeTx(..., signature_type=MinterTx.SIGNATURE_SINGLE_TYPE)`  

After that you can simply generate signature without setting it's signature type by overriding attribute.   
`signature = tx.generate_signature(private_key='PRIVATE_KEY')`

### Adding signature to multi signature type transaction
When multi signature transaction is created it can be partially signed, e.g. signed by 2 of 3 private keys.  
Then partially signed transaction can be transferred to another client and this client can add own signature to transaction.  
```python
from mintersdk.sdk.transactions import MinterTx

# Client 1
# Create transaction
tx = MinterSomeTx(...)

# Sign transaction
tx.sign(private_key=['PK_1', 'PK_2'], ms_address='Mx...')

# Then tx.signed_tx is transferred to Client 2


# Client 2
# Received raw_tx (tx.signed_tx from Client 1)
tx = MinterTx.add_signature(signed_tx=raw_tx, private_key='PK_3')
```  
Client 2 will get new tx object with client's 2 signature.  
Client 2 may pass `tx.signed_tx` to next client or just send `tx.signed_tx` to the network.


## Send transaction
When transaction is created and signed, you can send transaction to network. Signed transaction for sending can be found in `tx.signed_tx` attribute.  
```python
# Create transaction
tx = MinterSomeTx(...)

# Sign transaction
tx.sign(...)

# Send transaction
response = api.send_transaction(tx=tx.signed_tx)
```



# Create transaction from raw
You can create transaction object from raw transaction hash. You will get tx object of tx type.

```python
from mintersdk.sdk.transactions import MinterTx

tx = MinterTx.from_raw(raw_tx='...')
```



# Minter deeplink
Let's create a MinterSendCoinTx
```python
from mintersdk.sdk.transactions import MinterSendCoinTx
tx = MinterSendCoinTx(coin='BIP', to='Mx18467bbb64a8edf890201d526c35957d82be3d95', value=1.23456789, nonce=1, gas_coin='MNT', gas_price=1, payload='Hello World')
```

Now it's time to create deeplink
```python
from mintersdk.sdk.deeplink import MinterDeeplink
dl = MinterDeeplink(tx=tx, data_only=False)

# Deeplink is generated by all tx params (nonce, gas_price, gas_coin, payload) by default.
# If you want to create deeplink only by tx data, set `data_only=True`
```

After deeplink object is created, you can override it's attributes, e.g.
```python
dl = MinterDeeplink(tx=tx)
dl.nonce = ''
dl.gas_coin = 'MNT'
dl.gas_price = 10
```

When your deeplink object is ready, generate it
```python
url_link = dl.generate()

# If password check is needed, pass password to generate method
url_link = dl.generate(password='mystrongpassword')
```

Then you might want to create QR-code from your deeplink
```python
from mintersdk import MinterHelper
qr_code_filepath = MinterHelper.generate_qr(text=url_link)

# For additional params information for `MinterHelper.generate_qr()`, please see sourcecode for this method.
```



# Minter check
## Create and sign check
```python
from mintersdk.sdk.check import MinterCheck

# Create check without password
check = MinterCheck(nonce=1, due_block=300000, coin='MNT', value=1, gas_coin='MNT')

# Or create check with password
check = MinterCheck(nonce=1, due_block=300000, coin='MNT', value=1, gas_coin='MNT', passphrase='pass')

# Sign check
signed_check = check.sign(private_key='PRIVATE_KEY')
```


## Create proof
```python
from mintersdk.sdk.check import MinterCheck

proof = MinterCheck.proof(address='Mx...', passphrase='pass')
```


## Create check object from raw
```python
from mintersdk.sdk.check import MinterCheck

# Create and sign check
check = MinterCheck(nonce=1, due_block=300000, coin='MNT', value=1, gas_coin='MNT')
signed_check = check.sign(private_key='PRIVATE_KEY')

# Create object from signed check
check = MinterCheck.from_raw(rawcheck=signed_check)
```



# Minter Wallet
```python
from mintersdk.sdk.wallet import MinterWallet

# Create new wallet
wallet = MinterWallet.create()

# Get wallet data from existing mnemonic
wallet = MinterWallet.create(mnemonic='YOUR MNEMONIC PHRASE')
```



# Helpers
## Convert between PIP and BIP
```python
from mintersdk.shortcuts import to_pip, to_bip

# Get BIP from PIP
pip_value = 1000000000000000000
bip_value = to_bip(pip_value)

# Get PIP from BIP
bip_value = 100
pip_value = to_pip(bip_value)
```
